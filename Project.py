from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# -------------------------------------------------
# BASIC CAMERA / WORLD STATE
# -------------------------------------------------
camera_pos = [0, 600, 250]
camera_angle = 45
first_person = False
fovY = 80

GRID_LENGTH = 1000
ARENA_SIZE = 500

px, py = 0, -ARENA_SIZE + 80
g_angle = 90

player_health = 100
score = 0
level = 1
next_level_score = 20

max_arrows = 15
arrow_count = 15

cheat_mode = False

game_over = False
paused = False

frame = 0

# Power-ups
powerups = []
active_shield = 0
active_speed = 0
active_multishot = 0
POWERUP_DURATION = 300

# Arrow types
current_arrow_type = 0  # 0=normal, 1=fire, 2=ice
frozen_animals = {}

# Combo system
combo_count = 0
combo_timer = 0
COMBO_TIMEOUT = 180
last_hit_time = 0
score_multiplier = 1

# Boss system
boss_animal = None  # [type, x, y, angle, speed, phase, health]
boss_health = 0
MAX_BOSS_HEALTH = 5
boss_spawned_level = 0

# Environment
rocks = []
water_patches = []
bushes = []

# Particles
particles = []

# Stamina
max_stamina = 100
stamina = 100
sprinting = False

# Day/Night cycle
time_of_day = 0

# UI buttons
BTN_PLAY = [950, 750, 990, 790]
BTN_RESTART = [910, 750, 945, 785]

# -------------------------------------------------
# FOREST / ARENA TREES
# -------------------------------------------------
trees = []
OUTER_TREE_COUNT = 220
INNER_TREE_COUNT = 100

for _ in range(OUTER_TREE_COUNT):
    while True:
        x = random.randint(-GRID_LENGTH + 80, GRID_LENGTH - 80)
        y = random.randint(-GRID_LENGTH + 80, GRID_LENGTH - 80)
        if abs(x) > ARENA_SIZE + 40 or abs(y) > ARENA_SIZE + 40:
            break
    trunk_h = random.randint(30, 60)
    trunk_r = random.uniform(2.5, 4.5)
    foliage_r = random.uniform(12.0, 22.0)
    style = random.randint(0, 1)
    trees.append([x, y, trunk_h, trunk_r, foliage_r, style])

for _ in range(INNER_TREE_COUNT):
    while True:
        x = random.randint(-ARENA_SIZE + 60, ARENA_SIZE - 60)
        y = random.randint(-ARENA_SIZE + 60, ARENA_SIZE - 60)
        if math.hypot(x - px, y - py) > 60:
            break
    trunk_h = random.randint(28, 52)
    trunk_r = random.uniform(2.0, 4.0)
    foliage_r = random.uniform(10.0, 18.0)
    style = random.randint(0, 1)
    trees.append([x, y, trunk_h, trunk_r, foliage_r, style])


def position_blocked(x, y):
    for t in trees:
        tx, ty, trunk_h, trunk_r, foliage_r, style = t
        col_r = max(10.0, trunk_r * 4.0)
        dx = x - tx
        dy = y - ty
        if dx * dx + dy * dy < col_r * col_r:
            return True
    return False


# -------------------------------------------------
# ANIMALS
# -------------------------------------------------
animals = []
ANIMAL_TYPES = ["tiger", "elephant", "snake", "bear", "lion"]
ANIMALS_PER_TYPE = 4
WORLD_SPAWN_MARGIN = 150

for t_type in range(len(ANIMAL_TYPES)):
    for _ in range(ANIMALS_PER_TYPE):
        x = random.randint(-GRID_LENGTH + WORLD_SPAWN_MARGIN,
                           GRID_LENGTH - WORLD_SPAWN_MARGIN)
        y = random.randint(-GRID_LENGTH + WORLD_SPAWN_MARGIN,
                           GRID_LENGTH - WORLD_SPAWN_MARGIN)
        angle = random.uniform(0, 360)
        if t_type == 1:
            speed = random.uniform(0.08, 0.14)
        elif t_type == 2:
            speed = random.uniform(0.18, 0.26)
        else:
            speed = random.uniform(0.12, 0.22)
        phase = random.uniform(0, 2 * math.pi)
        animals.append([t_type, x, y, angle, speed, phase])


# -------------------------------------------------
# COLLECTABLES (ARROWS ONLY)
# -------------------------------------------------
collectables = []  # [x, y, type] type = 0 arrow


def spawn_level_collectables():
    """Spawn fewer arrow collectables per level (reduced spawn rate)."""
    for _ in range(8):  # was 20; now 8 arrows per level
        cx = random.randint(-ARENA_SIZE + 100, ARENA_SIZE - 100)
        cy = random.randint(-ARENA_SIZE + 100, ARENA_SIZE - 100)
        collectables.append([cx, cy, 0])


def spawn_powerup():
    px_spawn = random.randint(-ARENA_SIZE + 100, ARENA_SIZE - 100)
    py_spawn = random.randint(-ARENA_SIZE + 100, ARENA_SIZE - 100)
    p_type = random.randint(0, 2)
    powerups.append([px_spawn, py_spawn, p_type, frame])


def spawn_boss():
    global boss_animal, boss_health, boss_spawned_level
    boss_type = random.randint(0, 4)
    bx = random.randint(-GRID_LENGTH + 200, GRID_LENGTH - 200)
    by = random.randint(-GRID_LENGTH + 200, GRID_LENGTH - 200)
    angle = random.uniform(0, 360)
    speed = 0.15
    phase = random.uniform(0, 2 * math.pi)
    boss_health = MAX_BOSS_HEALTH
    boss_animal = [boss_type, bx, by, angle, speed, phase, boss_health]
    boss_spawned_level = level


def spawn_environment():
    global rocks, water_patches, bushes
    rocks.clear()
    water_patches.clear()
    bushes.clear()

    for _ in range(15):
        rx = random.randint(-ARENA_SIZE + 50, ARENA_SIZE - 50)
        ry = random.randint(-ARENA_SIZE + 50, ARENA_SIZE - 50)
        rocks.append([rx, ry, 15.0])

    for _ in range(8):
        wx = random.randint(-ARENA_SIZE + 100, ARENA_SIZE - 100)
        wy = random.randint(-ARENA_SIZE + 100, ARENA_SIZE - 100)
        water_patches.append([wx, wy, 40.0])

    for _ in range(20):
        bx = random.randint(-ARENA_SIZE + 50, ARENA_SIZE - 50)
        by = random.randint(-ARENA_SIZE + 50, ARENA_SIZE - 50)
        bushes.append([bx, by, 25.0])


