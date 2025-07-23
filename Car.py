from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import numpy as np
import math

rotation_matrix = np.identity(4, dtype=np.float32)
# Initialize rotation matrix to rotate around the X-axis by 20 degrees
last_pos = None

zoom_distance = -10.0

win_width = 800
win_height = 600
pivot = np.array([0.0, 0.0, 0.0], dtype=np.float32)
local_translation = np.array([0.0, 0.0, 0.0], dtype=np.float32)
is_dragging = False
drag_mode = None
# Toggle display of light source spheres
show_light_spheres = True
enable_fog = False
wireframe_mode = False
show_axes = True

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.05, 0.05, 0.1, 1.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    # Enable lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

    # Light 0: White light
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 5.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

    # Light 1: Blue-ish light
    glLightfv(GL_LIGHT1, GL_POSITION, [-5.0, 3.0, -5.0, 1.0])
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.6, 0.6, 1.0, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.6, 0.6, 1.0, 1.0])

    # Enable color material and link glColor to material
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Add specular reflection to all materials
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)

    # Normalize normals after transformations like scaling
    glEnable(GL_NORMALIZE)

    # Fog settings (optional)
    glFogfv(GL_FOG_COLOR, [0.1, 0.1, 0.2, 1.0])
    glFogi(GL_FOG_MODE, GL_EXP)
    glFogf(GL_FOG_DENSITY, 0.03)
    glHint(GL_FOG_HINT, GL_NICEST)

def reshape(w, h):
    global win_width, win_height
    win_width, win_height = w, h
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    #guy change hte prespective to zoom in and out
    gluPerspective(60.0, w / h, 0.1, 100.0)

   # gluPerspective(60.0, w / h, 0.5, 500.0)  # Adjust near and far planes for better depth handling gUY Change

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def map_to_sphere(x, y):
    x = 2.0 * x / win_width - 1.0
    y = 1.0 - 2.0 * y / win_height
    length2 = x * x + y * y
    if length2 > 1.0:
        norm = 1.0 / math.sqrt(length2)
        return np.array([x * norm, y * norm, 0.0])
    else:
        return np.array([x, y, math.sqrt(1.0 - length2)])

def mouse_click(button, state, x, y):
    global last_pos, zoom_distance, is_dragging, drag_mode
    if state == GLUT_DOWN:
        if button == 3:
            zoom_distance += 0.3
        elif button == 4:
            zoom_distance -= 0.3
        elif button == GLUT_LEFT_BUTTON:
            last_pos = map_to_sphere(x, y)
            is_dragging = True
            drag_mode = 'rotate'
        elif button == GLUT_RIGHT_BUTTON:
            last_pos = np.array([x, y])
            is_dragging = True
            drag_mode = 'translate'
    elif state == GLUT_UP:
        is_dragging = False
        drag_mode = None

def mouse_motion(x, y):
    global last_pos, rotation_matrix, pivot
    if not is_dragging or last_pos is None:
        return
    if drag_mode == 'rotate':
        curr_pos = map_to_sphere(x, y)
        axis = np.cross(last_pos, curr_pos)
        angle = np.arccos(np.clip(np.dot(last_pos, curr_pos), -1.0, 1.0))
        if np.linalg.norm(axis) < 1e-6:
            return
        axis = axis / np.linalg.norm(axis)
        rot = rotation_matrix_axis_angle(axis, np.degrees(angle))
        rotation_matrix = rot @ rotation_matrix
        last_pos = curr_pos
    elif drag_mode == 'translate':
        dx = (x - last_pos[0]) / win_width * 4.0
        dy = (y - last_pos[1]) / win_height * 4.0
        pivot[0] += dx
        pivot[1] -= dy
        last_pos = np.array([x, y])
    glutPostRedisplay()

