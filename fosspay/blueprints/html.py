from flask import Blueprint, render_template, abort, request, redirect, session, url_for, send_file, Response
from flask.ext.login import current_user, login_user, logout_user
from fosspay.objects import *
from fosspay.database import db
from fosspay.common import *
from fosspay.config import _cfg, load_config

import locale

encoding = locale.getdefaultlocale()[1]
html = Blueprint('html', __name__, template_folder='../../templates')

@html.route("/")
def index():
    if User.query.count() == 0:
        load_config()
        return render_template("setup.html")
    return render_template("index.html")

@html.route("/setup", methods=["POST"])
def setup():
    if not User.query.count() == 0:
        abort(400)
    email = request.form.get("email")
    password = request.form.get("password")
    if not email or not password:
        return redirect("/") # TODO: Tell them what they did wrong (i.e. being stupid)
    user = User(email, password)
    user.admin = True
    db.add(user)
    db.commit()
    login_user(user)
    return redirect("/admin?first-run=1")

@html.route("/admin")
@adminrequired
def admin():
    first = request.args.get("first-run") is not None
    projects = Project.query.all()
    return render_template("admin.html",
            first=first,
            projects=projects,
            one_times=lambda p: sum([d.amount for d in p.donations if d.type == DonationType.one_time]),
            recurring=lambda p: sum([d.amount for d in p.donations if d.type == DonationType.recurring])
        )

@html.route("/create-project", methods=["POST"])
@adminrequired
def create_project():
    name = request.form.get("name")
    project = Project(name)
    db.add(project)
    db.commit()
    return redirect("/admin")

@html.route("/logout")
@loginrequired
def logout():
    logout_user()
    return redirect("/")
