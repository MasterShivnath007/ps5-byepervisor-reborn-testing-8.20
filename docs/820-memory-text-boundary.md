# 8.20 memory and text boundary

**Summary:** 8.20 kernel data is readable in an 8 MB window; kernel text is
execute-only; the guest-visible hypercall table is present, but NPT blocks
guest-side writes.

## QA page

A read-only payload read the 64 KB QA page at its direct-map alias. The page
begins with the `SSLP` structure and contains the QA field at `+0x88`:

```text
00 03 01 00 00 00 00 00 00 00 00 00 00 00 00 00
```

Little-endian dword `0x00010300`, the value the UMTX2/IPV6 chain writes for
QA/debug-menu flags (`qaf | 0x10300`). The same `SSLP` layout and QA field
appear in the 13.60 live dump.

There is only one copy of the 16-byte QA field in the 64 KB range. The field
already contains `0x10300`. The QA-bit sweep changed the field, but the
kernel-text PTE stayed `XO=1 RW=0`. The 8.20 QA route is closed.

## Data window

The safe data-only window is 8 MB:

```text
[QA-0x903000, QA-0x103000)
```

The preceding pages are execute-only kernel text (`XO=1`, `RW=0`). A 12 MB
backward dump entered that text and did not complete. An 8 MB data-only dump
completed with zero read errors.

The 8.20 direct map has holes for text and hypervisor memory. A guest PTE can
be present while the NPT still blocks access.

## Hypercall table

At `QA-0x2DAC00` there is a 32-bit relative hypercall dispatch table. Entry 0 is
`0xfebb9cf0`; `table_va + entry = ktext+0xBC40F0`, the known
`HV_MP_STARTUP_CALL` wrapper.

The table page is RO/NX. A dmap alias maps the same physical page with `RW=1`,
but a no-op write through it did not complete. The **NPT** blocks the write,
not the guest PTE. The guest-side table-write route is closed.

## Implication

8.20 kernel data is readable. Kernel text is not. The guest page tables are not
enough; a root-0 AP payload (VMCB/NPT root 1) or a new primitive is required to
read text or write the table.
