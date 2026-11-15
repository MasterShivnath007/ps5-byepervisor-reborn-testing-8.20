# 8.20 AP-state analysis from the 13.60 live dump

**Summary:** Recovers the 13.60 AP-start control flow and maps the 8.20
structures. Offline analysis; no console payload was sent.

## 13.60 control flow

`acpi_wakeup_cpus` starts at `ktext+0x3913B0`:

```text
0x3913BB  mov eax, [mp_ncpus]              ; ktext+0x3D0E8BC = 16
0x391404  mov rcx, [stopped_cpus]          ; ktext+0x349F240 = 0xfffe
0x39140E  mov r14d, 1
0x39142B  bt rcx, r14                      ; for cpu = 1 .. mp_ncpus-1
0x39142F  jae next
0x391437  call per_ap_function             ; ktext+0x391780
0x39144F  call hc_0x10_wrapper             ; ktext+0xC16F00
```

The per-AP function:

```text
0x391791  lea rax, [cpu_apic_ids]          ; ktext+0x3A77AD0
0x39179F  movsxd rbx, [rax + cpu*4]        ; selector
0x3917CF  movzx edi, bl                    ; RDI = selector
0x3917FF  lea rsi, [mp_startup_init_vector]; ktext+0x269FB8
0x391806  mov rdx, cr3                     ; RDX = current CR3
0x391809  call hc_0x0F_wrapper             ; ktext+0xC16EE0
```

The stock wrapper ABI is `hc 0x0F(selector, start_rip, cr3)`. The AP loop runs
**before** the hc `0x10` call.

## 13.60 data layout

```text
mp_ncpus          ktext+0x3D0E8BC   dword 16
started_mask      ktext+0x3D0E8D0   qword 0
source_cpu_set    ktext+0x3D0E8E8   qword 0xffff
stopped_cpus      ktext+0x349F240   qword 0xfffe
cpu_apic_ids      ktext+0x3A77AD0   16 dwords 0..15, then -1 padding
```

## 8.20 mapping

The 8.20 high data dump contains the same three-field block and selector table
at shifted offsets:

```text
mp_ncpus          ktext+0x3FA1D1C   dword 16
started_mask      ktext+0x3FA1D30   qword 0
source_cpu_set    ktext+0x3FA1D48   qword 0xffff
cpu_apic_ids      ktext+0x3CB8A90   16 dwords 0..15, then -1 padding
```

The block matches the 13.60 layout field for field (`+0x00` dword 16, `+0x14`
qword 0, `+0x2C` qword `0xffff`).

**No 8.20 stopped-mask address is verified.** `ktext+0x3F9F974` is a false
candidate: the dword there is `0x0001fffe`, its neighbours are `0x7fffffff`
limits, and bit 16 is set. The 13.60-relative prediction `ktext+0x37326A0`
lands in an all-zero hole in the 8.20 forward dump. Do not write either
address.

## 8.20 control-flow mapping

- The `acpi_wakeup_cpus` twin starts at `ktext+0x9CA170`; the hc `0x10` call is
  at `ktext+0x9CA20F` (`+0x9F`).
- The stock hc `0x0F` call is at `ktext+0x9CA5C9`, inside the per-AP function
  at `ktext+0x9CA540` (start `+0x3D0`, call `+0x89`), matching 13.60.
- The `0x9CA20F` hook is **after** the AP loop. Calling hc `0x0F` there is too
  late.
- The stock call site is the structurally correct site **if the loop runs**.
  It has negative results already; it is a retest target, not a fresh route.
- If the live stopped mask is 0, the loop skips the per-AP function and the
  stock call site cannot fire.

## Implication

The current AP route is the wrong window. The next experiment is read-only:
capture the stack at `0x9CA20F` to find the caller and the pre-loop trigger. Do
not write an unverified mask address and do not call hc `0x0F` at `0x9CA20F`.

## Caveats

- The 8.20 kernel text is unavailable; the mapping is structural.
- No verified 8.20 stopped-mask address exists.
- No AP, NPT or Linux claim is made.
