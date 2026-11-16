# Findings

**Status: negative result / data-blocked.** No AP entry, no NPT disable, no
kernel-text read, no Linux boot. The game SSD was not written. The wake test
restored the `#DB` gate and all 16 TSS IST6 rows and returned the console to
Orbis.

## Summary

The 8.20 port is blocked by missing information, not by a missing payload
trick:

1. The 8.20 trigger in the resume path **after `resumectx` and before
   `acpi_wakeup_cpus`**. The writeup's `acpi_sleep_machdep+0x18e` does not map
   to 8.20; the derived candidate `0x9C9E4E` did not fire.
2. The 8.20 kernel text and the real AP-start ABI. The offset table is
   inherited from 8.00; `ACPI_SLEEP_MACHDEP_HOOK` is missing.
3. The 8.20 stopped-CPU mask / AP-parking state. The stock AP loop appears to
   be skipped, and no stopped-mask address is verified.

The work did establish the kernel-side primitives and found the exact reason
the current AP route fails: **the proven `0x9CA20F` hook is after the AP loop**.

## 1. The AP loop runs before hc 0x10

The 13.60 live dump shows `acpi_wakeup_cpus` at `ktext+0x3913B0`:

```text
mov eax, [mp_ncpus]        ; 16
mov rcx, [stopped_cpus]    ; 0xfffe
bt rcx, cpu                ; CPUs 1..15
call per_ap_function       ; ktext+0x391780
call hc_0x10_wrapper       ; ktext+0xC16F00
```

The per-AP function calls hc `0x0F` with `(selector, MP_STARTUP_INIT_VECTOR,
cr3)`. The AP loop is **before** the hc `0x10` call.

The 8.20 structural twin:

```text
acpi_wakeup_cpus entry     ktext+0x9CA170
hc 0x10 call               ktext+0x9CA20F
per-AP function            ktext+0x9CA540
stock hc 0x0F call         ktext+0x9CA5C9
```

The `0x9CA20F` hook fires reliably, but it is after the loop. Every AP launch
there failed. The stock call site `0x9CA5C9` was tested and did not fire; the
function entry `0x9CA170` did not fire; the 13.60-derived earlier trigger
`0x9C9E4E` did not fire.

**Significance.** The current AP route is the wrong point in the control flow.
An 8.20 port must trigger **before** the loop, or force the stopped mask so the
loop enters the per-AP function.

**Next.** Use `0x9CA20F` only for read-only instrumentation: a stack capture to
identify the caller and the real pre-loop trigger. Do not call hc `0x0F` there
again.

## 2. Safe wake instrumentation

A DR0 execution breakpoint at `ktext+0x9CA20F` is delivered through the kernel
`#DB` gate with IST6. The wake-marker build arms with mask `0x56000043`, enters
rest, wakes, and returns to Orbis:

```text
BOOT mask=0x56000043
KHPRE len=0x50
KHINSTALL-OK
REST-RETURNED cpu=15
KHFRAMEPOST rip=...a20f cs=0x20 rflags=0x46
APMARKPOST rop=0x484f4f4b ap=0x0
```

The build saves the gate and all 16 TSS IST6 rows before arming, restores them
unconditionally after wake, and clears DR7:

```text
GATERESTORE rc=0
TSSIST restore rc=0
```

The khook wake chain/dispatch does not execute. A marker-only chain with
correct `DISP0`, `DISP1` and chain contents never landed its single store
(`mark=0`).

**Significance.** The hook is safe for read-only instrumentation. It is not a
working AP-launch mechanism.

## 3. Offset table and gadget validation

The 8.20 table is almost byte-for-byte the 8.00 table:

- `ACPIGBL_FACS`: `0x38F75A0` (8.20) vs `0x38F7590` (8.00).
- `IDT`, `COMMON_TSS`, `FUN_MEMCPY`: identical.
- `HV_MP_STARTUP_CALL`: `0xBC40F0` (8.20) vs `0xBC2C60` (8.00).
- `MP_STARTUP_INIT_VECTOR`: `0x2A5E28` (8.20) vs `0x2A5860` (8.00).
- `ACPI_SLEEP_MACHDEP_HOOK`: **missing**.

