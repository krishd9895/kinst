import requests
import telebot
import os
from webserver import keep_alive

telegram_token = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(telegram_token)

Api_key = os.environ['API_KEY']

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Please send me the Instagram URL.")

@bot.message_handler(func=lambda message: True)
def process_instagram_url(message):
    url = message.text.strip()

    if not url.startswith('https://www.instagram.com'):
        bot.reply_to(message, "Invalid Instagram URL.")
        return

    api_url = "https://instagram-media-downloader.p.rapidapi.com/rapid/post.php"
    querystring = {"url": url}

    headers = {
        "X-RapidAPI-Key": Api_key,
        "X-RapidAPI-Host": "instagram-media-downloader.p.rapidapi.com"
    }

    response = requests.get(api_url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        video_link = data.get("video")

        if video_link:
            markup = telebot.types.InlineKeyboardMarkup()
            video_button = telebot.types.InlineKeyboardButton(text="Download Video", url=video_link)
            markup.add(video_button)
            bot.send_message(message.chat.id, "Direct link to download the video:", reply_markup=markup)

            # Download the video
            video_file = f"video_{message.chat.id}.mp4"
            with open(video_file, 'wb') as file:
                file.write(requests.get(video_link).content)

            # Upload the video to Telegram
            with open(video_file, 'rb') as file:
                bot.send_video(message.chat.id, file)

            # Delete the video file
            os.remove(video_file)
        else:
            bot.reply_to(message, "Video link not found in the response.")
    else:
        bot.reply_to(message, f"Request failed with error code: {response.status_code}")

keep_alive()
bot.polling(none_stop=True, timeout=123)
                      
