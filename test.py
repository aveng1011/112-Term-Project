from PIL import Image
import random
import copy


def distance(value1, value2):
    w1, x1, y1, z1 = value1
    w2, x2, y2, z2 = value2

    return( (((w2-w1)**2) + (x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)**0.5 )

def generateCentroid():
    r = random.randrange(0, 255)
    g = random.randrange(0,255)
    b = random.randrange(0, 255)
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
    

    rgbNames = {'brown':(135,67,45, 255), 'black': (0,0,0,255), 'blue': (0, 0, 255, 255), 'red': (255, 0, 0, 255), 'gray': (80, 80, 80, 255), 'white': (255, 255, 255, 255), 'orange': (255, 165, 0, 255), 'yellow': (255, 255, 0, 255), 'green': (0, 255, 0, 255), 'blue': (0, 0, 255, 255), 'purple': (238, 130, 238, 255), 'beige': (232, 220, 202, 255), 'dark-beige':(215,194,168,255)}

    smallestDistance = None
    currColor = None
    for rgbColor in list(rgbNames.keys()):
        if smallestDistance == None or (distance(color, rgbNames[rgbColor]) < smallestDistance):
            currColor = rgbColor
            smallestDistance = distance(color,rgbNames[rgbColor])
    
    return currColor

print(getShirtColor('assets/shirts/3.png'))