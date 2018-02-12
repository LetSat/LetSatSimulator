# Texture Generation Script for OpenGL Simulator Sources
# 12 Feb 2018 - Initial Implementation

# Chandler Griscom

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


mkdir textures
for i in 0{1..9} {10..12};
do
echo Downloading month $i
wget -O textures/tmp.png https://eoimages.gsfc.nasa.gov/images/imagerecords/$(( dirlist[i]-dirlist[i]%1000 ))/$(( dirlist[i] ))/world.2004$i.3x21600x10800.png
echo Decompressing month $i - 16384x8192
convert -resize 16384x8192 textures/tmp.png textures/earth_16384_$i.tga
rm textures/tmp$i.png
done
echo Completed
