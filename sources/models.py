from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from CONSTANTS import *


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    userName = db.Column(db.String(MAX_USER_NAME_LENGTH), unique=True)
    validated = db.Column(db.Boolean)
    books = db.relationship('Book')
    sharedBooks = db.relationship('SharedBook')
    groups = db.relationship('Group')
    bookShareNotifications = db.relationship('BookShareNotification')
    # notes = db.relationship('Note') # NOT IMPLEMENTED
    # bookNotes = db.relationship('BookNotes') # NOT IMPLEMENTED


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    save_name = db.Column(db.String(BOOK_SAVE_NAME_LENGTH))
    name = db.Column(db.String(MAX_BOOK_NAME_LENGTH))
    description = db.Column(db.String(MAX_BOOK_DESCRIPTION_LENGTH))
    owned = db.Column(db.Boolean)
    shared = db.Column(db.Boolean)
    date = db.Column(db.DateTime(timezone=True), default=func.now())


class SharedBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookId = db.Column(db.Integer, db.ForeignKey('book.id'))
    fromId = db.Column(db.Integer)                                  # Sender, who uploaded the book
    toUser = db.Column(db.Boolean)                                  # Was it shared to a User or to a group?
    toGroup = db.Column(db.Boolean)
    toUserId = db.Column(db.Integer, db.ForeignKey('user.id'))      # To which user or group was it sent?
    toGroupId = db.Column(db.Integer, db.ForeignKey('group.id'))


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    adminId = db.Column(db.Integer, db.ForeignKey('user.id'))
    code = db.Column(db.String)
    name = db.Column(db.String(MAX_GROUP_NAME_LENGTH))
    books = db.relationship('SharedBook')
    members = db.relationship('GroupMember')


class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupId = db.Column(db.Integer, db.ForeignKey('group.id'))
    memberId = db.Column(db.Integer, db.ForeignKey('user.id'))


# THESE NOTIFICATIONS ARE SEND TO USER WHEN SOMEONE SHARES BOOKS WITH THEM
class BookShareNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookId = db.Column(db.Integer, db.ForeignKey('book.id'))
    fromId = db.Column(db.Integer)  # Sender, who uploaded the book
    toId = db.Column(db.Integer, db.ForeignKey('user.id'))

"""
CREAR OBJETOS QUE GUARDEN QUE LIBRO SE COMPARTIÓ A QUIEN; PARA EL UPLOADER
"""

# WIP
"""
class Preferences(db.Model):
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    backgroundType = db.Column(db.Integer) # 0=default 1= solid color 2=image
    backgroundLoc = db.Column(db.String)
"""


# NOT IMPLEMENTED
"""
class BookNotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())  # func.now()-> auto timezone
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    bookID = db.Column(db.Integer, db.ForeignKey('book.id'))
"""

# NOT IMPLEMENTED
"""
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now()) # func.now()-> auto timezone
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
"""