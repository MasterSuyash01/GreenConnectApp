from flask import render_template, request, redirect, url_for, session,Flask
import requests
from flask import Flask, request, jsonify
import json
app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure secret key

@app.route('/')
def index():
    # Fetch data from the /tree API
    api_url = 'http://127.0.0.1:5000/tree'
    response = requests.get(api_url)
    data = response.json()

    # Pass the data to the HTML template
    return render_template('index.html', trees=data['trees'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = {
            'username': request.form.get('username'),
            'password': request.form.get('password')
        }
        response = requests.post('http://127.0.0.1:5000/login', json=data)

        try:
            data = response.json()
        except json.JSONDecodeError:
            print(f"Response Content: {response.content}")
            print(f"Status Code: {response.status_code}")

            error_message = 'Invalid response from the server. Please try again.'
            return render_template('login.html', error_message=error_message)

        if response.status_code == 200:
            session['access_token'] = data.get('access_token')
            return redirect(url_for('dashboard'))

        error_message = 'Invalid credentials. Please try again.'
        return render_template('login.html', error_message=error_message)

    return render_template('login.html', error_message=None)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get signup data from the form
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        address = request.form.get('address')

        # Make a request to the /signup API
        api_url = 'http://127.0.0.1:5000/signup'
        response = requests.post(api_url, json={'username': username, 'password': password, 'email': email, 'address': address})

        if response.status_code == 201:
            # Successful signup, redirect to the login page
            return redirect(url_for('login'))
        else:
            # Display an error message
            error_message = 'Signup failed. Please try again.'
            return render_template('signup.html', error_message=error_message)

    return render_template('signup.html', error_message=None)
@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session data
    session.clear()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/dashboard')
def dashboard():
    # Retrieve user-specific data using the access token from the session
    access_token = session.get('access_token')

    if not access_token:
        # If the user is not logged in, redirect to the login page
        return redirect(url_for('login'))

    # Make a request to a user-specific API using the access token
    user_info_api_url = 'http://127.0.0.1:5000/user_info'
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(user_info_api_url, headers=headers)

    if response.status_code == 200:
        # Successfully fetched user information
        user_info = response.json()
        return render_template('dashboard.html', user_info=user_info)

    # If the user information API request fails, redirect to the login page
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True,port=4000)
