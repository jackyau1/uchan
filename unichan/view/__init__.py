import random
import string
import time
from functools import wraps
from urllib.parse import urlparse

from flask import send_from_directory, session, request, abort
from markupsafe import escape, Markup

import config
from unichan import g, app
from unichan.lib.cache.posts_cache import PostCacheProxy
from unichan.lib.models import Post


@app.context_processor
def inject_variables():
    site_config_cached = g.site_cache.find_site_config_cached()

    all_boards = None
    if site_config_cached.boards_top:
        all_boards = g.board_cache.all_boards()

    return dict(all_boards=all_boards, site_config=site_config_cached)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = ''.join(
                random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))
    return session['_csrf_token']


def generate_csrf_token_html():
    return Markup('<input name="token" type="hidden" value="{}">'.format(escape(generate_csrf_token())))


def with_token():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not check_csrf_token(request.form.get('token')):
                abort(400)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_csrf_token(form_token):
    session_token = session.get('_csrf_token', None)
    return session_token is not None and form_token is not None and session_token == form_token


def check_csrf_referer(request):
    referer = request.headers.get('Referer', None)
    if not referer:
        return False

    parsed_url = urlparse(referer)

    return '{}://{}'.format(parsed_url.scheme, parsed_url.hostname) == config.SITE_URL


app.jinja_env.globals['csrf_token'] = generate_csrf_token
app.jinja_env.globals['csrf_html'] = generate_csrf_token_html

if config.DEBUG:
    @app.route('/test')
    def test_view():
        list = []
        for i in range(100):
            post = Post()
            post.thread_id = 13371337
            post.date = int(time.time() * 1000)
            post.name = 'AnonymousAnonymousAnonymous'
            post.subject = 'AnonymousAnonymousAnonymous'
            post.text = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmodtempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodoconsequat. Duis aute irure dolor in reprehenderit in voluptate velit essecillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat nonproident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmodtempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodoconsequat. Duis aute irure dolor in reprehenderit in voluptate velit essecillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat nonproident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmodtempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodoconsequat. Duis aute irure dolor in reprehenderit in voluptate velit essecillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat nonproident, sunt in culpa qui officia deserunt mollit anim id est laborum.Excepteur sint occaecat cupidatat nonproident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmodtempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodoconsequat. Duis aute irure dolor in reprehenderit in voluptate velit essecillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat nonproident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmodtempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodoconsequat. Duis aute irure dolor in reprehenderit in voluptate velit essecillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat nonproident, sunt in culpa qui officia deserunt mollit anim id est laborum.Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmodtempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodoconsequat. Duis aute irure dolor in reprehenderit in voluptate velit essecillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat nonproident, sunt in culpa qui officia deserunt mollit anim id est laborum.Excepteur sint occaecat cupidatat nonproident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
            post.refno = 13371337
            list.append(PostCacheProxy(post))

        print('generated data, setting into cache')

        return 'res: ' + str(g.cache.set('test_thread', list))
