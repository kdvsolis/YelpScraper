from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time
import urllib
import ReviewsProcessor

PORT_NUMBER = 8080


class UPNPHTTPServerHandler(BaseHTTPRequestHandler):

    xmlVal = ""
    # Handler for the GET requests
    def do_GET(self):
        if self.path == '/input':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js">' +
                              b'var xmlVal = ""' + 
                              b'</script>' + 
                              b'<script>'+
                              b'function func(){' +
                              b'event.preventDefault();' +
                              b'document.getElementById("url_container").textContent = "Loading...";'
                              b'var newValue = $("#input-id").val();' +
                              b'$.ajax({' +
                                  b'type: "POST",' +
                                  b'timeout: 99999999999,' + 
                                  b'url: "/process",' +
                                  b'data: {"url":document.getElementById("input-id").value},' +
                                  b'datatype: "JSON",' +
                                  b'success: function(data){window.location.href = "http://localhost:8088/result"},' +
                                  b'error: function(){console.log("ERR"); document.getElementById("url_container").textContent = "' + self.xmlVal.encode() + b'";},' +
                              b'});' +
                              b'}</script><form id="form-id" onsubmit="func()"><input id="input-id" type="text"><input type="submit"></form>' + 
                              b'<div id="url_container"></div>')
            return
        if self.path == '/result':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            f = open("reviews.json", "r")
            self.json = f.read()
            self.wfile.write(self.json.encode())
            return
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Not found.")
            return

    # Handler for the POST requests
    def do_POST(self):
        if self.path == '/process':
            content_length = int(self.headers['Content-Length'])
            post_data = urllib.parse.unquote(self.rfile.read(content_length).decode("UTF-8")).replace("url=", "")
            print (post_data)
            rp = ReviewsProcessor.ReviewsProcessor(post_data)
            rp.process_scraping()
            f = open("reviews.json", "w")
            f.write(rp.getReviewsInJSON())
            f.close()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            return


class UPNPHTTPServerBase(HTTPServer):
    """
    A simple HTTP server that knows the information about a UPnP device.
    """
    def __init__(self, server_address, request_handler_class):
        HTTPServer.__init__(self, server_address, request_handler_class)
        self.port = None


class UPNPHTTPServer(threading.Thread):
    """
    A thread that runs UPNPHTTPServerBase.
    """

    def __init__(self, port):
        threading.Thread.__init__(self, daemon=True)
        self.server = UPNPHTTPServerBase(('', port), UPNPHTTPServerHandler)
        self.server.port = port

    def run(self):
        self.server.serve_forever()
		
http_server = UPNPHTTPServer(8088)
http_server.start()
while True:
    """"""