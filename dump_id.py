import sys
import time
import struct
import socket

MAP_IDS = {
    "\x28\x00": "guardian",
    "\x2A\x80": "riverworld",
    "\x58\x20": "s3d_avalanche",
    "\x57\xE0": "s3d_edge",
    "\x57\x80": "s3d_reactor",
    "\x03\xE0": "s3d_turf" 
}

def int_to_string(i):
    hi = hex(i).replace("0x", "").replace("L", "")
    if len(hi) % 2:
        hi = "0" + hi
    return hi.decode("hex")

def int_to_ip_string(i):
    si = int_to_string(i)
    final_list = []
    for s in si:
        final_list.append(str(ord(s)))
    final_list.reverse()
    return ".".join(final_list)

def flip_int(i):
    si = int_to_string(i)
    li = list(si)
    li.reverse()
    hi = "0x"
    for l in li:
        hi += hex(ord(l)).replace("0x", "")
    return int(hi, 0)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
sock.bind(("", int(sys.argv[1])))

message = "\x01\x62\x6C\x61\x6D\x00\x00\x00\x09\x81\x00\x02\x00\x01\x36\xB7\x34\x33\x66\x54\xA4\x4E\x60"
sock.sendto(message, ("<broadcast>", int(sys.argv[2])))

resp, addr = sock.recvfrom(8192)
fp = open("resp.bin", "wb")
fp.write(resp[len(message):])
fp.close()

resp = resp[10 + len(message):]
name_len = resp.find("\x00")
name = struct.unpack_from("%ss" % name_len, resp)[0]
print name

resp = resp[name_len + 1:]
connect_id = struct.unpack_from("17s", resp)[0]
print "".join(hex(ord(x))[2:].zfill(2) for x in connect_id)