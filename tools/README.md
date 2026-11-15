# Tools

These are small, self-contained helpers from the research. No firmware,
payload binaries, or upstream source code is vendored here.

## `check-820-pup.sh`

Verifies that a downloaded PUP is one of the known 8.20 system updates by MD5.

```sh
tools/check-820-pup.sh /path/to/PS5UPDATE.PUP
```

Known hashes are in the script. A mismatch means do not put the file on the
console.

## `send-payload-hold.py`

Sends an ELF payload to an elfldr on TCP 9021 and keeps the socket open while
it runs. The console address is taken from the environment; the default is a
TEST-NET address (not a real console).

```sh
PS5_IP=<console-ip> PS5_PORT=9021 \
  python3 tools/send-payload-hold.py payload.elf
```

`HOLD_SECONDS` and `IDLE_SECONDS` control the hold; use a long hold for the PUP
decrypt (e.g., `HOLD_SECONDS=2400 IDLE_SECONDS=2400`).

## PUP extraction

The actual decrypt/unpack code is upstream:

- [ps5-pup-decrypt](https://github.com/zecoxao/ps5-pup-decrypt) — console-side
  PUP decrypt. The `sdk/` build runs under a modern ELF loader.
- [ps5-pup-unpacker](https://github.com/zecoxao/ps5-pup-unpacker) — host-side
  unpacker.

The 8.20.02 result is documented in
`../docs/pup-extraction-negative-result.md`: the container
and the `system`/`system_ex` rootfs images decrypt, but `5_kernel.bin` remains
encrypted. No PUP or rootfs content is included in this repository.

## Legal

Use only on a console you own. See `../DISCLAIMER.md`.
