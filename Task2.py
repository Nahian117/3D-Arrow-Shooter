from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import time

blinking = False
last_blink_time = 0
blink_state = False
ball_speed = 0.03
temp = ball_speed
w_wid = 1000
w_ht = 600
ball_x,ball_y = 0,0
point_list = []
r,g,b = 0,0,0
freez = False
default_rgb =[]

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    for x, y,r,g,b,dx,dy in point_list:
        draw_points(x,y,r,g,b)
    glutSwapBuffers()


def draw_points(x, y,r,g,b):
    glPointSize(5)
    glBegin(GL_POINTS)
    glColor3f(r, g, b)
    glVertex2f(x, y)
    glEnd()

def setup_projection():
    glViewport(0, 0, 1000, 600)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 1000.0, 0.0, 600.0, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)

def animation():
    global w_ht,w_wid, ball_speed, last_blink_time, blink_state, blinking
    for i in range(len(point_list)):
        x,y,r,g,b,dx,dy= point_list[i]
        if x>=w_wid or x<=0:
            dx*=-1
        if y>=w_ht or y<=0:
            dy*=-1
        x = (x+dx*ball_speed)
        y = (y+dy*ball_speed)
        point_list[i] = [x, y, r, g, b,dx,dy]
    if blinking:
        current_time = time.time()
        if current_time - last_blink_time >= 1:
            blink_state = not blink_state
            last_blink_time = current_time

        for i in range(len(point_list)):
            x, y, r, g, b, dx, dy = point_list[i]
            if blink_state:
                r, g, b = 0, 0, 0
            else:
                for j in range(len(default_rgb)):
                    r,g,b = default_rgb[i]
            point_list[i] = [x, y, r, g, b, dx, dy]

    glutPostRedisplay()

def special_key_listener(key, x, y):
    global ball_speed
    if key == GLUT_KEY_UP:
        ball_speed+=0.01
    elif key == GLUT_KEY_DOWN:
        ball_speed= max(0.0, ball_speed-0.01)

    glutPostRedisplay()

def keyboard_listener(key, x, y):
    global ball_speed ,freez ,temp
    if key == b' ' and  freez == False :
        ball_speed = 0
        freez = True
    elif key==b' ' and freez:
        ball_speed = temp
        freez = False
    glutPostRedisplay()

def mouse_listener(button, state, x, y):
    global ball_x,ball_y ,r,g,b,blinking
    r = round(random.random(), 1)
    g = round(random.random(), 1)
    b = round(random.random(), 1)
    default_rgb.append([r,g,b])
    direction = [(1, 1), (1, -1), (-1, -1), (-1, 1)]  # diagonal directions
    dx, dy = random.choice(direction)
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        ball_x, ball_y = x,600-y
        point_list.append([ball_x,ball_y,r,g,b,dx,dy])
    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        blinking = not blinking


def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(1000, 600)
    glutInitWindowPosition(200, 100)
    glutCreateWindow(b"OpenGL Dots")
    setup_projection()
    glutDisplayFunc(display)
    glutIdleFunc(animation)
    glutSpecialFunc(special_key_listener)
    glutKeyboardFunc(keyboard_listener)
    glutMouseFunc(mouse_listener)
    glutMainLoop()

if __name__ == "__main__":
    main()

