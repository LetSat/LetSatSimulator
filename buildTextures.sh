#!/bin/bash
# Texture Generation Script for OpenGL Simulator Sources
# 12 Feb 2018 - v0.1 - Initial Implementation
# 12 Feb 2018 - v0.2 - Add ground truth generation, switch to BMP
# v0.2
# Chandler Griscom

DIALATIONS=2  # For ground truth

# NASA Image Source Directories
dirlist[ 1]=73938
dirlist[ 2]=73967
dirlist[ 3]=73992
dirlist[ 4]=74017
dirlist[ 5]=74042
dirlist[ 6]=76487
dirlist[ 7]=74092
dirlist[ 8]=74117
dirlist[ 9]=74142
dirlist[10]=74167
dirlist[11]=74192
dirlist[12]=74218

# Create
mkdir build_textures


for i in 0{1..9} {10..12}; do
  echo Downloading month $i
  wget -O build_textures/tmp$i.png https://eoimages.gsfc.nasa.gov/images/imagerecords/$(( dirlist[10#$i]-dirlist[10#$i]%1000 ))/$(( dirlist[10#$i] ))/world.2004$i.3x21600x10800.png
  echo Decompressing month $i - 16384x8192
  convert -resize 16384x8192 build_textures/tmp$i.png build_textures/earth_16384_$i.bmp
  echo Building GT for month $i - 16384x8192
  python2 BuildGroundTruth.py build_textures/earth_16384_$i.bmp build_textures/gt_16384_$i.bmp $DIALATIONS
  rm build_textures/tmp$i.png
done
echo Completed
