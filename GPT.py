from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# =============================================================================
# Global Variables
# =============================================================================

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800

GRID_LENGTH = 500
GRID_STEP = 50
WALL_HEIGHT = 100
FOV_Y = 60

score = 0
lives = 5
missed_bullets = 0
game_over = False

# Player
player_pos = [0, 0, 0]
player_angle = 0
player_speed = 5
player_radius = 20

# Camera
camera_mode = 0
camera_orbit_angle = 0.0
camera_height = 400
camera_dist = 800

# Bullets
bullets = []
bullet_size = 5

# Enemies
enemies = []
num_enemies = 5
enemy_base_radius = 15
enemy_speed = 0.2  # Slow enemy speed

# Animation
scale_factor = 1.0
scale_growing = True

# Cheat Mode
cheat_mode = False
cheat_camera_follow = False
cheat_cooldown = 0


# =============================================================================
# Helper Functions
# =============================================================================

def get_forward_vector(angle_deg):
    angle_rad = math.radians(angle_deg)
    return math.cos(angle_rad), math.sin(angle_rad)


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def spawn_enemies():
    global enemies
    while len(enemies) < num_enemies:
        x = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        y = random.randint(-GRID_LENGTH + 50, GRID_LENGTH - 50)

        if distance((x, y), (player_pos[0], player_pos[1])) < 200:
            continue

        enemies.append({
            'x': x,
            'y': y,
            'color': (1.0, 0.0, 0.0),
            'targeted': False
        })


def init_game():
    global score, lives, missed_bullets, game_over, player_pos, player_angle
    global bullets, enemies, cheat_mode, cheat_camera_follow, camera_mode

    score = 0
    lives = 5
    missed_bullets = 0
    game_over = False
    player_pos = [0, 0, 0]
    player_angle = 0
    bullets = []
    enemies = []
    cheat_mode = False
    cheat_camera_follow = False
    camera_mode = 0
    spawn_enemies()


# =============================================================================
# Drawing Functions
# =============================================================================

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
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


def draw_grid_and_walls():
    # Floor
    glBegin(GL_QUADS)
    for x in range(-GRID_LENGTH, GRID_LENGTH, GRID_STEP):
        for y in range(-GRID_LENGTH, GRID_LENGTH, GRID_STEP):
            if ((x // GRID_STEP) + (y // GRID_STEP)) % 2 == 0:
                glColor3f(0.2, 0.2, 0.2)
            else:
                glColor3f(0.4, 0.4, 0.4)
            glVertex3f(x, y, 0)
            glVertex3f(x + GRID_STEP, y, 0)
            glVertex3f(x + GRID_STEP, y + GRID_STEP, 0)
            glVertex3f(x, y + GRID_STEP, 0)
    glEnd()

    # Walls
    glColor3f(0.6, 0.4, 0.8)
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)

    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)

    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)

    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, WALL_HEIGHT)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, WALL_HEIGHT)
    glEnd()


