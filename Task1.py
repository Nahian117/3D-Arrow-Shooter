from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random

no_rain = random.randint(125,150)
r,g,b = 0.6, 0.8, 1
day = True
rain_dir = 0
raindrops = [[random.randint(0,1000),random.randint(0,600)] for i in range(no_rain)] #no of drop spawn from random point

def draw_rain():
    if day:
        glColor3f(0.3, 0.3, 1.0)
    else:
        glColor3f(0.8, 0.8, 1.0)
    glBegin(GL_LINES)
    # loop rain lines
    for i in raindrops:
        glVertex2f(i[0],i[1])
        glVertex2f(i[0]+rain_dir, i[1] - random.randint(20,50)) # change dir + dif lenght line
    glEnd()

def draw_points(x, y):
    glPointSize(8)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()
def draw_line(x1, y1, x2, y2, width=2):
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

def draw_triangle(x1, y1, x2, y2, x3, y3, width=2):
    glLineWidth(width)
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()

def setup_projection():
    glViewport(0, 0, 1000, 600)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 1000.0, 0.0, 600.0, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    #Draw bg square lower
    glColor3f(0,1,0)
    body = 0
    while body<1000:
        draw_line(body,0,body,350)
        body+=1
    # Draw bg square upper
    glColor3f(r,g,b)
    x = 0
    while x < 1000:
        draw_line(x, 350, x, 600)
        x += 1
    #grass
    glColor3f(0.5, 1, 0.3)
    x = 0
    while x<1000:
        draw_triangle(x,300,x+50,300,(x+x+50)//2,450)
        x+=50
    #roof
    glColor3f(1, 0, 0)
    draw_triangle(280,400,720,400,500,480)
    #lower bottom square
    glColor3f(0, 0, 1)
    lb = 295
    while lb<705:
        draw_line(lb,190,lb,200)
        lb+=1
    # house body
    glColor3f(1, 1, 1)
    c= 300
    while c<700:
        draw_line(c,200,c,400)
        c+=1
    #Door
    glColor3f(1, 0, 0)
    d = 450
    while d<550:
        draw_line(d,200,d,320)
        d+=1
    #Left window
    glColor3f(0, 0, 1)
    lw = 340
    while lw<400:
        draw_line(lw,270,lw,330)
        lw+=1
    #Right Window
    rw = 600
    while rw<660:
        draw_line(rw,270,rw,330)
        rw+=1
    #mid lines
    glColor3f(0,0,0)
    draw_line(370, 270,370,330)
    draw_line(340,300,400,300)
    draw_line(630,270,630,330)
    draw_line(600,300,660,300)
    draw_line(500,200,500,320)

    #door point
    glColor3f(0,0,0)
    draw_points(510,260)
    draw_rain() #rain
    glutSwapBuffers()

def rain_animation():
    global raindrops
    for i in raindrops:
        i[0] += rain_dir
        i[1] -= 15  # fall speed
        if i[1] < 0:
            i[1] = 600 #capping
            i[0] = random.randint(0, 1000)
    glutPostRedisplay()

def special_key_listener(key, x, y):
    global r,g,b,rain_dir
    if key == GLUT_KEY_UP:  # day
        r =max(0.0, r-0.05 )
        g = max(0.0, g-0.05)
        b = max(0.0, b-0.05)
        day = True
    elif key == GLUT_KEY_DOWN:  # night
        r =min(1.0, r+0.05 )
        g = min(1.0, g+0.05)
        b = min(1.0, b+0.05)
        day = False
    elif key == GLUT_KEY_LEFT:
        rain_dir-=.5
    elif key ==GLUT_KEY_RIGHT:
        rain_dir+=.5
    glutPostRedisplay()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(1000, 600)
    glutInitWindowPosition(200, 100)
    glutCreateWindow(b"OpenGL House")
    setup_projection()
    glutDisplayFunc(display)
    glutIdleFunc(rain_animation)
    glutSpecialFunc(special_key_listener)
    glutMainLoop()

if __name__ == "__main__":
    main()



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

