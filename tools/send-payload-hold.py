#!/usr/bin/env python3
"""Send a PS5 payload and keep the socket open while it runs.

`nc` closes the connection when it reaches EOF on stdin; the loader then gets
SIGPIPE while printing and dies before arming. This sender keeps the socket
open for up to HOLD_SECONDS and streams the payload's output.
"""
import os
import socket
import sys
import time

IP = os.environ.get("PS5_IP", "192.0.2.10")
PORT = int(os.environ.get("PS5_PORT", "9021"))
HOLD_SECONDS = int(os.environ.get("HOLD_SECONDS", "60"))
IDLE_SECONDS = int(os.environ.get("IDLE_SECONDS", "15"))


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <payload.elf>", file=sys.stderr)
        return 2
    path = sys.argv[1]
    data = open(path, "rb").read()

    s = socket.create_connection((IP, PORT), timeout=10)
    s.sendall(data)
    s.settimeout(IDLE_SECONDS)

    start = time.time()
    last = start
    while time.time() - start < HOLD_SECONDS:
        try:
            chunk = s.recv(4096)
        except socket.timeout:
            if time.time() - last >= IDLE_SECONDS:
                break
            continue
        if not chunk:
            break
        last = time.time()
        sys.stdout.write(chunk.decode("utf-8", "replace"))
        sys.stdout.flush()
    s.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