def rotation_matrix_axis_angle(axis, angle_deg):
    angle_rad = np.radians(angle_deg)
    x, y, z = axis
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    t = 1 - c
    return np.array([
        [t*x*x + c,   t*x*y - s*z, t*x*z + s*y, 0],
        [t*x*y + s*z, t*y*y + c,   t*y*z - s*x, 0],
        [t*x*z - s*y, t*y*z + s*x, t*z*z + c,   0],
        [0, 0, 0, 1]
    ], dtype=np.float32)

def draw_axes(length=3):
    glLineWidth(0.4)
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(length, 0, 0)
    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, length, 0)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, length)
    glEnd()
    glLineWidth(1.0)

def draw_chassis():
    glPushMatrix()
    glTranslatef(-0.5, 0, 0)
    glColor3f(0.25, 0.25, 0.25)
    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_CULL_FACE)

    # Define bottom and top face widths
    bottom_w = 2.6
    top_w = 3
    height = -0.6
    depth = 1.4

    glBegin(GL_QUADS)

    # Bottom face
    glNormal3f(0, -1, 0)
    glVertex3f(-bottom_w, 0, depth)
    glVertex3f(bottom_w, 0, depth)
    glVertex3f(bottom_w, 0, -depth)
    glVertex3f(-bottom_w, 0, -depth)

    # Top face
    glNormal3f(0, 1, 0)
    glVertex3f(-top_w, height, depth)
    glVertex3f(top_w, height, depth)
    glVertex3f(top_w, height, -depth)
    glVertex3f(-top_w, height, -depth)

    # Front face
    glNormal3f(0, 0, 1)
    glVertex3f(-bottom_w, 0, depth)
    glVertex3f(bottom_w, 0, depth)
    glVertex3f(top_w, height, depth)
    glVertex3f(-top_w, height, depth)

    # Back face
    glNormal3f(0, 0, -1)
    glVertex3f(-bottom_w, 0, -depth)
    glVertex3f(bottom_w, 0, -depth)
    glVertex3f(top_w, height, -depth)
    glVertex3f(-top_w, height, -depth)

    # Left face
    glNormal3f(-1, 0, 0)
    glVertex3f(-bottom_w, 0, depth)
    glVertex3f(-bottom_w, 0, -depth)
    glVertex3f(-top_w, height, -depth)
    glVertex3f(-top_w, height, depth)

    # Right face
    glNormal3f(1, 0, 0)
    glVertex3f(bottom_w, 0, depth)
    glVertex3f(bottom_w, 0, -depth)
    glVertex3f(top_w, height, -depth)
    glVertex3f(top_w, height, depth)

    glEnd()
    glPopAttrib()
    glPopMatrix()

def draw_roof():
    glPushMatrix()
    glTranslatef(0, 0, 0)
    glColor3f(0.3, 0.3, 0.3)
    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_CULL_FACE)

    # Define bottom and top face widths
    bottom_w = 1.4
    top_w = 1
    height = 0.6
    depth = 1.4

    glBegin(GL_QUADS)

    # Bottom face
    glNormal3f(0, -1, 0)
    glVertex3f(-bottom_w, 0, depth)
    glVertex3f(bottom_w, 0, depth)
    glVertex3f(bottom_w, 0, -depth)
    glVertex3f(-bottom_w, 0, -depth)

    # Top face
    glNormal3f(0, 1, 0)
    glVertex3f(-top_w, height, depth)
    glVertex3f(top_w, height, depth)
    glVertex3f(top_w, height, -depth)
    glVertex3f(-top_w, height, -depth)

    # Front face
    glNormal3f(0, 0, 1)
    glVertex3f(-bottom_w, 0, depth)
    glVertex3f(bottom_w, 0, depth)
    glVertex3f(top_w, height, depth)
    glVertex3f(-top_w, height, depth)

    # Back face
    glNormal3f(0, 0, -1)
    glVertex3f(-bottom_w, 0, -depth)
    glVertex3f(bottom_w, 0, -depth)
    glVertex3f(top_w, height, -depth)
    glVertex3f(-top_w, height, -depth)

    # Left face
    glNormal3f(-1, 0, 0)
    glVertex3f(-bottom_w, 0, depth)
    glVertex3f(-bottom_w, 0, -depth)
    glVertex3f(-top_w, height, -depth)
    glVertex3f(-top_w, height, depth)

    # Right face
    glNormal3f(1, 0, 0)
    glVertex3f(bottom_w, 0, depth)
    glVertex3f(bottom_w, 0, -depth)
    glVertex3f(top_w, height, -depth)
    glVertex3f(top_w, height, depth)

    glEnd()

    glPopAttrib()
    glPopMatrix()

