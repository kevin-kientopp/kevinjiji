from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import logging

from kevinjiji.auth import login_required
from kevinjiji.db import get_db

bp = Blueprint('ads', __name__)

logger = logging.getLogger()

@bp.route('/')
def index():
    db = get_db()
    ads = db.execute(
        'SELECT a.id, title, description, a.created, user_id, username'
        ' FROM ad a JOIN user u ON a.user_id = u.id'
        ' ORDER BY a.created DESC'
    ).fetchall()
    return render_template('ads/index.html', ads=ads)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO ad (title, description, user_id)'
                ' VALUES (?, ?, ?)',
                (title, description, g.user['id'])
            )
            db.commit()
            return redirect(url_for('ads.index'))

    return render_template('ads/create.html')


def get_ad(id, check_user=True):
    ad = get_db().execute(
        'SELECT a.id, title, description, a.created, user_id, username, email'
        ' FROM ad a JOIN user u ON a.user_id = u.id'
        ' WHERE a.id = ?',
        (id,)
    ).fetchone()

    if ad is None:
        abort(404, "Ad id {0} doesn't exist.".format(id))

    if check_user and ad['user_id'] != g.user['id']:
        abort(403)

    return ad


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    ad = get_ad(id)

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE ad SET title = ?, description = ?'
                ' WHERE id = ?',
                (title, description, id)
            )
            db.commit()
            return redirect(url_for('ads.index'))

    return render_template('ads/update.html', ad=ad)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_ad(id)
    db = get_db()
    db.execute('DELETE FROM ad WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('ads.index'))


@bp.route('/<int:id>/view', methods=('GET', 'POST'))
def view(id):
    logger.info('view called')
    ad = get_ad(id, check_user=False)
    logger.info(f'ad = {ad["title"]}')

    return render_template('ads/view.html', ad=ad)
