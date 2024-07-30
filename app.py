from flask import Flask, Response, render_template, request, jsonify, redirect
from core.generateResponse import *
from functools import wraps
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

app = Flask(__name__)

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
    return languages_content.get(lang, languages_content["en"]).get(page, {})


@app.route("/")
@app.route("/<lang>/")
@language_redirect
def index(lang="en"):
    content = get_content("index", lang)
    return render_template("index.html", **content)


@app.route("/about")
@app.route("/<lang>/about")
@language_redirect
def about(lang="en"):
    content = get_content("about", lang)
    return render_template("about.html", **content)


@app.route("/privacy")
@app.route("/<lang>/privacy")
@language_redirect
def privacy(lang="en"):
    template_name = "privacy_zh.html"
    if lang == "en":
        template_name = "privacy.html"
    elif lang == "ja":
        template_name = "privacy_ja.html"
    return render_template(template_name)

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route("/generate", methods=["POST"])
async def generate():
    if not request.referrer.startswith(request.host_url):
        return jsonify({"response": "Error Occured in Backend, Error Code: 403"})
    input_text = request.form.get("input_text")
    model = request.form.get("model")
    context = json.loads(request.form.get("context")) if request.form.get("context") != "" else None
    rag = request.form.get("rag") == 'true'
    logging.info(f"[app.py] Received request with input_text: {input_text}, model: {model}, context: {context}, rag: {rag}")
    response = await generate_response(input_text=input_text, model=model, context=context, rag=rag)
    logging.info(f"[app.py] Finished Generation. Response: {response}")
    return jsonify({"response": response})

@app.errorhandler(404)
def page_not_found(e):
    content = get_content("404", "en")
    content['details'] = content['details'].replace("$$path$$", f"<b>{request.url}</b>")
    return render_template("404.html", **content), 404


if __name__ == "__main__":
    app.run()