def create_particles(x, y, z, color, count=10):
    for _ in range(count):
        vx = random.uniform(-2, 2)
        vy = random.uniform(-2, 2)
        vz = random.uniform(0, 3)
        life = random.randint(20, 40)
        particles.append([x, y, z, vx, vy, vz, color[0], color[1], color[2], life])


# -------------------------------------------------
# ARROWS
# -------------------------------------------------
arrows = []  # [x, y, angle_deg, type]
arrow_speed = 2.5


# -------------------------------------------------
# TEXT
# -------------------------------------------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch) & 0xFF)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


# -------------------------------------------------
# GRID + TREES
# -------------------------------------------------
def draw_grid():
    outer_tile = 80
    for x in range(-GRID_LENGTH, GRID_LENGTH, outer_tile):
        for y in range(-GRID_LENGTH, GRID_LENGTH, outer_tile):
            ix = x // outer_tile + 1357
            iy = y // outer_tile + 2467
            v = ix * 374761393 + iy * 668265263
            v ^= (v >> 13)
            v &= 0xFF
            noise = v / 255.0
            grass_factor = 0.4 + 0.6 * noise
            dirt_factor = 1.0 - grass_factor

            r = 0.18 * dirt_factor + 0.08 * grass_factor
            g = 0.10 * dirt_factor + 0.35 * grass_factor
            b = 0.04 * dirt_factor + 0.05 * grass_factor

            glColor3f(r, g, b)
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + outer_tile, y, 0)
            glVertex3f(x + outer_tile, y + outer_tile, 0)
            glVertex3f(x, y + outer_tile, 0)
            glEnd()

    for t in trees:
        x, y, trunk_h, trunk_r, foliage_r, style = t
        glPushMatrix()
        glTranslatef(x, y, 0)

        glColor3f(0.38, 0.24, 0.10)
        glPushMatrix()
        glTranslatef(0, 0, trunk_h * 0.5)
        glScalef(trunk_r, trunk_r, trunk_h)
        glutSolidCube(1)
        glPopMatrix()

        quad = gluNewQuadric()
        if style == 0:
            glColor3f(0.05, 0.35, 0.07)
            glPushMatrix()
            glTranslatef(0, 0, trunk_h + foliage_r * 0.7)
            gluSphere(quad, foliage_r, 12, 12)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(foliage_r * 0.5, 0, trunk_h + foliage_r * 0.5)
            gluSphere(quad, foliage_r * 0.6, 10, 10)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(-foliage_r * 0.4, foliage_r * 0.3,
                         trunk_h + foliage_r * 0.8)
            gluSphere(quad, foliage_r * 0.55, 10, 10)
            glPopMatrix()
        else:
            glColor3f(0.04, 0.30, 0.05)
            levels = 3
            for i in range(levels):
                factor = 1.0 - i * 0.25
                r_level = foliage_r * factor
                z = trunk_h + foliage_r * 0.4 + i * (foliage_r * 0.6)
                glPushMatrix()
                glTranslatef(0, 0, z)
                gluSphere(quad, r_level, 10, 10)
                glPopMatrix()

        glPopMatrix()


# -------------------------------------------------
# WALLS
# -------------------------------------------------
def draw_walls():
    h = 10.0
    glColor3f(0.25, 0.25, 0.27)

    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, h)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, h)
    glEnd()

    glBegin(GL_QUADS)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, h)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, h)
    glEnd()

    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, h)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, h)
    glEnd()

    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, h)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, h)
    glEnd()


