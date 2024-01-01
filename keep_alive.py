from flask import Flask, render_template
from threading import Thread

app = Flask('Groovebot')

@app.route('/')
def home():
  return "<h1>GrooveBot Online!</h1>"

def run():
  app.run(host='0.0.0.0',port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()