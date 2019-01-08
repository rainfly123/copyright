#!/usr/bin/env python
# -*-   coding: utf-8 -*-
'''
抓取soutv网站的电视节目单
抓取荔枝网的广东本地电视台节目单
'''
import os
import sys
import re
import random
reload(sys)
sys.setdefaultencoding("utf-8")
import datetime
import time
from argparse import ArgumentParser
import mysql
try:
    import xml.etree.CElementTree as ET
except:
    import xml.etree.ElementTree as ET

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

from connect import get, post, json_load
from log import LOG

INPUT_DATE = None

def get_tomorrow_date(fmt='%Y-%m-%d'):
    date = datetime.datetime.now() + datetime.timedelta(days=1)
    if INPUT_DATE:
        date = datetime.datetime.strptime(INPUT_DATE, '%Y-%m-%d')
    return date.strftime(fmt)

def timestamp_to_time(timestamp):
    '''
    把时间戳转换成yyyy-mm-dd HH24:MM:SS
    '''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))

def sleep():
    num = random.randint(2, 5)
    time.sleep(num)



def get_gdtv_channels():
    data = mysql.getAllLiveEpg()
    channels = [{'gid': epg['gid'], 'cid': epg['channel_id']} for epg in data if epg['origin'] == 'gdtv']
    return channels


def process_tvsou(cid, date, retry=3):
    url = 'https://www.tvsou.com/api/ajaxGetPlay'
    sub_data = {'date': date, 'channelid': cid}
    data = None
    while retry > 0:
        data = post(url, sub_data, ctype='json')
        if not data:
            LOG.error('[%s]No data, try again.' % cid)
            retry -= 1
        else:
            break
    if not data:
        return None
    datas = list()
    data = json_load(data)
    for obj in data.get('list'):
        datas.append({'time': timestamp_to_time(
            obj.get('playtimes')), 'program_name': obj.get('title')})
    return datas


def process_gdtv(cid, date, retry=3):
    url = 'http://epg.gdtv.cn/f/%s/%s.xml' % (cid, date)
    data = None
    while retry > 0:
        data = get(url, ctype='xml')
        if not data:
            LOG.error('[%s]No data, try again.' % cid)
            retry -= 1
        else:
            break
    if not data:
        return None
    root = ET.fromstring(data.encode('utf8'))
    datas = list()
    for obj in root[1].findall('content'):
        datas.append({'time': timestamp_to_time(
            obj.attrib['time1']), 'program_name': obj.text})
    return datas


#def run_tvsou(channels=[{'gid':'cctv5', 'cid':"6b26bee1"}]):
def run_tvsou(channels=[{'gid':'cctv5', 'cid':"6b26bee1"},{'gid':"cctv5p", "cid":"e4e3801d"}]):
    '''
    获取搜视网的非广东电视频道的节目
    '''
    date = get_tomorrow_date('%Y%m%d')
    result = dict()
    for channel in channels:
        data = process_tvsou(channel['cid'], date)
        if data:
            result[channel['gid']] = data
        sleep()
    return result


def run_gdtv(channels=None):
    '''
    获取广东本地的电视节目
    '''
    if not channels:
        channels = get_gdtv_channels()
    date = get_tomorrow_date()
    result = dict()
    url = 'http://epg.gdtv.cn/f/%s/%s.xml'
    for channel in channels:
        data = process_gdtv(channel['cid'], date)
        result[channel['gid']] = data
        sleep()
    return result


def save_program(gid, data):
    pattern = re.compile(u'亚洲杯')
    pn = re.compile(u'录像')
    p = re.compile(u'足球之夜')
    for program in data:
        #print(gid, program['program_name'], program['time'], "/data/" + gid)
        name = program['program_name']
        time = program['time']
        find1 = pattern.findall(name)
        find2 = pn.findall(name)
        find3 = p.findall(name)
        if len(find1) > 0 and len(find2) == 0 and len(find3) == 0 :
            print name , gid,  time
            i = data.index(program)
            if (i + 1) == len(data):
                which = i
            else:
                which = i + 1
            nextprogram = data[which]
            start = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            if which != i :
                end = datetime.datetime.strptime(nextprogram['time'], "%Y-%m-%d %H:%M:%S") - datetime.timedelta(seconds=60)
            else:
                end = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=9000)
            if start.day != end.day:
                end = datetime.datetime(start.year, start.month, start.day + 1) - datetime.timedelta(seconds=60)
                start2 = datetime.datetime(start.year, start.month, start.day + 1) 
                end2 = datetime.datetime(start.year, start.month, start.day + 1)  + datetime.timedelta(seconds=18000)
                mysql.UpdateLiveTask(gid, name, start, end)
                mysql.UpdateLiveTask(gid, name, start2, end2)
            else:
                mysql.UpdateLiveTask(gid, name, start, end)
    


def main():
    #data1 = run_gdtv()
    data2 = run_tvsou()
    result = data2
    for key, val in result.items():
        if not val:
            LOG.error('[%s]channel clawl failed.' % key)
            continue
        #print(val)
        save_program(key, val)
    sys.exit(0)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--date', type=str, help='crawl date, eg. 2018-01-01')
    args = parser.parse_args()
    regex = r'^\d{4}-\d{2}-\d{2}'
    if args.date:
        if re.match(regex, args.date):
            INPUT_DATE = args.date
        else:
            LOG.error('Date format is incorrect.')
            sys.exit(1)
    main()
