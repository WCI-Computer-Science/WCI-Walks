from flask import Flask, render_template

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html', message='123')

if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0')