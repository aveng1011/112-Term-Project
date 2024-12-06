from cmu_graphics import *
import cv2
import numpy as np
from PIL import Image, ImageOps
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import math


def crop(maskPath, referencePath):
    mask = Image.open(maskPath)
    input = Image.open(referencePath)

    maskw, maskh = mask.size
    inputW, inputH = input.size

    maskResult = mask.crop((0,maskh-inputH-300, maskw, inputH+(maskh-inputH-300)))
    rw, rh = maskResult.size

    print('mask', maskw, maskh)
    print('captured image', inputW, inputH)
    maskResult.save('assets/templates/cropped_shirt_mask.png')

crop('assets/templates/shirt_mask.png', 'captured_image.jpg')


def create_mask(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    shirt_contour = contours[0] 
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [shirt_contour], -1, 255, thickness=cv2.FILLED)
    mask = Image.fromarray(mask)
    mask.save('skin_mask.png')
    return mask

#create_mask('assets/templates/skin.png')

def changeSkinTone(image_path, currSkinTone, newColor):
    image = Image.open(image_path)
    imagePixels = image.load()

    w, h = image.size

    for y in range(h):
        for x in range(w):
            if imagePixels[x,y] == currSkinTone:
                imagePixels[x,y] = newColor
    #image.show()
    image.save("assets/pants/2.png")

# changeSkinTone('assets/templates/pants_color.png', (192,136,230, 255), (255, 0, 255, 255))

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

# overlayImage('assets/templates/shirt_mask.png', 'captured_image.jpg', 'result2.png')

def pixelateShirt(imagePath):
    combined = Image.open(imagePath)
    pixelation_scale = 0.15
    small_size = (int(combined.size[0] * pixelation_scale), int(combined.size[1] * pixelation_scale))
    small_image = combined.resize(small_size, Image.NEAREST)
    pixelated_image = small_image.resize(combined.size, Image.NEAREST)
    pixelated_image.show()
    pixelated_image.save('p_avatar_outline.png')

#pixelateShirt('assets/templates/avatar_outline.png')


def onAppStart(app):
    app.background = 'black'
    image = Image.open('assets/templates/shirt_mask.png')
    app.widthI, app.heightI = image.size

    app.width = 800
    app.height=1000


def redrawAll(app):
    #image = Image.open('result.png')
    #drawImage(image, app.width/2, app.height/2, width=app.widthI/2, height=app.heightI/2, align='center')
    drawImage('/Users/maggiechen/Documents/15-112 Term Project/result2.png', app.width/2, app.height/2-300, width=app.widthI/2, height=app.heightI/2, align='center')
    


def main():
    runApp()

#main()