def draw_wheel(x, y, z):
    quad = gluNewQuadric()
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(90, 0, 1, 90)
    glColor3f(0.8, 0.2, 0.2)
    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_CULL_FACE)
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluCylinder(quad, 0.4, 0.4, 0.3, 30, 1)
    glNormal3f(0, 0, -1)
    gluDisk(quad, 0, 0.4, 50, 1)
    glTranslatef(0, 0, 0.3)
    glNormal3f(0, 0, 1)
    gluDisk(quad, 0, 0.4, 50, 1)
    glPopAttrib()
    glPopMatrix()

def draw_light(x, y, z):
    quad = gluNewQuadric()
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(90, 0, 1, 0)
    glColor3f(1.0, 1.0, 0.7)
    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_CULL_FACE)
    gluQuadricNormals(quad, GLU_SMOOTH)
    gluCylinder(quad, 0.15, 0.15, 0.2, 20, 1)
    glNormal3f(0, 0, -1)
    gluDisk(quad, 0, 0.15, 20, 1)
    glPopAttrib()
    glPopMatrix()

# Draw small spheres at light source positions. 
def draw_light_spheres():
    if not show_light_spheres:
        return  # Skip drawing spheres if toggled off

    # White light sphere at LIGHT0 position
    glPushMatrix()
    glTranslatef(5.0, 5.0, 5.0)
    glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 1.0, 1.0, 1.0])  # Emit white light
    glutSolidSphere(0.2, 20, 20)
    glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])  # Reset emission
    glPopMatrix()

    # Blue light sphere at LIGHT1 position
    glPushMatrix()
    glTranslatef(-5.0, 3.0, -5.0)
    glMaterialfv(GL_FRONT, GL_EMISSION, [0.6, 0.6, 1.0, 1.0])  # Emit blue light
    glutSolidSphere(0.2, 20, 20)
    glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])  # Reset emission
    glPopMatrix()

def draw_window_front():
    glPushMatrix()
    glColor3f(1, 1, 1)
    glTranslatef(-1.4, 0, 0)
    glRotatef(327, 0, 0, 1)
    glRotatef(270, 0, 1, 0)
    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_CULL_FACE)
    glBegin(GL_QUADS)
    glNormal3f(0, 0, 1)
    glVertex3f(-1.2, 0, 0)
    glVertex3f(1.2, 0, 0)
    glVertex3f(1.2, 0.55, 0)
    glVertex3f(-1.2, 0.55, 0)
    glEnd()
    glPopAttrib()
    glPopMatrix()

def draw_window_back():
    glPushMatrix()
    glColor3f(1, 1, 1)
    glTranslatef(1.4, 0, 0)
    glRotatef(33, 0, 0, 1)
    glRotatef(90, 0, 1, 0)
    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_CULL_FACE)
    glBegin(GL_QUADS)
    glNormal3f(0, 0, -1)
    glVertex3f(-1.2, 0, 0)
    glVertex3f(1.2, 0, 0)
    glVertex3f(1.2, 0.55, 0)
    glVertex3f(-1.2, 0.55, 0)
    glEnd()
    glPopAttrib()
    glPopMatrix()

