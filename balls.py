import os
import requests
import telebot

# Define the bot token and weather API key as environment variables
bot_token = os.environ.get('BOT_TOKEN')
weather_api_key = os.environ.get('WEATHER_API_KEY')

# Create a bot instance using the bot token
bot = telebot.TeleBot(bot_token)

# Define a message handler for the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Weather Bot! Please enter the name of a city to get the current weather and clothing recommendations.")

# Define a message handler for text messages
@bot.message_handler(func=lambda message: True)
def send_weather(message):
    # Get the city name from the user's message
    city_name = message.text

    # Construct the API URL for the weather API
    api_url = f'https://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city_name}'

    # Send a request to the weather API
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        # Get the temperature and weather description from the response
        temperature = data['current']['temp_c']
        weather_description = data['current']['condition']['text']

        # Determine the appropriate clothing recommendation based on the temperature
        if temperature < 10:
            clothing_recommendation = 'It is very cold outside. You should wear a heavy coat, gloves, and a hat.'
        elif temperature < 20:
            clothing_recommendation = 'It is a bit chilly outside. You should wear a light jacket or sweater.'
        else:
            clothing_recommendation = 'It is warm outside. You can wear a t-shirt and shorts.'

        # Send a message to the user with the temperature, weather description, and clothing recommendation
        bot.reply_to(message, f'The temperature in {city_name} is {temperature}°C and the weather is {weather_description}. {clothing_recommendation}')
    else:
        # Send an error message to the user if the request was unsuccessful
        bot.reply_to(message, 'Sorry, I could not get the weather information for that city. Please try again later.')

# Start the bot
bot.polling()
