#!/usr/bin/env python3
import timeit

from flask import Flask, render_template, request, g, Response

from grinbase.constants.MysqlConstants import MysqlConstants
from grinbase.dbaccess import database
from grinbase.dbaccess.database import database_details
from webui.views.home import home_profile

app = Flask(__name__)
app.secret_key = "E2CCDDE32C54C58152AEFA883F73214"

app.register_blueprint(home_profile)


def set_my_request_var(name, value):
    if 'my_request_var' not in g:
        g.my_request_var = {}
    g.my_request_var[name] = value

@app.before_first_request
def initialize_database():
    print("Initializing...")
    # database.db = database_details(MYSQL_CONSTANTS=MysqlConstants(), user="pool")
    # database.db.initialize()
    # database.db.destroySession()


@app.before_request
def pre_request():
    if request.url_rule and request.url_rule.rule and request.url_rule.rule != "/static/<path:filename>":
        # database.db.initializeSession()
        remote_user = request.environ.get('REMOTE_USER')
        username = remote_user if remote_user else "Guest"
        set_my_request_var("request_start_time", timeit.default_timer())
        print("{0:28} {1:62} {2:30}".format("User: " + username, "Requested URL: "+ request.url, "URL_RULE: " + request.url_rule.rule))


@app.teardown_request
def teardn_request(response):
    if request.url_rule and request.url_rule.rule and request.url_rule.rule != "/static/<path:filename>":
        # database.db.destroySession()
        remote_user = request.environ.get('REMOTE_USER')
        username = remote_user if remote_user else "Guest"
        elapsed = timeit.default_timer() - g.get('my_request_var', {}).pop("request_start_time")
        print("{0:29} {1:61} {2:30} {3:30}".format("User: " + username, "Recieved URL: "+ request.url, "URL_RULE: " + request.url_rule.rule, "Elapsed: " + str(elapsed)))
    return response


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=13424, debug=True)

@app.errorhandler(401)
def custom_401(error):
    return Response('You are unauthorized to view this page', 401, {'WWWAuthenticate':'Basic realm="Login Required"'})