def draw_windows(x, y, z, is_left):
    shift = -0.1 if is_left else -0.2
    glTranslatef(shift, 0, 0)
    glColor3f(1, 1, 1)  # Window color
    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_CULL_FACE)

    glBegin(GL_QUADS)
    # Front window (more angled trapezoid)
    glVertex3f(x + shift + -0.65, y, z)    # Bottom-left
    glVertex3f(x + shift + 0.1, y, z)    # Bottom-right
    glVertex3f(x + shift + 0.1, y + 0.4, z)    # Top-right
    glVertex3f(x + shift + -0.3, y + 0.4, z)    # Top-left

    # Back window (less angled trapezoid)
    glVertex3f(x + -shift, y, z)     # Bottom-left
    glVertex3f(x + -shift + 0.75, y, z)     # Bottom-right
    glVertex3f(x + -shift + 0.45, y + 0.4, z)     # Top-right
    glVertex3f(x + -shift, y + 0.4, z)     # Top-left
    
    glEnd()
    glPopAttrib()

def draw_doors(x, y, z, is_left):
    glColor3f(0.1, 0.1, 0.1)

    # Dimensions for slanted trapezoidal doors
    outer_bottom = -1.2 if is_left else 1.2
    inner_bottom =  0.15  # Center merge at x = 0
    inner_top    = -0.15 if is_left else 0.15
    outer_top    = -0.8 if is_left else 0.9

    # Shared verticals
    bottom_y = 0.0
    top_y    = 0.45
    peak_y   = 0.95

    if is_left:
        # Front door (left side)
        glBegin(GL_LINE_LOOP)
        glVertex3f(x + outer_bottom + 0.4, y + bottom_y, z)  # Outer bottom
        glVertex3f(x + inner_bottom, y + bottom_y, z)  # Inner bottom (center)
        glVertex3f(x + inner_top + 0.3,    y + top_y + 0.5,    z)  # Inner top
        glVertex3f(x + outer_top + 0.4,    y + peak_y,   z)  # Outer angled top
        glVertex3f(x + outer_bottom + 0.4, y + top_y,    z)  # Outer top back to side
        glEnd()

        # Rear door (left side)
        glBegin(GL_LINE_LOOP)
        glVertex3f(x + inner_bottom, y + bottom_y, z)  # Inner bottom (center)
        glVertex3f(x - outer_bottom - 0.5, y + bottom_y, z)  # Outer bottom
        glVertex3f(x - outer_bottom, y + top_y,    z)  # Outer top
        glVertex3f(x - outer_top,    y + peak_y,   z)  # Outer angled top
        glVertex3f(x + inner_top + 0.3,    y + top_y + 0.5,    z)  # Inner top
        glEnd()
    else:
        # Same for right side (mirrored geometry)
        glBegin(GL_LINE_LOOP)
        glVertex3f(x + outer_bottom - 0.5, y + bottom_y, z)
        glVertex3f(x + inner_bottom, y + bottom_y, z)
        glVertex3f(x + inner_top,    y + top_y + 0.5,    z)
        glVertex3f(x + outer_top - 0.1,    y + peak_y,   z)
        glVertex3f(x + outer_bottom, y + top_y,    z)
        glEnd()

        glBegin(GL_LINE_LOOP)
        glVertex3f(x + inner_bottom, y + bottom_y, z)
        glVertex3f(x - outer_bottom + 0.3, y + bottom_y, z)
        glVertex3f(x - outer_bottom + 0.3, y + top_y,    z)
        glVertex3f(x - outer_top + 0.4,    y + peak_y,   z)
        glVertex3f(x + inner_top,    y + top_y + 0.5,    z)
        glEnd()

def draw_car():
    draw_chassis()
    draw_roof()

    draw_window_front()
    draw_window_back()
    
    # Right side
    draw_windows(0.1, 0, 1.401, is_left=False)
    draw_doors(0, -0.45, 1.401, is_left=False)

    # Left side
    draw_windows(0.1, 0, -1.401, is_left=True)
    draw_doors(0, -0.45, -1.401, is_left=True)

    for x in [-2, 1.4]:
        for z in [-1.5, 1.2]:
            draw_wheel(x, -0.6, z)

    draw_light(-3.1, -0.3, 0.7)
    draw_light(-3.1, -0.3, -0.7)

