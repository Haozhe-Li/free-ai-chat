from flask import Flask, Response, render_template, request, jsonify, redirect
from core.generateResponse import *
import json

app = Flask(__name__)

@app.route('/')
def index():
    if request.referrer is None:
        user_language = request.accept_languages.best_match(['en', 'zh'])
    else:
        user_language = 'zh' if '/zh' in request.referrer else 'en'
        print(request.referrer)
    if user_language == 'zh':
        return redirect('/zh')
    else:
        content = json.load(open('./i18n/en.json'))
    return render_template('index.html', **content)

@app.route('/zh')
def index_zh():
    content = json.load(open('./i18n/zh.json'))
    return render_template('index.html', **content)

@app.route('/about')
def about():
    if request.referrer is None:
        user_language = request.accept_languages.best_match(['en', 'zh'])
    else:
        user_language = 'zh' if '/zh' in request.referrer else 'en'
    if user_language == 'zh':
        return redirect('/zh/about')
    else:
        content = json.load(open('./i18n/about_en.json'))
    return render_template('about.html', **content)

@app.route('/zh/about')
def about_zh():
    content = json.load(open('./i18n/about_zh.json'))
    return render_template('about.html', **content)

@app.route('/generate', methods=['POST'])
def generate():
    input_text = request.form.get('input_text')
    model= request.form.get('model')
    try:
        response = generate_response(input_text, model)["choices"][0]["message"]["content"]
        data = json.loads(response)
        response = data['answer']
    except Exception as e:
        return jsonify({"error": "An error occurred while generating the response. Please try again"})
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)