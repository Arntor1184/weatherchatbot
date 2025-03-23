from flask import Flask, render_template, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from datetime import datetime, timedelta
import requests

# Initialize Flask app
app = Flask(__name__)

# Initialize chatbot
chatbot = ChatBot('WeatherHolidayBot')
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train('chatterbot.corpus.english')

# API Keys (Replace with your own keys)
HOLIDAY_API_KEY = '5e231eee3a984e1b8a9b4a85914d8852'
WEATHER_API_KEY = '6976f4d9774d703417c2d6810b1e4317'


# Function to fetch holidays
def get_holidays(country, year, month, day):
    url = f"https://holidays.abstractapi.com/v1/?api_key={HOLIDAY_API_KEY}&country={country}&year={year}&month={month}&day={day}"
    response = requests.get(url)
    data = response.json()
    return [holiday['name'] for holiday in data] if response.status_code == 200 and data else None


# Function to get the next holiday
def get_next_holiday(country):
    today = datetime.now()
    for i in range(30):  # Look ahead 30 days
        check_date = today + timedelta(days=i)
        holidays = get_holidays(country, check_date.year, check_date.month, check_date.day)
        if holidays:
            return f"The next holiday is {holidays[0]} on {check_date.strftime('%Y-%m-%d')}."
    return "No upcoming holidays found in the next 30 days."


# Function to fetch weather data and give advice based on temperature
def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric'
    response = requests.get(url)
    data = response.json()

    if data['cod'] == 200:
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']

        # Advice based on temperature
        if temperature < 0 or temperature > 35:
            advice = "Just stay inside."
        elif 0 <= temperature < 5:
            advice = "It's freezing outside! Wear a warm coat, gloves, and a scarf."
        elif 5 <= temperature < 10:
            advice = "It's cold! Dress warmly in layers and don't forget a hat and gloves."
        elif 10 <= temperature < 15:
            advice = "It's chilly. A thick jacket and warm accessories will keep you cozy."
        elif 15 <= temperature < 20:
            advice = "It's a bit cold. A coat with a scarf and gloves would be a good choice."
        elif 20 <= temperature < 25:
            advice = "It's warm. A light jacket or sweater will be comfortable."
        elif 25 <= temperature < 30:
            advice = "It's hot. Wear light, breathable clothing and drink plenty of water."
        else:
            advice = "It's scorching hot! Stay inside, wear light clothing, and hydrate."

        return f"Weather in {city}: {description}, {temperature}°C, Humidity: {humidity}%\n\nAdvice: {advice}"

    return "Sorry, I couldn't find the weather for that location."


# Serve chatbot UI
@app.route('/')
def index():
    return render_template('index.html')


# Chatbot response handling
@app.route('/get', methods=['GET'])
def get_bot_response():
    user_input = request.args.get('user_input').lower()

    if 'weather' in user_input:
        city = request.args.get('city')
        return jsonify({'response': get_weather(city) if city else 'Please provide a city name.'})

    if 'next holiday' in user_input:
        country = 'GB' if 'london' in user_input else 'US'  # Adjust country detection
        return jsonify({'response': get_next_holiday(country)})

    return jsonify({'response': str(chatbot.get_response(user_input))})


if __name__ == '__main__':
    app.run(debug=True)

