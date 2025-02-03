import os
import sqlite3

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_discord import requires_authorization, Unauthorized, DiscordOAuth2Session

auth = Blueprint('auth', __name__, url_prefix='/auth')

discord = None

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('db.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_discord(app):
    """Initialize Discord OAuth2 settings"""
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
    app.config["DISCORD_CLIENT_ID"] = os.getenv("CLIENT_ID")
    app.config["DISCORD_CLIENT_SECRET"] = os.getenv("SECRET") 
    app.config["DISCORD_REDIRECT_URI"] = os.getenv("URI")
    app.config["DISCORD_BOT_TOKEN"] = os.getenv("TOKEN")
    return DiscordOAuth2Session(app)

@auth.record
def record(state):
    """Initialize discord client when blueprint is registered"""
    global discord
    discord = init_discord(state.app)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        
        if user is None:
            error = 'Incorrect email or password.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect email or password.'
            
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            flash('Successfully logged in!', 'success')
            return redirect(url_for('home'))
        
        flash(error, 'danger')
        
    return render_template('auth/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        db = get_db()
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone() is not None:
            error = f'Email {email} is already registered.'

        if error is None:
            db.execute(
                'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                (name, email, generate_password_hash(password))
            )
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

        flash(error, 'danger')

    return render_template('auth/register.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@auth.route("/discord")
def discord_login():
    if discord is None:
        flash('Discord authentication is not configured properly', 'danger')
        return redirect(url_for('auth.login'))
    return discord.create_session(
        scope=["identify", "email"],
        prompt=True
    )

@auth.route("/callback/")
@auth.route("/callback")
def callback():
    try:
        discord.callback()
        user = discord.fetch_user()
        
        session['discord_user'] = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'avatar_url': user.avatar_url
        }
        
        db = get_db()
        existing_user = db.execute('SELECT * FROM users WHERE email = ?', (user.email,)).fetchone()
        
        if existing_user is None:
            db.execute(
                'INSERT INTO users (email, name, password) VALUES (?, ?, ?)',
                (user.email, user.name, generate_password_hash("discord_user"))
            )
            db.commit()
            user_id = db.execute('SELECT id FROM users WHERE email = ?', (user.email,)).fetchone()['id']
        else:
            user_id = existing_user['id']
        
        session['user_id'] = user_id
        flash('Successfully logged in with Discord!', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error during Discord login: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))