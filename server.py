#  coding: utf-8
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        #print ("Got a request of: %s\n" % self.data)
        """ sample data recv: b'GET / HTTP/1.1\r\nHost: 127.0.0.1:8080\r\nConnection: keep-alive\r\n ... """
        try:
            _data = self.data.decode().split(" ")
        except:
            return
        # check if method can be handled
        if _data[0] == "GET":
            # then check the path
            OK, file_type, file_content = self.get_path(_data[1])
            if OK:
                self.OK_200(file_content, file_type)
            else:
                if file_type == "redirect":
                    redirect =  _data[1] + "/"
                    Headers = "HTTP/1.1 301 Permanently moved to %s\r\n" % redirect
                    Headers += "Content-Type: text/html;\r\n"
                    content = "<html><head></head><body><center><h1>301 - This Page is moved to %s .</h1></center></body></html>" % redirect
                    self.request.sendall(bytearray(Headers + "\r\n" + content, 'utf8'))
                else:
                    self.not_found_404()
        else:
            Headers = "HTTP/1.1 405 Method Not Allowed\r\n"
            Headers += "Content-Type: text/html;\r\n"
            content = "<html><head></head><body><center><h1>405 - The Request Method is not Allowed</h1></center></body></html>"
            self.request.sendall(bytearray(Headers + "\r\n" + content, 'utf8'))

    def get_path(self, path):
        # valid path
        try:
            file_path = "www"
            file_path += path
            # dir
            if file_path[-1:] == "/":
                file_path += "index.html"
                resource_file = open(file_path).read()
                return True, "html", resource_file
            # check mimetype
            else:
                if path[-3:] == "css":
                    resource_file = open(file_path).read()
                    return True, "css", resource_file
                elif path[-4:] == "html":
                    resource_file = open(file_path).read()
                    return True, "html", resource_file
                # no file type
                else:
                    file_path += "/"
                    if os.path.exists(file_path):
                        return False, "redirect", "nothing"
                    else:
                        return False, "empty", "nothing"
        # invalid path
        except:
            return False, "empty", "nothing"

    def not_found_404(self):
        Headers = "HTTP/1.1 404 NOT FOUND\r\n"
        Headers += "Content-Type: text/html;\r\n"
        content = "<html><head></head><body><center><h1>404 - NOT FOUND</h1></center></body></html>"
        self.request.sendall(bytearray(Headers + "\r\n" + content, 'utf8'))
        return

    def OK_200 (self, file_content, file_type):
        Headers = "HTTP/1.1 200 OK\r\n"
        Headers += "Content-Type: text/%s;\r\n" % file_type
        content = file_content
        self.request.sendall(bytearray(Headers + "\r\n" + content, 'utf8'))
        return

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
