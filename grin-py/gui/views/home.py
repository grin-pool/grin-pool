import datetime
import hashlib
import timeit
from urllib.parse import urlparse, urljoin

from flask import Flask, Blueprint, render_template, request, session, make_response, flash, url_for, redirect
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField
from flask import Flask, Blueprint, render_template, request, session, make_response


home_profile = Blueprint('search_profile'
                           , __name__
                           , template_folder='templates'
                           , static_folder='static'
                           )


@home_profile.route('/')
def home_template():
    ## get data
    message = "Hello World"
    return render_template('home/home.html', message=message)