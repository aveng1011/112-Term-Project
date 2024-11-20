from cmu_graphics import *
import requests
from bs4 import BeautifulSoup

#will return temperature
def getTemp(city):
    url = "https://www.google.com/search?q="+"weather"+city
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'html.parser')
    temp = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
    return temp

def onAppStart(app):
    app.temp = getTemp("Pittsburgh")

def redrawAll(app):
    drawLabel(f'Weather in Pittsburgh: {app.temp}', app.width/2, app.height/2)

def main():
    runApp()

main()

