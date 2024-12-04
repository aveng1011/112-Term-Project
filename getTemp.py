from cmu_graphics import *
import requests
from bs4 import BeautifulSoup

#will return temperature
# def getTemp(city):
#     url = "https://www.google.com/search?q="+"weather"+city
#     html = requests.get(url).content
#     soup = BeautifulSoup(html, 'html.parser')
#     temp = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
#     return temp


def getWeather(city):
    file = requests.get(f'https://www.google.com/search?q=weather+{city}', headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15' })

    soup = BeautifulSoup(file.text, 'html.parser')

    temp = soup.find('span', id='wob_tm').text
    rain = soup.find('span', id='wob_pp').text
    wind = soup.find('span', id='wob_ws').text

    return temp, rain, wind


    
print(getWeather('pittsburgh'))
