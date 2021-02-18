from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)
from werkzeug.exceptions import abort

import mistune
from . import highlighter
from flaskr.auth import login_required
from flaskr.db import get_db
from feedgen.feed import FeedGenerator
try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo

bp = Blueprint('blog', __name__)


@bp.route('/blog/')
@bp.route('/blog')
def blog_index():
    return redirect('/blog/0')


@bp.route('/blog/<int:offset>')
def blog(offset):
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC LIMIT 5 OFFSET ?', (offset, )
    ).fetchall()
    total_posts = db.execute(
        'SELECT COUNT(p.id)'
        ' FROM post p JOIN user u ON p.author_id = u.id'
    ).fetchone()
    return render_template('blog/index.html', posts=posts, mistune=mistune, highlighter=highlighter, offset=offset,
                           total_posts=total_posts, len=len)


@bp.route('/rss')
def rss():
    fg = FeedGenerator()
    fg.title('lukebriggs.dev')
    fg.description('All the blog posts of Luke Briggs')
    fg.link(href='https://www.lukebriggs.dev')

    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    for post in posts: # get_news() returns a list of articles from somewhere
        fe = fg.add_entry()
        fe.title(post['title'])
        fe.link(href=f"/{post['id']}")
        fe.description(mistune.markdown(post['body'], renderer=highlighter.HighlightRenderer()))
        fe.guid(str(post['id']), permalink=True)
        fe.author(name=post['username'], email="contact@lukebriggs.dev")
        fe.pubDate(post['created'].replace(tzinfo=zoneinfo.ZoneInfo("Europe/London")))

    response = make_response(fg.rss_str())
    response.headers.set('Content-Type', 'application/rss+xml')

    return response


@bp.route('/<int:id>')
def post(id):
    db = get_db()
    post = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?', (id, )
    ).fetchone()

    return render_template('blog/post.html', post=post, mistune=mistune, highlighter=highlighter)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        error = None

        if not title:
            error = 'Title is required'

        if not body:
            error = 'Body is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post(title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.blog'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.blog_index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))