# -------------------------------------------------
# PLAYER WITH BOW
# -------------------------------------------------
def draw_player():
    glPushMatrix()
    glTranslatef(px, py, 0)
    glRotatef(g_angle, 0, 0, 1)

    leg_h = 18.0
    leg_th = 3.0
    body_h = 22.0
    body_w = 8.0
    body_d = 10.0
    head_r = 5.0

    hip_z = leg_h
    body_center_z = hip_z + body_h * 0.5
    shoulder_z = hip_z + body_h * 0.85
    neck_z = hip_z + body_h + head_r * 0.4
    head_center_z = hip_z + body_h + head_r * 1.1

    if not first_person:
        glColor3f(0.15, 0.18, 0.25)
        for side in (-1, 1):
            glPushMatrix()
            glTranslatef(0, side * 2.5, leg_h * 0.5)
            glScalef(leg_th, leg_th, leg_h)
            glutSolidCube(1)
            glPopMatrix()

        glColor3f(0.2, 0.35, 0.8)
        glPushMatrix()
        glTranslatef(0, 0, body_center_z)
        glScalef(body_d, body_w, body_h)
        glutSolidCube(1)
        glPopMatrix()

        glColor3f(1.0, 0.85, 0.7)
        glPushMatrix()
        glTranslatef(body_d * 0.05, 0, neck_z)
        glScalef(2.5, 2.5, 4.0)
        glutSolidCube(1)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(body_d * 0.05, 0, head_center_z)
        glutSolidSphere(head_r, 24, 24)
        glPopMatrix()

        arm_len = 16.0
        arm_th = 2.2
        shoulder_y = body_w * 0.55

        glPushMatrix()
        glTranslatef(body_d * 0.4, shoulder_y, shoulder_z)
        glRotatef(-10, 0, 1, 0)
        glScalef(arm_len, arm_th, arm_th)
        glutSolidCube(1)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(body_d * 0.1, -shoulder_y, shoulder_z)
        glRotatef(-25, 0, 1, 0)
        glScalef(arm_len * 0.9, arm_th, arm_th)
        glutSolidCube(1)
        glPopMatrix()

        hand_r = 1.6
        glPushMatrix()
        glTranslatef(body_d * 0.4 + arm_len * 0.5, shoulder_y, shoulder_z)
        glutSolidSphere(hand_r, 10, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(body_d * 0.1 + arm_len * 0.45, -shoulder_y, shoulder_z)
        glutSolidSphere(hand_r, 10, 10)
        glPopMatrix()

        bow_h = 20.0
        bow_th = 0.7
        bow_x = body_d * 0.4 + arm_len * 0.5
        bow_y = shoulder_y
        bow_z = shoulder_z

        glPushMatrix()
        glTranslatef(bow_x, bow_y, bow_z)

        glColor3f(0.45, 0.26, 0.08)
        glPushMatrix()
        glScalef(bow_th, bow_th, bow_h)
        glutSolidCube(1)
        glPopMatrix()

        tip_offset_z = bow_h * 0.5
        glPushMatrix()
        glTranslatef(0, 0, tip_offset_z)
        glRotatef(20, 0, 1, 0)
        glScalef(1.4, bow_th, 3.0)
        glutSolidCube(1)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0, -tip_offset_z)
        glRotatef(-20, 0, 1, 0)
        glScalef(1.4, bow_th, 3.0)
        glutSolidCube(1)
        glPopMatrix()

        glColor3f(0.9, 0.9, 0.9)
        glPushMatrix()
        glTranslatef(-1.0, 0, 0)
        glScalef(bow_th * 0.2, bow_th * 0.2, bow_h * 0.95)
        glutSolidCube(1)
        glPopMatrix()

        glPopMatrix()
    else:
        arm_len = 16.0
        arm_th = 2.2
        shoulder_y = body_w * 0.55

        glTranslatef(0, 0, 5.0)

        glColor3f(1.0, 0.85, 0.7)
        glPushMatrix()
        glTranslatef(body_d * 0.3, shoulder_y * 0.8, shoulder_z - 8)
        glRotatef(-5, 0, 1, 0)
        glScalef(arm_len * 0.9, arm_th, arm_th)
        glutSolidCube(1)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(body_d * 0.1, -shoulder_y * 0.7, shoulder_z - 7)
        glRotatef(-20, 0, 1, 0)
        glScalef(arm_len * 0.8, arm_th, arm_th)
        glutSolidCube(1)
        glPopMatrix()

        hand_r = 1.6
        glPushMatrix()
        glTranslatef(body_d * 0.3 + arm_len * 0.45,
                     shoulder_y * 0.8,
                     shoulder_z - 8)
        glutSolidSphere(hand_r, 10, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(body_d * 0.1 + arm_len * 0.4,
                     -shoulder_y * 0.7,
                     shoulder_z - 7)
        glutSolidSphere(hand_r, 10, 10)
        glPopMatrix()

        bow_h = 20.0
        bow_th = 0.7
        bow_x = body_d * 0.3 + arm_len * 0.45
        bow_y = shoulder_y * 0.8
        bow_z = shoulder_z - 8

        glPushMatrix()
        glTranslatef(bow_x, bow_y, bow_z)

        glColor3f(0.45, 0.26, 0.08)
        glPushMatrix()
        glScalef(bow_th, bow_th, bow_h)
        glutSolidCube(1)
        glPopMatrix()

        tip_offset_z = bow_h * 0.5
        glPushMatrix()
        glTranslatef(0, 0, tip_offset_z)
        glRotatef(20, 0, 1, 0)
        glScalef(1.4, bow_th, 3.0)
        glutSolidCube(1)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0, -tip_offset_z)
        glRotatef(-20, 0, 1, 0)
        glScalef(1.4, bow_th, 3.0)
        glutSolidCube(1)
        glPopMatrix()

        glColor3f(0.9, 0.9, 0.9)
        glPushMatrix()
        glTranslatef(-1.0, 0, 0)
        glScalef(bow_th * 0.2, bow_th * 0.2, bow_h * 0.95)
        glutSolidCube(1)
        glPopMatrix()

        glPopMatrix()

    glPopMatrix()


# -------------------------------------------------
# ENVIRONMENT / POWERUPS
# -------------------------------------------------
def draw_collectables():
    for cx, cy, c_type in collectables:
        glPushMatrix()
        glTranslatef(cx, cy, 8.0)

        glColor3f(0.9, 0.7, 0.1)
        glPushMatrix()
        glRotatef(90, 0, 0, 1)
        glScalef(8.0, 0.25, 0.25)
        glutSolidCube(1)
        glPopMatrix()

        glColor3f(0.95, 0.95, 0.95)
        glPushMatrix()
        glTranslatef(4.5, 0, 0)
        glScalef(1.0, 0.5, 0.5)
        glutSolidCube(1)
        glPopMatrix()

        glPopMatrix()


def draw_powerups():
    for pw_x, pw_y, pw_type, spawn_time in powerups:
        bob = math.sin(frame * 0.1) * 3
        glPushMatrix()
        glTranslatef(pw_x, pw_y, 15.0 + bob)
        glRotatef(frame * 2, 0, 0, 1)

        if pw_type == 0:
            glColor3f(0.2, 0.5, 1.0)
            glutSolidCube(10)
        elif pw_type == 1:
            glColor3f(1.0, 0.9, 0.2)
            glutSolidSphere(6, 12, 12)
        elif pw_type == 2:
            glColor3f(1.0, 0.3, 0.1)
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 8, 0)
            glVertex3f(-7, -4, 0)
            glVertex3f(7, -4, 0)
            glEnd()
            glBegin(GL_TRIANGLES)
            glVertex3f(0, -8, 0)
            glVertex3f(-7, 4, 0)
            glVertex3f(7, 4, 0)
            glEnd()

        glPopMatrix()


def draw_environment():
    for rx, ry, rad in rocks:
        glPushMatrix()
        glTranslatef(rx, ry, rad * 0.5)
        glColor3f(0.4, 0.35, 0.3)
        glScalef(rad, rad, rad)
        glutSolidCube(1)
        glPopMatrix()

    for wx, wy, rad in water_patches:
        glColor3f(0.2, 0.4, 0.7)
        glBegin(GL_QUADS)
        glVertex3f(wx - rad, wy - rad, 0.5)
        glVertex3f(wx + rad, wy - rad, 0.5)
        glVertex3f(wx + rad, wy + rad, 0.5)
        glVertex3f(wx - rad, wy + rad, 0.5)
        glEnd()

    for bx, by, rad in bushes:
        glPushMatrix()
        glTranslatef(bx, by, rad * 0.4)
        glColor3f(0.15, 0.4, 0.15)
        glutSolidSphere(rad * 0.6, 8, 8)
        glPopMatrix()


def draw_particles():
    glPointSize(5)
    glBegin(GL_POINTS)
    for p in particles:
        px, py, pz, vx, vy, vz, r, g, b, life = p
        alpha = life / 40.0
        glColor3f(r * alpha, g * alpha, b * alpha)
        glVertex3f(px, py, pz)
    glEnd()


def draw_shield_effect():
    if active_shield > 0:
        glPushMatrix()
        glTranslatef(px, py, 20)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pulse = 0.3 + 0.2 * math.sin(frame * 0.2)
        glColor4f(0.2, 0.5, 1.0, pulse)
        glutSolidSphere(30, 16, 16)
        glDisable(GL_BLEND)
        glPopMatrix()


