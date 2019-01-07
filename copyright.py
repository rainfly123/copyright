#!/usr/bin/env python
import daemon
import mysql
import socket
import json
import datetime

if __name__ == '__main__':
    #daemon.daemonize("/tmp/copyright.pid")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR  , 1)
    s.bind(("127.0.0.1", 6000))
    s.settimeout(10)
    alltask = []

    while True:
        try :
            data, addr = s.recvfrom(1024)
            print data
            task = json.loads(data)
 
        except:
            print "erro"
        now = datetime.datetime.now()
        if 
   
    

