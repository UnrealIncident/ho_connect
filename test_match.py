import sys
import time
import json
import struct
import socket
import thread
import requests

MATCH_TYPE = {
    "campaign": 1,
    "matchmaking": 2,
    "custom": 3,
    "forge": 4,
    "theater": 5
}

GAME_MODE = {
    "ctf": 1,
    "slayer": 2,
    "oddball": 3,
    "koth": 4,
    "forge": 5,
    "vip": 6,
    "juggernaut": 7,
    "territories": 8,
    "assault": 9,
    "infection": 10
}

MAP_IDS = {
    "guardian": "\x28\x00",
    "riverworld": "\x2A\x80",
    "s3d_avalanche": "\x58\x20",
    "s3d_edge": "\x57\xE0",
    "s3d_reactor": "\x57\x80",
    "s3d_turf": "\x03\xE0"
}

MASTER_SERVER = "http://halo.center:11100/get/"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  
try:
    sock.bind(("", 11774))
except socket.error:
    exit = input("Woops! Something went wrong. Make sure the game is closed and try again.\nPress enter to exit.")
    sys.exit(1)

print "connect.exe (Find Game)"
print "======================="
print "1. Close all instances of the game (eldorado.exe)"
print "2. Close any VPNs (Evolve/OracleNet)"
print "3. Start connect.exe"
print "4. Start the game"
print "5. Go to System Link \"Find Game\""
print "6. Connect"
print "7. Play"
print ""
print "Just close this window it opens to kill the program."

def flip_port(port):
    start = port >> 8
    xor_key = start << 8
    end = (port ^ xor_key) << 8
    return end + start

def flip_long(l):
    s = struct.pack("<Q", l)
    s = s[1:]
    s += "\x00"
    return struct.unpack(">Q", s)[0]

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

def create_map_name(name):
    split = list(name)
    fixed = []
    for s in split:
        fixed.append(chr(ord(s) << 1))
    return "\x00".join(fixed)

def int_to_key(key):
    key = key << 4
    #print hex(key)
    end = hex(key).replace("L", "")[-2:]
    key = key >> 8
    key = hex(key).replace("L", "").replace("0x", "")
    if len(key) % 2:
        key = "0" + key
    #print key, end
    return key.decode("hex"), int(end, 16) >> 4

def build_packet_json(j):
    return build_packet(j["name"].encode("ascii"), j["ingame"], j["ingame"] + j["slots_left"], 
                        j["server_id"], j["connect_id"], j["match_type"], j["game_mode"], 
                        j["map"].encode("ascii"), j["pub_ip"].encode("ascii"), j["port"])

def build_packet(name, players, max_players, key, cid, matchtype=3, gamemode=2, mapname="riverworld", ip="127.0.0.1", port=11774):
    #print name, players, max_players, key, cid, matchtype, gamemode, mapname, ip, port
    #print name, type(name)
    pack_str = ">10s%ss17s15s16sI2cx8s2s16s9xQ35s" % (len(name) + 1)
    player_int = max_players - players
    player_int = player_int << 10
    player_int += players
    player_int = player_int << 12
    key, remaining = int_to_key(key)
    #print hex(player_int + (remaining << 28))
    cid = hex(cid).replace("0x", "").replace("L", "")
    if len(cid) % 2:
        cid = "0" + cid
    #print cid
    cid = cid.decode("hex")
    #print cid
    #print name, cid, key, hex(player_int + (remaining << 28))
    pack = struct.pack(pack_str, 
        "\x2D\x00\x04\x05\x01\x00\x01\xA0\xD5\x54", 
        name,
        cid,
        "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        key,
        player_int + (remaining << 28),
        chr(matchtype << 4),
        chr(gamemode),
        "\x00\xFF\xFF\xFF\xFF\x40\x00\x00",
        MAP_IDS[mapname],
        "\x00\xE6\x00\x66\x00\xC8\x00\xBE\x00\xE8\x00\xEA\x00\xE4\x00\xCC",
        ip_port_to_long(ip, port) + 0x4210000000000000,
        "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\xA8\x03\x70\x03\x90\x03\x28\x03\x08\x03\x60\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
    return pack

def update_servers():
    global servers
    while True:
        try:
            data = requests.get(MASTER_SERVER)
        except Exception as e:
            print e
            time.sleep(10.0)
            continue
        if data.status_code != 200:
            time.sleep(10.0)
            continue
        try:
            info = json.loads(data.text)
        except ValueError:
            time.sleep(10.0)
            continue
        new_servers = []
        for i in info:
            try:
                new_servers.append(build_packet_json(i))
            except Exception as e:
                print e
                pass
        servers = new_servers
        time.sleep(10.0)

#print hex(ip_port_to_long("8.8.8.8", 11774))
#print hex(flip_port(11774))

servers = []

thread.start_new_thread(update_servers, ())

while True:
    message, address = sock.recvfrom(8192)
    add_byte = message[-1]
    add_byte = str(chr(ord(add_byte) + 1))
    message = message[:-1] + add_byte
    msg_list = list(message)
    msg_list[10] = '\xAC'
    msg_list[11] = '\x9A'
    message = "".join(msg_list)
    for s in servers:
        sock.sendto(message + s, ("127.0.0.1", 11775))