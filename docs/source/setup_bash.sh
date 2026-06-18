#!/bin/bash

# Base directories
BASE_DIR="Tools"
DOC_DIR="$BASE_DIR/coupling_ASPECT-fastscape"

# Create directories
mkdir -p $DOC_DIR/{00_overview,01_cpp_basics,02_aspect_side,03_plugin_layer,04_fastscape_side,05_coupling_cycle,06_code_walkthrough,07_equations_and_physics,08_hands_on,09_summary}

echo "Directories created..."

# -----------------------------
# Helper function to write files
# -----------------------------
write_file() {
  FILE=$1
  CONTENT=$2
  echo "$CONTENT" > $FILE
}

# -----------------------------
# MAIN INDEX
# -----------------------------
write_file "$DOC_DIR/index.rst" "
FastScape–ASPECT Coupling
=========================

.. toctree::
   :maxdepth: 2

   00_overview/index
   01_cpp_basics/index
   02_aspect_side/index
   03_plugin_layer/index
   04_fastscape_side/index
   05_coupling_cycle/index
   06_code_walkthrough/index
   07_equations_and_physics/index
   08_hands_on/index
   09_summary/index
"

# -----------------------------
# 00 OVERVIEW
# -----------------------------
write_file "$DOC_DIR/00_overview/index.rst" "
Overview
========

.. toctree::
   :maxdepth: 1

   coupling_concept
   developer_design_philosophy
"

write_file "$DOC_DIR/00_overview/coupling_concept.rst" "
Coupling Concept
================

::

    ASPECT (FEM)
        ↓
    Plugin Layer
        ↓
    FastScape (Grid)
        ↓
    Updated Topography
        ↓
    Mesh Deformation

.. math::

    \\frac{\\partial h}{\\partial t} = U - E + D \\nabla^2 h
"

write_file "$DOC_DIR/00_overview/developer_design_philosophy.rst" "
Developer Philosophy
====================

- Separate physics solvers
- Couple via surface elevation
- Maintain modularity

.. math::

    U = v_z
"

# -----------------------------
# 01 CPP BASICS
# -----------------------------
write_file "$DOC_DIR/01_cpp_basics/index.rst" "
C++ Basics
==========

.. toctree::
   :maxdepth: 1

   cpp_for_aspect
   extern_c_interface
   mpi_basics
"

write_file "$DOC_DIR/01_cpp_basics/cpp_for_aspect.rst" "
C++ for ASPECT
==============

ASPECT uses object-oriented C++.

.. code-block:: cpp

   class FastScape : public Interface<dim> {};
"

write_file "$DOC_DIR/01_cpp_basics/extern_c_interface.rst" "
C++–Fortran Interface
=====================

.. code-block:: cpp

   extern \"C\" {
       void fastscape_execute_step_();
   }
"

write_file "$DOC_DIR/01_cpp_basics/mpi_basics.rst" "
MPI Basics
==========

.. code-block:: cpp

   Utilities::MPI::this_mpi_process(comm);
"

# -----------------------------
# 02 ASPECT SIDE
# -----------------------------
write_file "$DOC_DIR/02_aspect_side/index.rst" "
ASPECT Side
===========

.. toctree::
   :maxdepth: 1

   aspect_velocity_field
   surface_extraction
   mesh_deformation_interface
"

write_file "$DOC_DIR/02_aspect_side/aspect_velocity_field.rst" "
ASPECT Velocity Field
=====================

.. math::

    \\nabla \\cdot \\sigma + \\rho g = 0

.. math::

    U = v_z
"

write_file "$DOC_DIR/02_aspect_side/surface_extraction.rst" "
Surface Extraction
==================

Extract surface nodes from FEM mesh.
"

write_file "$DOC_DIR/02_aspect_side/mesh_deformation_interface.rst" "
Mesh Deformation
================

.. math::

    v_z = \\frac{\\Delta h}{\\Delta t}
"

# -----------------------------
# 03 PLUGIN LAYER
# -----------------------------
write_file "$DOC_DIR/03_plugin_layer/index.rst" "
Plugin Layer
============

.. toctree::
   :maxdepth: 1

   plugin_architecture
   data_transfer
   timestep_control
   boundary_conditions
"

write_file "$DOC_DIR/03_plugin_layer/plugin_architecture.rst" "
Plugin Architecture
===================

Bridge between ASPECT and FastScape.
"

write_file "$DOC_DIR/03_plugin_layer/data_transfer.rst" "
Data Transfer
=============

