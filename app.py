from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    app.run(debug=True)