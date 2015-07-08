import sys
import time
import json
import struct
import socket
import requests

MASTER_SERVER = "http://i.r0t.co:11100/put/"

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

def connect_id_to_int(cid):
    hex_id = "".join(hex(ord(x)).replace("0x", "").replace("L", "").zfill(2) for x in cid)
    iid = int(hex_id, 16)
    return iid

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
sock.settimeout(5.0)

print "Red Alert v0.0.1"

try:
    sock.bind(("", 11776))
except socket.error:
    exit = input("Woops! Something went wrong. Make sure the game is closed and try again.\nPress enter to exit.")
    sys.exit(1)

print "host.exe (Host Game)"
print "===================="
print "1. Close all instances of the game (eldorado.exe)"
print "2. Close any VPNs (Evolve/OracleNet)"
print "3. Start the game"
print "4. Go to System Link \"Host Game\""
print "5. Start host.exe"
print "6. Wait for people to join"
print "7. Play"
print ""
print "Just close this window it opens to kill the program."

while True:
    message = "\x01\x62\x6C\x61\x6D\x00\x00\x00\x09\x81\x00\x02\x00\x01\x36\xB7\x34\x33\x66\x54\xA4\x4E\x60"
    expected = "\x01\x62\x6C\x61\x6D\x00\x00\x00\x09\x81\xAC\x9A\x00\x01\x36\xB7\x34\x33\x66\x54\xA4\x4E\x61"
    sock.sendto(message, ("<broadcast>", 11774))

    try:
        resp, addr = sock.recvfrom(8192)
    except socket.timeout:
        #print "Timeout, trying again"
        continue
    except Exception as e:
        print e
        break

    if resp.find(expected) != 0:
        continue

    '''fp = open("resp4.bin", "wb")
    fp.write(resp[len(message):])
    fp.close()'''

    '''fp = open("resp3.bin", "rb")
    resp = fp.read()
    fp.close()'''

    resp = resp[10 + len(message):]
    #resp = resp[10:]
    name_len = resp.find("\x00")
    name = struct.unpack_from("%ss" % name_len, resp)[0]
    #print name

    temp = resp[name_len + 1:]
    connect_id = struct.unpack_from("17s", temp)[0]
    #print connect_id
    connect_id = connect_id_to_int(connect_id)
    #print connect_id, hex(connect_id)


    resp = resp[name_len + 33:]
    sid1, sid2, sid3 = struct.unpack_from(">QQc", resp)
    sid = sid1 << 68
    sid += sid2 << 4
    sid += ord(sid3) >> 4
    #print hex(sid1), hex(sid2), hex(ord(sid3))
    #print sid, hex(sid)

    resp = resp[16:]
    players = struct.unpack_from(">I", resp)[0]
    ingame = ((players >> 12) | 0xFFFFE0) ^ 0xFFFFE0
    slots_left = ((players >> 22) | 0xFFFFE0) ^ 0xFFFFE0
    #print ingame, slots_left, ingame + slots_left

    resp = resp[4:]
    game_info = struct.unpack_from(">H", resp)[0]
    game_mode = (game_info | 0XFFF0) ^ 0XFFF0
    match_type = game_info >> 12
    #print game_mode, match_type

    resp = resp[3:]
    gm_len = resp.find("\x00\xFF\xFF\xFF\xFF\x40")
    gm_name = struct.unpack_from("%ss" % (gm_len), resp)[0].decode("UTF-16")
    #print gm_name

    resp = resp[gm_len+8:]
    map_id = struct.unpack_from(">2s", resp)[0]
    #print MAP_IDS[map_id]

    resp = resp[3:]
    mn_len = resp.find("\x00\x00") + 1
    mn_name = struct.unpack_from("%ss" % (mn_len), resp)[0]
    mn_list = list(mn_name)
    for x in range(len(mn_list)):
        mn_list[x] = chr(ord(mn_list[x]) >> 1)
    mn_name = "".join(mn_list).decode("UTF-16")
    #print mn_name

    resp = resp[mn_len + 8:]
    conn_info = struct.unpack_from(">Q", resp)[0]
    port = (conn_info >> 4) - ((conn_info >> 20) << 16)
    ip = ((conn_info >> 20) | 0xFFFFFFFF00000000) ^ 0xFFFFFFFF00000000
    #print int_to_ip_string(ip), flip_int(port)

    result = {"name": name, "game_mode": game_mode, "map": MAP_IDS[map_id], "map_name": mn_name.encode("ascii"), 
              "game_mode_name": gm_name.encode("ascii"),  "ingame": ingame, "slots_left": slots_left, "match_type": match_type,
              "inter_ip": int_to_ip_string(ip), "port": flip_int(port), "server_id": sid, "connect_id": connect_id}
    try:
        up = requests.post(MASTER_SERVER, json.dumps(result))
    except Exception as e:
        print up
        print e

    time.sleep(5.0)

'''sid1 = sid1 << 4
sid1 += (sid1 >> 60)
sid2 = sid2 << 4
sid2 += ord(sid3) >> 4'''