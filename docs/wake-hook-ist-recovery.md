# Safe 8.20 wake hook and IST recovery

**Summary:** A repeatable way to instrument the 8.20 wake path without losing
the console. Safe for read-only diagnostics; not a working AP-launch mechanism.

## Hook

- Target: `ktext+0x9CA20F`, the hc `0x10` call site in the 8.20
  `acpi_wakeup_cpus` twin.
- Mechanism: a DR0 execution breakpoint; the `#DB` is delivered through the
  kernel `#DB` gate with IST6.
- Mask: **`0x56000043`**. Do not use `0x5E000043`; bit `0x08000000` selects the
  read-only gadget dump and breaks the arm path.
- The wake-marker build arms, enters rest, wakes, and returns to Orbis.

## Gate and all 16 IST6 rows

The wake `#DB` can arrive on a CPU whose TSS row is not row 0. Programming only
row 0 is insufficient: the `#DB` falls back to the stock IST6 and the handler
does not run. The proven sequence:

- save all 16 TSS IST6 slots before arming;
- point every row at a valid handler stack while armed;
- restore the gate **and** all 16 IST6 slots unconditionally after wake;
- clear DR7 before restoring.

Hook evidence:

```text
BOOT mask=0x56000043
KHPRE len=0x50
KHINSTALL-OK
REST-RETURNED cpu=15
KHFRAMEPOST rip=...a20f cs=0x20 rflags=0x46
APMARKPOST rop=0x484f4f4b ap=0x0
```

Gate/IST evidence:

```text
GATERESTORE rc=0
TSSIST restore rc=0
```

## Proven and not proven

Proven:

- the hook fires at wake (`KHFRAMEPOST rip=ktext+0x9CA20F`);
- the console returns to Orbis;
- the gate and all 16 IST6 rows restore.

Not proven:

- wake chain/dispatch execution. A marker-only chain with correct `DISP0`,
  `DISP1` and chain contents never landed its single store (`mark=0`).
- AP entry, NPT access, or kernel text read.

Use this hook for **read-only instrumentation only**. Do not use it to call hc
`0x0F` or to run a wake chain.
## Test conditions

- Arm `ktext+0x9CA20F` with mask `0x56000043`; save the gate and all 16 TSS IST6
  slots before arming.
- Verify `KHFRAMEPOST rip=...a20f`, `GATERESTORE rc=0`, `TSSIST restore rc=0`.
- One payload per true cold boot; true power cycle after a crash; do not resend
  blindly.