def draw_boss_healthbar():
    if boss_animal and boss_health > 0:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        bar_width = 300
        bar_height = 20
        bar_x = 350
        bar_y = 750

        glColor3f(0.3, 0.1, 0.1)
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + bar_width, bar_y)
        glVertex2f(bar_x + bar_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()

        health_width = (boss_health / MAX_BOSS_HEALTH) * bar_width
        glColor3f(0.9, 0.1, 0.1)
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + health_width, bar_y)
        glVertex2f(bar_x + health_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()

        glColor3f(1, 1, 1)
        glBegin(GL_LINE_LOOP)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + bar_width, bar_y)
        glVertex2f(bar_x + bar_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)


# -------------------------------------------------
# ARROW DRAWING
# -------------------------------------------------
def draw_bullets():
    for arrow_data in arrows:
        ax, ay, ang = arrow_data[0], arrow_data[1], arrow_data[2]
        arr_type = arrow_data[3] if len(arrow_data) > 3 else 0

        glPushMatrix()
        glTranslatef(ax, ay, 18.0)
        glRotatef(ang, 0, 0, 1)

        if arr_type == 1:
            glColor3f(1.0, 0.3, 0.1)
        elif arr_type == 2:
            glColor3f(0.3, 0.7, 1.0)
        else:
            glColor3f(0.6, 0.4, 0.1)

        glPushMatrix()
        glTranslatef(6.0, 0, 0)
        glScalef(12.0, 0.3, 0.3)
        glutSolidCube(1)
        glPopMatrix()

        glColor3f(0.85, 0.85, 0.85)
        glPushMatrix()
        glTranslatef(12.5, 0, 0)
        glScalef(1.4, 0.6, 0.6)
        glutSolidCube(1)
        glPopMatrix()

        if arr_type == 1:
            glColor3f(1.0, 0.5, 0.1)
        elif arr_type == 2:
            glColor3f(0.5, 0.9, 1.0)
        else:
            glColor3f(0.9, 0.1, 0.1)

        glPushMatrix()
        glTranslatef(0.0, 0.0, 0.5)
        glScalef(1.2, 1.8, 0.12)
        glutSolidCube(1)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.0, 0.0, -0.5)
        glScalef(1.2, 1.8, 0.12)
        glutSolidCube(1)
        glPopMatrix()

        glPopMatrix()