def draw_player():
    global player_pos, player_angle, game_over

    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 30)

    if game_over:
        glRotatef(90, 1, 0, 0)
        glTranslatef(0, 0, -20)

    glRotatef(player_angle, 0, 0, 1)

    # Body
    glColor3f(1, 1, 0)
    glPushMatrix()
    glScalef(0.8, 1.5, 2.0)
    glutSolidCube(15)
    glPopMatrix()

    # Head
    glColor3f(0.9, 0.8, 0.7)
    glPushMatrix()
    glTranslatef(0, 0, 22)
    gluSphere(gluNewQuadric(), 8, 16, 16)
    glPopMatrix()

    # Legs
    glColor3f(1, 0, 0)
    glPushMatrix()
    glTranslatef(-5, 0, -15)
    glRotatef(180, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 0, 20, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(5, 0, -15)
    glRotatef(180, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 3, 0, 20, 10, 10)
    glPopMatrix()

    # Gun
    glColor3f(0, 1, 0)
    glPushMatrix()
    glTranslatef(-10, 0, 10)
    glRotatef(-90, 0, 1, 0)
    gluCylinder(gluNewQuadric(), 4, 0, 35, 10, 10)
    glPopMatrix()

    glPopMatrix()


def draw_enemies():
    global scale_factor
    for e in enemies:
        glPushMatrix()
        glTranslatef(e['x'], e['y'], 20)
        glColor3fv(e['color'])
        glScalef(scale_factor, scale_factor, scale_factor)
        gluSphere(gluNewQuadric(), enemy_base_radius, 12, 12)

        glPushMatrix()
        glTranslatef(0, 0, enemy_base_radius)
        gluSphere(gluNewQuadric(), enemy_base_radius / 1.5, 10, 10)
        glPopMatrix()
        glPopMatrix()


def draw_bullets():
    glColor3f(1, 1, 1)
    for b in bullets:
        glPushMatrix()
        glTranslatef(b['x'], b['y'], 20)
        glutSolidCube(bullet_size * 2)
        glPopMatrix()


# =============================================================================
# Input Listeners
# =============================================================================

def keyboardListener(key, x, y):
    global player_pos, player_angle, cheat_mode, cheat_camera_follow, game_over

    if game_over:
        if key == b'r':
            init_game()
        return

    dx, dy = get_forward_vector(player_angle)
    dx *= player_speed
    dy *= player_speed

    if key == b'w':
        player_pos[0] -= dx
        player_pos[1] -= dy
    if key == b's':
        player_pos[0] += dx
        player_pos[1] += dy

    limit = GRID_LENGTH - 20
    player_pos[0] = max(-limit, min(limit, player_pos[0]))
    player_pos[1] = max(-limit, min(limit, player_pos[1]))

    if key == b'a':
        player_angle += 4
    if key == b'd':
        player_angle -= 4
    if key == b'c':
        cheat_mode = not cheat_mode
        print(f"Cheat Mode: {cheat_mode}")
    if key == b'v':
        if cheat_mode:
            cheat_camera_follow = not cheat_camera_follow
    if key == b'r':
        init_game()


def specialKeyListener(key, x, y):
    global camera_height, camera_orbit_angle
    if key == GLUT_KEY_UP:
        camera_height += 10
        if camera_height > 1000: camera_height = 1000
    if key == GLUT_KEY_DOWN:
        camera_height -= 10
        if camera_height < 50: camera_height = 50
    if key == GLUT_KEY_LEFT:
        camera_orbit_angle -= 0.05
    if key == GLUT_KEY_RIGHT:
        camera_orbit_angle += 0.05


def mouseListener(button, state, x, y):
    global camera_mode, bullets, player_pos, player_angle, game_over

    if game_over: return

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        dx, dy = get_forward_vector(player_angle)
        # Manual speed: 2
        bullets.append({
            'x': player_pos[0],
            'y': player_pos[1],
            'dx': -dx,
            'dy': -dy,
            'speed': 2
        })

    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = 1 - camera_mode
        if camera_mode == 1:
            print("Switched to First Person")
        else:
            print("Switched to Third Person")


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV_Y, 1.25, 1, 3000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == 1 or (cheat_mode and cheat_camera_follow):
        dx, dy = get_forward_vector(player_angle)
        head_offset = 15
        eyeX = player_pos[0] - dx * head_offset
        eyeY = player_pos[1] - dy * head_offset
        eyeZ = 50
        targetX = eyeX - dx * 200
        targetY = eyeY - dy * 200
        targetZ = 50
        gluLookAt(eyeX, eyeY, eyeZ, targetX, targetY, targetZ, 0, 0, 1)
    else:
        eyeX = camera_dist * math.cos(camera_orbit_angle)
        eyeY = camera_dist * math.sin(camera_orbit_angle)
        eyeZ = camera_height
        gluLookAt(eyeX, eyeY, eyeZ, 0, 0, 0, 0, 0, 1)


def idle():
    global scale_factor, scale_growing, game_over, score, lives, missed_bullets
    global bullets, enemies, player_pos, player_angle, cheat_cooldown

    if game_over:
        glutPostRedisplay()
        return

    # 1. Animation
    if scale_growing:
        scale_factor += 0.02
        if scale_factor > 1.2: scale_growing = False
    else:
        scale_factor -= 0.02
        if scale_factor < 0.8: scale_growing = True

    # 2. Enemy Movement
    for e in enemies:
        vx = player_pos[0] - e['x']
        vy = player_pos[1] - e['y']
        dist = math.sqrt(vx * vx + vy * vy)
        if dist > 0:
            e['x'] += (vx / dist) * enemy_speed
            e['y'] += (vy / dist) * enemy_speed

    # 3. Bullets Logic
    bullets_to_remove = []
    for b in bullets:
        speed = b.get('speed', 2)
        b['x'] += b['dx'] * speed
        b['y'] += b['dy'] * speed

        # Check Boundaries
        if abs(b['x']) > GRID_LENGTH or abs(b['y']) > GRID_LENGTH:
            bullets_to_remove.append(b)
            # CHANGED: Added logic back - if 10 missed, GAME OVER
            missed_bullets += 1
            if missed_bullets >= 10:
                game_over = True

    # 4. Collision: Enemy touches Player
    enemies_to_respawn = []
    for e in enemies:
        d = distance((e['x'], e['y']), (player_pos[0], player_pos[1]))
        if d < (player_radius + enemy_base_radius):
            enemies_to_respawn.append(e)
            lives -= 1
            if lives <= 0:
                game_over = True

    # 5. Collision: Bullet hits Enemy
    for b in bullets:
        hit = False
        speed = b.get('speed', 2)
        hitbox_size = enemy_base_radius * 2 + bullet_size + speed

        for e in enemies:
            d = distance((b['x'], b['y']), (e['x'], e['y']))
            if d < hitbox_size:
                enemies_to_respawn.append(e)
                bullets_to_remove.append(b)
                score += 1
                hit = True
                break
        if hit and b not in bullets_to_remove:
            bullets_to_remove.append(b)

    # 6. Clean up
    for b in bullets_to_remove:
        if b in bullets: bullets.remove(b)
    for e in enemies_to_respawn:
        if e in enemies:
            enemies.remove(e)
            spawn_enemies()

    # 7. Cheat Mode Logic
    if cheat_mode:
        nearest_e = None
        min_dist = 99999

        for e in enemies:
            d = distance((e['x'], e['y']), (player_pos[0], player_pos[1]))
            if d < min_dist:
                min_dist = d
                nearest_e = e

        if nearest_e:
            vec_x = nearest_e['x'] - player_pos[0]
            vec_y = nearest_e['y'] - player_pos[1]
            dist_val = math.sqrt(vec_x ** 2 + vec_y ** 2)

            # Rotate to enemy
            if dist_val > 0:
                angle_rad = math.atan2(vec_y, vec_x)
                angle_deg = math.degrees(angle_rad)
                player_angle = angle_deg + 180

                # Fire single shot
                if not nearest_e.get('targeted', False):
                    cheat_cooldown += 1
                    if cheat_cooldown >= 20:
                        cheat_cooldown = 0
                        aim_dx = vec_x / dist_val
                        aim_dy = vec_y / dist_val

                        bullets.append({
                            'x': player_pos[0],
                            'y': player_pos[1],
                            'dx': aim_dx,
                            'dy': aim_dy,
                            'speed': 4
                        })
                        nearest_e['targeted'] = True

    spawn_enemies()
    glutPostRedisplay()


def showScreen():
    global game_over

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    setupCamera()
    draw_grid_and_walls()

    if not game_over:
        draw_player()
        draw_enemies()
        draw_bullets()

        draw_text(10, WINDOW_HEIGHT - 30, f"Score: {score}")
        draw_text(10, WINDOW_HEIGHT - 60, f"Lives: {lives}")
        # CHANGED: Show limit
        draw_text(10, WINDOW_HEIGHT - 90, f"Missed: {missed_bullets}/10")

        if cheat_mode:
            draw_text(10, WINDOW_HEIGHT - 120, "CHEAT MODE ON")
    else:
        draw_player()
        draw_enemies()
        draw_text(WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2, "GAME OVER")
        draw_text(WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT // 2 - 30, f"Final Score: {score}")
        draw_text(WINDOW_WIDTH // 2 - 70, WINDOW_HEIGHT // 2 - 60, "Press R to Restart")

    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy - CSE 423 Lab 03")

    init_game()
    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()