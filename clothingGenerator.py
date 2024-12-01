import cv2
import numpy as np
from PIL import Image

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
    image.save('result.png')


mask = create_shirt_mask("assets/pants.png")
pixelatedImage = pixelateShirt('testShirt.jpg')
cropped_image = maskOverlay(pixelatedImage, mask)
overlaid_image = overlayToTemplate(cropped_image, 'avatarOutline.png')
removeBackground(overlaid_image, (57,225,20), 70)

