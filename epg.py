# -*-   coding: utf-8 -*-
'''
抓取soutv网站的电视节目单
抓取荔枝网的广东本地电视台节目单
'''
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import datetime
import time
import mysql
try:
    import xml.etree.CElementTree as ET
except:
    import xml.etree.ElementTree as ET

ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)

from connect import get, post, json_load


def get_tomorrow_date(fmt='%Y-%m-%d'):
    date = datetime.datetime.now() + datetime.timedelta(days=0)
    return date.strftime(fmt)


def timestamp_to_time(timestamp):
    '''
    把时间戳转换成yyyy-mm-dd HH24:MM:SS
    '''
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))


def get_et_root():
    file_path = os.path.join(ROOT_PATH, 'epg', 'tvs.xml')
    if not os.path.exists(file_path):
        print('tvs.xml file not exists.')
        sys.exit(1)
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root


def get_tvsou_channels():
    root = get_et_root()
    channels = list()
    for child in root:
        if child.attrib['site'] == 'tvsou':
            channels.append(
                {'gid': child.attrib['gid'], 'cid': child.attrib['cid']})
    return channels


def get_gdtv_channels():
    root = get_et_root()
    channels = list()
    for child in root:
        if child.attrib['site'] == 'gdtv':
            channels.append(
                {'gid': child.attrib['gid'], 'cid': child.attrib['cid']})
    return channels


def process_tvsou(cid, date, retry=3):
    url = 'https://www.tvsou.com/api/ajaxGetPlay'
    sub_data = {'date': date, 'channelid': cid}
    data = None
    while retry > 0:
        data = post(url, sub_data, ctype='json')
        if not data:
            print('[%s]No data, try again.' % cid)
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
            print('[%s]No data, try again.' % cid)
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


def run_tvsou(channels=None):
    '''
    获取搜视网的非广东电视频道的节目
    '''
    if not channels:
        channels = get_tvsou_channels()
    date = get_tomorrow_date('%Y%m%d')
    result = dict()
    for channel in channels:
        data = process_tvsou(channel['cid'], date)
        if data:
            result[channel['gid']] = data
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
    return result


def save_program(gid, data):
    for program in data:
        mysql.UpdateEPG(gid, program['program_name'], program['time'], "/data/" + gid)


def main():
    data1 = run_gdtv()
    data2 = run_tvsou()
    result = dict(data1.items() + data2.items())
    for key, val in result.items():
        if not val:
            print('[%s]channel clawl failed.' % key)
            continue
        save_program(key, val)
    sys.exit(0)

if __name__ == '__main__':
    main()
