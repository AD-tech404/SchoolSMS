from flask import Flask
from threading import Thread

keep_app = Flask('keep_alive')

@keep_app.route('/')
def home():
    return "Keep Alive Server Running!"

def run():
    keep_app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
