
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
import sys
import math
import time

import matplotlib.pyplot as plt
from Tkinter import *
import PIL
from PIL import ImageTk, Image


name = 'LetSat Camera Simulator'

RAD_EARTH = 6371000.
ALTITUDE =   650000.

def main():
    glutInit(sys.argv)
    global WINDOWED, SIZE
    WINDOWED = 0
    SIZE = 600
    
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(SIZE, SIZE)
    #glutInitWindowPosition(350, 200)
    glutCreateWindow(name)
    if not WINDOWED:
        glutHideWindow()
        fbo = glGenFramebuffers(1)
        color_buf = glGenRenderbuffers(1)
        depth_buf = glGenRenderbuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        
        
        glBindRenderbuffer(GL_RENDERBUFFER, color_buf)
        glRenderbufferStorage(GL_RENDERBUFFER,GL_RGBA8,SIZE,SIZE)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, color_buf)
        
        glBindRenderbuffer(GL_RENDERBUFFER, depth_buf)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, SIZE,SIZE)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_buf)
        
        #glBindFramebuffer(GL_FRAMEBUFFER, 0 )
        print glCheckFramebufferStatus(GL_FRAMEBUFFER)


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
    glutIdleFunc(displayscene)
    #glutSpecialFunc(special) # Called on key
    
    glMatrixMode(GL_PROJECTION)
    gluPerspective(fov, 1., ALTITUDE, RAD_EARTH + ALTITUDE) # fovy, aspect, near, far
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(RAD_EARTH + ALTITUDE, 0, 0, # Eye XYZ
              0, 0, 0,  # Center
              0, 0, RAD_EARTH)  # Up
    glPushMatrix()
    glutPostRedisplay()
    glutMainLoopEvent()
    tkMAIN()
    return

def tkMAIN():
    
    
    root=Tk()
    global canvas, SIZE
    canvas=Canvas(root, height=SIZE, width=SIZE)
    
    repack()
    canvas.pack(side = TOP, expand=True, fill=BOTH)
    
    root.bind('w', handleKeypress)
    root.bind('a', handleKeypress)
    root.bind('s', handleKeypress)
    root.bind('d', handleKeypress)
    
    root.mainloop()

def repack():
    displayscene()
    global canvas, SIZE, image, photo #Image and photo must be preserved so GC doesn't eat them
    image = getImage(SIZE,SIZE)
    photo = ImageTk.PhotoImage(image)
    item4 = canvas.create_image(SIZE/2,SIZE/2, image=photo)
    

def handleKeypress(event):
    print event.char
    key = event.char
    global earthTex, tex1, tex2
    global angleA, angleX
    shift = 0#not (glutGetModifiers() ^ GLUT_ACTIVE_SHIFT)
    incAmount = 1
    if shift:
        incAmount = 7.5
    if key == 'h':
        if earthTex == tex1:
            earthTex = tex2
        else:
            earthTex = tex1
    
    if key == 'w':
        angleX += incAmount
    if key == 's':
        angleX -= incAmount

    if key == 'a':
        angleA += incAmount
    if key == 'd':
        angleA -= incAmount

    repack()
        

fov = 141. # 141 is 1.8mm camera lens
angleX = 0
angleA = 0
def displayscene():
    global WINDOWED
    global sphere, angleA, angleX, fov, earthTex
    global RAD_EARTH
    
    print 'disp', angleA, angleX
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    glRotate(angleA,0,0,1)
    glRotate(angleX,math.sin(angleA/180.*3.1415),math.cos(angleA/180.*3.1415),0)
    glBindTexture(GL_TEXTURE_2D, earthTex)
    #         quadric       rad   slices   stacks
    gluSphere(sphere, RAD_EARTH,    360,     360) 
    
    glPopMatrix()
    if WINDOWED: 
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
    global WINDOWED
    if  not WINDOWED:
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        glReadBuffer(GL_COLOR_ATTACHMENT0)
    buff = glReadPixels(0, 0, width, height, GL_RGB, 
                             GL_UNSIGNED_BYTE)
    image = Image.frombytes(mode="RGB", size=(width, height), 
                             data=buff)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    return image



def display(image, wWidth, wHeight):
    root=Tk()
    canvas=Canvas(root, height=wHeight, width=wWidth)
    basewidth = wWidth
    wpercent = (basewidth / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    image = image.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(image)
    item4 = canvas.create_image(basewidth/2, basewidth/2, image=photo)

    canvas.pack(side = TOP, expand=True, fill=BOTH)
    root.mainloop()

if __name__ == '__main__':
    main()
