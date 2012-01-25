feeds = {
    'wiki': dict(
        url = 'http://hackerspace.pl/wiki/feed.php',
        max_title_length = 70,
        title_shortener = 'wiki',
        options = dict(
            type='atom1',
            ns='projects',
            linkto='current'
        ),
        format_str = '%(author)s just modified %(title)s on our wiki %(url)s'
    ),
    'blog': dict(
        url = 'http://hackerspace.pl/blog/feed/atom',
        max_title_length = 100,
        title_shortener = 'blog',
        options = {},
        format_str = 'New blog post: %(title)s %(url)s'
    )
}
log_name = './bot.log'
refresh = 60.0
