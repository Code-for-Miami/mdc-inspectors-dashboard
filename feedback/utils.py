# -*- coding: utf-8 -*-
'''Helper utilities and decorators.'''

import pytz

from flask import (
    flash, request, url_for, current_app
)
from tzlocal import get_localzone

from feedback.extensions import mail
from flask_mail import Message

local_tz = get_localzone()


def send_email(subject, sender, recipients, text_body, html_body):
    ''' E-mail utility function.
    '''
    recipients_list = recipients.split(",")

    try:
        current_app.logger.info(
            'EMAILTRY | Sending message:\nTo: {}\n:From: {}\nSubject: {}'.format(
                recipients_list,
                sender,
                subject
            )
        )
        msg = Message(
            subject,
            sender=sender,
            recipients=recipients_list)
        msg.body = text_body
        msg.html = html_body
        mail.send(msg)
    except Exception, e:
        current_app.logger.error(
            'EMAILFAIL | Error: {}\nTo: {}\n:From: {}\nSubject: {}'.format(
                e,
                recipients_list,
                sender,
                subject
            )
        )
        return False


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash("{0} - {1}"
                  .format(getattr(form, field).label.text, error), category)


def thispage():
    try:
        args = request.view_args.items().copy()
        args.update(request.args.to_dict().items())

        args['thispage'] = '{path}?{query}'.format(
            path=request.path, query=request.query_string
        )
        return url_for(request.endpoint, **args)
    # pass for favicon
    except AttributeError:
        pass


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)  # .normalize might be unnecessary
