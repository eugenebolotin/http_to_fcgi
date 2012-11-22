#!/usr/bin/env python

import sys, BaseHTTPServer
import flup_fcgi_client as fcgi_client

def send_fcgi_request( fcgi, host, port, url ):
    env = {
        'SCRIPT_FILENAME': url,
        'QUERY_STRING': url,
        'REQUEST_METHOD': 'GET',
        'SCRIPT_NAME': url,
        'REQUEST_URI': url,
        'GATEWAY_INTERFACE': 'CGI/1.1',
        'SERVER_SOFTWARE': 'ztc',
        'REDIRECT_STATUS': '200',
        'CONTENT_TYPE': '',
        'CONTENT_LENGTH': '0',
        'DOCUMENT_URI': url,
        'DOCUMENT_ROOT': '/',
        'DOCUMENT_ROOT': '/var/www/',
        'REMOTE_ADDR': '127.0.0.1',
        'REMOTE_PORT': '123',
        'SERVER_ADDR': host,
        'SERVER_PORT': str( port ),
        'SERVER_NAME': host,
        'SERVER_PROTOCOL': "HTTP/1.0"
    }

    return fcgi( env )

class FCGIProxyHandler( BaseHTTPServer.BaseHTTPRequestHandler ):
    @staticmethod
    def set_params( host, port ):
        FCGIProxyHandler.host = host
        FCGIProxyHandler.port = port
        FCGIProxyHandler.fcgi = fcgi_client.FCGIApp( host = host, port = port )

    def do_GET( s ):
        status, content_type, data, last = send_fcgi_request( FCGIProxyHandler.fcgi, FCGIProxyHandler.host, FCGIProxyHandler.port, s.path )
        s.send_response( int( status.split()[ 0 ] ) )
        s.send_header( "Content-type", content_type[ 0 ][ 1 ] )
        s.end_headers()
        s.wfile.write( data )

def serve_forever( port, server_class = BaseHTTPServer.HTTPServer, handler_class = BaseHTTPServer.BaseHTTPRequestHandler ):
    server_address = ( '', port )
    httpd = server_class( server_address, handler_class )
    while True:
        httpd.handle_request()

if len( sys.argv ) != 4:
    print "Usage: ./server.py HTTP_SERVE_PORT FCGI_HOST FCGI_PORT"
    exit( 1 )

HTTP_SERVE_PORT = int( sys.argv[ 1 ] )
FCGI_HOST = sys.argv[ 2 ]
FCGI_PORT = int( sys.argv[ 3 ] )

FCGIProxyHandler.set_params( FCGI_HOST, FCGI_PORT )
serve_forever( HTTP_SERVE_PORT, BaseHTTPServer.HTTPServer, FCGIProxyHandler )
