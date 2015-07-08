from twisted.web import server, resource
from twisted.internet import reactor, task

import copy
import json
import datetime

servers = []
CLEAN_TIME = 90

def returnable_servers(servers):
    returnable = []
    for s in servers:
        new_s = copy.copy(s)
        del new_s["last_time"]
        returnable.append(new_s)
    return returnable

def clean_servers():
    #print "Cleaning"
    now = datetime.datetime.now()
    for i, s in enumerate(servers):
        diff = now - s["last_time"]
        #print s["name"], diff.seconds
        if diff.seconds > CLEAN_TIME:
            servers.pop(i)

class Root(resource.Resource):
    pass

class Index(resource.Resource):
    isLeaf = True
    
    def render_GET(self, request):
        page = '<html>\n<head><title>Halo Center</title></head>\n<body>\n'
        if len(servers) == 1:
            page += "<h1>1 server online</h1>"
        else:
            page += "<h1>%s servers online</h1>" % len(servers)
        page += "</body></html>"
        return page

class ViewServers(resource.Resource):
    isLeaf = True
    
    def render_GET(self, request):
        return json.dumps(returnable_servers(servers))

class PostServer(resource.Resource):
    isLeaf = True

    def render_POST(self, request):
        content = request.content.getvalue()
        try:
            info = json.loads(content)
        except ValueError:
            request.setResponseCode(400)
            return "Mate. Come on..."
        info["last_time"] = datetime.datetime.now()
        info["pub_ip"] = request.getClientIP()
        for i, x in enumerate(servers):
            if x["pub_ip"] == info["pub_ip"]:
                servers[i] = info
                return "OK"
        servers.append(info)
        return "OK"

info = Root()
info.putChild("", Index())
info.putChild("put", PostServer())
info.putChild("get", ViewServers())

clean = task.LoopingCall(clean_servers)
clean.start(30.0, now=False)

site = server.Site(info)
reactor.listenTCP(11100, site)
reactor.run()