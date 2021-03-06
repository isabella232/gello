# -*- coding: utf-8 -*-

#
# Unless explicitly stated otherwise all files in this repository are licensed
# under the Apache 2 License.
#
# This product includes software developed at Datadog
# (https://www.datadoghq.com/).
#
# Copyright 2018 Datadog, Inc.
#

"""jira_parent_issue.py

JIRA parent issues model.
"""

from datetime import datetime
from .. import db
from . import SubscribedJIRAIssue


class JIRAParentIssue(db.Model):
    """JIRA issues that can hold subtasks"""

    __tablename__ = 'jira_parent_issues'

    # Attributes
    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(64), unique=False)
    jira_issue_key = db.Column(db.String(64), unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Associations

    project_key = db.Column(db.String(64), db.ForeignKey('projects.key'),
                            unique=False)
    subscribed_issues = db.relationship(
        'SubscribedJIRAIssue',
        foreign_keys=[SubscribedJIRAIssue.jira_issue_key],
        backref=db.backref('issue_subscribed_issue', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def to_json(self):
        return {
            'label': self.jira_issue_key,
            'value': self.jira_issue_key
        }
