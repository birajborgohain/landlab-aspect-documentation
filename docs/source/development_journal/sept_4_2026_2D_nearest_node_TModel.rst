September 4, 2026: Landlab T-Model Grid and Fixed Node Coordinate
====================================================================

.. figure:: /_images/deposition/T-model.png
    :align: center
    :width: 100%

This document explains how the Landlab ``RasterModelGrid`` is positioned and how
the fixed node used in the T-model is located. The goal is to understand the
difference between the **lower-left corner of the Landlab grid** and the
**coordinate of the fixed node**.

Model Parameters
----------------

The Landlab model uses the following parameters:

.. code-block:: python

   x_extent = 220e3      # 220,000 m = 220 km
   y_extent = 100e3      # 100,000 m = 100 km
   spacing  = 250.0      # 250 m = 0.25 km

These values describe the horizontal dimensions and resolution of the Landlab
grid.

.. list-table::
   :header-rows: 1
   :widths: 30 30

   * - Parameter
     - Value
   * - ``x_extent``
     - 220,000 m = 220 km
   * - ``y_extent``
     - 100,000 m = 100 km
   * - ``spacing``
     - 250 m = 0.25 km

Creating the Landlab Grid
-------------------------

The Landlab grid is created with:

.. code-block:: python

   model_grid = landlab.RasterModelGrid(
       (nrows, ncols),
       xy_spacing=(spacing, spacing),
       xy_of_lower_left=(
           -2*spacing,
           -y_extent / 2 - 2*spacing
       )
   )

There are three important pieces of information here:

.. code-block:: text

   (nrows, ncols)
       → number of rows and columns

   xy_spacing=(spacing, spacing)
       → distance between neighboring nodes

   xy_of_lower_left=(...)
       → physical coordinate of the lower-left corner of the grid

Grid Spacing
------------

The grid spacing is:

.. code-block:: python

   spacing = 250.0

This means that neighboring Landlab nodes are separated by:

.. math::

   \Delta x = \Delta y = 250\ {\rm m}.

Therefore, moving one node to the right changes ``x`` by 250 m, and moving one
node upward changes ``y`` by 250 m.

The Lower-Left Corner
---------------------

The lower-left corner is specified by:

.. code-block:: python

   xy_of_lower_left = (
       -2*spacing,
       -y_extent / 2 - 2*spacing
   )

The x-coordinate is:

.. math::

   x_{\rm LL} = -2(250) = -500\ {\rm m}.

Therefore:

.. math::

   x_{\rm LL}=-0.5\ {\rm km}.

The y-coordinate is:

.. math::

   y_{\rm LL}
   =
   -\frac{100000}{2}-2(250)
   =
   -50500\ {\rm m}.

Therefore:

.. math::

   y_{\rm LL}=-50.5\ {\rm km}.

The lower-left corner is therefore:

.. math::

   \boxed{(x,y)=(-500\ {\rm m},-50500\ {\rm m})}

or:

.. math::

   \boxed{(x,y)=(-0.5\ {\rm km},-50.5\ {\rm km})}.

This is the **starting coordinate of the Landlab grid**. It is not the location
of the fixed node.

The Fixed-Node Code
-------------------

The T-model contains:

.. code-block:: python

   node_id = model_grid.find_nearest_node(
       [x_extent / 2, -y_extent / 2 - spacing]
   )

   model_grid.status_at_node[node_id] = (
       model_grid.BC_NODE_IS_FIXED_VALUE
   )

   elevation[node_id] = 0

There are three separate operations here.

First: Define the Target Coordinate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The coordinate passed to ``find_nearest_node()`` is:

.. code-block:: python

   [x_extent / 2, -y_extent / 2 - spacing]

Using the model parameters:

.. math::

   x=\frac{220000}{2}=110000\ {\rm m}=110\ {\rm km}

and:

.. math::

   y=-\frac{100000}{2}-250
     =-50250\ {\rm m}
     =-50.25\ {\rm km}.

Therefore, the target coordinate is:

.. math::

   \boxed{(x,y)=(110000,-50250)\ {\rm m}}

or:

.. math::

   \boxed{(x,y)=(110,-50.25)\ {\rm km}}.

Second: Find the Nearest Landlab Node
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The code:

.. code-block:: python

   model_grid.find_nearest_node(
       [110000, -50250]
   )

asks Landlab:

.. code-block:: text

   Which existing grid node is closest to
   the coordinate (110000 m, -50250 m)?

Landlab returns the numerical ID of that node:

.. code-block:: python

   node_id

Conceptually:

.. code-block:: text

   physical coordinate
          |
          v
   (110000, -50250) m
          |
          | find_nearest_node()
          v
      node_id
          |
          v
   existing Landlab grid node

Because the grid spacing is 250 m and the requested coordinate is aligned with
the grid, the target coordinate should correspond to an existing raster-grid
node.

Third: Make the Node Fixed
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The next line is:

