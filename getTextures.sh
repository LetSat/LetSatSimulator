#Jan
#https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73938/world.200401.3x21600x10800.png
#Feb
#https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73967/world.200402.3x21600x10800.png
#Mar
#https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73992/world.200403.3x21600x10800.png
#Apr
#https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74017/world.200404.3x21600x10800.png
#May
#https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74042/world.200405.3x21600x10800.png
#Jun
#
#Jul
#
#Aug
#
#Sep
#
#Oct
#
#Nov
#
#Dec
#
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
##April
#wget -O textures/tmp.png https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74017/world.200404.3x21600x10800.png
#convert -resize 16384x8192 textures/tmp.png april_hi.tga
#rm textures/tmp.png
for i in 0{1..9} {10..12};
do
echo Downloading month $i
wget -O textures/tmp.png https://eoimages.gsfc.nasa.gov/images/imagerecords/$(( dirlist[i]-dirlist[i]%1000 ))/$(( dirlist[i] ))/world.2004$i.3x21600x10800.png
#echo Decompressing month $i - 21600x10800
#convert textures/tmp.png textures/earth_21600_$i.tga
echo Decompressing month $i - 16384x8192
convert textures/tmp.png textures/earth_16384_$i.tga
rm textures/tmp.png
done
