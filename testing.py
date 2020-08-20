from flask import Flask, request, render_template, redirect

app = Flask(__name__)   # Flask is the web framework we're using

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/hello', methods=['GET'])
def hello():
    return render_template('hello.html')

@app.route('/translateandemail')
def translateandemail():
    return render_template('translateandemail.html')

@app.route('/mailsend', methods=['POST'])
def mailsend():
    email = request.form['email']
    print("The email address is '" + email + "'")
    return render_template('confirmation.html')

#Hosts app on localhost

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)