import socket
import time
import json
import hmac
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import client

hostName = "0.0.0.0"
hostPort = 8000
new_followers_of = "some_twitch_user"


class MyServer(BaseHTTPRequestHandler):

        def do_GET(self):    
                query = urlparse(self.path).query
                try:
                        query_components = dict(qc.split("=") for qc in query.split("&"))
                        challenge = query_components["hub.challenge"]
                except:
                        query_components = None
                        challenge = None                      
                
                if challenge:
                    s = ''.join(x for x in challenge if x.isdigit())
                    print (s)
                    print (challenge)
                    self.send_response(200,None)
                    self.end_headers();
                    self.wfile.write(bytes(challenge, "utf-8"))
                else:
                    self.send_response(200,None)
                    self.end_headers();
                    self.wfile.write(bytes("Hello Stranger :)", "utf-8"))


        def do_POST(self):                
                if 'Content-Length' in self.headers:
                        content_length = int(self.headers['Content-Length'])
                        post_data      = self.rfile.read(content_length)
                if 'Content-Type' in self.headers:
                        content_type   = str(self.headers['Content-Type'])
                if 'X-Hub-Signature' in self.headers:        
                        hub_signature  = str(self.headers['X-Hub-Signature'])
                        algorithm, hashval = hub_signature.split('=')
                        print(hashval)
                        print(algorithm)
                        sec = client.secret
                        if post_data and algorithm and hashval:
                                gg = hmac.new(sec.encode(), post_data, algorithm)
                                if not hmac.compare_digest(hashval.encode(), gg.hexdigest().encode()):
                                       raise ConnectionError("Hash missmatch.")     

                if content_length is None or content_type is None or hub_signature is None:
                        raise ValueError("not all headers supplied.")
    
                if post_data:
                        j = json.loads(post_data)
                        userid = (j["data"][0]["from_id"])
                        print(userid)
                        print(self.headers)
                        print(content_length)
                        print(post_data)
                        print(len(post_data))
                        self.send_response(200)
                        self.end_headers()
                        #print("new follower: "+client.get_twitch_username(userid))


twitchId = client.get_twitch_userid(new_followers_of)
client.suscribe_to_get_followers(twitchId)

myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
        myServer.serve_forever()
except KeyboardInterrupt:
        pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
