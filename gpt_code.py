from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random

# ========= GLOBAL VARIABLES =========
num_drops = 120
raindrops = [[random.randint(0, 1000), random.randint(0,600)] for _ in range(num_drops)]  # all start from top
rain_dx = 0                # rain direction tilt
sky_r, sky_g, sky_b = 0.4, 0.7, 1.0   # default (day sky)
is_day = True

# ========= BASIC DRAW FUNCTIONS =========
def draw_point(x, y):
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def draw_line(x1, y1, x2, y2, width=1):
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

def draw_triangle(x1, y1, x2, y2, x3, y3):
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()

# ========= SETUP PROJECTION =========
def setup_projection():
    glViewport(0, 0, 1000, 600)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 1000.0, 0.0, 600.0, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)

# ========= DISPLAY FUNCTION =========
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # -------- SKY BACKGROUND (drawn using lines) --------
    glColor3f(sky_r, sky_g, sky_b)
    x = 0
    while x < 1000:
        draw_line(x, 350, x, 600)
        x += 1

    # -------- GROUND (green) --------
    glColor3f(0, 1, 0)
    g = 0
    while g < 1000:
        draw_line(g, 0, g, 350)
        g += 1

    # -------- GRASS TRIANGLES --------
    glColor3f(0.4, 0.9, 0.2)
    gx = 0
    while gx < 1000:
        draw_triangle(gx, 300, gx + 50, 300, (gx + gx + 50) // 2, 450)
        gx += 50

    # -------- HOUSE --------
    # roof
    glColor3f(1, 0, 0)
    draw_triangle(280, 400, 720, 400, 500, 480)

    # lower bottom
    glColor3f(0, 0, 1)
    b = 295
    while b < 705:
        draw_line(b, 190, b, 200)
        b += 1

    # house body
    glColor3f(1, 1, 1)
    c = 300
    while c < 700:
        draw_line(c, 200, c, 400)
        c += 1

    # door
    glColor3f(1, 0, 0)
    d = 450
    while d < 550:
        draw_line(d, 200, d, 320)
        d += 1

    # left window
    glColor3f(0, 0, 1)
    lw = 340
    while lw < 400:
        draw_line(lw, 270, lw, 330)
        lw += 1

    # right window
    rw = 600
    while rw < 660:
        draw_line(rw, 270, rw, 330)
        rw += 1

    # window crosses & door middle
    glColor3f(0, 0, 0)
    draw_line(370, 270, 370, 330)
    draw_line(340, 300, 400, 300)
    draw_line(630, 270, 630, 330)
    draw_line(600, 300, 660, 300)
    draw_line(500, 200, 500, 320)

    # door knob
    glColor3f(0, 0, 0)
    glPointSize(5)
    draw_point(510, 260)

    # -------- RAIN (as lines) --------
    if is_day:
        glColor3f(0.3, 0.3, 1.0)
    else:
        glColor3f(0.8, 0.8, 1.0)

    glLineWidth(1)
    glBegin(GL_LINES)
    for drop in raindrops:
        glVertex2f(drop[0], drop[1])
        glVertex2f(drop[0] + rain_dx, drop[1] - random.randint(20,50))
    glEnd()

    glutSwapBuffers()

# ========= ANIMATION =========
def animate():
    global raindrops
    for drop in raindrops:
        drop[0] += rain_dx
        drop[1] -= 15  # fall speed
        if drop[1] < 0:  # reached ground
            drop[1] = 600           # reset to top
            drop[0] = random.randint(0, 1000)  # random horizontal position
    glutPostRedisplay()

# ========= KEYBOARD INPUT =========
def special_key_listener(key, x, y):
    global rain_dx
    if key == GLUT_KEY_LEFT:
        rain_dx -= 0.3
    elif key == GLUT_KEY_RIGHT:
        rain_dx += 0.3
    glutPostRedisplay()

def keyboard_listener(key, x, y):
    global sky_r, sky_g, sky_b, is_day

    if key == b'd':  # day
        sky_r = min(0.4, sky_r + 0.05)
        sky_g = min(0.7, sky_g + 0.05)
        sky_b = min(1.0, sky_b + 0.05)
        is_day = True

    elif key == b'n':  # night
        sky_r = max(0.0, sky_r - 0.05)
        sky_g = max(0.0, sky_g - 0.05)
        sky_b = max(0.2, sky_b - 0.05)
        is_day = False

    glutPostRedisplay()

# ========= MAIN =========
def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(1000, 600)
    glutInitWindowPosition(200, 100)
    glutCreateWindow(b"OpenGL House in Rainfall (Top Rain Start)")
    setup_projection()
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboard_listener)
    glutSpecialFunc(special_key_listener)
    glutMainLoop()

if __name__ == "__main__":
    main()
