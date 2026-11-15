# Credits

This work builds on a large public research effort. The projects and people
below made the 8.20 investigation possible. No upstream code is vendored in
this repository; the links are for attribution and reproducibility.

## The bug, the exploit path and the AP payload

- **theflow0 (Andy Nguyen)** — initial discovery of the S3-resume
  `khv_startup_mp` AP-launch bug. The Byepervisor Reborn README credits the
  initial find to theflow0.
- **soniciso1** — the public S3-resume `khv_startup_mp` writeup
  ([ps5-hv-writeups](https://github.com/soniciso1/ps5-hv-writeups)), the
  blueprint for the 13.60/8.20 control-flow analysis.
- **EchoStretch** — [Byepervisor
  Reborn](https://github.com/EchoStretch/Byepervisor-Reborn), the 11.60
  reference and the AP payload / VMCB discovery studied here.
- **PS5Dev** — the original
  [Byepervisor](https://github.com/PS5Dev/Byepervisor).
- **nottingham00** — the Byepervisor Reborn fork studied during the port.

## Kernel dumps, ABI and porting methodology

- **terrafirma2021** — the [PS5 13.60 live kernel
  dump](https://github.com/terrafirma2021/ps5-13.60-kernel-dump), used to
  recover the AP-loop order and the hypercall ABI.
- **R0nov4** — the [PS5 13.60 kernel → QEMU boot
  kit](https://github.com/R0nov4/ps5-kernel-qemu), used for the 13.60
  kernel/ABI analysis.
- **gzimbric** — [PS5 hypervisor bypass
  porting](https://github.com/gzimbric/ps5-hv-bypass-porting), the per-core
  DR0/#DB and porting methodology.

## Toolchain and payload infrastructure

- **John Törnblom / ps5-payload-dev** — the
  [ps5-payload-sdk](https://github.com/ps5-payload-dev/sdk), elfldr and the
  payload toolchain used to build and send every test.
- **zecoxao** — [ps5-pup-decrypt](https://github.com/zecoxao/ps5-pup-decrypt)
  and [ps5-pup-unpacker](https://github.com/zecoxao/ps5-pup-unpacker).
- **SpecterDev, LeGend, LemonHaze, idc, l0lhax, Scene-Collective, Anonymous,
  0xThreadz, Creeeeger, enessmr, astrelsky** — the PUP decrypt/unpack code,
  its SDK port, and the authentication/workflow fixes. See the upstream
  READMEs and the `sdk/` PR #10 for the exact contributions.
- **RamalhoBoss** — [PS5 Memory
  Dumper](https://github.com/ramalhoboss/ps5-memory-dumper).
- **Pharaoh2k** — ps5debug-NG, the memory-dumper payload.
- **EchoStretch** — [kstuff-lite](https://github.com/EchoStretch/kstuff-lite)
  and the kernel-offset/porting resources.
- **The ps5-linux maintainers and contributors** —
  [ps5-linux-loader](https://github.com/ps5-linux/ps5-linux-loader) and the
  Linux boot/loader work.

## Background and inspiration

- **sleirsgoevy** — the kstuff offset/porting notes (the “OnOffsets” gist and
  the porting tool), background for the offset work.
- **fail0verflow** — early PS5 research and the root-key/PUP ecosystem,
  background for the firmware analysis.
- **theflow0** — kernel exploit research; the 8.20 kernel R/W and the S3 bug
  are part of that lineage.

## Further credits from the S3 writeup

The S3-resume writeup thanks **flat_z, specter, j0rdy, zecoxao, earthonion,
TorusHV, theflow, bollarz and Dr. Yenyen**. Those credits belong to that
writeup; they are repeated here for completeness.

## This repository

- **MasterShivnath007** — the 8.20.02 testing, the PUP extraction, the offset
  validation and this write-up. Errors and omissions are mine.

If you contributed to this work and are not listed, open an issue and credit
will be added.
