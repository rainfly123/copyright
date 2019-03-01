# -*-   coding: utf-8 -*-
import json
import urllib
import urllib2
import cookielib

from log import LOG

CKJ = cookielib.CookieJar()
OPENER = urllib2.build_opener(urllib2.HTTPCookieProcessor(CKJ))

# default http socket timeout 30 seconds
SOCK_TIMEOUT = 30


def set_headers(ctype='json', refer='tvsou'):
    '''
    :param ctype: <str> default json(json/xml/text)
    '''
    header = [
        ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'),
        ('Accept-Language', 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,zh-TW;q=0.6'),
        ('Connection', 'Keep-Alive'),
    ]
    ctype = ctype.lower()
    if ctype == 'json':
        header.append(('Content-Type', 'application/x-www-form-urlencoded'))
        header.append(
            ('Accept', 'application/json, text/javascript, */*; q=0.01'))
    elif ctype == 'xml':
        header.append(('Content-Type', 'text/xml'))
        header.append(('Accept', 'application/xml, text/xml, */*; q=0.01'))
    else:
        header.append(('Content-Type', 'text/html'))
        header.append(
            ('Accept', 'text/html,application/xhtml+xml,application/xml, */*; q=0.01'))
    if refer == 'tvsou':
        header.append(('Referer','https://www.tvsou.com'))
    elif refer == 'gdtv':
        header.append(('Referer','http://www.gdtv.cn'))
    return header


def post(url, values={}, ctype='json', refer="tvsou"):
    '''
    http/https post request
    :param url: <str> request url
    :param values: <dict> form data, eg:{'xx':'zz'}
    :param ctype: <str> default json, (json/xml/text)
    :except: connect error, return None
    :returns: string
    '''
    values = urllib.urlencode(values).encode('utf-8')
    OPENER.addheaders = set_headers(ctype, refer)
    try:
        result = OPENER.open(
            url, values, timeout=SOCK_TIMEOUT).read().decode('utf-8')
        return result
    # except (urllib2.HTTPError, urllib2.URLError) as ex:
    #     LOG.error('Connection error:[%s]' % ex)
    except Exception as exp:
        LOG.error('Connection error:[%s]' % exp)
    return None


def get(url, ctype='json', refer='gdtv'):
    '''
    http/https get request
    :param url: <str> request url
    :except: connect error, return None
    :param ctype: <str> default json, (json/xml/text)
    :returns: string
    '''
    OPENER.addheaders = set_headers(ctype, refer)
    try:
        result = OPENER.open(url, timeout=SOCK_TIMEOUT).read().decode('utf-8')
        return result
    # except (urllib2.HTTPError, urllib2.URLError) as err:
    #     LOG.error('Connection error:[%s]' % err)
    except Exception as exp:
        LOG.error('Connection error:[%s]' % exp)
    return None


def json_load(data):
    if not data:
        return dict()
    return json.loads(data)
