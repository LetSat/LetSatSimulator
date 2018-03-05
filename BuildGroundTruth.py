# Build Ground Truth from NASA Blue Marble Images
# v1.3
# Intended for use in OpenGL Simulator
# 29 Jan 2018 - v1.0 - Initial Implementation
# 12 Feb 2018 - v1.1 - Configurable dialation
# 12 Feb 2018 - v1.2 - Improve dialation order
# 05 Mar 2018 - v1.3 - Add cloud gt sourcing and classes
# Chandler Griscom

import cv2
import numpy as np
import sys

dialationIters = 1
cloudImg = ""
classSet = ['t1_viz', 't1_segnet', 't2_viz', 't2_segnet']

if len(sys.argv) < 4 or len(sys.argv) > 6:
    print "Usage: python2 BuildGroundTruth.py {class} {src_img} {out_img} [dialations] [cloudGT]"
    print "Classes are: %s" % str(classSet)
    quit(1)
    
className = str(sys.argv[1])
if className not in classSet:
    print 'Class "%s" not recognized. Classes are: %s' % (className, str(classSet))
    quit(1)

if len(sys.argv) >= 5:
    dialationIters = int(sys.argv[4])
if len(sys.argv) >= 6:
    cloudImg = sys.argv[5]

img_BGR = cv2.imread(sys.argv[2])
img_RGB = cv2.cvtColor(img_BGR, cv2.COLOR_BGR2RGB)
img_HSV = cv2.cvtColor(img_BGR, cv2.COLOR_BGR2HSV)

# Create Masks

def getMask(img, lowerBound, upperBound, dialationIters):
  lowerSpace = np.array(lowerBound, dtype = "uint8")
  upperSpace = np.array(upperBound, dtype = "uint8")

  mask = cv2.inRange(img, lowerSpace, upperSpace)
  
  mask = dialate(mask, dialationIters)
  
  return mask

def dialate(mask, dialationIters):
  if dialationIters > 0:
    mask = cv2.dilate(mask, np.ones((2,2), np.uint8), iterations=dialationIters)
  return mask


# Snow is low-sat, high-value
snowMask = getMask(img_HSV, [0, 0, 160], [180, 30, 255], 0)  # Unsaturated regions
# ^^ good and validated

# Ocean is high-sat, low value, blue
oceanMask = getMask(img_HSV, [60, 200, 0], [170, 255, 120], dialationIters)
# ^^ not bad

# Grass
grassMask = getMask(img_HSV, [35, 75, 0], [80, 255, 200], 0)

# Desert
desertMask = getMask(img_HSV, [0, 50, 100], [40, 255, 220], 0)

# Desert or Grass
eitherMask = getMask(img_HSV, [0, 50, 0], [90, 255, 220], dialationIters)

def getColorMask(origImage, mask, color):
  colorMask = getGTBase(origImage, color)
  colorMask = cv2.bitwise_and(colorMask, colorMask, mask=mask)
  return colorMask

def getGTBase(origImage, color):
  base = np.zeros(origImage.shape, origImage.dtype)
  base[:,:] = color
  return base

def overwriteWithMask(image, colorMask, binaryMask):
  return cv2.addWeighted(
      cv2.addWeighted(
          image.copy(),1,getColorMask(image, binaryMask, (255,255,255)),-1,0)
      ,1,colorMask,1,0)

def buildColorMask(origImage, maskColorPairs, baseColor):
  colorMask = getGTBase(origImage, baseColor)
  for pair in maskColorPairs:
    if pair[0] is None:
        continue
    colorMask = overwriteWithMask(colorMask,getColorMask(origImage,pair[0],pair[1]), pair[0])
  return colorMask

dialatedGrass = dialate(grassMask, dialationIters)
dialatedDesert = dialate(desertMask, dialationIters)
dialatedSnow = dialate(snowMask, dialationIters)

unclearLandMask = cv2.bitwise_and(dialatedGrass, dialatedDesert)
unclearSnowMask = cv2.bitwise_and(cv2.bitwise_or(dialatedGrass, dialatedDesert), dialatedSnow)
allLand = cv2.bitwise_or(cv2.bitwise_or(dialatedGrass, dialatedDesert), dialatedSnow)
unclear = cv2.bitwise_and(allLand, oceanMask)

cloudMask = None
if cloudImg != "":
    cloud_BGR = cv2.imread(cloudImg)
    cloud_HSV = cv2.cvtColor(cloud_BGR, cv2.COLOR_BGR2HSV)
    unclearCloudMask = getMask(cloud_HSV, [0, 0, 80], [180, 255, 100], 0)
    cloudMask = getMask(cloud_HSV, [0, 0, 100], [180, 255, 255], 0)
    unclear = cv2.bitwise_or(unclear, unclearCloudMask)

if className.endswith('viz'):
    eitherColor = (255,255,0)
    desertColor = (255,0,0)
    grassColor = (0,255,0)
    unclearLandColor = (255,255,0)
    snowColor = (255,255,255)
    unclearSnowColor = (127,127,127)
    oceanColor = (0,0,255)
    cloudColor = (0,255,255)
    unclearColor = (0,0,0)
elif className == ('t1_segnet'):
    eitherColor = (5,5,5)
    desertColor = (2,2,2)
    grassColor = (3,3,3)
    unclearLandColor = (5,5,5)
    snowColor = (4,4,4)
    unclearSnowColor = (5,5,5)
    oceanColor = (1,1,1)
    cloudColor = (5,5,5)
    unclearColor = (5,5,5)
elif className == ('t2_segnet'):
    eitherColor = (2,2,2)
    desertColor = (2,2,2)
    grassColor = (2,2,2)
    unclearLandColor = (2,2,2)
    snowColor = (3,3,3)
    unclearSnowColor = (5,5,5)
    oceanColor = (1,1,1)
    cloudColor = (4,4,4)
    unclearColor = (5,5,5)
    

imgViz = buildColorMask(img_RGB, [
    (eitherMask, eitherColor),
    (desertMask, desertColor),
    (grassMask, grassColor),
    (unclearLandMask, unclearLandColor),
    (snowMask, snowColor),
    (unclearSnowMask, unclearSnowColor),
    (oceanMask, oceanColor),
    (cloudMask, cloudColor),
    (unclear, unclearColor)
], (0,0,0))

cv2.imwrite(sys.argv[3], cv2.cvtColor(imgViz, cv2.COLOR_RGB2BGR));
print "Finished"
