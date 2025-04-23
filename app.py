from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# In-memory user for simplicity (replace with a database in a real application)
users = {
    'devops_learner': generate_password_hash('password123')
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_hash = users.get(username)
        if user_hash and check_password_hash(user_hash, password):
            session['username'] = username
            return redirect(url_for('progress'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/progress', methods=['GET', 'POST'])
def progress():
    if 'username' not in session:
        return redirect(url_for('login'))

    progress_data = session.get('progress_data', {})

    if request.method == 'POST':
        tool = request.form['tool']
        completion = request.form['completion']
        progress_data[tool] = completion
        session['progress_data'] = progress_data
        # In a real app, you'd store this in a database associated with the user

    return render_template('progress.html', username=session['username'], progress=progress_data)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('progress_data', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')