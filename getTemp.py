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
    list = []
    file = requests.get("https://weather.com/en-IN/weather/tenday/l/336ebf959ee8b55242536b9ce9a72f50cf94736edffbc2bf85a8ea3c6c983639")
    soup = BeautifulSoup(file.content, 'html.parser')
    
    all = soup.find("div", {"class":"locations-title ten-day-page-title"}).find("h1").text
    
    content = soup.find_all("table", {"class":"twc-table"})
    for items in content:
        for i in range(len(items.find_all("tr"))-1):
            dict = {}
            try: 
                dict["day"]= items.find_all("span", {"class":"date-time"})[i].text
                dict["date"]= items.find_all("span", {"class":"day-detail"})[i].text		 
                dict["desc"]= items.find_all("td", {"class":"description"})[i].text
                dict["temp"]= items.find_all("td", {"class":"temp"})[i].text
                dict["precip"]= items.find_all("td", {"class":"precip"})[i].text
                dict["wind"]= items.find_all("td", {"class":"wind"})[i].text
                dict["humidity"]= items.find_all("td", {"class":"humidity"})[i].text
            except: 
                dict["day"]="None"
                dict["date"]="None"
                dict["desc"]="None"
                dict["temp"]="None"
                dict["precip"]="None"
                dict["wind"]="None"
                dict["humidity"]="None"
            
            list.append(dict)
    
print(getWeather('pittsburgh'))
