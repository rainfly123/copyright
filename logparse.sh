#!/bin/sh
pid=$(ps ax | grep -v grep | grep logparse.py | awk '{print $1}')
if [ -n "$pid" ]; then
    kill -9 $pid
fi
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
FILE="/data/ngx_temp/access_${YESTERDAY}.log"
echo $FILE

/usr/bin/python /root/lhh/epg/logparse.py -f $FILE
