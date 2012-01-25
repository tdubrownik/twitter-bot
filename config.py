url = 'http://hackerspace.pl/wiki/feed.php'
refresh = 60.0
max_title_length = 70
options = dict(
    type='atom',
    ns='projects',
    linkto='current',
)
format_str = '%(author)s just modified %(title)s on our wiki %(url)s'
log_name = './bot.log'