`HV_MP_STARTUP_CALL = 0xBC40F0` is the hc **0x10** wrapper, not hc `0x0F`. The
hc `0x0F` candidate `0xBC40D0` was not validated. `ST_RCX_RAX` (`0x3061A2`) is
rejected. `SET_DR7` is ambiguous. Several gadgets are missing.

**Significance.** A name in the table is not a validation. Using an
unvalidated gadget can crash or brick the console.

## 4. Memory boundary and NPT wall

- QA page: `SSLP` structure, QA field at `+0x88` = `0x10300`. Only one copy in
  the 64 KB page. The QA-bit sweep did not clear XOTEXT, so the QA route is
  closed.
- Safe data window: `[QA-0x903000, QA-0x103000)` (8 MB). The preceding pages
  are execute-only kernel text; a 12 MB backward dump entered that text.
- Hypercall table: at `QA-0x2DAC00`; entry 0 is `0xfebb9cf0`, and
  `table_va + entry = ktext+0xBC40F0`.
- The table page is RO/NX. A dmap alias with `RW=1` maps the same physical
  page, but a no-op write through it did not complete. The **NPT** blocks the
  write, not the guest PTE.

**Significance.** 8.20 kernel data is readable; kernel text is not. The guest
page tables are insufficient. A root-0 AP payload or a new primitive is
required.

## 5. PUP extraction

The 8.20.02 system PUP (MD5 `a3aad7f04e84230e72af02f7c458d05a`) decrypted
on-console. The host unpack produced plaintext exFAT rootfs images containing
`libkernel.sprx`, `SceSysCore.elf`, `eap_kernel.ebin` and VSH/app files.

The x86 `5_kernel.bin` is still encrypted: 22,947,328 B, entropy 8.000, no
ELF/SELF magic. Its table segment (`16_for_5.img`) is also encrypted (entropy
7.850). The recovery PUP contains no kernel.

**Significance.** The PUP route gives the rootfs, not the kernel text. The
per-binary key is in console secure storage.

## 6. Next step

The highest-value 8.20 experiment is a read-only stack capture at the proven
`0x9CA20F` hook:

1. Reuse the wake-marker hook and the all-16 IST6 gate.
2. In the handler, store `RSP` and 8–16 kernel-stack qwords to the data
   oracle. Do not install a wake chain, call hc `0x0F`, or write NPT.
3. After wake, read the oracle and look for return addresses in the
   `0x9C8xxx`/`0x9C9xxx` range.
4. Map the caller against the 13.60 `acpi_sleep_machdep` shape and identify
   the pre-loop trigger.

If the stack is ambiguous, stop. Do not resume the `0x9CA20F` AP chain.

## Approaches not to repeat

- hc `0x0F` at `0x9CA20F`, or any new khook wake-chain variant.
- `0x9CA5C9` without a verified stopped-mask address.
- The `0xBC40D0` wrapper probe.
- Guest-side writes to the hypercall table page.
- The QA-bit sweep.
- `ST_RCX_RAX` (`0x3061A2`) and the shared-gate/row-0 handler.
- PUP extraction as a kernel-text source.
- Blind trigger candidates derived from 13.60 offsets.

## Limitations

- The 13.60 disassembly is from a full live kernel dump.
- The 8.20 mapping is **structural**, not a direct 8.20 text disassembly.
- The 8.20 stopped-mask address is unknown; `0x3F9F974` is a false candidate.
- No AP, NPT, kernel-text or Linux claim is made.

## Credits

See [CREDITS.md](CREDITS.md). This work builds on theflow0, soniciso1,
EchoStretch, PS5Dev, terrafirma2021, R0nov4, gzimbric, John Törnblom /
ps5-payload-dev, zecoxao and the PUP tool contributors, RamalhoBoss, Pharaoh2k,
kstuff-lite, and the ps5-linux maintainers.
