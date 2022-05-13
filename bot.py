import telebot
import os
import requests_cache
import functools
from geopy.geocoders import Nominatim
from flask import Flask, request

TOKEN = "5374213245:AAEYlvWyBb4LFzz9GwqcXY6sYqAbPB09SOM"
API_URL = 'https://indonesia-public-static-api.vercel.app/api/volcanoes'

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

def volcano_api(APIname):
    cached_data = requests_cache.CachedSession('volcano_cache')
    res = cached_data.get(APIname)
    json = res.json()

    return json

def geocode_parser(geocoordinate):
    try:
        geolocator = Nominatim(user_agent="marcofel.manugara@gmail.com")
        geocode = functools.lru_cache(maxsize=128)(functools.partial(geolocator.geocode, timeout=5))
         
        return geocode(geocoordinate)

    except AttributeError:
        print("problem processing geolocation")

def volcano(nama, bentuk, tinggi, letusan_terakhir, geolokasi):
    data = ''' 
nama: {}
bentuk: {}
tinggi: {}
estimasi letusan terakhir: {}
lokasi: {}
          '''.format(nama, bentuk, tinggi, letusan_terakhir, geolokasi)

    return data

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "hello i'am an echo bot!!")

@bot.message_handler(commands=['help'])
def about(message):
    about_bot = """
Apa yang Bot ini dapat Lakukan?
Bot ini berisi daftar Gunung- 
Gunung berapi aktif yang ada di Indonesia.

Daftar Gunung berapi dapat diakses dengan perintah:
                
/volcano - menunjukan seluruh daftar Gunung
/volcano "nama gunung" - menunjukan hanya data Gunung terkait

"""
    bot.reply_to(message, about_bot)


@bot.message_handler(commands=['volcano'])
def send_volcano(message):
    text = message.text
    volcano_name = text[9:]
    volcano_form = text[9:]

    #function call
    json_data = volcano_api(API_URL)

    for item in json_data:

        if volcano_name.upper() in item['nama'].upper():
            volcano_data = volcano(item['nama'], item['bentuk'], item['tinggi_meter'], item['estimasi_letusan_terakhir'], geocode_parser(item['geolokasi']))
            bot.reply_to(message, volcano_data)
        
        elif volcano_form.upper() in item['bentuk'].upper():
            volcano_data = volcano(item['nama'], item['bentuk'], item['tinggi_meter'], item['estimasi_letusan_terakhir'], geocode_parser(item['geolokasi']))
            bot.reply_to(message, volcano_data)
        
        else:
            pass

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    try:
        message = bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode["utf-8"])])
        return "!", 200, message
    
    except TypeError:
        print('terjadi error tipe')
    

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://cryptic-hamlet-60742.herokuapp.com/' + TOKEN)
    
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0",debug= True, port=int(os.environ.get('POST', 443)))
