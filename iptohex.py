import sys

def flip_port(port):
    start = port >> 8
    xor_key = start << 8
    end = (port ^ xor_key) << 8
    return end + start

def ip_port_to_long(ip, port):
    ip_int = 0
    split = ip.split(".")
    split.reverse()
    for s in split:
        ip_int += int(s)
        ip_int = ip_int << 8
    ip_int = ip_int << 8
    ip_int += flip_port(port)
    ip_int = ip_int << 4
    return ip_int

print hex(ip_port_to_long(sys.argv[1], int(sys.argv[2])) + 0x4210000000000000)