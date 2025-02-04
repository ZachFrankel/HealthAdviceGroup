# app.py
# Main application file for the Flask app.
# It sets up routes for weather, air quality, bookings, health metrics, and more.

import os
import requests
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify
from dotenv import load_dotenv
from flask_discord import DiscordOAuth2Session, Unauthorized
from datetime import datetime
from collections import defaultdict
from auth import auth  # Authentication blueprint for login, registration, etc.
from slowapi import ai_api  # Blueprint for AI responses

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

# Configure Discord OAuth2 settings (development mode using insecure transport)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true" 
app.config["DISCORD_CLIENT_ID"] = os.getenv("CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("SECRET")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("URI")
app.config["DISCORD_BOT_TOKEN"] = os.getenv("TOKEN")

discord = DiscordOAuth2Session(app)
app.register_blueprint(auth)
app.register_blueprint(ai_api, url_prefix='/api/ai')

# Utility function to get or create a database connection for the request context.
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('db.db')
        g.db.row_factory = sqlite3.Row
    return g.db

# Helper function to extract user information.
def get_user_info():
    if 'user_id' not in session:
        return None
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if 'discord_user' in session:
        return {
            'name': session['discord_user']['name'],
            'avatar': session['discord_user']['avatar_url'],
            'age': user['age'] if user else None,
            'weight': user['weight'] if user else None,
            'height': user['height'] if user else None
        }
    
    return {
        'name': user['name'] if user else 'User',
        'avatar': url_for('static', filename='images/default.png'),
        'age': user['age'] if user else None,
        'weight': user['weight'] if user else None,
        'height': user['height'] if user else None
    }

@app.context_processor
def utility_processor():
    # Make get_user_info available in all templates.
    return dict(get_user_info=get_user_info)

@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    # Redirect unauthorized users to the login page.
    return redirect(url_for("auth.login"))

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    # Fetch and display weather information.
    # The route fetches location, gathers weather data from OpenWeatherMap,
    # and handles both GET (auto-detect location) and POST (manual city input) requests.
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
    # Process weather data to generate health advice using AI.
    # This route extracts data from the posted JSON, constructs a prompt, and calls the AI API.
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
    # Retrieve and display the user's bookings.
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
    # Create a new booking after validating form inputs.
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
    # Handle deletion of a booking; ensure the user is authenticated and handle errors.
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

@app.route('/airquality', methods=['GET', 'POST'])
def airquality():
    # Fetch air quality data via external API and render the results.
    # Supports both auto-detection via IP and manual city input.
    air_quality_data = None
    if request.method == 'GET':
        ipify_api_key = os.getenv('IPIFY_API_KEY')
        try:
            ip_response = requests.get(
                "https://geo.ipify.org/api/v2/country,city",
                params={'apiKey': ipify_api_key}
            )
            if ip_response.status_code == 200:
                location_data = ip_response.json()
                lat = location_data['location']['lat']
                lon = location_data['location']['lng']
                air_params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': OPENWEATHERMAP_API_KEY
                }
                air_response = requests.get("http://api.openweathermap.org/data/2.5/air_pollution", params=air_params)
                if air_response.status_code == 200:
                    air_json = air_response.json()
                    if 'list' in air_json and len(air_json['list']) > 0:
                        air_quality_data = {
                            'city': location_data['location'].get('city', 'Your Location'),
                            'country': location_data['location'].get('country', ''),
                            'data': air_json['list'][0]
                        }
                    else:
                        flash('No air quality data available for your location.', 'warning')
                else:
                    flash('Error fetching air quality data.', 'danger')
            else:
                flash('Error detecting your location.', 'warning')
        except Exception as e:
            flash('Error detecting your location. Please try again.', 'danger')
    
    elif request.method == 'POST':
        city = request.form.get('city')
        if not city:
            flash('Please enter a city name.', 'danger')
            return redirect(url_for('airquality'))
        geo_params = {
            'q': city,
            'limit': 1,
            'appid': OPENWEATHERMAP_API_KEY
        }
        geo_response = requests.get("http://api.openweathermap.org/geo/1.0/direct", params=geo_params)
        if geo_response.status_code != 200 or not geo_response.json():
            flash('City not found or error connecting to geocoding service.', 'danger')
            return redirect(url_for('airquality'))
        geo_data = geo_response.json()[0]
        lat = geo_data['lat']
        lon = geo_data['lon']
        air_params = {
            'lat': lat,
            'lon': lon,
            'appid': OPENWEATHERMAP_API_KEY
        }
        air_response = requests.get("http://api.openweathermap.org/data/2.5/air_pollution", params=air_params)
        if air_response.status_code != 200:
            flash('Error fetching air quality data.', 'danger')
            return redirect(url_for('airquality'))
        air_json = air_response.json()
        if 'list' in air_json and len(air_json['list']) > 0:
            air_quality_data = {
                'city': geo_data.get('name', city),
                'country': geo_data.get('country', ''),
                'data': air_json['list'][0]
            }
        else:
            flash('No air quality data available for this location.', 'warning')
    
    return render_template('airquality.html', air_quality_data=air_quality_data)

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/health/', methods=['GET', 'POST'])
def health():
    # Display and record user health metrics (e.g., weight, blood pressure).
    if 'user_id' not in session:
        flash('Please login to track your health metrics.', 'danger')
        return redirect(url_for('auth.login'))

    db = get_db()

    if request.method == 'POST' and 'weight' in request.form:
        # Insert the new health metric record.
        weight = request.form.get('weight')
        blood_pressure = request.form.get('blood_pressure')
        heart_rate = request.form.get('heart_rate')
        notes = request.form.get('notes')
        if not weight or not blood_pressure or not heart_rate:
            flash('Please fill in all required fields.', 'danger')
        else:
            try:
                db.execute(
                    'INSERT INTO health_metrics (user_id, date, weight, blood_pressure, heart_rate, notes) VALUES (?, datetime("now", "localtime"), ?, ?, ?, ?)',
                    (session['user_id'], weight, blood_pressure, heart_rate, notes)
                )
                db.commit()
                flash('Health metrics recorded successfully!', 'success')
            except Exception as e:
                flash('Error recording health metrics.', 'danger')
        return redirect(url_for('health'))

    # Retrieve existing health metric entries.
    raw_metrics = db.execute(
        'SELECT * FROM health_metrics WHERE user_id = ? ORDER BY date DESC',
        (session['user_id'],)
    ).fetchall()
    metrics = [dict(row) for row in raw_metrics]

    return render_template('health.html', metrics=metrics)

