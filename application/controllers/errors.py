from flask import render_template


def error404(e):
  return render_template("error404.html"), 404

def error500(e):
  return render_template("error500.html"), 500
