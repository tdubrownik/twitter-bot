import xml.dom.minidom
import urllib, urllib2
import oauth2 as oauth
import logging
from logging.handlers import TimedRotatingFileHandler
from dateutil import parser
from time import mktime

import config
from token import *

last_timestamps = {}
formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] %(message)s')
serr = logging.StreamHandler()
serr.setFormatter(formatter)
th = TimedRotatingFileHandler(config.log_name, when='d')
th.setFormatter(formatter)
logger = logging.getLogger('bot')
logger.addHandler(th)
logger.addHandler(serr)
logger.setLevel(logging.INFO)

def wiki_shorten(title, max_length, placeholder='a page'):
    if len(title) > max_length:
        title = split(' ')[0]
    if len(title) > max_length:
        title = 'a page'
    return title

def blog_shorten(title, max_length):
    if len(title) > max_length:
        return title[:max_length-3] + '...'
    return title

shorteners = {
   'wiki': wiki_shorten,
   'blog': blog_shorten, 
}

def get_first_child(obj, name):
    return obj.getElementsByTagName(name)[0]

def get_text(obj, name):
    modified = get_first_child(obj, name)
    return modified.firstChild.data

def get_modified(obj):
    return parser.parse(get_text(obj, 'modified'))

def get_updated(obj):
    return parser.parse(get_text(obj, 'updated'))

def get_feed(url, options):
    optstr = urllib.urlencode(options)
    res = urllib2.urlopen(url + '?' + optstr)
    feed = xml.dom.minidom.parse(res)
    return get_updated(feed), feed.getElementsByTagName('entry')

def update(name, feed_config, ts_obj = last_timestamps):
    logger.info('fetching updates for feed ' + name)
    feed_update, entries = get_feed(feed_config['url'], feed_config['options'])
    if name in ts_obj:
        last_timestamp = ts_obj[name]
        for entry in entries:
            updated = get_updated(entry)
            timestamp = mktime(updated.utctimetuple())
            if timestamp > last_timestamp:
                post_update(entry, feed_config['format_str'],
                    shorteners[feed_config['title_shortener']], 
                    feed_config['max_title_length'])
    ts_obj[name] = mktime(feed_update.utctimetuple())

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

def post_update(entry, format_str, title_shortener, max_title_length):
    title = title_shortener(get_text(entry, 'title'), max_title_length)
    try:
        author = get_text(get_first_child(entry, 'author'), 'name')
    except IndexError:
        author = 'Somebody'
    url = get_first_child(entry, 'link').attributes['href'].value
    text = format_str % dict(title=title, author=author, url=url)
    logger.info('posting update (text: "%s")' % text)
    oauth_req('https://api.twitter.com/1/statuses/update.json', 'POST',
        { 'status': text })

def main():
    import traceback
    from time import sleep, time
    while True:
        for name in config.feeds:
            try:
                update(name, config.feeds[name], last_timestamps)
            except Exception as e:
                logger.error('Error! ' + traceback.format_exc(e))
        sleep(config.refresh)

if __name__ == '__main__':
    main()
