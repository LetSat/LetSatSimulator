#!/usr/bin/env python2

# LetSat OpenGL Renderer
# 14 Feb 2018 - v0.1 - Initial Implementation
# v0.1
# Chandler Griscom

from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
import sys
import math
import time

from Tkinter import *
from PIL import ImageTk

import numpy
import cv2
import PIL
from PIL import Image
import argparse

Image.MAX_IMAGE_PIXELS = 16384*8192

name = 'LetSat OpenGL Rendering'

RAD_EARTH = 6371000.
angleX = 0
angleA = 0

def main():
    parser = argparse.ArgumentParser(description='Export an OpenGL rendering with the given parameters and texture.')
    
    parser.add_argument('lat', type=float, 
                    help='Latitude of the satellite (-90.0 to 90.0)')
    
    parser.add_argument('long', type=float, 
                    help='Longitude of the satellite (-180.0 to 180.0)')
    
    parser.add_argument('alt', type=float, 
                    help='Altitude of the satellite in km')
    
    parser.add_argument('--size', type=int, default=1024,
                    help='Image size, default 1024')
    
    parser.add_argument('--fov', type=float, default=141,
                    help='Field of view angle, default 141')
    
    parser.add_argument('texture', type=str, 
                    help='Path to the earth texture file')
    
    parser.add_argument('outfile', type=str, 
                    help='Path to the output image')
    
    global args
    args = parser.parse_args()
    
    global angleA, angleX
    angleX = args.lat          # Set latitude
    angleA = -(args.long - 90) # Set longitude
    args.alt *= 1000           # Convert to meters
    
    glutInit(sys.argv)
    FRAMEBUFFER = 1
    
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(args.size, args.size)
    #glutInitWindowPosition(350, 200)
    glutCreateWindow(name)
    if FRAMEBUFFER:
        glutHideWindow()
        fbo = glGenFramebuffers(1)
        color_buf = glGenRenderbuffers(1)
        depth_buf = glGenRenderbuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        
        
        glBindRenderbuffer(GL_RENDERBUFFER, color_buf)
        glRenderbufferStorage(GL_RENDERBUFFER,GL_RGBA8,args.size,args.size)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, color_buf)
        
        glBindRenderbuffer(GL_RENDERBUFFER, depth_buf)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, args.size,args.size)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_buf)
        

    glClearColor(0., 0., 0., 1.)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LIGHTING)
    lightZeroPosition = [1.,1.,1., 1.]
    lightZeroColor = [0.8, 1.0, 0.8, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)
    
    glTranslatef(0, 0, 0)
    
    global RAD_EARTH
    global earthTex
    earthTex = loadtexture(args.texture)
    
    global sphere
    sphere = gluNewQuadric() # Create A Pointer To The Quadric Object
    
    gluQuadricNormals(sphere, GL_SMOOTH)
    gluQuadricTexture(sphere, GL_TRUE)
    glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    
    glutDisplayFunc(displayscene) # VCalled once
    glutIdleFunc(displayscene)
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(args.fov, 1., args.alt, RAD_EARTH + args.alt) # fovy, aspect, near, far
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(RAD_EARTH + args.alt, 0, 0, # Eye XYZ
              0, 0, 0,  # Center
              0, 0, RAD_EARTH)  # Up
    glPushMatrix()
    glutPostRedisplay()
    glutMainLoopEvent()
    displayscene()
    getImage(args.size,args.size)
    return

def displayscene():
    global sphere, angleA, angleX, fov, earthTex
    global RAD_EARTH
    
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    glRotate(angleA,0,0,1)
    glRotate(angleX,math.sin(math.radians(angleA)),math.cos(math.radians(angleA)),0)
    glBindTexture(GL_TEXTURE_2D, earthTex)
    #         quadric       rad   slices   stacks
    gluSphere(sphere, RAD_EARTH,    360,     360) 
    
    glPopMatrix()
    return

def loadtexture(fileImg):
    glEnable(GL_TEXTURE_2D)
    image = Image.open(fileImg)

    ix = image.size[0]
    iy = image.size[1]
    image = image.tobytes("raw", "RGBX", 0, -1)
    textID  = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textID)

    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    return textID

def getImage(width, height):
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    glReadBuffer(GL_COLOR_ATTACHMENT0)
    buff = glReadPixels(0, 0, width, height, GL_RGB, 
                             GL_UNSIGNED_BYTE)
    image = Image.frombytes(mode="RGB", size=(width, height), 
                             data=buff)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    
    image = performCVOps(image)
    
    return image

def performCVOps(pilImage):
    global args
    opencvImage = numpy.array(pilImage)
    cv2.imwrite(args.outfile, cv2.cvtColor(opencvImage, cv2.COLOR_BGR2RGB))
    return Image.fromarray(opencvImage)

if __name__ == '__main__':
    main()
