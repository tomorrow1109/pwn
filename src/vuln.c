#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/*
 * ret2win - a minimal pwn challenge.
 *
 * Compile flags intentionally weaken the binary:
 *   -fno-stack-protector  : no canary
 *   -no-pie               : fixed addresses
 * NX stays enabled, so the intended solution is ret2win instead of shellcode.
 */

__attribute__((noinline)) void win(void) {
  char buf[128] = {0};
  FILE *fp = fopen("/flag", "r");
  if (!fp) {
    puts("[-] /flag not found");
    return;
  }
  if (fgets(buf, sizeof(buf), fp)) {
    /* Use write() instead of printf(): stdio pulls in SSE code paths that
     * fault on a 8-byte-misaligned stack right after a plain `ret` into
     * win(). Keeping this simple means a bare ret2win payload works. */
    write(1, "[+] ", 4);
    write(1, buf, strlen(buf));
  }
  fclose(fp);
}

__attribute__((noinline)) void vuln(void) {
  char buf[64];
  puts("==============================================");
  puts("  ret2win :: can you reach win() ?");
  puts("==============================================");
  write(1, "payload> ", 9);
  read(0, buf, 0x200); /* unchecked read: 512 bytes into a 64-byte buffer */
}

int main(void) {
  setvbuf(stdout, NULL, _IONBF, 0);
  vuln();
  puts("bye");
  return 0;
}
