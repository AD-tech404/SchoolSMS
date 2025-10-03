from flask import Flask, render_template, request, redirect, url_for
from classes.class1.class1A import class1a_bp

app = Flask(__name__)

app.secret_key = 'ad'  # REQUIRED for flashing messages

app.register_blueprint(class1a_bp)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/submit', methods=['POST'])
def submit():
    class_name = request.form.get('class_name')
    if class_name == 'class1':
        return redirect(url_for('class1a.class1a_home'))
    else:
        return "Unknown module selected"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

    