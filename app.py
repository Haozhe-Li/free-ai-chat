# -*- coding: utf-8 -*-
# filename: app.py
# author: Haozhe Li
# date: 2024-09-01
# description: Flask app for the website. Router for the website.

from flask import Flask, render_template, request, jsonify, redirect
from core.generateResponse import *
from core.utils import gen_task_id, sysPrompt_leak_response
from functools import wraps
import json
import logging

logging.basicConfig(
    level=int(20),
    format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s",
    datefmt="%Y-%d-%m %H:%M:%S",
    encoding="utf-8",
)


app = Flask(__name__)

# Load the content for the website
languages_content = {
    "en": {
        "index": json.load(open("./i18n/en.json")),
        "about": json.load(open("./i18n/about_en.json")),
        "404": json.load(open("./i18n/404_en.json")),
    },
    "zh": {
        "index": json.load(open("./i18n/zh.json")),
        "about": json.load(open("./i18n/about_zh.json")),
        "404": json.load(open("./i18n/404_zh.json")),
    },
    "ja": {
        "index": json.load(open("./i18n/ja.json")),
        "about": json.load(open("./i18n/about_ja.json")),
        "404": json.load(open("./i18n/404_ja.json")),
    },
}


def language_redirect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        Redirect to the language specific page if the language is not supported
        """
        supported_languages = ["en", "zh", "ja"]
        user_language = request.accept_languages.best_match(
            supported_languages, default="en"
        )
        path_lang = request.path.split("/")[1]
        if path_lang not in supported_languages:
            return redirect(f"/{user_language}{request.path}")
        elif path_lang != user_language:
            pass
        return f(*args, **kwargs)

    return decorated_function


def get_content(page, lang="en"):
    """
    Get the content for the page in the language
    """
    return languages_content.get(lang, languages_content["en"]).get(page, {})


@app.route("/")
@app.route("/<lang>/")
@language_redirect
def index(lang="en"):
    """
    Render the index page
    """
    content = get_content("index", lang)
    return render_template("index.html", **content)


@app.route("/about")
@app.route("/<lang>/about")
@language_redirect
def about(lang="en"):
    """
    Render the about page
    """
    content = get_content("about", lang)
    return render_template("about.html", **content)


@app.route("/privacy")
@app.route("/<lang>/privacy")
@language_redirect
def privacy(lang="en"):
    """
    Render the privacy page
    """
    template_name = "privacy_zh.html"
    if lang == "en":
        template_name = "privacy.html"
    elif lang == "ja":
        template_name = "privacy_ja.html"
    return render_template(template_name)


@app.route("/favicon.ico")
def favicon():
    """
    Return the favicon
    """
    return app.send_static_file("favicon.ico")


@app.route("/generate", methods=["POST"])
async def generate():
    """
    Generate the response based on the input_text and model
    """
    task_id = gen_task_id()
    logging.info(f"[app.py] Received request with task_id: {task_id}")
    if not request.referrer.startswith(request.host_url):
        logging.error(f"[app.py] Error: Unauthorized request with task_id: {task_id}")
        return jsonify({"response": "Error Occured in Backend, Error Code: 403"})
    input_text = request.form.get("input_text")
    model = request.form.get("model")
    context = (
        json.loads(request.form.get("context"))
        if request.form.get("context") != ""
        else None
    )
    rag = request.form.get("rag") == "true"
    logging.info(
        f"[app.py] Received request with task_id: {task_id}. input_text: {input_text}, model: {model}, context: {context}, rag: {rag}"
    )
    response = await generate_response(
        input_text=input_text, model=model, context=context, rag=rag, task_id=task_id
    )
    return jsonify({"response": response})


@app.errorhandler(404)
def page_not_found(e):
    """
    Render the 404 page
    """
    content = get_content(
        "404", request.accept_languages.best_match(["en", "zh", "ja"], default="en")
    )
    content["details"] = content["details"].replace("$$path$$", f"<b>{request.url}</b>")
    return render_template("404.html", **content), 404


if __name__ == "__main__":
    app.run()
