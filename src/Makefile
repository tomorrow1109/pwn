CC      ?= gcc
CFLAGS  := -O0 -w -fno-stack-protector -fno-stack-clash-protection \
           -fcf-protection=none -no-pie -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0
TARGET  := vuln

all: $(TARGET)

$(TARGET): vuln.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(TARGET)

.PHONY: all clean