# -------------------------------------------------
# DRAW ANIMALS
# -------------------------------------------------
def draw_enemies():
    for a in animals:
        t_type, x, y, angle, speed, phase = a
        glPushMatrix()
        glTranslatef(x, y, 0)
        glRotatef(angle, 0, 0, 1)

        if t_type in (0, 3, 4):
            if t_type == 0:
                base_col = (0.9, 0.55, 0.15)
            elif t_type == 4:
                base_col = (0.85, 0.65, 0.25)
            else:
                base_col = (0.4, 0.25, 0.1)

            if t_type == 0:
                accent_col = (0.75, 0.45, 0.15)
                body_len, body_w, body_h = 32.0, 14.0, 12.0
                leg_h, leg_t = 9.0, 4.0
                stripes = True
                mane = False
            elif t_type == 4:
                accent_col = (0.75, 0.5, 0.2)
                body_len, body_w, body_h = 34.0, 15.0, 13.0
                leg_h, leg_t = 9.5, 4.2
                stripes = False
                mane = True
            else:
                accent_col = (0.35, 0.2, 0.09)
                body_len, body_w, body_h = 28.0, 16.0, 14.0
                leg_h, leg_t = 8.0, 5.0
                stripes = False
                mane = False

            body_bob = math.sin(phase * 1.2) * 0.6

            glColor3f(*base_col)
            glPushMatrix()
            glTranslatef(0, 0, leg_h + body_h / 2.0 + body_bob)
            glScalef(body_len, body_w, body_h)
            glutSolidCube(1)
            glPopMatrix()

            if t_type == 3:
                glColor3f(*base_col)
                glPushMatrix()
                glTranslatef(0, 0, leg_h + body_h * 0.75 + body_bob)
                glutSolidSphere(body_h * 0.7, 16, 16)
                glPopMatrix()

            leg_positions = [
                (+body_len * 0.3, +body_w * 0.33, 0.0),
                (+body_len * 0.3, -body_w * 0.33, math.pi),
                (-body_len * 0.3, +body_w * 0.33, math.pi),
                (-body_len * 0.3, -body_w * 0.33, 0.0),
            ]
            glColor3f(*accent_col)
            for lx, ly, shift in leg_positions:
                lift = math.sin(phase * 1.4 + shift) * 1.2
                glPushMatrix()
                glTranslatef(lx, ly, leg_h / 2.0 + lift)
                glScalef(leg_t, leg_t, leg_h)
                glutSolidCube(1)
                glPopMatrix()

            head_len = body_len * 0.35
            head_w = body_w * 0.8
            head_h = body_h * (1.1 if t_type != 3 else 0.9)

            glColor3f(*base_col)
            glPushMatrix()
            glTranslatef(body_len * 0.6,
                         0,
                         leg_h + body_h + head_h * 0.2 + body_bob)
            glScalef(head_len, head_w, head_h)
            glutSolidCube(1)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(body_len * 0.6 + head_len * 0.55,
                         0,
                         leg_h + body_h + head_h * 0.0 + body_bob)
            glScalef(head_len * 0.5, head_w * 0.6, head_h * 0.6)
            glutSolidCube(1)
            glPopMatrix()

            ear_size = 3.0
            ear_z = leg_h + body_h + head_h * 0.8 + body_bob
            glColor3f(0.2, 0.1, 0.05)
            glPushMatrix()
            glTranslatef(body_len * 0.5, head_w * 0.35, ear_z)
            glScalef(ear_size, ear_size, ear_size)
            glutSolidCube(1)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(body_len * 0.5, -head_w * 0.35, ear_z)
            glScalef(ear_size, ear_size, ear_size)
            glutSolidCube(1)
            glPopMatrix()

            glColor3f(*base_col)
            glPushMatrix()
            glTranslatef(-body_len * 0.6, 0,
                         leg_h + body_h * 0.7 + body_bob)
            glRotatef(20 * math.sin(phase * 1.5), 0, 1, 0)
            glScalef(body_len * 0.35, 2.0, 3.0)
            glutSolidCube(1)
            glPopMatrix()

            if stripes:
                glColor3f(0.05, 0.05, 0.05)
                for sx in (-0.2, -0.05, 0.1, 0.25):
                    glPushMatrix()
                    glTranslatef(body_len * sx, 0,
                                 leg_h + body_h * 0.9 + body_bob)
                    glScalef(2.0, body_w * 1.05, 1.5)
                    glutSolidCube(1)
                    glPopMatrix()

            if mane:
                mane_col = (0.55, 0.35, 0.15)
                glColor3f(*mane_col)
                center_z = leg_h + body_h + head_h * 0.3 + body_bob
                glPushMatrix()
                glTranslatef(body_len * 0.6, 0, center_z)
                glutSolidSphere(head_h * 0.9, 18, 18)
                glPopMatrix()

        elif t_type == 1:
            body_len, body_w, body_h = 40.0, 24.0, 22.0
            leg_h, leg_t = 16.0, 7.0
            base_col = (0.6, 0.62, 0.65)
            body_bob = math.sin(phase * 0.8) * 0.4

            glColor3f(*base_col)
            glPushMatrix()
            glTranslatef(0, 0, leg_h + body_h / 2.0 + body_bob)
            glScalef(body_len, body_w, body_h)
            glutSolidCube(1)
            glPopMatrix()

            leg_positions = [
                (+body_len * 0.25, +body_w * 0.35),
                (+body_len * 0.25, -body_w * 0.35),
                (-body_len * 0.25, +body_w * 0.35),
                (-body_len * 0.25, -body_w * 0.35),
            ]
            glColor3f(0.55, 0.57, 0.60)
            for lx, ly in leg_positions:
                glPushMatrix()
                glTranslatef(lx, ly, leg_h / 2.0)
                glScalef(leg_t, leg_t, leg_h)
                glutSolidCube(1)
                glPopMatrix()

            head_len, head_w, head_h = 18.0, 22.0, 20.0
            glColor3f(*base_col)
            glPushMatrix()
            glTranslatef(body_len * 0.55,
                         0,
                         leg_h + body_h * 0.8 + body_bob)
            glScalef(head_len, head_w, head_h)
            glutSolidCube(1)
            glPopMatrix()

            ear_thick = 2.5
            glColor3f(0.58, 0.6, 0.63)
            glPushMatrix()
            glTranslatef(body_len * 0.5,
                         head_w * 0.6,
                         leg_h + body_h * 0.8 + body_bob)
            glScalef(head_len * 0.7, head_w * 0.7, ear_thick)
            glutSolidCube(1)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(body_len * 0.5,
                         -head_w * 0.6,
                         leg_h + body_h * 0.8 + body_bob)
            glScalef(head_len * 0.7, head_w * 0.7, ear_thick)
            glutSolidCube(1)
            glPopMatrix()

            glColor3f(0.55, 0.57, 0.60)
            glPushMatrix()
            glTranslatef(body_len * 0.8,
                         0,
                         leg_h + body_h * 0.8 + body_bob)
            glRotatef(-50, 0, 1, 0)
            glScalef(18.0, 4.0, 4.0)
            glutSolidCube(1)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(body_len * 1.0,
                         0,
                         leg_h + body_h * 0.3 + body_bob)
            glRotatef(-85, 0, 1, 0)
            glScalef(14.0, 4.0, 4.0)
            glutSolidCube(1)
            glPopMatrix()

            glColor3f(0.95, 0.95, 0.9)
            tusk_len = 10.0
            tusk_t = 1.8
            for side in (+1, -1):
                glPushMatrix()
                glTranslatef(body_len * 0.9,
                             side * 4.0,
                             leg_h + body_h * 0.45 + body_bob)
                glRotatef(-20, 0, 1, 0)
                glScalef(tusk_len, tusk_t, tusk_t)
                glutSolidCube(1)
                glPopMatrix()

        elif t_type == 2:
            segs = 14
            spacing = 4.5
            wave_amp = 2.5
            wave_freq = 0.6

            glColor3f(0.16, 0.4, 0.14)
            for i in range(segs):
                off_x = -i * spacing
                off_y = math.sin(phase + i * wave_freq) * wave_amp
                off_z = 1.5
                glPushMatrix()
                glTranslatef(off_x, off_y, off_z)
                glScalef(4.0, 3.0, 3.0)
                glutSolidSphere(1.0, 12, 12)
                glPopMatrix()

            glColor3f(0.18, 0.5, 0.18)
            head_z = 2.0
            glPushMatrix()
            glTranslatef(2.0, 0, head_z)
            glScalef(5.0, 4.0, 4.0)
            glutSolidSphere(1.0, 14, 14)
            glPopMatrix()

            glColor3f(0, 0, 0)
            eye_z = head_z + 1.0
            eye_offset_y = 1.5
            for side in (+1, -1):
                glPushMatrix()
                glTranslatef(3.8, side * eye_offset_y, eye_z)
                glutSolidSphere(0.7, 8, 8)
                glPopMatrix()

        glPopMatrix()


# -------------------------------------------------
# INPUT
# -------------------------------------------------
def keyboardListener(key, x, y):
    global px, py, g_angle, first_person, game_over, paused, level, cheat_mode
    global current_arrow_type, arrow_count

    if key == b'r':
        restart_game()
        return

    if key == b'p':
        if not game_over:
            paused = not paused
        return

    if game_over:
        return

    if key == b'c':
        cheat_mode = not cheat_mode
        return

    if key == b'1':
        current_arrow_type = 0
        return
    if key == b'2':
        current_arrow_type = 1
        return
    if key == b'3':
        current_arrow_type = 2
        return

    if paused and key in (b'w', b's', b'a', b'd'):
        return

    base_step = 10.0
    step_increment = 1.0
    step = base_step + (level - 1) * step_increment

    if active_speed > 0:
        step *= 1.5

    rad = math.radians(g_angle)
    dx = math.cos(rad) * step
    dy = math.sin(rad) * step

    limit = GRID_LENGTH - 40

    if key == b'w':
        nx = px + dx
        ny = py + dy
        if -limit < nx < limit and -limit < ny < limit and not position_blocked(nx, ny):
            for wx, wy, wrad in water_patches:
                if math.hypot(nx - wx, ny - wy) < wrad:
                    nx = px + dx * 0.5
                    ny = py + dy * 0.5
                    break
            px, py = nx, ny

    if key == b's':
        nx = px - dx
        ny = py - dy
        if -limit < nx < limit and -limit < ny < limit and not position_blocked(nx, ny):
            for wx, wy, wrad in water_patches:
                if math.hypot(nx - wx, ny - wy) < wrad:
                    nx = px - dx * 0.5
                    ny = py - dy * 0.5
                    break
            px, py = nx, ny

    if key == b'a':
        g_angle = (g_angle + 5) % 360
    if key == b'd':
        g_angle = (g_angle - 5) % 360

    if key == b'v':
        first_person = not first_person