def draw_ground():
    glPushMatrix()

    glDisable(GL_LIGHTING)  # Disable lighting for the ground so it stays flat-colored
    glColor3f(0.2, 0.3, 0.2)
    glEnable(GL_NORMALIZE)
    glPushAttrib(GL_ENABLE_BIT)
    glDisable(GL_CULL_FACE)

    size_x = 8
    size_z = 6
    y = -1.02

    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-size_x, y, -size_z)
    glVertex3f(size_x, y, -size_z)
    glVertex3f(size_x, y, size_z)
    glVertex3f(-size_x, y, size_z)
    glEnd()
    glPopAttrib()
    glEnable(GL_LIGHTING)
    glEnable(GL_NORMALIZE)
    glPopMatrix()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, zoom_distance)
    glTranslatef(*pivot)

    # Set light positions BEFORE rotating the scene
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 5.0, 1.0])
    glLightfv(GL_LIGHT1, GL_POSITION, [-5.0, 3.0, -5.0, 1.0])

    # Apply rotation and translation after setting light
    glMultMatrixf(rotation_matrix.T)
    glTranslatef(*local_translation)

    # Handle fog activation
    if enable_fog:
        glEnable(GL_FOG)
    else:
        glDisable(GL_FOG)

    # Handle show axes activation
    if show_axes:
        draw_axes()

    # Handle Polygon activation
    if wireframe_mode:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glEnable(GL_NORMALIZE)
    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(1.0, 1.0)

    draw_ground()
    glEnable(GL_NORMALIZE)
    glDisable(GL_POLYGON_OFFSET_FILL)

    draw_car()
    draw_light_spheres()
    draw_position_label()
    glutSwapBuffers()

def timer(v):
    glutPostRedisplay()
    glutTimerFunc(33, timer, 0) # Register timer to be called again in ~33 ms (30 FPS)

def keyboard(key, x, y):
    global local_translation, show_light_spheres, enable_fog, wireframe_mode, show_axes
    step = 0.1
    key = key.decode('utf-8').lower()

    if key == 'w':  # Move forward (zoom in)
        local_translation += np.dot(rotation_matrix[:3, :3], [0, 0, -step])
    elif key == 's':  # Move backward (zoom out)
        local_translation += np.dot(rotation_matrix[:3, :3], [0, 0, step])
    elif key == 'd':  # Move right
        local_translation += np.dot(rotation_matrix[:3, :3], [step, 0, 0])
    elif key == 'z':  # Move left
        local_translation += np.dot(rotation_matrix[:3, :3], [-step, 0, 0])
    elif key == 'q':  # Move up
        local_translation += np.dot(rotation_matrix[:3, :3], [0, step, 0])
    elif key == 'e':  # Move down
        local_translation += np.dot(rotation_matrix[:3, :3], [0, -step, 0])
    elif key == 'a':  # Toggle display of XYZ axes
        show_axes = not show_axes
    elif key == 'l':  # Toggle visibility of light source spheres
        show_light_spheres = not show_light_spheres
    elif key == 'f':  # Toggle fog effect on/off
        enable_fog = not enable_fog
    elif key == 'p':  # Toggle between wireframe and filled polygon modes
        wireframe_mode = not wireframe_mode

    glutPostRedisplay()

# Draw the current local position (X, Y, Z) on screen
def draw_position_label():
    #print of data
    glDisable(GL_LIGHTING)  # Disable lighting for HUD text
    glColor3f(1.0, 1.0, 1.0)  # White text
    # Convert position to string with 2 decimal points
    label = f"x: {local_translation[0]:.2f}, y: {local_translation[1]:.2f}, z: {local_translation[2]:.2f}"

    # Set the window position (from bottom-left corner)
    glDisable(GL_LIGHTING)  # Disable lighting for text
    glColor3f(1.0, 1.0, 1.0)  # White color for text
    glWindowPos2f(10, win_height - 20)  # Top-left corner with margin

    for ch in label:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    glEnable(GL_LIGHTING)  # Re-enable lighting after text

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(win_width, win_height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"3D Car Model")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse_click)
    glutMotionFunc(mouse_motion)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, timer, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()