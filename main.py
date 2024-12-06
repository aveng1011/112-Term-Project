from cmu_graphics import *
import cv2
import numpy as np
from PIL import Image
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import math
import random
import copy

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

def getImageSize(path):
    image = 'assets/shirts/4.png'
    image = Image.open(path)

    width, height = image.size
    return (width, height)


def distance(value1, value2):
    w1, x1, y1, z1 = value1
    w2, x2, y2, z2 = value2

    return( (((w2-w1)**2) + (x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)**0.5 )

def generateCentroid():
    r = random.randrange(0,255)
    g = random.randrange(0,255)
    b = random.randrange(0,255)
    return (r,g,b, 255)

def kmeans(image_path, centroids=None, prevCentroids=None):
    image = Image.open(image_path)
    imagePixels = image.load()
    width, height = image.size

    if centroids==None:
        centroids = [(0,0,0, 0), (0,0,0, 0), (0,0,0, 0)]

    values = [[],[],[]]

    for i in range(3):
        if centroids[i] == (0,0,0,0):
            centroids[i] = generateCentroid()


    #assigning each pixel to a centroid's cluster
    for x in range(width):
        for y in range(height):
            min = 10000000
            minI = None
            for i in range(3):
                if imagePixels[x,y] != (0,0,0,0):
                    pixelD = distance(imagePixels[x,y], centroids[i])
                    if pixelD < min:
                        min = pixelD
                        minI = i
                    values[minI].append(imagePixels[x,y])


    # #calculating mean value of all values in a cluster
    for i in range(3):
        rVal = 0
        gVal = 0
        bVal = 0

        length = len(values[i])

        for pixel in values[i]:
            rVal += pixel[0]
            gVal += pixel[1]
            bVal += pixel[2]
        
        if length == 0:
            rAv, gAv, bAv = 0, 0, 0
        else: 
            rAv = rVal/length
            gAv = gVal/length
            bAv = bVal/length

        centroids[i] = (rAv, gAv, bAv, 255)

    #iterate
    if prevCentroids==None:
        prevCentroids = copy.deepcopy(centroids)
        return(kmeans(image_path, centroids, prevCentroids))
    elif ((
        distance(centroids[0], prevCentroids[0]) +
        distance(centroids[1], prevCentroids[1]) +
        distance(centroids[2], prevCentroids[2])
        ) // 3 >= 3):
        prevCentroids = copy.deepcopy(centroids)
        return(kmeans(image_path, centroids, prevCentroids))
    else: 
        longest = None
        l_index = None
        for i in range(3):
            if longest == None:
                longest = len(values[i])
                l_index = i
            elif len(values[i]) > longest:
                longest = len(values[i])
                l_index = i
            result = (centroids[i])
            return (result)
            
def getShirtColor(image_path):
    color = kmeans(image_path)
    print(color)

    rgbNames = {'light-blue':(158, 175, 179, 255), 'dark pink': (170, 51, 106, 255), 'maroon': (128,0,0, 255), 'dark green': (178, 172, 136, 255), 'brown':(135,67,45, 255), 'black': (0,0,0,255), 'blue': (0, 0, 255, 255), 'red': (255, 0, 0, 255), 'gray': (80, 80, 80, 255), 'white': (255, 255, 255, 255), 'orange': (255, 165, 0, 255), 'yellow': (255, 255, 0, 255), 'green': (0, 255, 0, 255), 'blue': (0, 0, 255, 255), 'purple': (238, 130, 238, 255), 'beige': (232, 220, 202, 255), 'dark-beige':(215,194,168,255)}

    smallestDistance = None
    currColor = None
    for rgbColor in list(rgbNames.keys()):
        if smallestDistance == None or (distance(color, rgbNames[rgbColor]) < smallestDistance):
            currColor = rgbColor
            smallestDistance = distance(color,rgbNames[rgbColor])
    
    return currColor
def getWeather(city):
    file = requests.get(f'https://www.google.com/search?q=weather+{city}', headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15' })

    soup = BeautifulSoup(file.text, 'html.parser')

    try:
        temp = soup.find('span', id='wob_tm').text
    except:
        temp = '20'
    try:
        rain = soup.find('span', id='wob_pp').text
    except:
        rain = '10%'
    try:
        wind = soup.find('span', id='wob_ws').text
    except:
        wind = '5 mph'

    return temp, rain, wind

def identifyButton(app, mousex,mousey, mode=None):
    if (mousex >= app.scrollLeft) and (mousex <= app.scrollLeft+app.scrollWidth) and (mousey >= app.scrollTop) and (mousey <= app.scrollTop+app.scrollHeight):
        app.trackingScroll = True
        app.initialY = mousey
        return
    
    if app.introScreen:
        buttonList = app.introButtons
    elif app.confirmationScreen:
        buttonList = app.confButtons
    else: 
        if app.closetDisplay == 'shirts':
            buttonList = app.mainButtons + app.shirtButtons
        else: 
            buttonList = app.mainButtons + app.pantButtons

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
                    tshirt = Shirt(attributes[1], attributes[2], f'{attributes[0]}.png', attributes[0])
                else:
                    Pant(attributes[1], attributes[2], f'{attributes[0]}.png', attributes[0])

def recommendOutfit(app, shirt = None, pants = None):
    Shirt.removeShirtByColor('purple-default')
    Pant.removePantByColor('blue-default')
    if shirt != None:
        item = recommendClothing('shirt')
        while app.avatarOutfit['shirt'] == item and (item in Shirt.worn):
            item = recommendClothing('shirt')

        print('recommended', item)
        app.avatarOutfit['shirt'] = item
    if pants != None:
        item = recommendClothing('pant')
        while app.avatarOutfit['pant'] == item and (item in Pant.worn):
            item = recommendClothing('pant')
        print('recommended', item)
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
        file.write(f'{date},{shirt.id},{pant.id}\n')

def getLastLine(path):
    with open(path,'r') as file:
        list = file.readlines()
        lLine = list[-1]
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
def overlayImage(maskPath, imagePath, outputPath):
    mask = Image.open(maskPath)
    image = Image.open(imagePath)

    maskW, maskH = mask.size

    image = image.resize(mask.size)
    image = image.convert('RGBA')

    mask_pixels = mask.load()
    image_pixels = image.load()
    for y in range(maskH):
        for x in range(maskW):
            if mask_pixels[x,y] == 0:
                image_pixels[x,y] = (0, 0, 0, 0)
    image.save(outputPath)
    return outputPath

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
    all =[]
    clean = []
    worn = []
    
    def __init__(self, color, type, path, id=None):
        self.color = color
        self.sleeve = type
        self.path = path
        if id == None:
            self.id = Shirt.idS
            Shirt.idS += 1
        else:
            self.id = id
        Shirt.clean.append(self)
        Shirt.all.append(self)
        
    
    def __repr__(self):
        return f'color: {self.color}, type: {self.sleeve}'

    
    def getById(id):
        for shirt in Shirt.all:
            if int(shirt.id) == (id):
                return shirt

    
    def removeShirtByColor(color):
        for shirt in Shirt.all:
            if shirt.color == color:
                Shirt.all.remove(shirt)
                Shirt.clean.remove(shirt)

class Pant:
    idP, __, __ = getLastLine('p_inventory.txt')
    idP += 1
    all = []
    clean = []
    worn = []
    
    def __init__(self, color, material, path, id=None):
        self.color = color
        self.material = material
        self.path = path
        if id == None:
            self.idP = Pant.idP
            Pant.idP += 1
        else:
            self.id = id
        Pant.clean.append(self)
        Pant.all.append(self)

    def __repr__(self):
        return f'color: {self.color}, material: {self.material}, id: {self.id}'
    
    def removePantByColor(color):
        for pant in Pant.all:
            if pant.color == color:
                Pant.all.remove(pant)
                Pant.clean.remove(pant)
    
    def getById(id):
        for pant in Pant.all:
            if int(pant.id) == int(id):
                return pant


#--------------- MODEL FUNCTIONS --------------------

def createButtons(app):
    column = 0
    itemLeft = 801
    itemTop = app.itemTop
    num = app.shirtNum

    buttons = [
        ('ready', 463, 541,(120-2) , (36-2), COLORS['coral']),
        ('take-picture-s', 815, 560, 50, 50, COLORS['dark_coral']),
        ('take-picture-p', 815+100, 560, 50, 50, COLORS['dark_coral']),
        ('scroll-up', app.width-42-20, 150, 20, 20, COLORS['pink']),
        ('scroll-down', app.width-42-20, app.height-150-20, 20, 20, COLORS['pink']),
        ('closet-shirt', 792, 95, 70, 52, COLORS['pink']),
        ('closet-pant', 792+70+4, 95, 70, 52, COLORS['coral']),
        ('customize-avatar', 792+70+70+8, 95, 68, 52,COLORS['coral']),
    ]

    app.mainButtons = [Button(*params) for params in buttons]
    
    shirtButtons = []
    item = 'shirt'
    num = app.shirtNum
    for i in range(num):
        if column == 1:
            shirtButtons.append((f'{item}{i}_btn', itemLeft+8+84+3, itemTop+3, 84-6, 84-6, COLORS['coral']))
            column = 0
        else:
            itemTop += (8+84)
            shirtButtons.append((f'{item}{i}_btn', itemLeft+3, itemTop+3, 84-6, 84-6, COLORS['coral']))
            column += 1

    app.shirtButtons = [Button(*params) for params in shirtButtons]

    pantButtons = []
    column = 0
    item = 'pant'
    itemTop = app.itemTop
    num = app.pantNum
    for i in range(num):
        if column == 1:
            pantButtons.append((f'{item}{i}_btn', itemLeft+8+84+3, itemTop+3, 84-6, 84-6, COLORS['coral']))
            column = 0
        else:
            itemTop += (8+84)
            pantButtons.append((f'{item}{i}_btn', itemLeft+3, itemTop+3, 84-6, 84-6, COLORS['coral']))
            column += 1

    app.pantButtons = [Button(*params) for params in pantButtons]

    confButtons = [
        ('confirm', app.width/2+40, 500, 105, 45, COLORS['dark_coral']),
        ('cancel', app.width/2-40-105, 500, 105, 45, 'white'),
        ('change-shirt-color', 395, 320, 180, 45, COLORS['coral']),
        ('change-sleeve', 395, 320+50+20, 180, 45, COLORS['coral'])
    ]
    app.confButtons = [Button(*params) for params in confButtons]

    introButtons = [
        ('set-name', app.width/2-75, 500, 150, 45, COLORS['dark_coral'])
    ]
    app.introButtons = [Button(*params) for params in introButtons]

def updateClosetButtons(app, section):
    itemTop = app.itemTop

    if section == 'shirt':
        for button in app.shirtButtons:
            button.top = app.itemTop
    else:
        for button in app.pantButtons:
            button.top = app.itemTop

def setDefaultLook(app):
    defaultTop = Shirt('black', 's-sleeve','0.png', 0)
    # Shirt.idS -= 1
    Shirt.all.remove(defaultTop)
    # Shirt.clean.remove(defaultTop)
    defaultBottom = Pant('dark-beige', 'cotton', '0.png', 0)
    Pant.all.remove(defaultBottom)
    # Pant.clean.remove(defaultBottom)
    app.avatarOutfit['shirt'] = defaultTop
    app.avatarOutfit['pant'] = defaultBottom

def getNum(app, filePath):
    id, color, sleeve = getLastLine(filePath)
    return id +1

def removeOldLogEntries(app):
    currDate, _ = getDate()

    with open('week_log.txt', 'r') as file:
        allLines = file.readlines()
    
    for line in allLines:
        lDate = line.split(',')[0] 
        sIndex = int(line.split(',')[1])
        pIndex = int(line.split(',')[2])
        
        format = "%Y-%m-%d"
        date1 = datetime.strptime(currDate, format)
        date2 = datetime.strptime(lDate, format)

        difference = str(date1-date2)
        list = difference.split(' days')
        difference = list[0]

        if ':' in difference:
            difference  = 0
    
        if int(difference) > 7:
            shirt = Shirt.getById(int(sIndex))
            Shirt.worn.remove(shirt)
            Shirt.clean.append(shirt)
            pant = Pant.getById(int(pIndex))
            Pant.clean.append(pant)
            try:
                Pant.worn.remove(pant)
            except:
                pass

            allLines.remove(line)
        else: 
            shirt = Shirt.getById(int(sIndex))
            Shirt.worn.append(shirt)
            try:
                Shirt.clean.remove(shirt)
            except:
                pass
            pant = Pant.getById(int(pIndex))
            Pant.worn.append(pant)
            try:
                Pant.clean.remove(pant)
            except:
                pass
        
        with open('week_log.txt', 'w') as file:
            for line in allLines:
                file.write(line)

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

    elif idButton.name == 'take-picture-s':
        takePicture(app)
        if app.capturedImage != None:
            imagePath = overlayImage('assets/templates/shirt_mask.png', 'captured_image.jpg', f'assets/shirts/{Shirt.idS}.png')
            color = getShirtColor(imagePath)
            imagePath = imagePath[13:]
            sleeve = None

            app.currCreation = Shirt(color, sleeve, imagePath, Shirt.idS-1)

            app.confirmationScreen = True

    
    elif idButton.name == 'take-picture-p':
        takePicture(app)
        if app.capturedImage != None:
            imagePath = overlayImage('assets/templates/pant_mask.png', 'captured_image.jpg', f'assets/pants/{Pant.idP}.png')
            color = getShirtColor(imagePath)
            imagePath = imagePath[13:]
            material = None

            app.currCreation = Pant(color, material, imagePath, Pant.idP-1)

            app.confirmationScreen = True

    
    elif idButton.name == 'ready':
        idButton.color = COLORS['pink']
        shirt = app.avatarOutfit['shirt']
        pant = app.avatarOutfit['pant']
        Shirt.worn.append(shirt)
        Pant.worn.append(shirt)
        addToLog(shirt, pant)
        app.animateMode = True
        app.centerMessage = 'Looking ready to seize the day!'
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

    elif 'btn' in idButton.name:
        if 'shirt' in idButton.name:
            shirtId = int(idButton.name[5:-4])
            app.avatarOutfit['shirt'] = Shirt.getById(shirtId)
        else:
            pantId = int(idButton.name[4:-4])
            app.avatarOutfit['pant'] = Pant.getById(pantId)



    elif idButton.name == 'confirm':
        if type(app.currCreation) == Shirt:
            path = 's_inventory.txt'
        else: 
            path = 'p_inventory.txt'
        with open(path ,'a') as file:
            if type(app.currCreation) == Shirt:
                line = f'\n{app.currCreation.idS},{app.currCreation.color},{app.currCreation.sleeve}'
            else: line = f'\n{app.currCreation.idP},{app.currCreation.color},{app.currCreation.material}'
            file.write(line)
        app.confirmationScreen  = False
        app.shirtNum = getNum(app, 's_inventory.txt')
        app.pantNum = getNum(app, 'p_inventory.txt')
        createButtons(app)
        loadInventory(app)

        
    elif idButton.name == 'cancel':
        app.confirmationScreen = False
    elif idButton.name == 'change-sleeve':
        if type(app.currCreation) == Shirt:
            if (app.currCreation.sleeve == None or app.currCreation.sleeve =='s-sleeve'):
                app.currCreation.sleeve = 'l-sleeve'
            elif type(app.currCreation == Shirt): 
                app.currCreation.sleeve = 's-sleeve'
        elif app.currCreation.material == None or app.currCreation.material == 'jeans':
            app.currCreation.material = 'cotton'
        else:
            app.currCreation.material = 'jeans'
    
    elif idButton.name == 'set-name':
        app.introScreen = False
    
    if inHoverRegion(mousex, mousey, app.sRegion):
        recommendOutfit(app, shirt='shirt')
    elif inHoverRegion(mousex, mousey, app.pRegion):
        recommendOutfit(app, pants='pant')


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
    elif inHoverRegion(mousex, mousey, app.pRegion):
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


#--------------- VIEW FUNCTIONS -----------------

def drawScreen(app):
    rectangles = [
    #screen
        (0, 0, app.width, 80, COLORS['strawberry']),
        (10, 65, app.width-20, 147-65, COLORS['dark_coral']),
        (10, 65, 792-10, app.height-75, COLORS['dark_coral']),
        (10, app.height-150, app.width-20, 150-10, COLORS['dark_coral']),
        (989, 65, app.width-10-989, app.height-75, COLORS['dark_coral'])
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
    drawLabel(f"{app.name}'s Closet - {app.formattedDate}", 65, 28, align='left-top', fill=COLORS['shadow'], size=25, font='Pixelify Sans')
    drawRect(app.width-84, 13, 44, 44, fill=COLORS['shadow'])
    drawRect(app.width-84, 13, 44-3, 44-3, fill=COLORS['coral'])
    drawRect(app.width-84+3,13+3, 44-6, 44-6, fill=COLORS['dark_coral'])
    drawLabel('X', app.width-84+10, 13+10, size=30, align='left-top', fill='white', font='Pixelify Sans')

    #center panel
    drawRect(283, 92, 481, 533, fill=COLORS['shadow'])
    drawRect(283+3, 92+3, 48-3, 533-3, fill=COLORS['pink'])
    drawImage('assets/center_background.png', 283+3, 92+3, width=481-3, height=533-3, align='left-top')
    drawLabel(app.centerMessage, (481+283+283)//2, 161,fill=COLORS['strawberry'], size=20, font='Pixelify Sans')
    drawRect((283+283+481)//2-60, 541, 120, 36, fill=COLORS['shadow'])

    drawImage('assets/templates/hair_color.png', app.width/2, app.height/2-40, width=340, height=340, align='center')
    drawImage(f'assets/pants/{app.avatarOutfit['pant'].path}', app.width/2, (app.height/2)+23, width=340, height=210, align='center')
    drawImage(f'assets/shirts/{app.avatarOutfit['shirt'].path}', app.width/2, app.height/2-36, width=340, height=210, align='center')
    partPaths = ['templates/skin_color.png', 'templates/eye0_br.png', 'templates/avatar_outline_t.png']
    for partPath in partPaths:
        drawImage(f'assets/{partPath}', app.width/2, app.height/2-40, width=340, height=340, align='center')
    
    #weather
    drawRect(42, 95, 213, 530, fill=COLORS['shadow'])
    drawRect(42+3, 95+3, 213-3, 530-3, fill=COLORS['pink'])
    drawLabel('Weather', (42+42+213)//2, 135, fill=COLORS['shadow'], size=25, font='Pixelify Sans')
    drawLabel('Forecast:', (42+42+213)//2, 165, fill=COLORS['shadow'], size=25, font='Pixelify Sans')
    
    drawImage('assets/weather/sun.png', (42+42+213)//2, 250, width=100, height=100, align='center')
    drawImage('assets/weather/rain.png', (42+42+213)//2-80, 450, width=50, height=50)
    drawLabel(app.rain, (42+42+213)//2-80+100, 450+15, size=20, fill=COLORS['shadow'], font='Pixelify Sans')
    drawImage('assets/weather/wind.png', (42+42+213)//2-80, 500, width=50, height=50)
    drawLabel(app.wind, (42+42+213)//2-80+100, 500+15, size=20, fill=COLORS['shadow'], font='Pixelify Sans')

    drawLabel('Current Temp:', (42+42+213)//2, 95+270, fill=COLORS['shadow'], size=20, font='Pixelify Sans')
    drawLabel(app.temp, (42+42+213)//2, 95+270+50, fill=COLORS['shadow'], size=50, font='Pixelify Sans')

    #scroll bar
    drawRect(app.width-41-21, 150, 21, 475, fill='white')
    drawRect(app.scrollLeft, app.scrollTop, app.scrollWidth, app.scrollHeight, fill=COLORS['coral'])
    drawRect(app.scrollLeft, app.scrollTop, app.scrollWidth-1, app.scrollHeight-1, fill='white')
    drawRect(app.scrollLeft+1, app.scrollTop+1, app.scrollWidth-2, app.scrollHeight-2, fill=COLORS['white-pink'])

    drawRect(app.width-42-20, app.height-150-20, 20, 20, fill=COLORS['pink'])

    #terminal
    drawRect(45, 637, app.width-90, 108, fill=COLORS['shadow'])
    drawRect(45+3, 637+3, app.width-90-3, 108-3, fill=COLORS['pink'])
    drawLabel(app.terminalMessage, 59, 656, size=20, align='left-top', fill=COLORS['shadow'], font='Pixelify Sans')

    #labels
    drawInfoLabels(app)

    #buttons
    for button in app.mainButtons:
        drawRect(button.left, button.top, button.width, button.height, fill=button.color)

    #closet (continued)
    drawImage('assets/templates/shirt_icon.png', (792+792+70)//2, (95+95+50)//2, height=40, width=35, align='center')
    drawImage('assets/templates/pant_icon.png', (792+792+70+70+74+4)//2, (95+95+50)//2, height=40, width=45, align='center')
    drawLabel('+', 833, 578, fill=COLORS['white-pink'], size=30, font='Pixelify Sans', align='left-top')
    drawLabel('+', 933, 578, fill=COLORS['white-pink'], size=30, font='Pixelify Sans', align='left-top')
    
    #center panel (continued)
    drawLabel('Ready!', (283+283+481)//2, (541+541+36)//2 ,fill=COLORS['shadow'], size=18, font='Pixelify Sans')

    #up and down arrows
    drawLabel('▲', app.width-42-20+5, 150+5, align='left-top', fill=COLORS['shadow'])
    drawLabel('▲', app.width-42-20+5, app.height-20-150+5, rotateAngle=180, align='left-top', fill=COLORS['shadow'])

    if app.animateMode:
        drawImage(f'assets/heart_animation/frame_{app.imageI}.png', 283, 92, width=481, height=533)
    if app.introScreen:
        drawIntroScreen(app)



def drawIntroScreen(app):
    drawRect(app.width/2, app.height/2, 647, 437, fill=COLORS['strawberry'], align='center')
    drawRect(app.width/2, app.height/2+20,637, 387, fill=COLORS['pink'], align='center')

    drawLabel(app.name, app.width/2, app.height/2-80, size=30, fill=COLORS['shadow'], font='Pixelify Sans')
    drawLabel('Welcome to your new closet!', app.width/2, app.height/2, size=25, fill=COLORS['shadow'], font='Pixelify Sans')
   

    for button in app.introButtons:
        drawRect(button.left-3, button.top-3, button.width+3, button.height+3, fill=COLORS['white-pink'])
        drawRect(button.left, button.top, button.width, button.height, fill=COLORS['shadow'])
        drawRect(button.left, button.top, button.width-3, button.height-3, fill=button.color)
        drawLabel('Get started', app.width/2,(button.top+button.top+button.height)//2, size=20, fill=COLORS['pink'], font='Pixelify Sans')


def drawConfirmationScreen(app):
    drawRect(app.width/2, app.height/2, 647, 437, fill=COLORS['strawberry'], align='center')
    drawRect(app.width/2, app.height/2+20,637, 387, fill=COLORS['pink'], align='center')

    drawRect(206, 176, 590, 30, fill=COLORS['shadow'])
    drawRect(206+2, 178, 588, 30, fill=COLORS['gum'])
    drawLabel('New Creation Alert! (1)', app.width/2-323+20, 185, align='left-top', fill=COLORS['shadow'], size=15, font='Pixelify Sans')

    drawRect(app.width/2 + 323-8-33, 175, 33, 33, fill=COLORS['shadow'])
    drawRect(app.width/2 + 323-8-33, 175, 33-3, 33-3, fill=COLORS['coral'])
    drawRect(app.width/2 +323 -8 -33 +3,175+3, 33-6, 33-6, fill=COLORS['dark_coral'])
    drawLabel('X', app.width/2+323-25, 175+15, size=28, align='center', fill='white', font='Pixelify Sans')

    #drawing buttons
    drawRect(app.width/2+40+4, 500+4, 105, 45, fill='white')
    drawRect(app.width/2-40-105+4, 500+4, 105, 45, fill=COLORS['dark_coral'])

    drawRect(395-2, 320-2, 180+4, 45+4, fill=COLORS['shadow'])
    drawRect(395-2, 320+50+20-2, 180+4, 45+4, fill=COLORS['shadow'])
    drawRect(395, 320, 180+2, 45+2, fill='white')
    drawRect(395, 320+50+20, 180+2, 45+2, fill='white')

    for button in app.confButtons:
        drawRect(button.left, button.top, button.width, button.height, fill=button.color)


    drawLabel('Yes', (app.width/2+40+app.width/2+40+105)//2, (500+500+45)//2, fill='white', size=25, font='Pixelify Sans')
    drawLabel('Cancel', (app.width/2-40-105+app.width/2-40-105+105)//2, (500+500+45)//2, fill=COLORS['shadow'], size=25, font='Pixelify Sans')

    drawRect(app.width-240-160, 253, 160, 210, fill=COLORS['gum'])
    if type(app.currCreation) == Shirt:
        ipath = f'assets/shirts/{app.currCreation.path}'
        typeLabel = 'Sleeve:'
        creationType = app.currCreation.sleeve
    else:
        ipath = f'assets/pants/{app.currCreation.path}'
        typeLabel = 'Material:'
        creationType = app.currCreation.material
    widthi, heighti = getImageSize(ipath)
    drawImage(ipath, (((app.width-240-160+(app.width-240-160)+160)//2)), (253+253+210)//2, width = widthi//7, height=heighti//7, align='center')

    drawLabel('Is this right?', 300, 253, align='left-top', fill=COLORS['shadow'], size=25, font='Pixelify Sans')
    drawLabel(f'Color:', 300, 253+20+45+15, align='left-top', fill=COLORS['shadow'], size=25, font='Pixelify Sans')
    drawLabel(f'{app.currCreation.color}', (395+395+180)//2, 253+20+45+22, align='center', fill=COLORS['shadow'], size=25, font='Pixelify Sans')
    

    drawLabel(f'{typeLabel}', 300, 253+50+20+20+45+15, align='left-top', fill=COLORS['shadow'], size=18, font='Pixelify Sans')
    if creationType == None:
        drawLabel('Select', (395+395+109)//2, (320+70+320+70+45)//2, align='center', fill=COLORS['shadow'], size=25, font='Pixelify Sans')
    else:
        drawLabel(f'{creationType}', (395+395+180)//2, (320+70+320+70+45)//2, align='center', fill=COLORS['shadow'], size=23, font='Pixelify Sans')
    
def drawCloset(app):

    if app.closetDisplay == 'shirts':
        for button in app.shirtButtons:
            drawRect(button.left, button.top, button.width, button.height, fill=button.color)
        num = app.shirtNum
    elif app.closetDisplay == 'pants':
        for button in app.pantButtons:
            drawRect(button.left, button.top, button.width, button.height, fill=button.color)
        num = app.pantNum
        path = 'assets/pants/'
    else:
        drawCustomizeAvatar(app)
        return

    column = 0
    itemLeft = 801
    itemTop = app.itemTop
    for i in range(num):
        if column == 1:
            drawRect(itemLeft+8+84, itemTop, 84, 84, fill=COLORS['strawberry'])
            drawRect(itemLeft+8+84, itemTop, 84-3, 84-3, fill=COLORS['white-pink'])
            drawRect(itemLeft+8+84+3, itemTop+3, 84-6, 84-6, fill=COLORS['coral'])
            if app.closetDisplay == 'shirts':
                path = f'assets/shirts/{Shirt.all[i].path}'
                app.shirtButtons[i].top = itemTop
            else:
                path = f'assets/pants/{Pant.all[i].path}'
                app.pantButtons[i].top = itemTop
            iwidth, iheight = getImageSize(path)
            drawImage(path, (itemLeft+8+84+itemLeft+8+84+84)//2, (itemTop+itemTop+84)//2, width=iwidth//7, height=iheight//7, align='center')
            column = 0
        else:
            itemTop += (8+84)
            drawRect(itemLeft, itemTop, 84, 84, fill=COLORS['strawberry'])
            drawRect(itemLeft, itemTop, 84-3, 84-3, fill=COLORS['white-pink'])
            drawRect(itemLeft+3, itemTop+3, 84-6, 84-6, fill=COLORS['coral'])
            if app.closetDisplay == 'shirts':
                path = f'assets/shirts/{Shirt.all[i].path}'
                app.shirtButtons[i].top = itemTop
            else:
                path = f'assets/pants/{Pant.all[i].path}'
                app.pantButtons[i].top = itemTop
            iwidth, iheight = getImageSize(path)
            drawImage(path, (itemLeft+3+itemLeft+3+84)//2, (itemTop+itemTop+84)//2, width=iwidth//7, height=iheight//7, align='center')
            column += 1
  
def drawCustomizeAvatar(app):
    pass

def drawInfoLabels(app):
    drawItems = False
    if app.showSLabel == True:
        drawItems = True
        label1= f'color: {app.avatarOutfit['shirt'].color}'
        label2 = f'sleeve: {app.avatarOutfit['shirt'].sleeve}'
        lineCoords = (323+114, 220+53, app.width/2, app.height/2-20)
        rectCoords = (323, 220, 114, 53)
        labelCoords = ((323+323+114)//2, 240)

    elif app.showPLabel == True:
        drawItems = True
        label1 = f'color: {app.avatarOutfit['pant'].color}'
        label2 = (f'material: {app.avatarOutfit['pant'].material}')
        lineCoords = (323+114, 220+53+53, app.width/2, 360+15+20)
        rectCoords = (323, 220+53, 114, 53)
        labelCoords = ((323+323+114)//2, 240+53)
        
    if drawItems == True: 
        drawRect(rectCoords[0], rectCoords[1], rectCoords[2], rectCoords[3], fill=COLORS['white-pink'], border=COLORS['dark_coral'])
        drawLine(lineCoords[0], lineCoords[1], lineCoords[2], lineCoords[3], fill=COLORS['dark_coral'])
        drawLabel(label1, labelCoords[0], labelCoords[1], fill=COLORS['shadow'], font='Pixelify Sans')
        drawLabel(label2, labelCoords[0], labelCoords[1]+20, fill=COLORS['shadow'], font='Pixelify Sans')


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
    app.introScreen = True 
    app.counter = 0

    app.imageI = 0
    app.stepsPerSecond = 8

    app.scrollLeft = 989
    app.scrollTop = 171
    app.scrollWidth = 16
    app.scrollHeight = 100
    app.trackingScroll = False
    app.initialY = None

    app.temp, app.rain, app.wind = getWeather('Pittsburgh')

    app.writingToTerminal = True
    app.terminalMessage = ''
    app.message = '> Good morning!! Here’s what’s recommended... Browse the closet to select other options.'
    app.centerMessage = 'Click on clothes to change recommendation'

    app.showSLabel, app.showPLabel = False, False

    app.capturedImage = None
    
    app.currCreation = None
   
    app.closetDisplay = 'shirts'
    app.avatarOutfit = {'shirt': None, 'pant': None}    
    setDefaultLook(app)
    
    app.sRegion = (482,360-37, 84, 55)
    app.pRegion = (484+6, 360+15, 75, 58)

    app.shirtNum = getNum(app, 's_inventory.txt')
    app.pantNum = getNum(app, 'p_inventory.txt')
    loadInventory(app)
    app.satisfiesEntries = False
    if app.shirtNum > 3:
        app.satisfiesEntries = True
        recommendOutfit(app, 'shirt', 'pants')
    app.itemTop = 157 - (8+84) #for closet item starting position
    app.closetHeight = (math.ceil((app.shirtNum / 2)) * 84+8) - 147
    
    app.name = None

    if app.introScreen:
        response = app.getTextInput('To get started, please enter your name')
        app.name = 'None' if response == '' else response

    app.mainButtons = []
    app.confButtons = []
    app.introButtons = []
    app.shirtButtons = []
    app.pantButtons = []
    createButtons(app)
    removeOldLogEntries(app)


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