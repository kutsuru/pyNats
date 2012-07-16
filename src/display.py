from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def init():
    glClearColor(1.0,1.0,1.0,0.0)
    glColor3f(0.0,0.0, 0.0)
    glPointSize(4.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0,640.0,0.0,480.0)


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    # Do something
    glEnd()
    glFlush()

if __name__ == '__main__':
    glutInit()
    glutInitWindowSize(512, 512)
    glutCreateWindow("Test")
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutDisplayFunc(display)
    init()
    glutMainLoop()
