from cmu_graphics import *
import cv2
import requests
from bs4 import BeautifulSoup

#--------------- WORKING FUNCTIONS ---------------------
def takePicture(app):
    camera = cv2.VideoCapture(0)
    app.capturedImage

    if not camera.isOpened():
        print("Error: Could not access the camera.")
        exit()

    cv2.namedWindow("Camera Feed")

    while True:
        ret, frame = camera.read()

        if not ret:
            print("Error: Could not capture image.")
            break

        cv2.imshow("Camera Feed", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):  
            cv2.imwrite("captured_image.jpg", frame)
            app.capturedImage = "captured_image.jpg"
            break

        elif key == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

def getTemp(city):
    url = "https://www.google.com/search?q="+"weather"+city
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'html.parser')
    temp = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
    return temp


#--------------- CLASSES --------------------

class Button:
    def __init__(self, name, left, top, width, height, color):
        self.name = name
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.color = color
    
    def __repr(self):
        return f'{self.name}: left={self.left}, top={self.top}, right={self.right}, bottom={self.bottom}'
    
class Shirt:
    def __init__(self, color, type):
        self.color = color
        self.sleeve = type

#--------------- MODEL FUNCTIONS --------------------

def createButtons(app):
    button1 = Button('take-picture', app.height/2, app.width/2, 50, 50, 'black')

    app.buttons.append(button1)

#--------------- CONTROLLER FUNCTIONS --------------------

def onMousePress(app, mousex, mousey):
    idButton = identifyButton(app, mousex,mousey)
    if idButton != None: 
        idButton.color = 'blue'
    
    if idButton.name == 'take-picture':
        takePicture(app)


def identifyButton(app, mousex,mousey):
    for button in app.buttons:
        if (mousex >= button.left) and (mousex <= button.left+button.width) and (mousey >= button.top) and (mousey <= button.top+button.height):
            return button
    return None
    


#--------------- VIEW FUNCTIONS -----------------

def drawScreen(app):
    # drawRect(0, 0, app.width, app.height, fill=app.colors['dark_coral'], border=app.colors['strawberry'], borderWidth=5)
    # drawRect(app.width/2, app.height/2, 500, 600, align='center', fill=app.colors['coral'])
    # drawLabel('Current Weather:', 80, 50)
    # drawLabel("Today's Outfit", app.width/2, 150)

    for button in app.buttons:
        drawRect(button.left, button.top, button.height, button.width, fill=button.color)

    temp = getTemp('Pittsburgh')
    drawLabel(temp, 100, 200)



#--------------- CMU GRAPHICS FUNCTIONS ---------------------
def onAppStart(app):
    app.width, app.height = 1000, 700

    app.colors = {'coral': rgb(255,200,201), 
                  'dark_coral': rgb(255,141,157), 
                  'pink': rgb(255,235,237), 
                  'yellow': rgb(248,240,204), 
                  'strawberry': rgb(214,122,145)}
    app.background = app.colors['dark_coral']

    app.buttons = []
    createButtons(app)

    app.capturedImage = None


def redrawAll(app):
    drawScreen(app)

def main():
    runApp()

main()





