from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
win_h, win_w = 750,500
point_size = 2.5

#Catcher Bar
cat_h= 12
cat_w= 120
cx,cy = win_w//2, 40
catcher_speed = 10 #change if the system is fast or slow !!!!!!!!!
cheat_speed = 2 #change if the system is fast or slow !!!!!!!!!
catcher_color = (1,1,1)
# diamond
diamond_x = random.randint(60, win_w - 60)
diamond_y = win_h - 200
diamond_size = 18
diamond_speed = 2 #change if the system is fast or slow !!!!!!!!!
diamond_r = random.random()
diamond_g = random.random()
diamond_b = random.random()
btn_w = 60
btn_h = 40
btn_restart = (0, win_h - btn_h, btn_w, btn_h)               # top-left
btn_playpause = (win_w // 2 - btn_w // 2, win_h - btn_h, btn_w, btn_h)  # top-center
btn_quit = (win_w - btn_w , win_h - btn_h, btn_w, btn_h)  # top-right
score = 0
play = True
game_over = False
cheat_mode = False
#Zone Algo
def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    adx = abs(dx)
    ady = abs(dy)
    if adx >= ady:
        if dx >= 0 and dy >= 0:
            return 0
        if dx >= 0 and dy < 0:
            return 7
        if dx < 0 and dy >= 0:
            return 3
        return 4
    else:
        if dx >= 0 and dy >= 0:
            return 1
        if dx >= 0 and dy < 0:
            return 6
        if dx < 0 and dy >= 0:
            return 2
        return 5

def to_zone0(x, y, zone):
    if zone == 0:
        return x, y
    if zone == 1:
        return y, x
    if zone == 2:
        return y, -x
    if zone == 3:
        return -x, y
    if zone == 4:
        return -x, -y
    if zone == 5:
        return -y, -x
    if zone == 6:
        return -y, x
    if zone == 7:
        return x, -y

def from_zone0(x, y, zone):
    if zone == 0:
        return x, y
    if zone == 1:
        return y, x
    if zone == 2:
        return -y, x
    if zone == 3:
        return -x, y
    if zone == 4:
        return -x, -y
    if zone == 5:
        return -y, -x
    if zone == 6:
        return y, -x
    if zone == 7:
        return x, -y

def plot_pixel(x, y, r, g, b):
    glColor3f(r, g, b)
    glBegin(GL_POINTS)
    glVertex2i(int(x), int(y))
    glEnd()

def midpoint_line(x1, y1, x2, y2, r, g, b):

    if x1 == x2 and y1 == y2:
        plot_pixel(x1, y1, r, g, b)
        return

    zone = find_zone(x1, y1, x2, y2)
    x1z, y1z = to_zone0(x1, y1, zone)
    x2z, y2z = to_zone0(x2, y2, zone)


    if x1z > x2z:
        x1z, x2z = x2z, x1z
        y1z, y2z = y2z, y1z

    dx = x2z - x1z
    dy = y2z - y1z

    d_init= 2 * dy - dx
    del_E = 2 * dy
    del_NE = 2 * (dy - dx)

    x = x1z
    y = y1z

    while x <= x2z:
        rx, ry = from_zone0(x, y, zone)
        plot_pixel(rx, ry, r, g, b)
        if d_init > 0:
            d_init += del_NE
            y += 1
        else:
            d_init += del_E
        x += 1

#Drawing
def draw_catcher(x, y, w, h, r, g, b):
    x0 = int(x - w)
    x1 = int(x + w)
    y0 = int(y - h)
    y1 = int(y + h)
    midpoint_line(x0, y0, x1, y0, r, g, b)
    midpoint_line(x1, y0, x1, y1, r, g, b)
    midpoint_line(x1, y1, x0, y1, r, g, b)
    midpoint_line(x0, y1, x0, y0, r, g, b)

def draw_diamond(x, y, size, r, g, b):
    top = (x, y + size)
    right = (x + size, y)
    bottom = (x, y - size)
    left = (x - size, y)
    midpoint_line(top[0], top[1], right[0], right[1], r, g, b)
    midpoint_line(right[0], right[1], bottom[0], bottom[1], r, g, b)
    midpoint_line(bottom[0], bottom[1], left[0], left[1], r, g, b)
    midpoint_line(left[0], left[1], top[0], top[1], r, g, b)

def has_collided(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return (x1 < x2 + w2 and x1 + w1 > x2 and
            y1 < y2 + h2 and y1 + h1 > y2)
def reset_game():
    global score, diamond_x, diamond_y, diamond_speed_frame, diamond_r, diamond_g, diamond_b
    global game_over, play, catcher_color
    catcher_color=(1,1,1)
    score = 0
    diamond_x = random.randint(60, win_w - 60)
    diamond_y = win_h - 60
    diamond_r = random.random()
    diamond_g = random.random()
    diamond_b = random.random()
    game_over = False
    play = True
    print("Restart")
def keyboard(key, x, y):
    global cheat_mode
    if key == b'c' or key == b'C':
        cheat_mode = not cheat_mode
        print("Cheat mode:", "ON" if cheat_mode else "OFF")
def special_input(key, x, y):
    global cx
    if not play or game_over:
        return
    if key == GLUT_KEY_LEFT:
        cx -= catcher_speed
        if cx - cat_w // 2 < 0:
            cx = cat_w // 2
    elif key == GLUT_KEY_RIGHT:
        cx += catcher_speed
        if cx + cat_w // 2 > win_w:
            cx = win_w - cat_w // 2

def mouse_click(button, state, mx, my):
    if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN:
        return
    rx = mx
    ry = win_h - my

    bx, by, bw, bh = btn_restart
    if bx <= rx <= bx + bw and by <= ry <= by + bh:
        reset_game()
        return

    bx, by, bw, bh = btn_playpause
    if bx <= rx <= bx + bw and by <= ry <= by + bh:
        global play
        play = not play
        print("Paused" if not play else "Resumed")
        return

    bx, by, bw, bh = btn_quit
    if bx <= rx <= bx + bw and by <= ry <= by + bh:
        print("Game Over. Score Earned:", score)
        glutLeaveMainLoop()
        return

def update():
    global diamond_x, diamond_y, score, game_over, cx, diamond_r, diamond_g, diamond_b
    global catcher_color

    if not play or game_over:
        glutPostRedisplay()
        return
    diamond_y -= diamond_speed
    if cheat_mode:
        dx = diamond_x - cx
        if dx != 0:
            move = cheat_speed if abs(dx) > cheat_speed else abs(dx)
            cx += move if dx > 0 else -move
            if cx - cat_w // 2 < 0:
                cx = cat_w // 2
            if cx + cat_w // 2 > win_w:
                cx = win_w - cat_w // 2

    if diamond_y - diamond_size <= 0:
        game_over = True
        catcher_color = (1, 0, 0)
        print("Game Over. Score:", score)
        glutPostRedisplay()
        return

    # collision test (AABB)
    diamond_box = (diamond_x - diamond_size, diamond_y - diamond_size, diamond_size * 2, diamond_size * 2)
    catcher_box = (cx - cat_w // 2, cy - cat_h // 2, cat_w, cat_h)

    if has_collided(diamond_box, catcher_box):
        score += 1
        catcher_color = (1,1,1)
        print("Score:", score)
        diamond_x = random.randint(60, win_w - 60)
        diamond_y = win_h - 60
        diamond_r = random.random()
        diamond_g = random.random()
        diamond_b = random.random()

    glutPostRedisplay()

def game_replay():
    # restart icon
    bx, by, bw, bh = btn_restart
    cx = bx + bw // 2
    cy = by + bh // 2
    midpoint_line(cx + 12, cy + 10, cx - 8, cy, 0.0, 0.7, 0.7)
    midpoint_line(cx + 12, cy - 10, cx - 8, cy, 0.0, 0.7, 0.7)
    midpoint_line(cx + 12, cy + 10, cx + 12, cy - 10, 0.0, 0.7, 0.7)

    # play/pause icon
    bx, by, bw, bh = btn_playpause
    cx = bx + bw // 2
    cy = by + bh // 2
    # play/pause icon
    bx, by, bw, bh = btn_playpause
    cx = bx + bw // 2
    cy = by + bh // 2
    if play:
        midpoint_line(cx - 6, cy + 10, cx - 6, cy - 10, 1.0, 0.6, 0.0)
        midpoint_line(cx + 6, cy + 10, cx + 6, cy - 10, 1.0, 0.6, 0.0)
    else:
        midpoint_line(cx - 8, cy - 12, cx + 10, cy, 1.0, 0.6, 0.0)
        midpoint_line(cx + 10, cy, cx - 8, cy + 12, 1.0, 0.6, 0.0)
        midpoint_line(cx - 8, cy - 12, cx - 8, cy + 12, 1.0, 0.6, 0.0)
    # quit icon
    bx, by, bw, bh = btn_quit
    cx = bx + bw // 2
    cy = by + bh // 2
    midpoint_line(cx - 10, cy - 10, cx + 10, cy + 10, 0.9, 0.1, 0.1)
    midpoint_line(cx - 10, cy + 10, cx + 10, cy - 10, 0.9, 0.1, 0.1)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    game_replay()
    draw_diamond(int(diamond_x), int(diamond_y), diamond_size, diamond_r, diamond_g, diamond_b)
    draw_catcher(int(cx), int(cy), cat_w // 2, cat_h // 2,catcher_color[0],catcher_color[1],catcher_color[2])
    glutSwapBuffers()

def setup_projection():
    glViewport(0, 0, win_w,win_h )
    glPointSize(point_size)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, win_w, 0, win_h)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGB)
    glutInitWindowSize(win_w, win_h)
    glutInitWindowPosition(1000, 0)
    glutCreateWindow(b"Catch The Diamonds")
    setup_projection()
    glutDisplayFunc(display)
    glutIdleFunc(update)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_input)
    glutMouseFunc(mouse_click)
    print("Controls: Left/Right to move the Catcher. C for toggle cheat")
    glutMainLoop()

if __name__ == '__main__':
    main()
