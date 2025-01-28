import os
import requests
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from dotenv import load_dotenv
from flask_discord import DiscordOAuth2Session, Unauthorized
from auth import auth

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# Discord OAuth2 Configuration
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"  # Only in development
app.config["DISCORD_CLIENT_ID"] = os.getenv("CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("SECRET")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("URI")
app.config["DISCORD_BOT_TOKEN"] = os.getenv("TOKEN")

discord = DiscordOAuth2Session(app)
app.register_blueprint(auth)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('db.db')
        g.db.row_factory = sqlite3.Row
    return g.db

def get_user_info():
    if 'user_id' not in session:
        return None
    
    if 'discord_user' in session:
        return {
            'name': session['discord_user']['name'],
            'avatar': session['discord_user']['avatar_url']
        }
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return {
        'name': user['name'] if user else 'User',
        'avatar': url_for('static', filename='images/default.png')
    }

@app.context_processor
def utility_processor():
    return dict(get_user_info=get_user_info)

@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("auth.login"))

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    weather_data = None
    
    if request.method == 'POST':
        city = request.form.get('city')
        if not city:
            flash('Please enter a city name.', 'danger')
        else:
            geo_params = {
                'q': city,
                'limit': 1,
                'appid': OPENWEATHERMAP_API_KEY
            }
            geo_response = requests.get(
                "http://api.openweathermap.org/geo/1.0/direct",
                params=geo_params
            )

            if geo_response.status_code != 200:
                flash(f'Error connecting to location service (HTTP {geo_response.status_code}). Please try again.', 'danger')
                return redirect(url_for('weather'))
                
            geo_data = geo_response.json()
            if not geo_data:
                flash('City not found. Please try again.', 'danger')
                return redirect(url_for('weather'))
            
            data = geo_data[0]
            lat = data['lat']
            lon = data['lon']
            
            weather_params = {
                'lat': lat,
                'lon': lon,
                'appid': OPENWEATHERMAP_API_KEY,
                'units': 'metric'
            }
            weather_response = requests.get(
                "http://api.openweathermap.org/data/2.5/forecast",
                params=weather_params
            )
            
            if weather_response.status_code == 200:
                weather_data = weather_response.json()
                forecasts = {}
                for entry in weather_data['list']:
                    date = entry['dt_txt'].split(' ')[0]
                    if date not in forecasts:
                        forecasts[date] = []
                    forecasts[date].append(entry)
                weather_data['forecasts'] = forecasts
            else:
                flash('Error fetching weather data. Please try again.', 'danger')
    
    return render_template('weather.html', weather_data=weather_data)

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)