import http.server
import socketserver # Establish the TCP Socket connections
import json

hostName = "localhost"
PORT = 9000

def getstore():
    with open('src/store.json', 'r') as openfile:
        json_object = json.load(openfile)
        print(json_object)
        return json_object
 
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '../src/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif self.path == '/getstore':
            self.path = '../src/store.json'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
 
Handler = MyHttpRequestHandler
 
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Http Server Serving at port", PORT)
    httpd.serve_forever()