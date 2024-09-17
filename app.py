from flask import Flask, render_template

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    return render_template('main.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)