#!/usr/bin/env python
import os
import sys
import argparse
import re
import mysql


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--logfile")
    parser.add_argument("-v", "--version", help="display version number", action="store_true")
    args = parser.parse_args()
    if args.version :
        print " "
        print " LogParser 1.0.0"
        print " xiechc@gmail.com"
        print " "
        sys.exit(0)
    print args.logfile
    with open(args.logfile, "r") as log:
        while True:
            line = log.readline()
            if line == "":
                sys.exit(0)
            result = re.findall("/\w+/pvr.+m3u8", line)
            if len(result) >= 1:
                mysql.updatePlayNum(result[0])
           
            #line = line.strip()
