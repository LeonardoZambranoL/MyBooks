from flask import Blueprint
from flask import render_template, redirect, url_for
from flask import request
from flask import flash
from flask import Markup
from flask import jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from .models import *
from . import db
from .functions import *

import json

from flask import send_file, send_from_directory
from io import BytesIO
from os import path
from os import remove


from CONSTANTS import *

views = Blueprint('views', __name__)


"""
views.py takes care of visual feedback given to the User.
views.py is in charge of rendering most templates, some exeptions are those that have to do with social deeds or the 
ones in charge of the authentication process.
"""


@views.route('/', methods=['GET'])
def home():
    if current_user.is_authenticated and current_user.validated:
        return render_template("personal_home.html", user=current_user, cover_folder_path=UPLOADED_COVER_PAGES_FOLDER)
    else:
        return render_template("general_home.html", user=current_user)


@views.route('/upload_book', methods=['POST', 'GET'])
@login_required
def upload_book():

    if current_user.is_authenticated:
        if request.method == 'POST':
            data = request.form
            name = data['name']
            description = data['description']
            file = request.files['book']
            save_name = random_name(BOOK_SAVE_NAME_LENGTH)
            name_already_used = Book.query.filter_by(save_name=save_name).first()  # To be treated as boolean
            while name_already_used:
                save_name = random_name(BOOK_SAVE_NAME_LENGTH)
                name_already_used = User.query.filter_by(save_name=save_name).first()

            if len(name) > MAX_BOOK_NAME_LENGTH:
                name = name[:MAX_BOOK_NAME_LENGTH]

            if len(description) > MAX_BOOK_DESCRIPTION_LENGTH:
                description = description[:MAX_BOOK_DESCRIPTION_LENGTH]

            if file.filename:
                #try:
                new_book = Book(save_name=save_name, name=name, description=description, owned= True, userId=current_user.id)
                db.session.add(new_book)

                store_book(file, save_name)

                message = 'Book created successfully!'
                flash(Markup(message), category='success')
            #except Exception as e:
                #    raise e
                #    return "<h1>Something unexpected happened, please try again</h1>"

                db.session.commit()
                return redirect(url_for('views.upload_book'))
            else:
                warning = 'Invalid file provided!'
                flash(Markup(warning), category='error')
                return redirect(url_for('views.upload_book'))

        elif request.method == 'GET':
            return render_template("book_upload.html", user=current_user)

    else:
        return redirect( url_for('views.home') )


@views.route('/edit_book', methods=['POST'])
@login_required
def edit_book():

    data = json.loads(request.data)
    bookId = data['bookId']
    newName = data['newName']
    newDescription = data['newDescription']
    newDescription = newDescription.strip()
    newName = newName.strip()

    print(newDescription)

    if len(newName) > MAX_BOOK_NAME_LENGTH:
        newName = newName[:MAX_BOOK_NAME_LENGTH]

    if len(newDescription) > MAX_BOOK_DESCRIPTION_LENGTH:
        newDescription = newDescription[:MAX_BOOK_DESCRIPTION_LENGTH]

    if newName and not newName.isspace():

            book = Book.query.get(bookId)

            if book:
                if book.userId == current_user.id:
                    book.name = newName
                    book.description = newDescription
                    db.session.commit()
                    return jsonify(msg="Changes Saved!")
                else:
                    return jsonify(msg="Not Allowed")

            else:
                return jsonify(msg="Not Allowed")

    else:
        return jsonify(msg="Title can not be blank.")


@views.route('/read_book/<bookId>')
@login_required
def read_book(bookId):
    book = Book.query.get(bookId)
    if book:
        if book.userId == current_user.id:
            return render_template("read_book.html", user=current_user, book=book, client_id="f8772d4514814c54824b650d26a30411")
        else:
            return "<h1> Not allowed </h1>"
    else:
        return "<h1>  Not allowed  </h1>"


# Sends book contents, used mainly for src in the html
@views.route('/get_book/<bookId>')
@login_required
def get_book(bookId):
    book = Book.query.get(bookId)
    if book:
        if book.userId == current_user.id: # Book is owned
            book_file_name = book.save_name
            book_path = os.path.join(UPLOADED_BOOKS_FOLDER, book_file_name) + ".pdf"
            if os.path.exists(book_path):
                with open(book_path, 'rb') as f:
                    data = f.read()
            else:
                data = return_default_book()
        else:
            data = return_default_book()
    else:
        data = return_default_book()

    return send_file(BytesIO(data), attachment_filename=f'{book.name}.pdf')


@views.route('/get_cover_page/<bookType>/<bookId>/<supplementaryId>')
@login_required
def get_cover_page(bookType, bookId, supplementaryId):
    # type 0 ---> owned
    # type 1 ---> shared notification
    # type 2 ---> shared book

    if bookType == "0":
        book = Book.query.get(bookId)
        if book:
            if book.userId == current_user.id:
                save_name = book.save_name
                cover_page_path = os.path.join(UPLOADED_COVER_PAGES_FOLDER, save_name)+".png"
                if os.path.exists(cover_page_path):
                    with open(cover_page_path, 'rb') as f:
                        data = f.read()
                else:
                    data = return_default_cover_page()
            else:
                data = return_default_cover_page()
        else:
            data = return_default_cover_page()

        return send_file(BytesIO(data), attachment_filename="cover_page")

    elif bookType == "1":  # cover page on notification
        notificationId = supplementaryId
        book = Book.query.get(bookId)
        notification = BookShareNotification.query.get(notificationId)
        if book and notification:
            if notification.bookId == book.id and notification.toId == current_user.id:
                save_name = book.save_name
                cover_page_path = os.path.join(UPLOADED_COVER_PAGES_FOLDER, save_name) + ".png"
                if os.path.exists(cover_page_path):
                    with open(cover_page_path, 'rb') as f:
                        data = f.read()
                else:
                    data = return_default_cover_page()
            else:
                data = return_default_cover_page()
        else:
            data = return_default_cover_page()

        return send_file(BytesIO(data), attachment_filename="cover_page")


@views.route('/customize')
@login_required
def customize():
    return render_template('customize.html', user=current_user)