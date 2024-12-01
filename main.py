from cmu_graphics import *
import cv2
import numpy as np
from PIL import Image
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import math
import random

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
        
        frame = cv2.flip(frame, 1)
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

def identifyButton(app, mousex,mousey, mode=None):
    if (mousex >= app.scrollLeft) and (mousex <= app.scrollLeft+app.scrollWidth) and (mousey >= app.scrollTop) and (mousey <= app.scrollTop+app.scrollHeight):
        app.trackingScroll = True
        app.initialY = mousey
        return
    
    if app.confirmationScreen:
        buttonList = app.confButtons
    else: buttonList = app.mainButtons

    for button in buttonList:
        if (mousex >= button.left) and (mousex <= button.left+button.width) and (mousey >= button.top) and (mousey <= button.top+button.height):
            return button
    return None

def loadInventory(app):
    pathList = [('s_inventory.txt', app.shirtNum), ('p_inventory.txt', app.pantNum)]
    for path in pathList:
        with open(path[0], 'r') as file:
            for i in range(path[1]):
                line = file.readline()
                attributes = line.split(',')
                if path[0] == 's_inventory.txt':
                    Shirt(attributes[1], attributes[2], attributes[0])
                else:
                    Pant(attributes[1], attributes[2], attributes[0])



def recommendOutfit(app, shirt = None, pants = None):
    if shirt != None:
        item = recommendClothing('shirt')
        while app.avatarOutfit['shirt'] == item:
            item = recommendClothing('shirt')
        app.avatarOutfit['shirt'] = item
    if pants != None:
        item = recommendClothing('shirt')
        while app.avatarOutfit['pant'] != item:
            item = recommendClothing('pant')
        app.avatarOutfit['pant'] = item

def recommendClothing(type):
    if type == 'shirt':
        item = random.choice(Shirt.clean)
    else:
        item = random.choice(Pant.clean)
    return item


