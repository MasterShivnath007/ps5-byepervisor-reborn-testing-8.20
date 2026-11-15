# Research roadmap — Byepervisor Reborn on 8.20

## Objective

A verified, repeatable 8.20 flow that:

1. enters the S3-resume AP-start window and starts an AP under NPT root 0;
2. locates the GameOS VMCBs and disables NPT;
3. reads and writes kernel text;
4. hands off to the Linux kernel and reaches userland.

A wake to Orbis is not success.

## Current state

Proven:

- kernel data read/write and a reliable rest/wake cycle;
- the `0x9CA20F` wake hook fires and the `#DB` gate plus all 16 IST6 rows
  restore;
- the 13.60 AP-loop order and the 8.20 structural mapping;
- the 8.20 PUP container/rootfs decrypt.

Blocked:

- the pre-loop S3 trigger;
- the real 8.20 hc `0x0F` ABI and AP carrier behavior;
- the stopped-CPU mask / AP-parking state;
- the 8.20 kernel text and VMCB layout.

## Critical path

### 1. Recover the 8.20 kernel text or the pre-loop trigger

The PUP route is closed for kernel text: the x86 `5_kernel.bin` remains
encrypted behind console secure storage. Viable sources:

- a public or trusted 8.20 live kernel text dump;
- a live text-read primitive that does not depend on the blocked khook chain;
- a read-only stack capture at the proven `0x9CA20F` hook to identify the
  caller of `acpi_wakeup_cpus` and the pre-loop trigger.

### 2. Identify the pre-loop trigger

Use the 13.60 `acpi_sleep_machdep` / `acpi_wakeup_cpus` shape as the reference.
The 8.20 trigger must be reached after `resumectx` and before the AP loop. The
current `0x9CA20F` hook is after the loop and is only an instrumentation point.

### 3. Enter the AP

Once the trigger is known:

- call hc `0x0F` with the real 8.20 ABI: logical core, start RIP, CR3;
- use the carrier page at `0x3FFFF000` and the appropriate CR3;
- test an AP marker payload first; avoid parking if the stock path waits for
  the init callback.

### 4. VMCB discovery and NPT disable

From the root-0 AP payload:

- locate the 16 GameOS VMCBs;
- validate the nested-paging fields;
- clear the nested-paging enable on all cores;
- read back a known kernel-text address.

### 5. Linux handoff

After NPT is off and kernel text is readable, stage `bzImage` and `initrd` and
jump. Verify with the Linux console, not just a wake to Orbis.

## Next step

A **read-only stack capture at the proven `0x9CA20F` hook**:

1. Reuse the wake-marker hook and the all-16 IST6 gate.
2. In the handler, store `RSP` and 8–16 kernel-stack qwords to the data oracle.
3. Do not install a wake chain, call hc `0x0F`, or write NPT.
4. After wake, read the oracle and look for return addresses in the
   `0x9C8xxx`/`0x9C9xxx` range.
5. Map the caller against the 13.60 `acpi_sleep_machdep` shape and identify the
   pre-loop trigger.

Success criterion: a plausible caller/return address that maps to the 8.20
resume function. Stop if the stack is ambiguous or the console crashes; do not
guess.

## Decision tree

```text
8.20 kernel text or pre-loop trigger available?
├─ yes → hook the pre-loop trigger → AP marker → VMCB/NPT → Linux
└─ no
   ├─ public/trusted 8.20 live text dump? → disassemble → continue
   ├─ live text primitive? → dump text → continue
   └─ no → stop console launches; use the supported 11.60 path or wait for an artifact
```

## Alternative

The supported 11.60 path is hardware-validated for Byepervisor Reborn and
supported by `ps5-linux`. It is the high-probability route to Linux on this
console, at the cost of leaving 8.20.

## Required artifacts

- 8.20 kernel text or a live text dump.
- The pre-loop trigger / `acpi_sleep_machdep` offset.
- The hc `0x0F` wrapper and argument ABI.
- The stopped-CPU mask / AP-parking state.
- The HV heap / VMCB physical range.

## Rules

- One unproven mechanism per cold boot; true power cycle after a crash.
- No game-SSD writes.
- No blind chain variants or blind trigger candidates.
- Preserve exact logs and payload hashes.
- No public 8.20 support claim before a verified Linux boot.
