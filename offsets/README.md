# 8.20 offset table — validation status

`8.20-offsets.csv` compares the public 8.20 `off_0820` table with the 8.00
`off_0800` table and records what was actually observed on this 8.20.02
console.

## Legend

| Value | Meaning |
| --- | --- |
| `proven` | The behavior needed by a chain was observed on 8.20. |
| `unproven` | Present in the table, but not behaviorally validated. |
| `rejected` | Did not return when used on 8.20. |
| `ambiguous` | Inconsistent results; do not use blindly. |
| `missing` | Not present in the 8.20 table. |
| `data / not behaviorally validated` | A data structure, physical address, or code offset that was not the subject of a chain test. |

## Important caveats

- The 8.20 table is almost byte-for-byte the **8.00** table, not a table
  derived from an 8.20 image. `ACPIGBL_FACS` differs by `+0x10`; several
  gadgets differ.
- `ACPIGBL_FACS` is known and was used for the FACS trigger. The S3
  `acpi_sleep_machdep` / `acpi_wakeup_cpus` function offsets are **not**
  present.
- `HV_MP_STARTUP_CALL = 0xBC40F0` is the hc **0x10** wrapper, not the hc
  `0x0F` wrapper. The hc `0x0F` candidate `0xBC40D0` is not validated. Do not
  treat the table label as proof.
- `MP_STARTUP_INIT_VECTOR = 0x2A5E28` is the inherited 8.20 value; it was not
  independently validated.
- `GAD_STORE_RCX_RAX_RET = 0x3061A2` is **rejected**: it did not return when
  used on 8.20.
- This CSV is a research artifact, not a working exploit. Using an unvalidated
  gadget can crash or brick a console.