def specialKeyListener(key, x, y):
    global camera_angle, camera_pos
    if key == GLUT_KEY_LEFT:
        camera_angle += 2
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 2
    if key == GLUT_KEY_UP:
        camera_pos[2] += 10
    if key == GLUT_KEY_DOWN:
        camera_pos[2] -= 10


def mouseListener(button, state, x, y):
    global arrows, paused, game_over, arrow_count, cheat_mode
    global current_arrow_type

    if state != GLUT_DOWN:
        return

    ui_x = x
    ui_y = 800 - y

    if (BTN_PLAY[0] <= ui_x <= BTN_PLAY[2] and
            BTN_PLAY[1] <= ui_y <= BTN_PLAY[3]):
        if not game_over:
            paused = not paused
        return

    if (BTN_RESTART[0] <= ui_x <= BTN_RESTART[2] and
            BTN_RESTART[1] <= ui_y <= BTN_RESTART[3]):
        restart_game()
        return

    if game_over or paused:
        return

    if button == GLUT_RIGHT_BUTTON:
        return

    if button == GLUT_LEFT_BUTTON:
        if arrow_count <= 0 and not cheat_mode:
            return
        if not cheat_mode:
            arrow_count -= 1

        shoot_angle = g_angle  # no auto-aim in cheat mode
        rad = math.radians(shoot_angle)
        start_x = px + math.cos(rad) * 15.0
        start_y = py + math.sin(rad) * 15.0

        if active_multishot > 0:
            for offset in [-15, 0, 15]:
                angle_with_offset = shoot_angle + offset
                rad_offset = math.radians(angle_with_offset)
                sx = px + math.cos(rad_offset) * 15.0
                sy = py + math.sin(rad_offset) * 15.0
                arrows.append([sx, sy, angle_with_offset, current_arrow_type])
        else:
            arrows.append([start_x, start_y, shoot_angle, current_arrow_type])


# -------------------------------------------------
# RESTART
# -------------------------------------------------
def restart_game():
    global px, py, g_angle, player_health, score, level, next_level_score
    global arrows, animals, game_over, paused, arrow_count, collectables, cheat_mode
    global powerups, active_shield, active_speed, active_multishot
    global current_arrow_type, frozen_animals, combo_count, combo_timer, score_multiplier
    global boss_animal, boss_health, boss_spawned_level
    global rocks, water_patches, bushes, particles
    global stamina, sprinting, time_of_day

    px, py = 0, -ARENA_SIZE + 80
    g_angle = 90
    player_health = 100
    score = 0
    level = 1
    next_level_score = 20
    arrow_count = max_arrows
    game_over = False
    paused = False
    cheat_mode = False

    current_arrow_type = 0
    active_shield = 0
    active_speed = 0
    active_multishot = 0
    combo_count = 0
    combo_timer = 0
    score_multiplier = 1
    boss_animal = None
    boss_health = 0
    boss_spawned_level = 0
    stamina = max_stamina
    sprinting = False
    time_of_day = 0

    arrows.clear()
    animals.clear()
    collectables.clear()
    powerups.clear()
    frozen_animals.clear()
    particles.clear()
    rocks.clear()
    water_patches.clear()
    bushes.clear()

    spawn_level_collectables()
    spawn_environment()

    for t_type in range(len(ANIMAL_TYPES)):
        for _ in range(ANIMALS_PER_TYPE):
            x = random.randint(-GRID_LENGTH + WORLD_SPAWN_MARGIN,
                               GRID_LENGTH - WORLD_SPAWN_MARGIN)
            y = random.randint(-GRID_LENGTH + WORLD_SPAWN_MARGIN,
                               GRID_LENGTH - WORLD_SPAWN_MARGIN)
            angle = random.uniform(0, 360)
            if t_type == 1:
                speed = random.uniform(0.08, 0.14)
            elif t_type == 2:
                speed = random.uniform(0.18, 0.26)
            else:
                speed = random.uniform(0.12, 0.22)
            phase = random.uniform(0, 2 * math.pi)
            animals.append([t_type, x, y, angle, speed, phase])


# -------------------------------------------------
# CAMERA
# -------------------------------------------------
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person:
        rad = math.radians(g_angle)
        look_dx = math.cos(rad)
        look_dy = math.sin(rad)

        eye_x = px
        eye_y = py
        eye_z = 30.0
        center_x = px + look_dx * 50
        center_y = py + look_dy * 50
        center_z = 30.0

        gluLookAt(eye_x, eye_y, eye_z,
                  center_x, center_y, center_z,
                  0, 0, 1)
    else:
        radius = 350
        x = math.cos(math.radians(camera_angle)) * radius
        y = math.sin(math.radians(camera_angle)) * radius
        gluLookAt(x, y, camera_pos[2],
                  0, 0, 40,
                  0, 0, 1)