@app.route('/remove_health_entry/<int:entry_id>', methods=['POST'])
def remove_health_entry(entry_id):
    # Delete the specified health metric entry from the database.
    if 'user_id' not in session:
        flash('Please login to remove a health entry.', 'danger')
        return redirect(url_for('auth.login'))
    db = get_db()
    try:
        db.execute(
            'DELETE FROM health_metrics WHERE id = ? AND user_id = ?',
            (entry_id, session['user_id'])
        )
        db.commit()
        flash('Health entry removed successfully!', 'success')
    except Exception as e:
        flash('Error removing health entry.', 'danger')
    return redirect(url_for('health'))

@app.route('/update_user_details', methods=['POST'])
def update_user_details():
    # Update the user's personal details (age, weight, height) in the database.
    # Validate inputs and return a JSON response with the updated data.
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Please login to update your details.'}), 401
        
    age = request.form.get('age')
    weight = request.form.get('weight')
    height = request.form.get('height')

    # Validate inputs
    if age and not age.isdigit():
        return jsonify({'success': False, 'error': 'Age must be a number.'}), 400
        
    if weight and not (weight.replace('.', '').isdigit()):
        return jsonify({'success': False, 'error': 'Weight must be a number.'}), 400
        
    if height and not height.isdigit():
        return jsonify({'success': False, 'error': 'Height must be a number.'}), 400

    db = get_db()
    try:
        db.execute(
            'UPDATE users SET age = ?, weight = ?, height = ? WHERE id = ?',
            (age or None, weight or None, height or None, session['user_id'])
        )
        db.commit()
        
        # Get updated user info
        user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        return jsonify({
            'success': True,
            'user': {
                'age': user['age'],
                'weight': user['weight'],
                'height': user['height']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': 'Error updating details.'}), 500

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)