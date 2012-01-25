import xml.dom.minidom
import urllib, urllib2
import oauth2 as oauth
import logging
from logging.handlers import TimedRotatingFileHandler
from dateutil import parser
from time import mktime

import config
from token import *

last_timestamp = None
formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] %(message)s')
serr = logging.StreamHandler()
serr.setFormatter(formatter)
th = TimedRotatingFileHandler(config.log_name, when='d')
th.setFormatter(formatter)
logger = logging.getLogger('bot')
logger.addHandler(th)
logger.addHandler(serr)
logger.setLevel(logging.INFO)

def get_first_child(obj, name):
    return obj.getElementsByTagName(name)[0]

def get_text(obj, name):
    modified = get_first_child(obj, name)
    return modified.firstChild.data

def get_modified(obj):
    return parser.parse(get_text(obj, 'modified'))

def fetch_updates(url, options):
    global last_timestamp
    logger.info('fetching updates')
    optstr = urllib.urlencode(options)
    res = urllib2.urlopen(url + '?' + optstr)
    feed = xml.dom.minidom.parse(res)
    if last_timestamp:
        for entry in feed.getElementsByTagName('entry'):
            modified = get_modified(entry)
            timestamp = mktime(modified.utctimetuple())
            if timestamp > last_timestamp:
                post_update(entry)
    feed_update = get_modified(feed)
    last_timestamp = mktime(feed_update.utctimetuple())

def oauth_req(url, http_method = 'GET', data = {}, headers = None):
    # za https://dev.twitter.com/docs/auth/oauth/single-user-with-examples#python
    from urllib import urlencode
    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    token = oauth.Token(key=oauth_token, secret=oauth_token_secret)
    client = oauth.Client(consumer, token)
    return client.request(
        url,
        method = http_method,
        body = urlencode(data),
        headers = headers)

def post_update(entry):
    title = get_text(entry, 'title')
    if len(title) > config.max_title_length:
        title = config.split(' ')[0]
    if len(title) > config.max_title_length:
        title = 'a page'
    try:
        author = get_text(get_first_child(entry, 'author'), 'name')
    except IndexError:
        author = 'Somebody'
    url = get_first_child(entry, 'link').attributes['href'].value
    text = config.format_str % dict(title=title, author=author, url=url)
    logger.info('posting update (text: "%s")' % text)
    oauth_req('https://api.twitter.com/1/statuses/update.json', 'POST',
        { 'status': text })

def main():
    global last_timestamp
    import traceback
    from time import sleep, time
    while True:
        try:
            fetch_updates(config.url, config.options)
            sleep(config.refresh)
        except Exception as e:
            logger.error('Error!')

if __name__ == '__main__':
    main()
