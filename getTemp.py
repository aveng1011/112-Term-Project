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
    url = f"https://www.google.com/search?q=weather+{city}"
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract current temperature
    temp = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
    
    # Extract weather details from another part of the page
    details = soup.find_all('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'})
    weather_info = details[1].text.split('\n') if len(details) > 1 else []

    # Parse additional details
    high_low = weather_info[0] if len(weather_info) > 0 else "N/A"
    chance_of_rain = weather_info[1] if len(weather_info) > 1 else "N/A"
    wind = weather_info[2] if len(weather_info) > 2 else "N/A"

    return {
        'current_temp': temp,
        'high_low': high_low,
        'chance_of_rain': chance_of_rain,
        'wind': wind
    }



print(getWeather('Pittsburgh'))

# def onAppStart(app):
#     app.temp = getWeather("Pittsburgh")

# def redrawAll(app):
#     drawLabel(f'Weather in Pittsburgh: {app.temp}', app.width/2, app.height/2)

# def main():
#     runApp()

# main()

