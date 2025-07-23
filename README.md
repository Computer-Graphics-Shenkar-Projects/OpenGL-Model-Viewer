# OpenGL Car Model & Viewer
## Overview

This project is a basic OpenGL application designed to model and render a 3D car. It supports interactive viewing, lighting and wireframe toggles. The car model is built using OpenGL primitives and transformations, and serves as a base for future exercises or extensions.

The project was developed as part of an academic exercise focused on practicing OpenGL techniques such as modeling, transformations, lighting and interactive camera controls using a virtual trackball system.

**Features**

* 3D car model with chassis, doors, windows, tires, and front lights

* Interactive viewing with mouse rotation and zoom

* Real-time rendering at 30 FPS

* Switch between wireframe and filled polygon modes

* Toggle coordinate axes and light source markers

* Modular design using matrix stack and hierarchical transformations

* Perspective projection with lighting and material effects

**Controls**

  **1.** Mouse Controls:
  
      * Rotate model: Drag the mouse (Virtual Trackball)

      * Zoom in/out: Mouse wheel scroll

      * Resize window: Automatically adjusts the aspect ratio without distortion

  **2.** Keyboard Controls:
  
      * w - Move camera forward (zoom in)

      * s - Move camera backward (zoom out)

      * d - Move camera right

      * z - Move camera left

      * q - Move camera up

      * e - Move camera down

      * a - Toggle XYZ axes display on/off

      * l - Toggle light source spheres visibility

      * f - Toggle fog effect on/off

      * p - Toggle between wireframe and filled polygon rendering modes

These controls allow for full 3D navigation, visual debugging, and display mode switching while exploring the car model.

**Modeling**

The car model is constructed using OpenGL primitives, including:

* Filled polygons for chassis and windows

* Wireframe lines for doors

* GLU cylinders and disks for tires and front lights

Symmetry is achieved using scaling and translation, avoiding redundant modeling. For example, a single tire or headlight is modeled and rendered multiple times using mirrored transformations.

**Lighting**

The scene includes at least two positional light sources. Lighting demonstrates both diffuse and specular effects using proper normals and material settings. Spheres at light positions serve as visual markers (toggled with the 'l' key), emitting light independently of other lighting effects.

**Viewing System**

The interactive camera is based on a Virtual Trackball implementation:

* Projects 2D mouse movements onto a sphere

* Computes the corresponding 3D rotation matrix

* Applies accumulated rotations to the model view matrix

Zooming is implemented via camera translation along the z-axis in a perspective projection setup.

**Technical Details**

* Back-face culling is always enabled for better rendering performance and realism

* GL_NORMALIZE is enabled to maintain correct lighting under scaling

* Projection and viewport transformations ensure the model is centered and well-scaled
