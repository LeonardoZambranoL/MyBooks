from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask import Markup
from flask_login import login_user, logout_user, login_required, current_user

from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from werkzeug.security import generate_password_hash,  check_password_hash

from .models import User
from . import db
from .functions import send_confirmation_mail

import json
from flask import jsonify, make_response

from CONSTANTS import *

auth = Blueprint('auth', __name__)

serializer = URLSafeTimedSerializer(b'\xf2\x07\xfc\x8ch\xf9\xb8\xee\x904E\xa7\x01\xb2\xa3$\x95^Q\xaf\xf6m\x922')
email_validation_salt = b'\x0c(g\xf0\xca|O\x01r\x1c\xa2\xa2\xd2\xb3Z\xd25J\xee\xfaQL\xe2\x03'


"""
auth.py is in charge of the authentication process.
"""


@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            if user.validated:
                if check_password_hash(user.password, password):
                    flash('Logged in!',  category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))

                else:
                    warning = 'Email-Password combination is incorrect.'
                    flash(Markup(warning), category='error')
            else:
                warning = 'Please validate your account before logging in. Click the validation link sent to ' \
                          'your email, check in spam as well. To get a new link sent to you, click ' \
                           f'<a href="#" onClick=resend_conf_mail("{email}")>here</a>.'
                flash(Markup(warning), category='error')
        else:
            message = f'This email is not registered, <a href="{url_for("auth.sign_up")}" class ="alert-link" >Sign Up!</a>'
            flash(Markup(message), category="info")

    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))


@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        user_name = data.get('user_name')
        password = data.get('password')
        password_repeat = data.get('passRep')

        warning = ''

        user = User.query.filter_by(email=email).first()
        user_name_taken = User.query.filter_by(userName=user_name).first()  # To be treated as boolean
        if user:
            if user.validated:
                warning += f'User already registered, <a href = "{url_for("auth.login")}" class ="alert-link">Login</a>'
                flash(Markup(warning), category="info")
                return render_template('sign_up.html', user=current_user)
            else:
                warning += f'User already registered but <b>not</b> validated. To validate your account,check the ' \
                           f'validation link sent to your email. To get a new link sent to you, click ' \
                           f'<a href="#" onClick=resend_conf_mail("{email}")>here</a>.'
                flash(Markup(warning), category="error")
                return render_template('sign_up.html', user=current_user)

        elif len(email) < 3:
            warning += 'Enter a valid email!'
        elif len(user_name) < 5:
            warning += 'User name too short!'
        elif len(user_name) > MAX_USER_NAME_LENGTH:
            warning += 'User name too long!'
        elif user_name.isspace():
            warning += 'Username can not be blank!'
        elif user_name_taken:
            warning += 'This username has already been taken, please use another one'
        elif len(password) < 7:
            warning += 'Password too short!'
        elif password.isspace():
            warning += 'Password can not be blank!'
        elif password != password_repeat:
            warning += 'Passwords must match!'

        if not warning:
            logout_user()
            new_user = User(email=email, password=generate_password_hash(password, method='sha256'), userName=user_name, validated=False)
            db.session.add(new_user)
            db.session.commit()
            send_confirmation_mail(email, serializer, email_validation_salt)

            flash('Account created. To validate your account, check the  email we sent you. ('
                  'the link provided will be valid for the next 30 minutes)', category='success')
            return redirect(url_for('views.home'))

        else:
            flash(Markup(warning), category='error')

    return render_template('sign_up.html', user=current_user)


@auth.route('/validate_email/<token>')
def validate_email(token):

    if token:
        link_age = 1800
        try:
            email = serializer.loads(token, salt=email_validation_salt, max_age=link_age)
            user = User.query.filter_by(email=email).first()
            if user:
                user.validated = True
                db.session.commit()
                message = 'Account validated, you can now log in!'
                flash(Markup(message), category='success')

                return redirect(url_for('auth.login'))
            else:
                return "<h1>Email not Found</h1>"

        except SignatureExpired:
            email = serializer.loads(token, salt=email_validation_salt)
            warning = f'This email validation link expired, click <a href="#" onClick=resend_conf_mail("{email}")>' \
                      f'here</a> to get a new link sent to your mail.'
            flash(Markup(warning), category='error')
            return redirect(url_for('views.home'))
    
        except:
            return "<h1>INVALID TOKEN</h1>"
    
    else:
        return redirect(url_for('auth.sign_up'))


@auth.route('/resend_link', methods=['POST'])
def resend_link():
    data = json.loads(request.data)
    email = data['email']
    send_confirmation_mail(email, serializer, email_validation_salt)
    return jsonify({})