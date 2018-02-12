# Build Ground Truth from NASA Blue Marble Images
# v1.1
# Intended for use in OpenGL Simulator
# 29 Jan 2018 - v1.0 - Initial Implementation
# 12 Feb 2018 - v1.1 - Configurable dialation
# Chandler Griscom

import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys

dialationIters = 1

if len(sys.argv) < 3 or len(sys.argv) > 4:
    print "Usage: python2 BuildGroundTruth.py {src_img} {out_img} [dialations]"
    quit(1)

if len(sys.argv) == 4:
    dialationIters = int(sys.argv[3])

img_BGR = cv2.imread(sys.argv[1])
img_RGB = cv2.cvtColor(img_BGR, cv2.COLOR_BGR2RGB)
img_HSV = cv2.cvtColor(img_BGR, cv2.COLOR_BGR2HSV)

# Create Masks

def getMask(img, lowerBound, upperBound, dialationIters):
  lowerSpace = np.array(lowerBound, dtype = "uint8")
  upperSpace = np.array(upperBound, dtype = "uint8")

  mask = cv2.inRange(img, lowerSpace, upperSpace)

  if dialationIters > 0:
    mask = cv2.dilate(mask, np.ones((2,2), np.uint8), iterations=dialationIters);

  return mask

_, plts = plt.subplots(1, 1, figsize = (20,12))

# Snow is low-sat, high-value
snowMask = getMask(img_HSV, [0, 0, 160], [180, 30, 255], dialationIters)  # Unsaturated regions
# ^^ good and validated

# Ocean is high-sat, low value, blue
oceanMask = getMask(img_HSV, [60, 200, 0], [170, 255, 120], dialationIters)
# ^^ not bad

# Grass
grassMask = getMask(img_HSV, [35, 75, 0], [80, 255, 200], dialationIters)

# Desert
desertMask = getMask(img_HSV, [0, 50, 100], [40, 255, 220], dialationIters)

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
    colorMask = overwriteWithMask(colorMask,getColorMask(origImage,pair[0],pair[1]), pair[0])
  return colorMask

unclearLandMask = cv2.bitwise_and(grassMask, desertMask)
unclearSnowMask = cv2.bitwise_and(cv2.bitwise_or(grassMask, desertMask), snowMask)
allLand = cv2.bitwise_or(cv2.bitwise_or(grassMask, desertMask), snowMask)
unclear = cv2.bitwise_and(allLand, oceanMask)

imgViz = buildColorMask(img_RGB, [
    (eitherMask, (255,255,0)),
    (desertMask, (255,0,0)),
    (grassMask, (0,255,0)),
    (unclearLandMask, (255,255,0)),
    (snowMask, (255,255,255)),
    (unclearSnowMask, (127,127,127)),
    (oceanMask, (0,0,255)),
    (unclear, (0,0,0))
], (0,0,0))

cv2.imwrite(sys.argv[2], cv2.cvtColor(imgViz, cv2.COLOR_RGB2BGR));
print "Finished"
