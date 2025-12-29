from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

camera_pos = [0, 500, 500]
camera_angle = 0
first_person = False
fovY = 120
GRID_LENGTH = 600
px, py = 0, 0
g_angle = 0
life = 5
game_over = False
bullets = []
miss_count = 0
cheat_mode = False
auto_follow = False
enemies = []
e_count = 5
b_speed = 1.5
e_speed = 0.1
frame = 0
score = 0

def spawn_enemy():
    x = random.choice([-1, 1]) * random.randint(200, GRID_LENGTH)
    y = random.choice([-1, 1]) * random.randint(200, GRID_LENGTH)
    return [x, y, 1.0, 0.01]
for _ in range(e_count):
    enemies.append(spawn_enemy())

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 0)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_grid():
    tile = 100
    for x in range(-GRID_LENGTH, GRID_LENGTH, tile):
        for y in range(-GRID_LENGTH, GRID_LENGTH, tile):
            if ((x + y) // tile) % 2 == 0:
                glColor3f(0.75, 0.6, 0.9)
            else:
                glColor3f(1, 1, 1)
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + tile, y, 0)
            glVertex3f(x + tile, y + tile, 0)
            glVertex3f(x, y + tile, 0)
            glEnd()

def draw_walls():
    h = 80
    glColor3f(0, 0, 1)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, h)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, h)
    glEnd()
    glColor3f(0, 1, 1)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, h)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, h)
    glEnd()
    glColor3f(0, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, h)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, h)
    glEnd()
    glColor3f(1, 1, 0)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, h)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, h)
    glEnd()

def draw_player():
    glPushMatrix()
    glTranslatef(px, py, 0)
    glRotatef(g_angle, 0, 0, 1)
    glColor3f(1.0, 0.85, 0.75)
    glPushMatrix()
    glTranslatef(0, 0, 30)
    glScalef(1, 0.6, 1.5)
    glutSolidCube(40)
    glPopMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(25, 0, 40)
    glScalef(1.5, 0.2, 0.2)
    glutSolidCube(20)
    glPopMatrix()
    glPopMatrix()
def draw_bullets():
    glColor3f(1, 0, 0)
    for b in bullets:
        glPushMatrix()
        glTranslatef(b[0], b[1], 20)
        glutSolidCube(10)
        glPopMatrix()

def draw_enemies():
    for e in enemies:
        glPushMatrix()
        glTranslatef(e[0], e[1], 25)
        glScalef(e[2], e[2], e[2])
        glColor3f(1, 0, 0)
        gluSphere(gluNewQuadric(), 25, 20, 20)
        glColor3f(0, 0, 0)
        gluSphere(gluNewQuadric(), 10, 20, 20)
        glPopMatrix()

def keyboardListener(key, x, y):
    global g_angle, px, py, cheat_mode, auto_follow
    global life, miss_count, bullets, enemies, game_over, score
    if game_over and key == b'r':
        px, py = 0, 0
        g_angle = 0
        life = 5
        score = 0
        miss_count = 0
        bullets.clear()
        enemies.clear()
        for _ in range(e_count):
            enemies.append(spawn_enemy())
        game_over = False
        return
    move_angle = g_angle
    if cheat_mode and not auto_follow:
        move_angle = camera_angle
    step = 10
    dx = math.cos(math.radians(move_angle)) * step
    dy = math.sin(math.radians(move_angle)) * step
    limit = GRID_LENGTH - 25
    if key == b'w':
        if -limit < px + dx < limit: px += dx
        if -limit < py + dy < limit: py += dy
    if key == b's':
        if -limit < px - dx < limit: px -= dx
        if -limit < py - dy < limit: py -= dy
    if not cheat_mode:
        if key == b'a': g_angle += 5
        if key == b'd': g_angle -= 5
    if key == b'c': cheat_mode = not cheat_mode
    if key == b'v': auto_follow = not auto_follow

def specialKeyListener(key, x, y):
    global camera_angle, camera_pos
    if key == GLUT_KEY_LEFT: camera_angle += 2
    if key == GLUT_KEY_RIGHT: camera_angle -= 2
    if key == GLUT_KEY_UP: camera_pos[2] += 10
    if key == GLUT_KEY_DOWN: camera_pos[2] -= 10

def mouseListener(button, state, x, y):
    global bullets, first_person
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        bullets.append([px, py, g_angle])
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person = not first_person

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person:
        look_angle = g_angle if (cheat_mode and auto_follow) else (g_angle if not cheat_mode else camera_angle)
        if cheat_mode and not auto_follow: look_angle = camera_angle
        cx = px - math.cos(math.radians(look_angle)) * 50
        cy = py - math.sin(math.radians(look_angle)) * 50
        gluLookAt(cx, cy, 80, px, py, 40, 0, 0, 1)
    else:
        x = math.cos(math.radians(camera_angle)) * 500
        y = math.sin(math.radians(camera_angle)) * 500
        gluLookAt(x, y, camera_pos[2], 0, 0, 0, 0, 0, 1)

def idle():
    global bullets, miss_count, life, game_over, g_angle, frame, score
    if game_over: return
    frame += 1
    for b in bullets[:]:
        b[0] += math.cos(math.radians(b[2])) * b_speed
        b[1] += math.sin(math.radians(b[2])) * b_speed
        if abs(b[0]) > GRID_LENGTH or abs(b[1]) > GRID_LENGTH:
            bullets.remove(b)
            if not cheat_mode:
                miss_count += 1
    for e in enemies:
        dx = px - e[0]
        dy = py - e[1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            e[0] += (dx / dist) * e_speed
            e[1] += (dy / dist) * e_speed
        e[2] += e[3]
        if e[2] > 1.2 or e[2] < 0.8: e[3] *= -1
        if dist < 40:
            life -= 1
            enemies.remove(e)
            enemies.append(spawn_enemy())
    for b in bullets[:]:
        for e in enemies:
            if math.hypot(b[0] - e[0], b[1] - e[1]) < 40:
                bullets.remove(b)
                enemies.remove(e)
                enemies.append(spawn_enemy())
                score += 1
                break
    if cheat_mode and enemies:
        closest_enemy = None
        min_dist = 999999.999999
        for e in enemies:
            d = (px - e[0]) ** 2 + (py - e[1]) ** 2
            if d < min_dist:
                min_dist = d
                closest_enemy = e
        if closest_enemy:
            target_dx = closest_enemy[0] - px
            target_dy = closest_enemy[1] - py
            aim_angle = math.degrees(math.atan2(target_dy, target_dx))
            g_angle = aim_angle
            if frame % 500 == 0:
                bullets.append([px, py, g_angle])
    if life <= 0 or miss_count >= 10:
        game_over = True
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    draw_grid()
    draw_walls()
    draw_player()
    draw_bullets()
    draw_enemies()
    draw_text(10, 770, f"Player Remaining Life: {life}")
    draw_text(10, 740, f"Game Score: {score}")
    draw_text(10, 710, f"Player Bullet Missed: {miss_count}")
    if game_over: draw_text(400, 400, "GAME OVER - PRESS R")
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()