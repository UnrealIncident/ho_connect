import sys
import time
import struct
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
sock.bind(("", 11775))

message = "\x01\x62\x6C\x61\x6D\x00\x00\x00\x09\x81\x00\x02\x00\x01\x36\xB7\x34\x33\x66\x54\xA4\x4E\x60"
sock.sendto(message, ("<broadcast>", 11774))

resp, addr = sock.recvfrom(8192)
fp = open("dump.bin", "wb")
fp.write(resp[len(message):])
fp.close()