# -------------------------------------------------
# IDLE
# -------------------------------------------------
def idle():
    global frame, animals, arrows, player_health, score, game_over
    global level, next_level_score, collectables, arrow_count
    global active_shield, active_speed, active_multishot, powerups
    global combo_count, combo_timer, score_multiplier, frozen_animals
    global boss_animal, boss_health, boss_spawned_level, particles, time_of_day

    if paused or game_over:
        glutPostRedisplay()
        return

    frame += 1
    time_of_day = (time_of_day + 0.2) % 360

    if active_shield > 0:
        active_shield -= 1
    if active_speed > 0:
        active_speed -= 1
    if active_multishot > 0:
        active_multishot -= 1

    if combo_timer > 0:
        combo_timer -= 1
        if combo_timer == 0:
            combo_count = 0
            score_multiplier = 1

    for p in particles[:]:
        p[0] += p[3]
        p[1] += p[4]
        p[2] += p[5]
        p[5] -= 0.1
        p[9] -= 1
        if p[9] <= 0 or p[2] < 0:
            particles.remove(p)

    if frame % 600 == 0 and random.random() < 0.3:
        spawn_powerup()

    for pw in powerups[:]:
        if frame - pw[3] > 1800:
            powerups.remove(pw)

    # Spawn boss once per multiple-of-5 level
    if level % 5 == 0 and boss_animal is None and boss_spawned_level != level:
        spawn_boss()

    if arrow_count <= 0 and not cheat_mode:
        game_over = True
        glutPostRedisplay()
        return

    for rx, ry, rrad in rocks:
        if math.hypot(px - rx, py - ry) < rrad + 10:
            if active_shield <= 0 and not cheat_mode:
                player_health = 0
                game_over = True

    # Arrow collectables
    for col in collectables[:]:
        cx, cy, c_type = col
        dx = px - cx
        dy = py - cy
        if dx * dx + dy * dy < 30 * 30:
            collectables.remove(col)
            arrow_count = min(arrow_count + 2, 100 if cheat_mode else max_arrows)
            create_particles(cx, cy, 8, (0.9, 0.7, 0.1), 5)

    # Powerups
    for pw in powerups[:]:
        pw_x, pw_y, pw_type, _ = pw
        if math.hypot(px - pw_x, py - pw_y) < 30:
            powerups.remove(pw)
            if pw_type == 0:
                active_shield = POWERUP_DURATION
            elif pw_type == 1:
                active_speed = POWERUP_DURATION
            elif pw_type == 2:
                active_multishot = POWERUP_DURATION
            create_particles(pw_x, pw_y, 15, (1, 1, 0), 15)

    # Move arrows
    for arr in arrows[:]:
        arr_type = arr[3] if len(arr) > 3 else 0
        ax, ay, ang = arr[0], arr[1], arr[2]
        rad = math.radians(ang)
        ax += math.cos(rad) * arrow_speed
        ay += math.sin(rad) * arrow_speed
        arr[0] = ax
        arr[1] = ay
        if abs(ax) > GRID_LENGTH or abs(ay) > GRID_LENGTH:
            arrows.remove(arr)

    for idx in list(frozen_animals.keys()):
        frozen_animals[idx] -= 1
        if frozen_animals[idx] <= 0:
            del frozen_animals[idx]

    # Arrows vs animals
    for arr in arrows[:]:
        ax, ay, ang = arr[0], arr[1], arr[2]
        arr_type = arr[3] if len(arr) > 3 else 0
        hit = False

        for i, a in enumerate(animals):
            t_type, x, y, angle, speed, phase = a
            dx = ax - x
            dy = ay - y
            dist2 = dx * dx + dy * dy

            if t_type == 2:
                r2 = 25 * 25
            elif t_type == 1:
                r2 = 40 * 40
            else:
                r2 = 35 * 35

            if dist2 < r2:
                arrows.remove(arr)
                combo_timer = COMBO_TIMEOUT
                combo_count += 1
                if combo_count >= 10:
                    score_multiplier = 5
                elif combo_count >= 5:
                    score_multiplier = 3
                elif combo_count >= 3:
                    score_multiplier = 2
                else:
                    score_multiplier = 1

                points = 1 * score_multiplier
                if arr_type == 1:
                    points *= 2
                score += points

                if arr_type == 2:
                    frozen_animals[i] = 180

                color = (0.8, 0.1, 0.1)
                if arr_type == 1:
                    color = (1.0, 0.5, 0.1)
                elif arr_type == 2:
                    color = (0.3, 0.7, 1.0)
                create_particles(x, y, 15, color, 20)

                old_level = level
                while score >= next_level_score:
                    level += 1
                    next_level_score += 10

                if level > old_level:
                    spawn_level_collectables()

                x_new = random.randint(-GRID_LENGTH + WORLD_SPAWN_MARGIN,
                                       GRID_LENGTH - WORLD_SPAWN_MARGIN)
                y_new = random.randint(-GRID_LENGTH + WORLD_SPAWN_MARGIN,
                                       GRID_LENGTH - WORLD_SPAWN_MARGIN)
                a[1] = x_new
                a[2] = y_new
                a[3] = random.uniform(0, 360)
                a[5] = random.uniform(0, 2 * math.pi)
                hit = True
                break
        if hit:
            continue

    # Boss hits
    if boss_animal:
        for arr in arrows[:]:
            ax, ay = arr[0], arr[1]
            bx, by = boss_animal[1], boss_animal[2]
            if math.hypot(ax - bx, ay - by) < 80:
                arrows.remove(arr)
                boss_health -= 1
                boss_animal[6] = boss_health
                create_particles(bx, by, 30, (1, 0, 0), 30)
                if boss_health <= 0:
                    score += 50
                    boss_animal = None
                break

    max_r = GRID_LENGTH - 80
    CHASE_RADIUS = 260.0
    CHASE_MULTIPLIER = 2.0

    player_hidden = False
    for bx, by, brad in bushes:
        if math.hypot(px - bx, py - by) < brad:
            player_hidden = True
            break

    for i, a in enumerate(animals):
        t_type, x, y, angle, speed, phase = a

        if i in frozen_animals:
            a[5] += 0.02
            continue

        dxp = px - x
        dyp = py - y
        distp = math.hypot(dxp, dyp)

        is_chasing = (not cheat_mode) and (distp < CHASE_RADIUS) and (not player_hidden)
        if is_chasing:
            angle = math.degrees(math.atan2(dyp, dxp))

        move_speed = speed * (CHASE_MULTIPLIER if is_chasing else 1.0)
        rad = math.radians(angle)
        x += math.cos(rad) * move_speed
        y += math.sin(rad) * move_speed

        bounced = False
        if x < -max_r or x > max_r:
            angle = (180 - angle) % 360
            x = max(-max_r, min(max_r, x))
            bounced = True
        if y < -max_r or y > max_r:
            angle = (-angle) % 360
            y = max(-max_r, min(max_r, y))
            bounced = True
        if (not bounced) and (not is_chasing) and random.random() < 0.01:
            angle += random.uniform(-40, 40)

        phase += 0.08
        a[1] = x
        a[2] = y
        a[3] = angle
        a[5] = phase

        if not game_over and player_health > 0 and not cheat_mode:
            dxp2 = px - x
            dyp2 = py - y
            dist2p = dxp2 * dxp2 + dyp2 * dyp2

            if t_type == 1:
                touch_r2 = 45 * 45
            elif t_type == 2:
                touch_r2 = 28 * 28
            else:
                touch_r2 = 35 * 35

            if dist2p < touch_r2:
                if active_shield <= 0:
                    player_health = 0
                    game_over = True
                else:
                    create_particles(px, py, 20, (0.2, 0.5, 1.0), 10)

    if boss_animal:
        b_angle = boss_animal[3]
        b_speed = boss_animal[4]
        bx, by = boss_animal[1], boss_animal[2]

        dbx = px - bx
        dby = py - by
        b_angle = math.degrees(math.atan2(dby, dbx))

        rad = math.radians(b_angle)
        bx += math.cos(rad) * b_speed * 1.5
        by += math.sin(rad) * b_speed * 1.5

        boss_animal[1] = bx
        boss_animal[2] = by
        boss_animal[3] = b_angle
        boss_animal[5] += 0.08

        if math.hypot(px - bx, py - by) < 60 and active_shield <= 0 and not cheat_mode:
            player_health = 0
            game_over = True

    glutPostRedisplay()


