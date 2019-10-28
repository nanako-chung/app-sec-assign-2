from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
# Create dict with key as user and value as { password, 2fa }
accounts = {}
import re
import subprocess

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# http://localhost:5000/login - this will be the login page, we need to use both GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if 'username' and 'password' POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'two_factor_auth' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        hashedPassword = hashlib.md5(password.encode('utf-8')).hexdigest()
        two_factor_auth = request.form['two_factor_auth'].encode('ascii', 'ignore')

        # Check if account exists using dict
        account = {}
        if username in accounts and accounts[username]['password'] == hashedPassword:
            if accounts[username]['two_factor_auth'] == two_factor_auth:
                # Fetch one record from dict and return result
                account['username'] = username
                account['password'] = hashedPassword
                account['two_factor_auth'] = two_factor_auth
                # Account exists in accounts dict in out database
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['username'] = account['username']
                msg = 'Success!'
                # Redirect to home page
                return redirect(url_for('spell_check'))
            else:
                msg = 'Failure: Incorrect two-factor authentication'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Failure: Incorrect username or password'
    return render_template('index.html', msg=msg)

# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if 'username' and 'password' POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'two_factor_auth' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        hashedPassword = hashlib.md5(password.encode('utf-8')).hexdigest()
        two_factor_auth = request.form['two_factor_auth'].encode('ascii', 'ignore')

        # Check if account exists using dict
        account = {}
        if username in accounts:
            if accounts[username]['password'] == hashedPassword and accounts[username]['two_factor_auth'] == two_factor_auth:
                # Fetch one record from dict and return result
                account['username'] = username
                account['password'] = hashedPassword
                account['two_factor_auth'] = two_factor_auth

        # If account exists in accounts dict in out database
        if bool(account):
            msg = 'Failure: Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Failure: Username must contain only characters and numbers!'
        elif not re.match(r'[0-9]+', two_factor_auth):
            msg = 'Failure: Enter phone number for 2fa'
        elif not username or not password:
            msg = 'Failure: Please fill out the form!'
        else:
            # Account doesn't exists and the form data is valid, now insert new account into dict
            # Hash password
            hashedPassword = hashlib.md5(password.encode('utf-8')).hexdigest()
            accounts[username] = {
                'password': hashedPassword,
                'two_factor_auth': two_factor_auth
            }
            msg = 'Success!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Failure: Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# http://localhost:5000/spell_check - this will be the home page, only accessible for loggedin users
@app.route('/spell_check', methods=['GET', 'POST'])
def spell_check():
    msg = ''
    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == 'POST' and 'inputtext' in request.form:
            inputtext = request.form['inputtext']
            # Put inputtext into file
            f = open('input.txt', 'w')
            f.write(inputtext)
            f.close()
            output = subprocess.check_output(['./spell_check', 'input.txt', 'wordlist.txt']).split()
            msg = ', '.join(output)
        # User is loggedin show them the home page
        return render_template('spell_check.html', username=session['username'], msg=msg)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))