#!/bin/sh
pid=$(ps ax | grep -v grep | grep epg.py | awk '{print $1}')
if [ -n "$pid" ]; then
    kill -9 $pid
fi

#/usr/bin/python /root/xiechc/epg/epga.py
#/usr/bin/python /root/xiechc/epg/epgb.py
#/usr/bin/python /root/xiechc/epg/epgc.py
/usr/bin/python /root/lhh/epg/epg.py
