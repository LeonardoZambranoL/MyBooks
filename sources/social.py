from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask import Markup
from flask_login import login_user, logout_user, login_required, current_user

from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash

from .models import Book, SharedBook, BookShareNotification, User
from . import db
from .functions import send_confirmation_mail

import json
from flask import jsonify, make_response

from CONSTANTS import *

social = Blueprint('social', __name__)

"""
Social-related processes like sharing a Book or creating/using a group are taken care of by social.py
"""


@social.route('/share_book', methods=['GET', 'POST'])
@login_required
def share_book():
    if request.method == 'POST':
        data = request.form
        bookToShareId = data['bookToShare']
        recieverType = data['receiverType']
        if data and bookToShareId:
            bookToShare = Book.query.get(bookToShareId)
            if bookToShare:
                if bookToShare.userId == current_user.id:

                    if recieverType == "0":  # Person
                        recieverPersonUserName = data['userName']
                        recieverPerson = User.query.filter_by(userName=recieverPersonUserName).first()
                        if recieverPerson:
                            new_notification = BookShareNotification(bookId=bookToShare.id, fromId=current_user.id, toId=recieverPerson.id)
                            db.session.add(new_notification)
                            db.session.commit()
                            message = "Book shared!"
                            flash(Markup(message), category="success")
                            return redirect(url_for('social.share_book'))

                        else:
                            warning = "The user could not be found"
                            flash(Markup(warning), category="error")
                            return redirect(url_for('social.share_book'))

                    elif recieverType == "1":  # Group
                        pass
                        #recieverGroupId = data['']
                    else:
                        warning = "Something unexpected happened, please try again."
                        flash(Markup(warning), category="error")
                        return redirect(url_for('social.share_book'))
                else:
                    warning = "Something unexpected happened, please try again."
                    flash(Markup(warning), category="error")
                    return redirect(url_for('social.share_book'))
            else:
                warning = "Book could not be found, please try again."
                flash(Markup(warning), category="error")
                return redirect(url_for('social.share_book'))
        else:
            warning = "Book could not be shared, make sure to enter all the information."
            flash(Markup(warning), category="error")
            return redirect(url_for('social.share_book'))

    elif request.method == 'GET':
        books_info = {}
        for notification in current_user.bookShareNotifications:
            bookId = notification.bookId
            book = Book.query.get(bookId)
            senderID = notification.fromId
            sender = User.query.get(senderID)
            if book:
                book_name = book.name
                book_description = book.description
            else:
                book_name = "not found"
                book_description = "not found"

            if sender:
                sender_name = sender.userName
            else:
                sender_name = "not found"
            books_info[notification.id] = dict(name=book_name, description=book_description, sender=sender_name)
        return render_template('share_book.html', user=current_user, books_info=books_info)