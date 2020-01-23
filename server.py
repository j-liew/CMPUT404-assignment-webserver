#  coding: utf-8 
import socketserver
import os
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
        request = self.data.decode().split()

        # ignore any empty requests
        if len(request) < 1:
            return

        method = request[0]
        requestPath = request[1]

        # only accept GET requests
        if method != 'GET':
            self.sendMethodNotAllowed()
            return

        # www folder path
        basePath = os.getcwd() + '/www' 

        # verify that client is requesting from www folder
        requestAbsPath = os.path.abspath(basePath + requestPath)
        if requestAbsPath[:len(basePath)] != basePath:
            self.sendNotFound()
            return
        
        # process request
        while True:
            try:
                # open requested file
                path = basePath + requestPath                    
                f = open(path, 'r')
                fileType = requestPath.split('.')[-1]
                fileSize = os.path.getsize(path)
                self.sendOk(f, fileType, fileSize)
            except (FileNotFoundError, NotADirectoryError):
                self.sendNotFound()
            except IsADirectoryError:
                # serve default page of directory
                if requestPath[-1] == '/':
                    requestPath += 'index.html'
                    continue
                # otherwise, use a redirect to correct the path ending
                else:
                    newLocation = 'http://127.0.0.1:8080' + requestPath + '/'
                    self.sendRedirect(newLocation)
            break

    def sendOk(self, fileHandle, fileType, fileSize):
        content = fileHandle.read()
        status = 'HTTP/1.1 200 OK\r\n'
        contentType = ''
        if fileType == 'html':
            contentType = 'Content-Type: text/html\r\n'
        elif fileType == 'css':
            contentType = 'Content-Type: text/css\r\n'
        contentLength = 'Content-Length: ' + str(fileSize) + '\r\n'
        headerEnd = '\r\n'
        response = status + contentType + contentLength + headerEnd + content
        self.request.sendall(bytes(response, 'utf-8'))

    def sendRedirect(self, newLocation):
        status = 'HTTP/1.1 301 Moved Permanently\r\n'
        location = 'Location: ' + newLocation + '\r\n'
        headerEnd = '\r\n'
        response = status + location + headerEnd
        self.request.sendall(bytes(response, 'utf-8'))

    def sendNotFound(self):
        content = "<h1>404 Not Found</h1>\n"
        status = 'HTTP/1.1 404 Not Found\r\n'
        contentType = 'Content-Type: text/html\r\n'
        contentLength = 'Content-Length: ' + str(len(bytes(content, 'utf-8'))) + '\r\n'
        headerEnd = '\r\n'
        response = status + contentType + contentLength + headerEnd + content
        self.request.sendall(bytes(response, 'utf-8'))

    def sendMethodNotAllowed(self):
        content = '<h1>405 Method Not Allowed</h1>\n'
        status = 'HTTP/1.1 405 Method Not Allowed\r\n'
        allow = 'Allow: GET\r\n'
        contentType = 'Content-Type: text/html\r\n'
        contentLength = 'Content-Length: ' + str(len(bytes(content, 'utf-8'))) + '\r\n'
        headerEnd = '\r\n'
        response = status + allow + contentType + headerEnd + content
        self.request.sendall(bytes(response, 'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
