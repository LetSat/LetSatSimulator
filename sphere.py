
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import math

import matplotlib.pyplot as plt
from Tkinter import *
import PIL
from PIL import ImageTk, Image


name = 'LetSat Camera Simulator'

RAD_EARTH = 6371000.
ALTITUDE =   650000.

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(600, 600)
    #glutInitWindowPosition(350, 200)
    glutCreateWindow(name)

    glClearColor(0., 0., 0., 1.)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    lightZeroPosition = [1.,1.,1., 1.]
    lightZeroColor = [0.8, 1.0, 0.8, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)
    
    
    #color = [1.0, 0.0, 0.0, 1.0]
    #glMaterialfv(GL_FRONT, GL_DIFFUSE, color)
    glTranslatef(0, 0, 0)
    
    global RAD_EARTH, ALTITUDE
    global earthTex, tex1, tex2
    tex1 = loadtexture('earth.jpg')
    tex2 = loadtexture('earth_hi.jpg')
    earthTex = tex1
    
    global sphere
    sphere = gluNewQuadric()                # Create A Pointer To The Quadric Object
    
    gluQuadricNormals(sphere, GL_SMOOTH)
    gluQuadricTexture(sphere, GL_TRUE)
    glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    
    glutDisplayFunc(displayscene) # VCalled once
    glutSpecialFunc(special) # Called on key
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(fov, 1., ALTITUDE, RAD_EARTH + ALTITUDE) # fovy, aspect, near, far
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(RAD_EARTH + ALTITUDE, 0, 0, # Eye XYZ
              0, 0, 0,  # Center
              0, 0, RAD_EARTH)  # Up
    glPushMatrix()
    glutMainLoop()
    return

# Keyboard controller for sphere
def special(key, x, y):
        global earthTex, tex1, tex2
        global angleA, angleX
        shift = not (glutGetModifiers() ^ GLUT_ACTIVE_SHIFT)
        incAmount = 1
        if shift:
            incAmount = 7.5
        if key == GLUT_KEY_F1:
            if earthTex == tex1:
                earthTex = tex2
            else:
                earthTex = tex1
        if key == GLUT_KEY_F2:
            image = getImage(640,640)
            display(image)
            
        if key == GLUT_KEY_UP:
            angleX += incAmount
        if key == GLUT_KEY_DOWN:
            angleX -= incAmount

        if key == GLUT_KEY_LEFT:
            angleA += incAmount
        if key == GLUT_KEY_RIGHT:
            angleA -= incAmount

        glutPostRedisplay()

fov = 141. # 141 is 1.8mm camera lens
angleX = 0
angleA = 0
def displayscene():
    
    global sphere, angleA, angleX, fov, earthTex
    global RAD_EARTH
    
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    
    
    
    glRotate(angleA,0,0,1)
    glRotate(angleX,math.sin(angleA/180.*3.1415),math.cos(angleA/180.*3.1415),0)
    glBindTexture(GL_TEXTURE_2D, earthTex)
    #         quadric       rad   slices   stacks
    gluSphere(sphere, RAD_EARTH,    360,     360) 
    
    glPopMatrix()
    glutSwapBuffers()
    return

def loadtexture(fileImg):
    """
    Defines a global texture for applying
    in any time as fucntion
    :return:
    """
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
    buff = glReadPixels(0, 0, width, height, GL_RGB, 
                             GL_UNSIGNED_BYTE)
    image = Image.frombytes(mode="RGB", size=(width, height), 
                             data=buff)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    return image

def display(image):
    root=Tk()
    canvas=Canvas(root, height=640, width=640)
    basewidth = 640
    wpercent = (basewidth / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    image = image.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)
    item4 = canvas.create_image(basewidth/2, basewidth/2, image=photo)

    canvas.pack(side = TOP, expand=True, fill=BOTH)
    root.mainloop()

if __name__ == '__main__':
    main()
