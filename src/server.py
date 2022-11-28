# Python 3 server example
import http.server
import socketserver # Establish the TCP Socket connections

hostName = "localhost"
PORT = 9000

def gettest():
    print("this works!")
 
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '../src/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif self.path == '/gettest':
            gettest()
            return '', 200
 
Handler = MyHttpRequestHandler
 
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Http Server Serving at port", PORT)
    httpd.serve_forever()