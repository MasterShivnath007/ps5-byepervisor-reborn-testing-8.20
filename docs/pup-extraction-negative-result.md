# PUP extraction — 8.20.02

**Summary:** The PUP container and rootfs decrypt, but the x86 kernel blob
remains encrypted.

## Input

The 8.20.02 system PUP:

```text
1,336,378,880 bytes
MD5 a3aad7f04e84230e72af02f7c458d05a
BLS magic SLB2, file_count=2
entry 1: PS5UPDATE1.PUP  (system update, ~1.18 GB)
entry 2: PS5UPDATE2.PUP  (recovery, ~151 MB)
```

The MD5 matches the 8.20.02 system update. The recovery PUP contains no kernel.

## Result

Console-side decrypt:

```text
PS5UPDATE1.PUP.dec  1,184,754,277 B
PS5UPDATE2.PUP.dec    151,622,861 B
```

No failure lines; the log ends with `done`.

Host unpack:

- `5_kernel.bin` — 22,947,328 B, entropy 8.000, no ELF/SELF magic. Still
  encrypted. This is the x86 kernel candidate.
- `515_ssd0.system_b` — 371,458,048 B, plaintext exFAT rootfs.
- `516_ssd0.system_ex_b` — 1,312,686,080 B, plaintext exFAT rootfs.
- The rootfs contains `libkernel.sprx`, `SceSysCore.elf`, `eap_kernel.ebin`
  and VSH/app files, but not the x86 kernel.
- The `5_kernel.bin` table segment (`16_for_5.img`, 1,408 B) is also encrypted
  (entropy 7.850). The update-mode nested PUP is entropy 8.000.

## Conclusion

The PUP tool decrypts the outer container and the rootfs. The per-binary kernel
blob remains encrypted; the key is in console secure storage. No plaintext
8.20 kernel text was obtained. The rootfs is useful for VSH/app research but
does not unblock the hypervisor port.

The PUP route for kernel text is a hard stop.
