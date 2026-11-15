# Open research requirements

The 8.20 port is blocked by missing information, not by a missing payload or
chain variant. If you can provide any of the following **with evidence**, open
an issue. Do **not** upload firmware, PUP files, rootfs images, kernel dumps,
or keys to this repository; link to a public source or describe the method.

1. **8.20 kernel text** — a decrypted `x86_kernel.elf`, a live kernel text
   dump, or a validated symbol/offset table derived from one.
2. **8.20 ACPI wake/sleep offsets** — the real `acpi_sleep_machdep` trigger
   (the writeup uses `+0x18e`) and `acpi_wakeup_cpus`, or the equivalent
   resume-path function.
3. **8.20 HCALL `0x0F` ABI** — the wrapper address and the argument order
   (logical core, start RIP, CR3), confirmed on 8.20.
4. **8.20 hypervisor layout** — the HV heap / VMCB physical range, or a
   validated way to find the VMCBs from a root-0 AP payload.
5. **`5_kernel.bin` second stage** — the per-binary key, or confirmation that
   it is only available through the console's secure storage.

## What would count as evidence

- A reproducible read of the 8.20 kernel text or a named function.
- A tested AP entry (marker or register dump) on 8.20.02.
- A validated VMCB write/read-back on 8.20.02.
- A PUP decrypt result that produces a plaintext `5_kernel.bin`.

Negative results are welcome too: “this address does not fire on 8.20.02” is
useful if the test is described precisely.