# -------------------------------------------------
# DISPLAY
# -------------------------------------------------
def showScreen():
    time_factor = math.sin(math.radians(time_of_day))
    if time_factor > 0:
        sky_r = 0.55
        sky_g = 0.78 - 0.3 * (1 - time_factor)
        sky_b = 0.98
    else:
        sky_r = 0.05
        sky_g = 0.05 + 0.1 * (1 + time_factor)
        sky_b = 0.15
    glClearColor(sky_r, sky_g, sky_b, 1.0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()

    draw_environment()
    draw_grid()
    draw_walls()
    draw_powerups()
    draw_collectables()
    draw_player()
    draw_bullets()
    draw_enemies()
    draw_particles()
    draw_shield_effect()

    # Boss as scaled-up animal
    if boss_animal:
        b_type, bx, by, b_angle, b_speed, b_phase, b_hp = boss_animal
        glPushMatrix()
        glTranslatef(bx, by, 0)
        glRotatef(b_angle, 0, 0, 1)
        glScalef(3, 3, 3)

        tmp_animals = animals[:]
        animals.clear()
        animals.append([b_type, 0, 0, 0, b_speed, b_phase])
        draw_enemies()
        animals.clear()
        animals.extend(tmp_animals)

        glPopMatrix()
        draw_boss_healthbar()

    draw_text(10, 770, f"<3 - {player_health}")
    draw_text(10, 740, f"Points: {score}")
    draw_text(10, 710, f"Level: {level}")

    if combo_count > 0:
        combo_color = ""
        if score_multiplier >= 5:
            combo_color = "ULTRA "
        elif score_multiplier >= 3:
            combo_color = "MEGA "
        elif score_multiplier >= 2:
            combo_color = "SUPER "
        draw_text(10, 620, f"{combo_color}COMBO x{combo_count} ({score_multiplier}X)")

    if cheat_mode:
        draw_text(10, 680, f"Arrows: {arrow_count}")
    else:
        draw_text(10, 680, f"Arrows: {arrow_count}/{max_arrows}")

    arrow_names = ["Normal", "Fire", "Ice"]
    draw_text(10, 650, f"Arrow: {arrow_names[current_arrow_type]} (Keys 1-3)")

    y_pos = 590
    if active_shield > 0:
        draw_text(10, y_pos, f"Shield: {active_shield // 60}s")
        y_pos -= 30
    if active_speed > 0:
        draw_text(10, y_pos, f"Speed: {active_speed // 60}s")
        y_pos -= 30
    if active_multishot > 0:
        draw_text(10, y_pos, f"Multi-Shot: {active_multishot // 60}s")
        y_pos -= 30

    if cheat_mode:
        draw_text(10, y_pos, "CHEAT MODE: ON")

    if game_over:
        if player_health <= 0:
            draw_text(420, 400, "GAME OVER")
        else:
            draw_text(380, 400, "OUT OF ARROWS!")
        draw_text(380, 360, f"Final Score: {score}")
        draw_text(350, 320, "Press R to Restart")

    # UI buttons
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)

    # Play/Pause button
    glBegin(GL_LINE_LOOP)
    glVertex2f(BTN_PLAY[0], BTN_PLAY[1])
    glVertex2f(BTN_PLAY[2], BTN_PLAY[1])
    glVertex2f(BTN_PLAY[2], BTN_PLAY[3])
    glVertex2f(BTN_PLAY[0], BTN_PLAY[3])
    glEnd()

    cx = (BTN_PLAY[0] + BTN_PLAY[2]) / 2.0
    cy = (BTN_PLAY[1] + BTN_PLAY[3]) / 2.0
    size = (BTN_PLAY[2] - BTN_PLAY[0]) * 0.3

    if paused or game_over:
        glBegin(GL_TRIANGLES)
        glVertex2f(cx - size * 0.4, cy - size)
        glVertex2f(cx - size * 0.4, cy + size)
        glVertex2f(cx + size, cy)
        glEnd()
    else:
        bw = size * 0.4
        bh = size
        glBegin(GL_QUADS)
        glVertex2f(cx - bw * 1.2, cy - bh)
        glVertex2f(cx - bw * 0.2, cy - bh)
        glVertex2f(cx - bw * 0.2, cy + bh)
        glVertex2f(cx - bw * 1.2, cy + bh)

        glVertex2f(cx + bw * 0.2, cy - bh)
        glVertex2f(cx + bw * 1.2, cy - bh)
        glVertex2f(cx + bw * 1.2, cy + bh)
        glVertex2f(cx + bw * 0.2, cy + bh)
        glEnd()

    # Restart button
    glBegin(GL_LINE_LOOP)
    glVertex2f(BTN_RESTART[0], BTN_RESTART[1])
    glVertex2f(BTN_RESTART[2], BTN_RESTART[1])
    glVertex2f(BTN_RESTART[2], BTN_RESTART[3])
    glVertex2f(BTN_RESTART[0], BTN_RESTART[3])
    glEnd()

    rcx = (BTN_RESTART[0] + BTN_RESTART[2]) / 2.0
    rcy = (BTN_RESTART[1] + BTN_RESTART[3]) / 2.0
    r = (BTN_RESTART[2] - BTN_RESTART[0]) * 0.35

    glBegin(GL_LINE_STRIP)
    segments = 18
    for i in range(segments + 1):
        ang = math.radians(230 - i * 260 / segments)
        glVertex2f(rcx + r * math.cos(ang),
                   rcy + r * math.sin(ang))
    glEnd()

    ah = math.radians(-20)
    tip_x = rcx + r * math.cos(ah)
    tip_y = rcy + r * math.sin(ah)
    glBegin(GL_TRIANGLES)
    glVertex2f(tip_x, tip_y)
    glVertex2f(tip_x - 6, tip_y + 4)
    glVertex2f(tip_x - 2, tip_y - 6)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glutSwapBuffers()



def main():
    spawn_environment()
    spawn_level_collectables()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Arrow Arena - ULTIMATE EDITION")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.55, 0.78, 0.98, 1.0)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()