.. code-block:: python

   model_grid.status_at_node[node_id] = (
       model_grid.BC_NODE_IS_FIXED_VALUE
   )

This changes the status of that particular node to a fixed-value boundary
condition.

The following line:

.. code-block:: python

   elevation[node_id] = 0

sets the elevation of that node to:

.. math::

   \boxed{0\ {\rm m}}.

Together, the three lines mean:

.. code-block:: text

   Find the node near (110 km, -50.25 km)
                     |
                     v
            identify its node ID
                     |
                     v
          make that node fixed-value
                     |
                     v
          set its elevation to 0 m

Relationship Between the Grid Origin and the Fixed Node
--------------------------------------------------------

It is important not to confuse these two coordinates.

The lower-left corner is:

.. math::

   \boxed{(-0.5,-50.5)\ {\rm km}}

while the fixed node is:

.. math::

   \boxed{(110,-50.25)\ {\rm km}}.

They represent two different locations.

.. list-table::
   :header-rows: 1
   :widths: 35 30 30

   * - Location
     - x
     - y
   * - Lower-left corner
     - -0.5 km
     - -50.5 km
   * - Fixed-node target
     - 110 km
     - -50.25 km

Why Is the Fixed Node 250 m Above the Bottom?
----------------------------------------------

The bottom boundary of the grid has:

.. math::

   y=-50.5\ {\rm km}.

The fixed node has:

.. math::

   y=-50.25\ {\rm km}.

The difference is:

.. math::

   -50.25-(-50.5)=0.25\ {\rm km}.

Since:

.. math::

   0.25\ {\rm km}=250\ {\rm m},

the fixed node is exactly **one grid spacing above the bottom boundary**.

The fixed node is also located at:

.. math::

   x=110\ {\rm km},

which is the center of the nominal 220-km x-extent.

Distance from the Left Edge
---------------------------

The left edge of the Landlab grid is:

.. math::

   x=-0.5\ {\rm km}.

The fixed node is:

.. math::

   x=110\ {\rm km}.

Therefore, the horizontal distance from the left edge to the fixed node is:

.. math::

   110-(-0.5)=110.5\ {\rm km}.

So the fixed node is:

.. code-block:: text

   110.5 km from the left edge

and:

.. code-block:: text

   250 m above the bottom edge.

Simple Sketch
-------------

A simplified plan-view representation is:

.. code-block:: text

                         y
                         ↑

       y = +49.5 km     ┌───────────────────────────────┐
                         │                               │
                         │                               │
                         │                               │
                         │                               │
                         │                               │
                         │                               │
                         │                               │
                         │                               │
                         │              ●                │
                         │              ↑                │
                         │              │                │
       y = -50.5 km     └───────────────────────────────┘
                        x = -0.5 km          x = 219.5 km
                                      →
                                      x

                                  ●
                                  │
                                  │ Fixed node
                                  │
                           (110 km, -50.25 km)

The important dimensions are:

.. code-block:: text

   x extent = 220 km
   y extent = 100 km
   grid spacing = 0.25 km

   lower-left corner = (-0.5 km, -50.5 km)

   fixed node = (110 km, -50.25 km)

The Coordinate Difference
-------------------------

There are two coordinate calculations that should be kept separate.

The first calculation determines where the **Landlab grid begins**:

.. code-block:: python

   xy_of_lower_left = (
       -2*spacing,
       -y_extent / 2 - 2*spacing
   )

which gives:

.. math::

   \boxed{(-0.5,-50.5)\ {\rm km}}.

The second calculation determines where Landlab should **look for the fixed
node**:

.. code-block:: python

   [
       x_extent / 2,
       -y_extent / 2 - spacing
   ]

which gives:

.. math::

   \boxed{(110,-50.25)\ {\rm km}}.

These are not the same point.

Conceptual Interpretation
--------------------------

The easiest way to think about the code is:

.. code-block:: text

   1. Build the Landlab grid
              |
              v
      lower-left corner
       (-0.5, -50.5) km
              |
              v
   2. Define a target location
       (110, -50.25) km
              |
              v
   3. Find the nearest grid node
              |
              v
   4. Make that node fixed-value
              |
              v
   5. Set its elevation to 0 m

Thus, the code is **not moving the origin of the grid** to
``(110 km, -50.25 km)``. The grid still begins at
``(-0.5 km, -50.5 km)``.

Instead, it selects one existing node within that grid and assigns it a special
fixed-value condition.

Important Point for the T-Model Discussion
-------------------------------------------

For the T-model, the important observation is that the fixed node is located
near the **bottom boundary of the Landlab horizontal grid**:

.. math::

   (x,y)=(110,-50.25)\ {\rm km}.

The fixed-node code specifies a Landlab ``(x,y)`` coordinate. It does not
explicitly specify the vertical ``z`` coordinate of the ASPECT model.

Therefore, before using this boundary condition as an explanation for the
3D problem, it is important to establish why the original T-model selected
this particular node and what physical or numerical purpose the fixed
``elevation = 0`` condition was intended to serve.
