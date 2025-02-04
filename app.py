import os
import requests
import sqlite3
import google.generativeai as genai
import json
import httpx

from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify
from dotenv import load_dotenv
from flask_discord import DiscordOAuth2Session, Unauthorized
from datetime import datetime
from collections import defaultdict
from auth import auth
from slowapi import ai_api

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
app.register_blueprint(ai_api, url_prefix='/api/ai')

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
    
    if request.method == 'GET':
        ipify_api_key = os.getenv('IPIFY_API_KEY')
        try:
            ip_response = requests.get(
                f"https://geo.ipify.org/api/v2/country,city",
                params={'apiKey': ipify_api_key}
            )
            
            if ip_response.status_code == 200:
                location_data = ip_response.json()
                lat = location_data['location']['lat']
                lon = location_data['location']['lng']
                
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
                        date_obj = datetime.strptime(entry['dt_txt'].split(' ')[0], '%Y-%m-%d')
                        date = date_obj.strftime('%d/%m/%Y')
                        if date not in forecasts:
                            forecasts[date] = []
                        forecasts[date].append(entry)
                    weather_data['forecasts'] = forecasts
                else:
                    flash('Error fetching weather data. Please try again.', 'danger')
            else:
                flash('Error detecting location. Please enter a city manually.', 'warning')
        except Exception as e:
            flash('Error detecting location. Please enter a city manually.', 'warning')
    
    elif request.method == 'POST':
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
                    date_obj = datetime.strptime(entry['dt_txt'].split(' ')[0], '%Y-%m-%d')
                    date = date_obj.strftime('%d/%m/%Y')
                    if date not in forecasts:
                        forecasts[date] = []
                    forecasts[date].append(entry)
                weather_data['forecasts'] = forecasts
            else:
                flash('Error fetching weather data. Please try again.', 'danger')
    
    return render_template('weather.html', weather_data=weather_data)

@app.route('/get_health_advice', methods=['POST'])
def get_health_advice():
    weather_data = request.json.get('weather_data')
    if not weather_data or 'forecasts' not in weather_data:
        return jsonify({'error': 'Invalid weather data'}), 400

    try:
        date = request.json.get('date')
        entries = weather_data['forecasts'].get(date, [])
        if not entries:
            return jsonify({'error': 'Invalid date'}), 400

        mid_entry = entries[len(entries)//2]
        
        prompt = f"""Analyze these weather conditions and provide health recommendations:

        Date: {date}
        Temperature: {mid_entry['main']['temp']}°C
        Feels like: {mid_entry['main']['feels_like']}°C
        Humidity: {mid_entry['main']['humidity']}%
        Weather: {mid_entry['weather'][0]['description']}
        Wind Speed: {mid_entry['wind']['speed']} m/s
        Pressure: {mid_entry['main']['pressure']} hPa

        Provide 3 health recommendations in this exact format:
        [emoji] [recommendation title]: [brief advice]

        Example format:
        🌡️ Temperature Safety: Stay hydrated and wear appropriate clothing
        ☔ Weather Protection: Use umbrella and waterproof gear
        🌬️ Wind Advisory: Secure loose items and protect against windchill

        Keep each recommendation under 15 words."""

        response = requests.post(
            'http://localhost:5000/api/ai/generate',
            json={'prompt': prompt}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                full_response = result['response'].strip()
                
                if '<think>' in full_response and '</think>' in full_response:
                    think_start = full_response.find('<think>')
                    think_end = full_response.find('</think>') + len('</think>')
                    full_response = full_response[think_end:].strip()
                
                valid_lines = []
                for line in full_response.split('\n'):
                    line = line.strip()
                    if line and ':' in line and any(c for c in line if ord(c) > 127):
                        valid_lines.append(line)
                
                if valid_lines:
                    advice = '\n'.join(valid_lines)
                else:
                    advice = "🌡️ Weather Notice: Please check back later for health recommendations"
                
                return jsonify({
                    'success': True,
                    'date': date,
                    'advice': advice
                })
            else:
                raise Exception
        else:
            raise Exception
        
    except Exception as e:
        print("\n[DEBUG] Main Exception:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/booking', methods=['GET'])
def booking():
    if 'user_id' in session:
        db = get_db()
        bookings = db.execute('''
            SELECT 
                id,
                strftime('%d/%m/%Y %H:%M', date) as date,
                address,
                strftime('%d/%m/%Y %H:%M', created_at) as created_at,
                status
            FROM bookings 
            WHERE user_id = ? 
            ORDER BY date DESC
        ''', (session['user_id'],)).fetchall()
        return render_template('booking.html', bookings=bookings)
    return render_template('booking.html', bookings=None)

@app.route('/create_booking', methods=['POST'])
def create_booking():
    if 'user_id' not in session:
        flash('Please login to create a booking.', 'danger')
        return redirect(url_for('auth.login'))
    
    date = request.form.get('date')
    address = request.form.get('address')
    
    if not date or not address:
        flash('Please fill in all fields.', 'danger')
        return redirect(url_for('booking'))
    
    try:
        db = get_db()
        db.execute(
            'INSERT INTO bookings (user_id, date, address, created_at, status) VALUES (?, ?, ?, ?, ?)',
            (session['user_id'], date, address, datetime.now(), 'pending')
        )
        db.commit()
        flash('Booking created successfully!', 'success')
    except sqlite3.Error as e:
        flash('An error occurred while creating your booking.', 'danger')
    
    return redirect(url_for('booking'))

@app.route('/clear_booking/<int:booking_id>', methods=['POST'])
def clear_booking(booking_id):
    if 'user_id' not in session:
        flash('Please login to clear a booking.', 'danger')
        return redirect(url_for('auth.login'))
    
    try:
        db = get_db()
        db.execute(
            'DELETE FROM bookings WHERE id = ? AND user_id = ?',
            (booking_id, session['user_id'])
        )
        db.commit()
        flash('Booking cleared successfully!', 'success')
    except sqlite3.Error as e:
        flash('An error occurred while clearing your booking.', 'danger')
    
    return redirect(url_for('booking'))

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)