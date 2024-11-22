from cmu_graphics import *
import cv2
import numpy as np
from PIL import Image
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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

def identifyButton(app, mousex,mousey):
    if app.confirmationScreen:
        buttonList = app.confButtons
    else: buttonList = app.mainButtons

    for button in buttonList:
        if (mousex >= button.left) and (mousex <= button.left+button.width) and (mousey >= button.top) and (mousey <= button.top+button.height):
            return button
    return None

def recommendOutfit(app, shirt = None, pants = None):
    #!!! actually write this function
    if shirt != None:
        return Shirt.clean[0]
    if pants != None:
        return Pant.clean[0]

def addToLog(shirt, pant):
    date = datetime.today().date()
    print(date)

    with open('week_log.txt', 'a') as file:
        file.write(f'{date}, {shirt.id}, {pant}\n') #!!! write the shirt and pant ids to the log

#1.
def create_shirt_mask(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    shirt_contour = contours[0] 
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [shirt_contour], -1, 255, thickness=cv2.FILLED)
    mask = Image.fromarray(mask)
    return mask

#2.
def pixelateShirt(imagePath):
    combined = Image.open(imagePath)
    pixelation_scale = 0.15
    small_size = (int(combined.size[0] * pixelation_scale), int(combined.size[1] * pixelation_scale))
    small_image = combined.resize(small_size, Image.NEAREST)
    pixelated_image = small_image.resize(combined.size, Image.NEAREST)
    return(pixelated_image)

#3.
def maskOverlay(image, mask):
    new_image = np.array(image)
    new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    mask_resized = mask.resize((new_image.shape[1], new_image.shape[0]))
    mask_np = np.array(mask_resized)
    mask_3ch = cv2.merge([mask_np, mask_np, mask_np])
    neon_green = np.array([57, 255, 20], dtype=np.uint8)
    result = np.where(mask_3ch == 255, new_image, neon_green)
    result_image = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    return result_image

#4.
def overlayToTemplate(image, templatePath):
    image=image.convert('RGBA')
    template = Image.open(templatePath).convert("RGBA")
    template = template.resize(image.size)
    overlaidImg = Image.alpha_composite(image, template)
    # overlaidImg = overlaidImg.convert('RGB')
    # overlaidImg.save('overlaidimg.jpg')
    return overlaidImg

#5.
def removeBackground(image, bgColor, threshold):
    values = image.getdata()
    newValues = []
    for value in values:
        if all(abs(value[i] - bgColor[i]) < threshold for i in range(3)):
            newValues.append((255,255,255,0))
        else:
            newValues.append(value)
    image.putdata(newValues)
    image.save(f'result_{Shirt.id}.png')
    path = f'result_{Shirt.id}.png'
    return path
    

#--------------- CLASSES --------------------

class Button:
    def __init__(self, name, left, top, width, height, color):
        self.name = name
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.color = color
    
    def __repr__(self):
        return f'{self.name}: left={self.left}, top={self.top}, width={self.width}, height={self.height}, color={self.color}'


class Shirt:
    id = 0
    clean = []
    worn = []
    
    def __init__(self, color, type):
        self.color = color
        self.sleeve = type
        self.id = id
        Shirt.clean.append(self)
        Shirt.id += 1
    
    def __repr__(self):
        return f'color: {self.color}, type: {self.sleeve}'

class Pant:
    clean = []
    worn = []
    
    def __init__(self, color, material):
        self.color = color
        self.material = material
        Pant.clean.append(self)
    
    def __repr__(self):
        return f'color: {self.color}, material: {self.material}'

#--------------- MODEL FUNCTIONS --------------------

def createButtons(app):
    buttons = [
        ('take-picture', 200, 300, 50, 50, 'black'),
        ('set-outfit', 330, 100, 50, 50, 'green'),
        ('change-outfit', 400, 400, 50, 50, 'brown')
    ]
    app.mainButtons = [Button(*params) for params in buttons]

    confButtons = [
        ('confirm', 200, 300, 50, 50, 'black')
    ]
    app.confButtons = [Button(*params) for params in confButtons]


def setDefaultLook(app):
    defaultTop = Shirt('black-default', 's-sleeve')
    defaultBottom = Pant('black-default', 'cotton')
    app.avatarOutfit['shirt'] = defaultTop
    app.avatarOutfit['pant'] = defaultBottom


#--------------- CONTROLLER FUNCTIONS --------------------

def onMousePress(app, mousex, mousey):
    idButton = identifyButton(app, mousex,mousey)
    if idButton == None:
        pass

    elif idButton.name == 'take-picture':
        idButton.color = 'blue'
        takePicture(app)
        if app.capturedImage != None:
            mask = create_shirt_mask("assets/template.jpg")
            pixelatedImage = pixelateShirt('captured_image.jpg')
            cropped_image = maskOverlay(pixelatedImage, mask)
            overlaid_image = overlayToTemplate(cropped_image, 'assets/transparent_template.png')
            path = removeBackground(overlaid_image, (57,225,20), 70)
            
            app.confirmationScreen = True
    
    elif idButton.name == 'set-outfit':
        idButton.color = 'orange'
        shirt = app.avatarOutfit['shirt']
        pant = app.avatarOutfit['pant']
        addToLog(shirt, pant)
        #!!! remove change clothes buttons

    elif idButton.name == 'change-outfit' and app.satisfiesEntries:
        idButton.color = 'white'
        app.avatarOutfit['shirt'] = recommendOutfit(app, 'shirt')
    

    elif idButton.name == 'confirm':
        with open('s_inventory.txt','a') as file:
            file.write('creatingnewshirt') #!!! how do i access shirt variables

def takeStep(app):
    pass

#--------------- VIEW FUNCTIONS -----------------

def drawScreen(app):
    for button in app.mainButtons:
        drawRect(button.left, button.top, button.height, button.width, fill=button.color)
    #temp = getTemp('Pittsburgh')
    #drawLabel(temp, 100, 200)

    drawLabel(str(app.avatarOutfit), 200, 400)

def drawConfirmationScreen(app):
    drawRect(100, 100, 400, 400, fill='white')
    drawLabel('Confirm details', 200, 200)
    color, sleeve = getLastLine()
    drawLabel(f'shirt color:{color}', 220, 250)
    drawLabel(f'type:{sleeve}', 220, 270)

    for button in app.confButtons:
        drawRect(button.left, button.top, button.height, button.width, fill=button.color)

def getLastLine():
    with open('s_inventory.txt','r') as file:
        lLine = file.readlines() [-1]    
    features = lLine.split(',')
    return features[1], features[2]
    

#--------------- CMU GRAPHICS FUNCTIONS ---------------------
def onAppStart(app):
    app.width, app.height = 1000, 700

    app.colors = {'coral': rgb(255,200,201), 
                  'dark_coral': rgb(255,141,157), 
                  'pink': rgb(255,235,237), 
                  'yellow': rgb(248,240,204), 
                  'strawberry': rgb(214,122,145)}
    app.background = app.colors['dark_coral']
    app.animateMode = True
    app.confirmationScreen = False
    app.counter = 0
    app.cloudIndex = 1

    app.mainButtons = []
    app.confButtons = []
    createButtons(app)

    app.capturedImage = None

    app.avatarOutfit = {'shirt': None, 'pant': None}
    app.satisfiesEntries = False
    setDefaultLook(app)

def onStep(app):
    if app.animateMode:
        app.counter += 1
        takeStep(app)

def redrawAll(app):
    drawScreen(app)
    if app.confirmationScreen:
        drawConfirmationScreen(app)


def main():
    runApp()

main()