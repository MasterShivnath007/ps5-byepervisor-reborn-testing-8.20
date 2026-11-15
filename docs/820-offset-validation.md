# 8.20 offset validation

**Summary:** The 8.20 table is almost byte-for-byte the 8.00 table. A name in
the table is not a validation.

## Data offsets

| Name | 8.20 | 8.00 | Note |
| --- | --- | --- | --- |
| `ACPIGBL_FACS` | `0x38F75A0` | `0x38F7590` | `+0x10`; used for the FACS trigger |
| `IDT` | `0x3B23DF0` | same | gate/IST work proven |
| `COMMON_TSS` | `0x3B26AD0` | same | all 16 IST6 rows saved/restored |
| `FUN_MEMCPY` | `0x282FA0` | same | kernel shellcode |
| `HV_MP_STARTUP_CALL` | `0xBC40F0` | `0xBC2C60` | **hc `0x10` wrapper, not hc `0x0F`** |
| `MP_STARTUP_INIT_VECTOR` | `0x2A5E28` | `0x2A5860` | inherited; not independently validated |
| `ACPI_SLEEP_MACHDEP_HOOK` | **missing** | **missing** | the 8.20 wake/ACPI function is unknown |

`HV_MP_STARTUP_CALL = 0xBC40F0` is the hc **0x10** wrapper. The hc `0x0F`
candidate `0xBC40D0` was not validated. Do not treat the table label as proof
of the hc `0x0F` wrapper.

## Gadget matrix

| Status | Gadgets | Evidence |
| --- | --- | --- |
| Proven | `PIVOT`, `IRETQ`, `POP_RAX`, `POP_RDI`, `POP_RCX`, `STORE_RDI8_RCX`, `DBREG_RESUME`, `RET_TRAMP`, `POP_RSP` | arm/return chains completed |
| Rejected | `ST_RCX_RAX` (`0x3061A2`) | did not return on 8.20 |
| Unproven | `POP_RSI`, `POP_RDX`, `MOV_RAX_RDI`, `REP_MOVSB` | not exercised by the return-only control; AP-arg builds did not complete |
| Ambiguous | `SET_DR7` | inconsistent; padding required |
| Missing | `POP_R8`, `STORE_RCX_R8`, `MOV_RAX_RSI`, `ST_RCX_RDX`, `OR_RCX_EAX` | absent from the 8.20 table |

## Lessons

1. **Validate behaviorally.** The 11.60 validation does not transfer.
2. **Use the all-16 IST6 gate.** A shared gate or row 0 only is not enough.
3. **Do not trust wrapper labels.** `0xBC40F0` is the hc `0x10` wrapper.
4. **The ACPI/AP offsets are missing.** Without the 8.20 text, the trigger and
   stopped-mask addresses cannot be derived from this table.

See [`offsets/8.20-offsets.csv`](../offsets/8.20-offsets.csv) for the full
comparison.