Interpolation between grids.
"

write_file "$DOC_DIR/03_plugin_layer/timestep_control.rst" "
Timestep Control
================

.. math::

    \\Delta t_{FS} = \\frac{\\Delta t_{ASPECT}}{N}
"

write_file "$DOC_DIR/03_plugin_layer/boundary_conditions.rst" "
Boundary Conditions
===================

Handles domain edges.
"

# -----------------------------
# 04 FASTSCAPE SIDE
# -----------------------------
write_file "$DOC_DIR/04_fastscape_side/index.rst" "
FastScape Side
==============

.. toctree::
   :maxdepth: 1

   fastscape_equations
   grid_and_discretization
   erosion_models
"

write_file "$DOC_DIR/04_fastscape_side/fastscape_equations.rst" "
FastScape Equations
===================

.. math::

    \\frac{\\partial h}{\\partial t} = U - K A^m S^n
"

write_file "$DOC_DIR/04_fastscape_side/grid_and_discretization.rst" "
Grid
====

Structured grid system.
"

write_file "$DOC_DIR/04_fastscape_side/erosion_models.rst" "
Erosion Models
==============

.. math::

    E = K A^m S^n
"

# -----------------------------
# 05 COUPLING
# -----------------------------
write_file "$DOC_DIR/05_coupling_cycle/index.rst" "
Coupling Cycle
==============

.. toctree::
   :maxdepth: 1

   step_by_step_coupling
   velocity_to_uplift
   topography_feedback
"

write_file "$DOC_DIR/05_coupling_cycle/step_by_step_coupling.rst" "
Step-by-Step Coupling
=====================

1. Solve ASPECT
2. Run FastScape
3. Update mesh
"

write_file "$DOC_DIR/05_coupling_cycle/velocity_to_uplift.rst" "
Velocity to Uplift
==================

.. math::

    U = v_z
"

write_file "$DOC_DIR/05_coupling_cycle/topography_feedback.rst" "
Topography Feedback
===================

.. math::

    v_z = \\frac{\\Delta h}{\\Delta t}
"

# -----------------------------
# 06 CODE WALKTHROUGH
# -----------------------------
write_file "$DOC_DIR/06_code_walkthrough/index.rst" "
Code Walkthrough
================

.. toctree::
   :maxdepth: 1

   initialize_function
   compute_velocity_constraints
   execute_fastscape
"

write_file "$DOC_DIR/06_code_walkthrough/initialize_function.rst" "
Initialize
==========

Setup FastScape grid.
"

write_file "$DOC_DIR/06_code_walkthrough/compute_velocity_constraints.rst" "
Compute Velocity Constraints
============================

Core coupling logic.
"

write_file "$DOC_DIR/06_code_walkthrough/execute_fastscape.rst" "
Execute FastScape
=================

Run solver step.
"

# -----------------------------
# 07 EQUATIONS
# -----------------------------
write_file "$DOC_DIR/07_equations_and_physics/index.rst" "
Equations
=========

.. toctree::
   :maxdepth: 1

   governing_equations
   stream_power_law
   diffusion_equation
"

write_file "$DOC_DIR/07_equations_and_physics/governing_equations.rst" "
Governing Equations
===================

.. math::

    \\frac{\\partial h}{\\partial t} = U - E + D \\nabla^2 h
"

write_file "$DOC_DIR/07_equations_and_physics/stream_power_law.rst" "
Stream Power Law
================

.. math::

    E = K A^m S^n
"

write_file "$DOC_DIR/07_equations_and_physics/diffusion_equation.rst" "
Diffusion
=========

.. math::

    \\frac{\\partial h}{\\partial t} = D \\nabla^2 h
"

# -----------------------------
# 08 HANDS ON
# -----------------------------
write_file "$DOC_DIR/08_hands_on/index.rst" "
Hands-on
========

.. toctree::
   :maxdepth: 1

   modify_uplift
   add_new_parameter
   minimal_plugin_example
"

write_file "$DOC_DIR/08_hands_on/modify_uplift.rst" "
Modify Uplift
=============

Change uplift in code.
"

write_file "$DOC_DIR/08_hands_on/add_new_parameter.rst" "
Add Parameter
=============

Extend plugin.
"

write_file "$DOC_DIR/08_hands_on/minimal_plugin_example.rst" "
Minimal Plugin
==============

Basic example.
"

echo "✅ FastScape–ASPECT documentation structure created successfully!"
