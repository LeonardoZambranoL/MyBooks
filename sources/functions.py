import random
import string
import os
from flask import url_for
from flask import current_app
from flask import Blueprint
from flask_login import login_required
from flask import request
from flask_login import current_user
from flask import send_file

import smtplib
from email.message import EmailMessage

from .models import *
from CONSTANTS import *

import json
from flask import jsonify

import fitz

from .models import *

from io import BytesIO

functions = Blueprint('functions', __name__)

"""
function.py will contain all operations that occur 'under the hood'.
It will not render any templates but do processes that do not require visual feedback to the user.
Some of its functions will be called by other blueprints.
Not all of the functions in functions.py are app routes.
"""


def random_name(length):
    letters = string.ascii_letters
    digits = string.digits
    characters = letters+digits
    name = ''.join(random.sample(characters, length))

    return name


def valid_name(name):
    letters = string.ascii_letters
    digits = string.digits
    punctuation = string.punctuation
    characters = letters + digits + punctuation + " "

    if name.isspace():
        return False
    
    if name:
        for char in name:
            if char not in characters:
                return False
    else:
        return False

    return True


def valid_general_entry(content):
    letters = string.ascii_letters
    digits = string.digits
    punctuation = string.punctuation
    characters = letters + digits + punctuation + " " + "\n" + "\t" + "" + "\r"

    for char in content:
        if char:
            if char not in characters:
                return False

    return True


def random_key_gen():
    return os.urandom(24)


def send_confirmation_mail(email, serializer, salt):
    token = serializer.dumps(email, salt=salt)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            msg = EmailMessage()
            msg["Subject"] = "My books account validation"
            msg["From"] = current_app.config['MAIL_USERNAME']
            msg["to"] = email
            conf_link = url_for('auth.validate_email', token=token, _external=True)
            body = f'To validate your account, click on the following link:\n{conf_link}'
            msg.set_content(body)
            smtp.send_message(msg)
    except Exception as e:
        print(" ERROR WHEN SENDING CONF MAIL")
        print(str(e))


def store_book(data, save_name):
    cover_page_name = f'{save_name}.png'
    book_save_name = f'{save_name}.pdf'
    book_save_path = os.path.join(UPLOADED_BOOKS_FOLDER, book_save_name)
    cover_page_path= os.path.join(UPLOADED_COVER_PAGES_FOLDER, cover_page_name)

    data.save(book_save_path)
    pdf = fitz.open(book_save_path)
    page = pdf.loadPage(0)
    pix = page.getPixmap()
    pix.writeImage(cover_page_path)


# returns the contents of the default book, used mainly for src in html.
def return_default_book():
    default_book_path = 'sources' + url_for('static', filename='DefaultBook.pdf')
    with open(default_book_path, 'rb') as f:
        data = f.read()
    return data


# returns the contents of the default cover page, used mainly for src in html.
def return_default_cover_page():
    default_cover_page_path = 'sources' + url_for('static', filename='DefaultCoverPage.png')
    with open(default_cover_page_path, 'rb') as f:
        data = f.read()
    return data


# Gets the title and description of a book stored in the data base.
@functions.route("/get_book_data", methods=['POST'])
@login_required
def get_book_data():
    # OWNED BOOKS
    data = json.loads(request.data)
    bookId = data['bookId']
    book = Book.query.get(bookId)
    if book:
        if book.userId == current_user.id:
            return jsonify(name=book.name, description=book.description)
        else:
            return jsonify(name='not found', description='not found')
    else:
        return jsonify(name='not found', description='not found')


"""
@functions.route("/get_book_data_from_jinja/<bookId>")
@login_required
def get_book_data_from_jinja(bookId):
    book = Book.query.get(bookId)
    if book:
        if book.userId == current_user.id:
            return {"name": book.name, "description": book.description}
        else:
            return {"name": "not found", "description": "not found"}
    else:
        return {"name": "not found", "description": "not found"}
"""


@functions.route('/download_book/<bookId>')
@login_required
def download_book(bookId):
    book = Book.query.get(bookId)
    if book:
        if book.userId == current_user.id:
            book_file_name = book.save_name
            book_path = os.path.join(UPLOADED_BOOKS_FOLDER, book_file_name) + ".pdf"
            with open(book_path, 'rb') as f:
                data = f.read()
            return send_file(BytesIO(data), attachment_filename=f'{book.name}.pdf', as_attachment=True)
        else:
            data = return_default_book()
            return send_file(BytesIO(data), attachment_filename='not_found.pdf', as_attachment=True)
    else:
        data = return_default_book()
        return send_file(BytesIO(data), attachment_filename='not_found.pdf', as_attachment=True)


# Deletes item from data base
@functions.route('/delete_item', methods=['POST'])
@login_required
def delete_item():
    data = json.loads(request.data)
    itemType = data['itemType']
    itemID = data['itemID']

    if itemType == 'book':
        item = Book.query.get(itemID)
    elif itemType == 'note':
        #item = Note.query.get(itemID)
        return jsonify({})
    else:
        # return '<h1> INVALID </h1>'
        return jsonify({})

    if item:
        if item.userId == current_user.id:
            if itemType == 'book':
                bookPath = os.path.join(UPLOADED_BOOKS_FOLDER, item.save_name)+".pdf"
                if os.path.exists(bookPath):
                    os.remove(bookPath)
                coverPath = os.path.join(UPLOADED_COVER_PAGES_FOLDER, item.save_name)+".png"
                if os.path.exists(coverPath):
                    os.remove(coverPath)

            db.session.delete(item)
            db.session.commit()

    return jsonify({})


@functions.route("/accept_decline_shared_book", methods=['POST'])
@login_required
def accept_decline_shared_book():
    # OWNED BOOKS
    data = json.loads(request.data)
    notifId = data['notifId']
    action = data['action']
    notif = BookShareNotification.query.get(notifId)
    if notif:
        if notif.toId == current_user.id:

            if action == 0:  # decline

                try:
                    db.session.delete(notif)
                    db.session.commit()
                    return jsonify(msg="notification deleted", status="success")
                except:
                    return jsonify(msg="notification could not be deleted, please try again later", status="error")

            elif action == 1:  # accept
                book = Book.query.get(notif.bookId)
                if book:
                    try:
                        newSharedBook = SharedBook(bookId=notif.bookId, fromId=notif.fromId, toUser=True, toGroup=False,
                                                   toUserId=current_user.id)
                        db.session.add(newSharedBook)
                        db.session.commit()
                        book.shared = True
                        db.session.commit()
                        db.session.delete(notif)
                        db.session.commit()
                        return jsonify(msg="book added to your library", status="success")
                    except:
                        return jsonify(msg="something unexpected occurred, please try again later", status= "error")
                else:
                    return jsonify(msg="The book could not be found, it could have been deleted by its uploader.", status="error")

            else:  # invalid
                return jsonify(msg="something unexpected occurred, please try again later", status="error")
        else:
            return jsonify(msg="something unexpected occurred, please try again later", status="error")
    else:
        return jsonify(msg="something unexpected occurred, please try again later", status="error")