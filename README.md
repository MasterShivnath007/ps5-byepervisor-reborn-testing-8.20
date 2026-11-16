# PS5 Byepervisor Reborn Testing on 8.20

## Abstract

Technical investigation of the S3-resume `startup_mp` hypervisor path on a
retail PS5 running firmware **8.20.02** (`0x08200006`). The work establishes
the kernel-side primitives and identifies the control-flow and information
barriers that prevent a working Byepervisor Reborn port on this firmware. It
contains no exploit, firmware, keys, PUP/rootfs content, kernel dumps, or Linux
boot.

## Status

- No AP entry, no NPT disable, no kernel-text read, no Linux boot.
- The game SSD was not written. The console returned to Orbis after the wake
  test.
- The 8.20 route is data-blocked: the pre-loop trigger, the 8.20 kernel
  text/AP ABI, and the stopped-CPU mask are missing.

## Findings

1. **AP-loop ordering.** The stock AP loop runs before hc `0x10`; the proven
   `0x9CA20F` hook is after the loop. hc `0x0F` at that point is too late. The
   stock call site and earlier entry candidates did not fire.
2. **Safe wake instrumentation.** The `0x9CA20F` hook fires and the `#DB` gate
   plus all 16 TSS IST6 rows restore. The khook wake chain/dispatch does not
   execute, even a single store.
3. **Offset provenance.** The 8.20 table is inherited from 8.00.
   `HV_MP_STARTUP_CALL` is the hc `0x10` wrapper, not hc `0x0F`; the ACPI sleep
   offset is missing; several gadgets are unvalidated or rejected.
4. **Memory boundary.** 8.20 kernel data is readable in an 8 MB window. Kernel
   text is execute-only. The guest-visible hypercall table is present, but NPT
   blocks guest-side writes.
5. **PUP result.** The 8.20.02 PUP container and rootfs decrypt; the x86 kernel
   blob remains encrypted. No offline key was found.
6. **Next step.** A read-only stack capture at the proven wake hook to locate
   the pre-loop trigger. AP entry also requires the real hc `0x0F` ABI and the
   stopped-CPU mask.

## Documents

- [Findings](FINDINGS.md)
- [AP-loop analysis](docs/s3-ap-loop-analysis.md)
- [13.60 wrapper reference](docs/13.60-wrapper-reference.md)
- [Wake hook and IST recovery](docs/wake-hook-ist-recovery.md)
- [Memory and text boundary](docs/820-memory-text-boundary.md)
- [Offset validation](docs/820-offset-validation.md)
- [PUP extraction result](docs/pup-extraction-negative-result.md)
- [Research roadmap](docs/research-roadmap.md)

## Data and tooling

- [8.20 offset table](offsets/8.20-offsets.csv)
- [Tools](tools/README.md)

## Test conditions

Retail PS5 8.20.02; one payload per true cold boot; true power cycle after a
crash; game SSD untouched; Linux medium separate; no blind chain variants.

## Scope and limitations

The 8.20 kernel text is unavailable; the mapping is structural, not a direct
disassembly. The stopped-mask address is unknown. No AP, NPT, kernel-text or
Linux claim is made.

## Credits and legal

See [CREDITS.md](CREDITS.md), [NOTICE](NOTICE) and [DISCLAIMER.md](DISCLAIMER.md).
No firmware, PUP/rootfs content, kernel dumps or keys are included.
