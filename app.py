from flask import Flask, Response, render_template, request, jsonify, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
from core.generateResponse import *
import json

app = Flask(__name__)
limiter = Limiter(
    get_remote_address, app=app, default_limits=["10 per minute", "300 per hour"]
)


@app.route("/")
def index():
    if request.referrer is None:
        user_language = request.accept_languages.best_match(["en", "zh"])
    else:
        user_language = "zh" if "/zh" in request.referrer else "en"
        print(request.referrer)
    if user_language == "zh":
        return redirect("/zh")
    else:
        content = json.load(open("./i18n/en.json"))
    return render_template("index.html", **content)


@app.route("/zh")
def index_zh():
    content = json.load(open("./i18n/zh.json"))
    return render_template("index.html", **content)


@app.route("/about")
def about():
    if request.referrer is None:
        user_language = request.accept_languages.best_match(["en", "zh"])
    else:
        user_language = "zh" if "/zh" in request.referrer else "en"
    if user_language == "zh":
        return redirect("/zh/about")
    else:
        content = json.load(open("./i18n/about_en.json"))
    return render_template("about.html", **content)


@app.route("/zh/about")
def about_zh():
    content = json.load(open("./i18n/about_zh.json"))
    return render_template("about.html", **content)


@app.route("/privacy")
def privacy():
    if request.referrer is None:
        user_language = request.accept_languages.best_match(["en", "zh"])
    else:
        user_language = "zh" if "/zh" in request.referrer else "en"
    if user_language == "zh":
        return redirect("/zh/privacy")
    else:
        return render_template("privacy.html")


@app.route("/zh/privacy")
def privacy_zh():
    return render_template("privacy_zh.html")


@app.route("/generate", methods=["POST"])
@limiter.limit("30 per minute")
async def generate():
    if not request.referrer.startswith(request.host_url):
        return jsonify({"response": "Error Occured in Backend, Error Code: 403"})
    input_text = request.form.get("input_text")
    model = request.form.get("model")
    response = await generate_response(input_text, model)
    return jsonify({"response": response})


@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    return jsonify({"response": "Error Occured in Backend, Error Code: 429"})


if __name__ == "__main__":
    app.run()