def getDate():
    numtoMonths = {1: 'January', 2: 'Feburary', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

    date = str(datetime.today().date())
    monthI = date[5:].find('-') + 5
    monthNum = int(date[5:monthI])
    month = numtoMonths[monthNum]
    day = date[monthI+1:]
    formattedDate = f'{month} {day}, {date[:4]}'
    return date, formattedDate

def addToLog(shirt, pant):
    date, formattedDate = getDate()

    with open('week_log.txt', 'a') as file:
        file.write(f'{date}, {shirt.idS}, {pant.idP}\n')

def getLastLine(path):
    with open(path,'r') as file:
        lLine = file.readlines() [-1]    
    features = lLine.split(',')
    return int(features[0]), features[1], features[2]

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
    image.save(f'assets/shirts/{Shirt.idS}.png')
    path = f'assets/shirts/{Shirt.idS}.png'
    return path
    
def getShirtColor(attribute):
    return 'blue'

def getSleeve(attribute):
    return 's-sleeve'

def inHoverRegion(mousex, mousey, region):
    if (mousex >= region[0]) and (mousex <= region[0]+region[2]) and (mousey >= region[1]) and (mousey <= region[1]+region[3]):
            return True
    return False

#--------------- CLASSES --------------------

class Button:
    allButtons = []
    def __init__(self, name, left, top, width, height, color):
        self.name = name
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.color = color
        Button.allButtons.append(self)
    
    def __repr__(self):
        return f'{self.name}: left={self.left}, top={self.top}, width={self.width}, height={self.height}, color={self.color}'

    def getButtonByName(name):
        for button in Button.allButtons:
            if button.name == name:
                return button

class Shirt: 
    idS, __, __ = getLastLine('s_inventory.txt')
    idS += 1
    clean = []
    worn = []
    
    def __init__(self, color, type, id=None):
        self.color = color
        self.sleeve = type
        if id == None:
            self.id = Shirt.idS
            Shirt.idS += 1
        else:
            self.id = id
        Shirt.clean.append(self)
        
    
    def __repr__(self):
        return f'color: {self.color}, type: {self.sleeve}'
    
    def changeColor(self, color):
        self.color = color

class Pant:
    idP, __, __ = getLastLine('p_inventory.txt')
    clean = []
    worn = []
    
    def __init__(self, color, material, id=None):
        self.color = color
        self.material = material
        if id == None:
            self.idP = Pant.idP
            Pant.idP += 1
        else:
            self.id = id
        Pant.clean.append(self)
       
    

    def __repr__(self):
        return f'color: {self.color}, material: {self.material}'

#--------------- MODEL FUNCTIONS --------------------

def createButtons(app):
    buttons = [
        ('ready', 463, 541,(120-2) , (36-2), COLORS['coral']),
        ('take-picture', 815, 560, 50, 50, COLORS['dark_coral']),
        ('scroll-up', app.width-42-20, 150, 20, 20, COLORS['pink']),
        ('scroll-down', app.width-42-20, app.height-150-20, 20, 20, COLORS['pink']),
        ('closet-shirt', 792, 95, 70, 52, COLORS['pink']),
        ('closet-pant', 792+70+4, 95, 70, 52, COLORS['coral']),
        ('customize-avatar', 792+70+70+8, 95, 68, 52,COLORS['coral'])
    ]
    app.mainButtons = [Button(*params) for params in buttons]

    confButtons = [
        ('confirm', app.width/2+40, 500, 105, 45, COLORS['dark_coral']),
        ('cancel', app.width/2-40-105, 500, 105, 45, 'white'),
        ('change-shirt-color', 395, 320, 109, 45, COLORS['dark_coral']),
        ('change-sleeve', 395, 320+50+20, 180, 45, COLORS['dark_coral'])
    ]
    app.confButtons = [Button(*params) for params in confButtons]


def setDefaultLook(app):
    defaultTop = Shirt('purple-default', 's-sleeve')
    defaultBottom = Pant('blue-default', 'jeans')
    app.avatarOutfit['shirt'] = defaultTop
    app.avatarOutfit['pant'] = defaultBottom

def getNum(app, filePath):
    id, color, sleeve = getLastLine(filePath)
    return id +1

#--------------- CONTROLLER FUNCTIONS --------------------

def onMousePress(app, mousex, mousey):
    idButton = identifyButton(app, mousex,mousey)
    app.selectedButton = idButton
    print(app.selectedButton)

    if idButton == None:
        pass

    elif idButton.name == 'scroll-down':
        adjustScrollbar(app, buttonPress='down')
    elif idButton.name == 'scroll-up':
        adjustScrollbar(app, buttonPress='up')

    elif idButton.name == 'take-picture':
        takePicture(app)
        if app.capturedImage != None:
            mask = create_shirt_mask("assets/templates/shirt.png")
            pixelatedImage = pixelateShirt('captured_image.jpg')
            cropped_image = maskOverlay(pixelatedImage, mask)
            overlaid_image = overlayToTemplate(cropped_image, 'assets/transparent_template.png')  #!!! this doesn't exist yet
            path = removeBackground(overlaid_image, (57,225,20), 70)
            
            attribute = None
            color = getShirtColor(attribute)
            sleeve = getSleeve(attribute)

            app.currCreation = Shirt(color, sleeve) #!!! This won't work

            app.confirmationScreen = True
    
    elif idButton.name == 'ready':
        idButton.color = COLORS['pink']
        shirt = app.avatarOutfit['shirt']
        pant = app.avatarOutfit['pant']
        addToLog(shirt, pant)
        app.animatedMode = True
        #!!! remove change clothes buttons

    elif idButton.name == 'closet-shirt':
        idButton.color = COLORS['pink']
        app.closetDisplay = 'shirts'
        Button.getButtonByName('closet-pant').color = COLORS['coral']
        Button.getButtonByName('customize-avatar').color = COLORS['coral']


    elif idButton.name == 'closet-pant':
        idButton.color = COLORS['pink']
        app.closetDisplay = 'pants'
        Button.getButtonByName('closet-shirt').color = COLORS['coral']
        Button.getButtonByName('customize-avatar').color = COLORS['coral']


    elif idButton.name == 'cusotmize-avatar':
        idButton.color = COLORS['pink']
        app.closetDisplay = 'avatar'
        Button.getButtonByName('closet-pant').color = COLORS['coral']
        Button.getButtonByName('closet-shirt').color = COLORS['coral']



    elif idButton.name == 'confirm':
        with open('s_inventory.txt','a') as file:
            if type(app.currCreation) == Shirt:
                line = f'\n{app.currCreation.idS},{app.currCreation.color},{app.currCreation.sleeve}'
            else: line = f'\n{app.currCreation.idS},{app.currCreation.color},{app.currCreation.material}'
            file.write(line)
        app.confirmationScreen  = False
    elif idButton.name == 'cancel':
        app.confirmationScreen = False
    elif idButton.name == 'change-shirt-color':
        idButton.color = 'yellow'
        newColor = 'maroon' # detectSelection() !!! write this function
        app.currCreation.changeColor(newColor)
    
    if inHoverRegion(mousex, mousey, app.sRegion):
        recommendOutfit(app, shirt='shirt')

def onMouseDrag(app, mousex, mousey):
    if app.trackingScroll:
        adjustScrollbar(app, mousey=mousey)

def onMouseRelease(app, mousex, mousey):
    if app.trackingScroll:
        app.trackingScroll = False
        adjustScrollbar(app, mousey=mousey) 

def onMouseMove(app, mousex, mousey):
    pRegion = (50, 100, 50, 50)
    if inHoverRegion(mousex, mousey, app.sRegion):
        app.showSLabel = True
    elif inHoverRegion(mousex, mousey, pRegion):
        app.showPLabel = True
    else:
        app.showSLabel = False
        app.showPLabel = False

def onMouseRelease(app, mouseX, mouseY):
    if app.selectedButton != None and app.selectedButton.name == 'ready':
        app.selectedButton.color = COLORS['coral']
        app.selectedButton = None

def adjustScrollbar(app, mousey=None, buttonPress=None):
    if buttonPress == 'up':
        currTop = app.scrollTop - 10
        app.itemTop += 10
    elif buttonPress == 'down':
        currTop = app.scrollTop + 10
        app.itemTop -= 10
    else:
        dy = mousey - app.initialY
        app.initialY = mousey
        currTop = app.scrollTop + dy
        app.itemTop -= dy
    
    currBottom = currTop + app.scrollHeight
    minTop = 145 + 22
    maxBottom = 145+479 - 22

    if currTop < minTop:
        app.scrollTop = minTop
        app.itemTop = 157 - (8+84)
    elif currBottom > maxBottom:
        app.scrollTop = maxBottom-app.scrollHeight
        app.itemTop = 157 - (8+84) - app.closetHeight
    else:
        app.scrollTop = currTop

def takeStep(app):
    if app.imageI < 10:
        app.imageI += 1
    else:
        app.animateMode = False
        app.imageI = 0

# def writeToTerminal(message):
#     if len(app.terminalMessage) == message:
#         app.writingToTerminal == False
#         app.
#         return
#     else:
#         app.terminalMessage = message[0]
#         writeToTerminal

#--------------- VIEW FUNCTIONS -----------------

def drawScreen(app):
    rectangles = [
    #screen
        (0, 0, app.width, 80, COLORS['strawberry']),
        (10, 65, app.width-20, 147-65, COLORS['dark_coral']),
        (10, 65, 792-10, app.height-75, COLORS['dark_coral']),
        (10, app.height-150, app.width-20, 150-10, COLORS['dark_coral']),
        (989, 65, app.width-10-989, app.height-75, COLORS['dark_coral']),
    ]

    #background
    drawRect(0, 0, app.width, app.height, fill=COLORS['strawberry'])
    
    
    for rectangle in rectangles:
        drawRect(rectangle[0], rectangle[1], rectangle[2], rectangle[3], fill=rectangle[4])

    #closet
    drawRect(792, 147, 216, 479, fill=COLORS['pink'])
    drawCloset(app)

    drawRect(792, 0, 216, 65, fill=COLORS['strawberry'])
    drawRect(792, 65, 216, 147-65, fill=COLORS['dark_coral'])
    drawRect(792, 147+479, 216, app.height-147-479-10, fill=COLORS['dark_coral'])
    drawRect(792, app.height-10, 216, 10, fill=COLORS['strawberry'])

    drawRect(792-3, 95, 3, 530, fill=COLORS['shadow'])
    drawRect(792-3, 95-3, 73, 3, fill=COLORS['shadow'])



    #header bar
    drawRect(45, 13, 907+3, 41, fill=COLORS['shadow'])
    drawRect(45+3, 13+3, 907, 41, fill=COLORS['gum'])
    drawLabel(f"Maggie's Closet - {app.formattedDate}", 65, 28, align='left-top', fill=COLORS['shadow'], size=25)
    drawRect(app.width-84, 13, 44, 44, fill=COLORS['shadow'])
    drawRect(app.width-84, 13, 44-3, 44-3, fill=COLORS['coral'])
    drawRect(app.width-84+3,13+3, 44-6, 44-6, fill=COLORS['dark_coral'])
    drawLabel('X', app.width-84+10, 13+10, size=30, align='left-top', fill='white')

    #center panel
    drawRect(283, 92, 481, 533, fill=COLORS['pink'])
    drawLabel('Click on clothes to change recommendation', (481+283+283)//2, 161,fill=COLORS['strawberry'], size=20)
    drawRect((283+283+481)//2-60, 541, 120, 36, fill=COLORS['shadow'])

    partPaths = ['hair_color.png', 'pants_color.png', 'shirt_color.png','skin_color.png', 'eye0_b.png', 'avatar_outline_t.png']
    for partPath in partPaths:
        drawImage(f'assets/templates/{partPath}', app.width/2, app.height/2-40, width=340, height=340, align='center')
    
    #weather
    drawRect(42, 95, 213, 530, fill=COLORS['shadow'])
    drawRect(42+3, 95+3, 213-3, 530-3, fill=COLORS['pink'])
    drawLabel('Weather', (42+42+213)//2, 135, fill=COLORS['shadow'], size=25)
    drawLabel('Forecast:', (42+42+213)//2, 165, fill=COLORS['shadow'], size=25)
    
    drawImage('assets/weather/sun.png', (42+42+213)//2, 250, width=100, height=100, align='center')

    drawLabel('Current Temp:', (42+42+213)//2, 95+270, fill=COLORS['shadow'], size=20)
    drawLabel('20', (42+42+213)//2, 95+270+50, fill=COLORS['shadow'], size=50)

    #scroll bar
    drawRect(app.width-41-21, 150, 21, 475, fill='white')
    drawRect(app.scrollLeft, app.scrollTop, app.scrollWidth, app.scrollHeight, fill=COLORS['coral'])
    drawRect(app.scrollLeft, app.scrollTop, app.scrollWidth-1, app.scrollHeight-1, fill='white')
    drawRect(app.scrollLeft+1, app.scrollTop+1, app.scrollWidth-2, app.scrollHeight-2, fill=COLORS['white-pink'])

    drawRect(app.width-42-20, app.height-150-20, 20, 20, fill=COLORS['pink'])

    #terminal
    drawRect(45, 637, app.width-90, 108, fill=COLORS['shadow'])
    drawRect(45+3, 637+3, app.width-90-3, 108-3, fill=COLORS['pink'])
    drawLabel(app.terminalMessage, 59, 656, size=20, align='left-top', fill=COLORS['shadow'])

    #labels
    drawInfoLabels(app)

    #buttons
    for button in app.mainButtons:
        drawRect(button.left, button.top, button.width, button.height, fill=button.color)

    #center panel (continued)
    drawLabel('Ready!', (283+283+481)//2, (541+541+36)//2 ,fill=COLORS['shadow'], size=18)

    #up and down arrows
    drawLabel('▲', app.width-42-20+5, 150+5, align='left-top', fill=COLORS['shadow'])
    drawLabel('▲', app.width-42-20+5, app.height-20-150+5, rotateAngle=180, align='left-top', fill=COLORS['shadow'])

    drawLabel(str(app.avatarOutfit), 200, 400)
    drawRect(482,360-37, 84, 55, fill=None)

    if app.animateMode == True:
        drawImage(f'assets/heart_animation/frame_{app.imageI}.png', 283, 92)

def drawConfirmationScreen(app):
    drawRect(app.width/2, app.height/2, 647, 437, fill=COLORS['strawberry'], align='center')
    drawRect(app.width/2, app.height/2+20,637, 387, fill=COLORS['pink'], align='center')

    drawRect(206, 176, 590, 30, fill=COLORS['shadow'])
    drawRect(206+2, 178, 588, 30, fill=COLORS['gum'])
    drawLabel('New Creation Alert! (1)', app.width/2-323+20, 185, align='left-top', fill=COLORS['shadow'], size=15)

    drawRect(app.width/2 + 323-8-33, 175, 33, 33, fill=COLORS['shadow'])
    drawRect(app.width/2 + 323-8-33, 175, 33-3, 33-3, fill=COLORS['coral'])
    drawRect(app.width/2 +323 -8 -33 +3,175+3, 33-6, 33-6, fill=COLORS['dark_coral'])
    drawLabel('X', app.width/2+323-25, 175+15, size=28, align='center', fill='white')

    drawRect(app.width-240-160, 253, 160, 210, fill=COLORS['gum'])

    drawLabel('Is this right?', 300, 253, align='left-top', fill=COLORS['shadow'], size=25)
    drawLabel('Color:', 300, 253+20+45, align='left-top', fill=COLORS['shadow'], size=25)
    drawLabel('Sleeve:', 300, 253+50+20+20+45, align='left-top', fill=COLORS['shadow'], size=25)

    #drawing buttons
    drawRect(app.width/2+40+4, 500+4, 105, 45, fill=COLORS['dark_coral'])
    drawRect(app.width/2-40-105+4, 500+4, 105, 45, fill=COLORS['dark_coral'])

    for button in app.confButtons:
        drawRect(button.left, button.top, button.width, button.height, fill=button.color)

    drawLabel('Yes', (app.width/2+40+app.width/2+40+105)//2, (500+500+45)//2, fill=COLORS['shadow'], size=25)
    drawLabel('Cancel', (app.width/2-40-105+app.width/2-40-105+105)//2, (500+500+45)//2, fill=COLORS['shadow'], size=25)

    # drawLabel(f'shirt color:{app.currCreation.color}', 220, 250)
    # if type(app.currCreation) == Shirt:
    #     label = f'type:{app.currCreation.sleeve}'
    # else: label = f'type:{app.currCreation.material}'
    # drawLabel(label, 220, 270)

def drawCloset(app):
    if app.closetDisplay == 'shirts':
        num = app.shirtNum
    elif app.closetDisplay == 'pants':
        num = app.pantNum
    else:
        drawCustomizeAvatar(app)
        return

    column = 0
    itemLeft = 801
    itemTop = app.itemTop
    for i in range(num):
        if column == 1:
            drawRect(itemLeft+8+84, itemTop, 84, 84, fill=COLORS['coral'])
            column = 0
        else:
            itemTop += (8+84)
            drawRect(itemLeft, itemTop, 84, 84, fill=COLORS['coral'])
            column += 1
  
def drawCustomizeAvatar(app):
    pass

def drawInfoLabels(app):
    drawItems = False
    if app.showSLabel == True:
        drawItems = True
        label1= f'color: {app.avatarOutfit['shirt'].color}'
        label2 = f'sleeve: {app.avatarOutfit['shirt'].sleeve}'

    elif app.showPLabel == True:
        drawItems = True
        label1 = f'color: {app.avatarOutfit['pant'].color}'
        label2 = (f'material: {app.avatarOutfit['pant'].material}')
        
    if drawItems == True: 
        drawRect(323, 220, 114, 53, fill=COLORS['pink'], border=COLORS['dark_coral'])
        drawLine(323+114, 220+53, app.width/2, app.height/2, fill=COLORS['dark_coral'])
        drawLabel(label1, (323+323+114)//2, 240, fill=COLORS['shadow'])
        drawLabel(label2, (323+323+114)//2, 270, fill=COLORS['shadow'])


#--------------- CMU GRAPHICS FUNCTIONS ---------------------
COLORS = {
    'coral': rgb(255,200,201),
    'dark_coral': rgb(255,141,157), 
    'pink': rgb(255,235,237), 
    'yellow': rgb(248,240,204), 
    'strawberry': rgb(214,122,145),
    'shadow': rgb(162,93,110),
    'white-pink': rgb(255, 238, 240),
    'gum': rgb(244, 202, 213)
    }

def onAppStart(app):
    app.width, app.height = 1049, 776
    app.background = COLORS['strawberry']
    date, formattedDate = getDate()
    app.formattedDate = formattedDate
    app.selectedButton = None

    app.animateMode = False
    app.confirmationScreen = False
    app.counter = 0

    app.imageI = 0
    app.stepsPerSecond = 8

    app.scrollLeft = 989
    app.scrollTop = 171
    app.scrollWidth = 16
    app.scrollHeight = 100
    app.trackingScroll = False
    app.initialY = None

    app.mainButtons = []
    app.confButtons = []
    createButtons(app)

    #app.temp = getTemp('Pittsburgh')

    app.writingToTerminal = True
    app.terminalMessage = ''
    app.message = '> Good morning!! Here’s what’s recommended... Browse the closet to select other options.'

    app.showSLabel, app.showPLabel = False, False

    app.capturedImage = None
    
    app.currCreation = None
   
    app.closetDisplay = 'shirts'
    app.avatarOutfit = {'shirt': None, 'pant': None}    
    setDefaultLook(app)
    
    app.sRegion = (482,360-37, 84, 55)

    app.shirtNum = getNum(app, 's_inventory.txt')
    app.pantNum = getNum(app, 'p_inventory.txt')
    loadInventory(app)
    app.satisfiesEntries = False
    if app.shirtNum > 3:
        app.satisfiesEntries = True
        recommendOutfit(app, 'shirt', 'pants')
    
    app.itemTop = 157 - (8+84) #for closet item starting position
    app.closetHeight = (math.ceil((app.shirtNum / 2)) * 84+8) - 147
    

def onStep(app):
    if app.animateMode:
        app.counter += 1
        takeStep(app)
    if app.writingToTerminal:
        if len(app.message) == 0:
            app.writingToTerminal == False
        else:
            app.terminalMessage += app.message[0]
            app.message = app.message[1:]




def redrawAll(app):
    drawScreen(app)
    if app.confirmationScreen:
        drawConfirmationScreen(app)

def main():
    runApp()

main()