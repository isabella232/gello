# -*- coding: utf-8 -*-

"""repos/views.py

repos-related routes and view-specific logic.
"""

from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app
from flask_login import login_required, current_user
from . import repo
from .forms import RepoForm, RefreshForm
from ... import db
from ...models import Repo
from ...services import GitHubService


@repo.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Updates the repositories saved on POST request."""
    form = RefreshForm()
    if form.validate_on_submit():
        github_service = GitHubService()

        # Add all the repositories to the Database for the organization
        for r in github_service.repos():
            _r = Repo(
                name=r.name,
                url=r.html_url,
                github_repo_id=r.id
            )
            # Add repository to database
            db.session.add(_r)

        # persist the repositories
        db.session.commit()
        flash('The repos have been updated.')

        return redirect(url_for('.index'))

    page = request.args.get('page', 1, type=int)
    query = Repo.query
    pagination = query.order_by(Repo.timestamp.desc()).paginate(
        page, per_page=10,
        error_out=False
    )
    repos = pagination.items

    return render_template(
        'repos.html',
        repos=repos,
        form=form,
        pagination=pagination
    )


@repo.route('/repo/<int:id>', methods=['GET', 'POST'])
@login_required
def show(id):
    repo = Repo.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (repo.issues.count() - 1) / \
            10 + 1
    return render_template('repo.html', repos=[repo])


@repo.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    repo = Repo.query.get_or_404(id)
    if current_user != repo.author:
        abort(403)

    form = RepoForm()
    if form.validate_on_submit():
        repo.body = form.body.data
        db.session.add(repo)
        flash('The repo has been updated.')
        return redirect(url_for('.repo', id=repo.id))

    form.body.data = repo.body
    return render_template('edit_repo.html', form=form)
