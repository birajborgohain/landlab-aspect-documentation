September, 12, 2026: FastScape Basement and ASPECT Boundary Composition
===========================================================================

Purpose
-------

This section continues the earlier investigation of sediment representation in
FastScape/FastScapeLib and ASPECT. It records the specific questions that arose
after the initial working hypothesis about the FastScape sediment-deposition
implementation.

The main questions are:

* Is FastScape ``basement`` the same thing as sea level?
* Does ``Sea level = -2000`` create the FastScape basement field?
* How is the FastScape basement initialized and restored?
* What does ASPECT ``Boundary composition model`` mean?
* What is a Dirichlet boundary condition?
* Why does the ASPECT ``sediment_thick`` field have a boundary value?
* What does ``if(z>140e3, DZ - SeaLevel - z, 0)`` mean?
* What different values are imposed at the top and bottom boundaries?

The conclusions are based on the FastScapeLib documentation, the
FastScape--ASPECT source code, and the ASPECT parameter file used in this
experiment.

FastScape basement is not sea level
------------------------------------

A central distinction is:

.. math::

   \mathrm{sea\ level} \neq \mathrm{basement}.

FastScape has a separate internal basement state. The FastScapeLib interface
provides separate operations for topography and basement, including
``FastScape_Init_H``, ``FastScape_Set_Basement``, and
``FastScape_Copy_Basement``.

For the FastScape sediment representation,

.. math::

   H_s = h-b,

where :math:`h` is FastScape topography and :math:`b` is FastScape basement.

Therefore a lower sea level does not by itself define the basement.

Sea level in the ASPECT FastScape plugin
----------------------------------------

The parameter file contains:

.. code-block:: text

   subsection Marine parameters
     set Sea level = -2000
   end

The FastScape--ASPECT plugin describes this as sea level relative to the
ASPECT surface. A sea level of zero corresponds to the maximum ASPECT
vertical extent.

Thus ``Sea level = -2000`` is a marine reference, not the basement array.

It is used by the marine component to distinguish marine from non-marine
conditions. It does not create the FastScape basement field.

FastScape initialization and basement state
--------------------------------------------

The ASPECT FastScape source contains a separate operation:

.. code-block:: cpp

   fastscape_set_basement_(basement.data());

The source comments describe FastScape sediment as the difference between
topography and basement.

On a normal first run, however, the plugin initializes FastScape with:

.. code-block:: cpp

   std::vector<double> empty_basement, empty_silt_fraction;

   initialize_fastscape(elevation,
                        empty_basement,
                        empty_silt_fraction,
                        false);

The final argument is ``restart = false``.

Inside initialization, topography is passed using:

.. code-block:: cpp

   fastscape_init_h_(elevation.data());

The call to ``fastscape_set_basement_`` is inside the restart branch.
Therefore a normal new run does not construct a FastScape basement from
``Sea level = -2000`` and pass it to FastScape.

During restart, the previously saved basement is explicitly restored with
``fastscape_set_basement_``.

This establishes that basement is persistent FastScape state, separate from
the sea-level parameter.

Conceptually:

.. code-block:: text

       FastScape topography h
                |
                v
       +----------------+
       |   sediment     |
       +----------------+
                |
                v
       FastScape basement b

       sediment thickness:
              Hs = h - b

       separately:

       sea level SL
              |
              v
       marine / non-marine
       treatment

ASPECT compositional fields
---------------------------

The parameter file contains ten compositional fields:

.. code-block:: text

   sediment_age
   noninitial_plastic_strain
   plastic_strain
   viscous_strain
   sediment
   sediment_thick
   crust_upper
   crust_lower
   mantle_lithosphere
   asthenosphere

It also specifies:

.. code-block:: text

   set Compositional field methods = particles

Therefore ``sediment`` and ``sediment_thick`` are ASPECT compositional fields
represented using ASPECT's particle-based composition method.

They should not automatically be identified with FastScape's internal
``h``, ``b``, or ``h-b``.

Initial composition versus boundary composition
------------------------------------------------

ASPECT has separate concepts for an ``Initial composition model`` and a
``Boundary composition model``.

The initial composition model specifies composition initially inside the
computational domain.

The boundary composition model specifies composition values at selected
boundaries.

Conceptually:

.. code-block:: text

   Initial composition
          |
          v
   What composition exists
   inside the model at t = 0?


   Boundary composition
          |
          v
   What composition is prescribed
   at a selected boundary?

Boundary composition model in this experiment
---------------------------------------------

The parameter file contains:

.. code-block:: text

   subsection Boundary composition model
     set Model name = function
     set Fixed composition boundary indicators = top, bottom
     set Allow fixed composition on outflow boundaries = true
   end

This tells ASPECT to use the ``function`` boundary-composition model on the
``top`` and ``bottom`` boundaries.

The word ``fixed`` refers to prescribing a value through a Dirichlet-type
boundary condition. It does not mean that the value must be constant in time.

For example,

.. code-block:: text

   if(z>140e3, t/1e6, 0)

changes with time even though it is part of a fixed-composition boundary
condition.

Dirichlet boundary condition
----------------------------

A Dirichlet boundary condition prescribes the value of the unknown field at
the boundary.

For a generic field :math:`C`,

.. math::

   C|_{\partial\Omega}=C_{\mathrm{boundary}}.

For example,

.. math::

   T=273\ \mathrm{K}

prescribes the temperature value at a boundary.

A Neumann condition instead prescribes a derivative or flux, such as

.. math::

   \frac{\partial T}{\partial n}=0.

For the ASPECT composition problem, a boundary composition condition provides
the composition value used at a specified boundary when composition is
transported by the velocity field.

Why composition needs a boundary condition
-------------------------------------------

A compositional field is transported by the material velocity. Conceptually,

.. math::

   \frac{\partial C}{\partial t}
   +
   \mathbf{u}\cdot\nabla C=0.

The transport equation determines how composition evolves inside the domain,
but boundary information is also required where material enters or where the
chosen boundary formulation prescribes composition.

For incoming material, the solver needs to know its composition.

Thus a boundary composition condition can be viewed as:

.. code-block:: text

   material entering through boundary
                |
                v
        what composition?
                |
                v
        sediment = 1
        sediment_thick = prescribed value

The boundary condition is therefore not, by itself, a calculation of the
composition everywhere inside the domain.

Allow fixed composition on outflow boundaries
---------------------------------------------

The parameter file contains:

.. code-block:: text

   set Allow fixed composition on outflow boundaries = true

Composition prescriptions are especially important on inflow boundaries
because incoming material requires a specified composition.

This option explicitly permits the prescribed composition to remain active
even on portions of the selected boundary that are outflow boundaries.

The ten boundary expressions
----------------------------

The ten expressions correspond to the ten compositional fields in order:

.. list-table:: Mapping of compositional fields to boundary expressions
   :header-rows: 1
   :widths: 8 30 62

   * - No.
     - Compositional field
     - Boundary expression

   * - 1
     - ``sediment_age``
     - ``if(z>140e3, t/1e6, 0)``

   * - 2
     - ``noninitial_plastic_strain``
     - ``0``

   * - 3
     - ``plastic_strain``
     - ``0``

   * - 4
     - ``viscous_strain``
     - ``0``

   * - 5
     - ``sediment``
     - ``if(z>140e3, 1, 0)``

   * - 6
     - ``sediment_thick``
     - ``if(z>140e3, DZ - SeaLevel - z, 0)``

   * - 7
     - ``crust_upper``
     - ``0``

   * - 8
     - ``crust_lower``
     - ``0``

   * - 9
     - ``mantle_lithosphere``
     - ``0``

   * - 10
     - ``asthenosphere``
     - ``if(z==0.,1,0)``

This mapping is important because the ``1`` values belong to different
compositional fields.

The ``1`` in ``if(z>140e3, 1, 0)`` belongs to ``sediment``.

The ``1`` in ``if(z==0.,1,0)`` belongs to ``asthenosphere``.

Neither is the ``sediment_thick`` expression.

Meaning of ``z``
----------------

The function declares:

.. code-block:: text

   set Coordinate system = cartesian
   set Variable names = x,y,z,t

Therefore:

* ``x`` is the first spatial coordinate;
* ``y`` is the second spatial coordinate;
* ``z`` is the third spatial coordinate, the vertical Cartesian coordinate;
* ``t`` is time.

The ASPECT box has:

.. code-block:: text

   X extent = 300e3
   Y extent = 120e3
   Z extent = 150e3

so the original vertical coordinate range is approximately

.. math::

   0 \le z \le 150000\ \mathrm{m}.

The ``z`` appearing in the boundary function is the coordinate at the point
where the function is evaluated. It is not itself the ``sediment_thick`` field.

The expression ``if(z>140e3, DZ - SeaLevel - z, 0)``
------------------------------------------------------

The sixth expression is:

.. code-block:: text

   if(z>140e3, DZ - SeaLevel - z, 0)

with:

.. code-block:: text

   DZ = 150e3
   SeaLevel = -2000

Therefore:

.. math::

   f(z)=
   \begin{cases}
   150000-(-2000)-z, & z>140000,\\
   0, & z\le140000.
   \end{cases}

or:

.. math::

   f(z)=
   \begin{cases}
   152000-z, & z>140000,\\
   0, & z\le140000.
   \end{cases}

The three arguments of ``if`` are:

.. code-block:: text

   if(condition, value_if_true, value_if_false)

Thus the expression means:

* if ``z`` is greater than 140 km, calculate ``DZ - SeaLevel - z``;
* otherwise return zero.

The result is assigned as the boundary value of the sixth compositional
field, ``sediment_thick``.

Thus ``z`` is the input coordinate and ``sediment_thick`` is the field
receiving the resulting boundary value.

Top boundary
------------

The top of the original ASPECT box is:

.. math::

   z=150000\ \mathrm{m}.

At the top,

.. math::

   z>140000,

so the nonzero branch is used:

.. math::

   sediment\_thick
   =
   150000-(-2000)-150000
   =
   2000\ \mathrm{m}.

Therefore:

.. math::

   \boxed{sediment\_thick=2000\ \mathrm{m}}.

At the same top boundary,

.. math::

   sediment=1

and

.. math::

   sediment\_age=t/10^6.

Thus the top boundary prescribes sediment-related composition.

Bottom boundary
---------------

The bottom of the ASPECT box is:

.. math::

   z=0.

For ``sediment_thick``,

.. math::

   0>140000

is false, so:

.. math::

   \boxed{sediment\_thick=0}.

The ``sediment`` expression also gives:

.. math::

   sediment=0.

The tenth expression is:

.. code-block:: text

   if(z==0.,1,0)

which belongs to ``asthenosphere``.

Therefore at the bottom:

.. math::

   \boxed{asthenosphere=1}.

Top and bottom do not receive one common sediment-thickness value
------------------------------------------------------------------

The statement

.. code-block:: text

   set Fixed composition boundary indicators = top, bottom

does not mean that the same numerical value is imposed on both boundaries.

The same boundary function is evaluated at the coordinates of the respective
boundary points.

For ``sediment_thick``:

.. list-table:: Boundary evaluation of ``sediment_thick``
   :header-rows: 1
   :widths: 25 25 50

   * - Boundary
     - ``z``
     - Prescribed ``sediment_thick``

   * - Top
     - 150 km
     - 2 km

   * - Bottom
     - 0 km
     - 0

The different values arise because the function depends on ``z``.

The ``1`` values belong to different fields
--------------------------------------------

At the top, ``z=150 km``:

.. code-block:: text

   sediment_age        = t / 1e6
   sediment            = 1
   sediment_thick      = 2000 m
   asthenosphere       = 0

At the bottom, ``z=0``:

.. code-block:: text

   sediment_age        = 0
   sediment            = 0
   sediment_thick      = 0
   asthenosphere       = 1

Therefore the ``1`` does not mean ``sediment_thick = 1`` at either boundary.

What the expression does and does not mean
-------------------------------------------

The expression

.. code-block:: text

   if(z>140e3, DZ - SeaLevel - z, 0)

does mean:

.. code-block:: text

   take vertical coordinate z
                |
                v
   check whether z > 140 km
                |
          +-----+-----+
          |           |
         yes          no
          |           |
          v           v
      152 km - z      0
          |
          v
   prescribe this as
   sediment_thick
   at the boundary

It does not mean:

* ``z`` is the sediment thickness;
* ``z`` is automatically the current FastScape topographic elevation;
* ``SeaLevel = -2000`` is the FastScape basement;
* the expression calculates sediment thickness throughout the entire
  3-D domain; or
* the expression directly calculates FastScape's internal basement.

Instead, it is a boundary prescription for the ASPECT compositional field
``sediment_thick``.

Evolving surface versus coordinate ``z``
-----------------------------------------

The ``z`` in the parsed boundary function is the Cartesian coordinate at the
point where the function is evaluated.

It should not automatically be interpreted as

.. math::

   z=h(x,y,t),

where :math:`h` is the evolving surface elevation.

The evolving ASPECT/FastScape surface and the Cartesian coordinate used by
the parsed function are conceptually different quantities.

The mathematical function itself would return a negative value if evaluated
at ``z=160 km``:

.. math::

   152-160=-8\ \mathrm{km}.

However, the original ASPECT box in this experiment has ``Z extent = 150 km``,
so ``z=160 km`` lies outside the original computational domain.

Relationship to the FastScape sediment representation
------------------------------------------------------

The investigation identifies two separate sediment representations:

.. code-block:: text

   FastScape
   ----------
   topography h
   basement b
   sediment thickness approximately h - b


   ASPECT
   ------
   compositional field: sediment
   compositional field: sediment_thick
   particle-based composition method

The ASPECT boundary condition

.. code-block:: text

   if(z>140e3, DZ - SeaLevel - z, 0)

belongs to the second representation.

It should not be used as evidence that FastScape constructs its basement
from the ASPECT ``Sea level`` parameter.

Three quantities that must not be conflated
-------------------------------------------

.. list-table:: Three distinct quantities
   :header-rows: 1
   :widths: 25 35 40

   * - Quantity
     - Meaning in this experiment
     - Role

   * - ``Sea level = -2000``
     - FastScape marine sea-level reference
     - Determines marine versus non-marine treatment

   * - FastScape ``basement``
     - Internal FastScape surface beneath sediment
     - Used with topography to represent sediment thickness

   * - ASPECT ``sediment_thick``
     - ASPECT compositional field
     - Receives the boundary value from the function and is transported with
       the ASPECT composition framework

Current conclusion
------------------

The source-level investigation leads to the following conclusions.

#. ``Sea level = -2000`` is **not** the FastScape basement.

#. FastScape has a separate basement state, represented by a basement array
   and accessed through dedicated FastScapeLib routines.

#. On a normal first run, the FastScape--ASPECT plugin initializes the
   topographic surface with ``FastScape_Init_H`` rather than constructing and
   passing a basement from the sea-level parameter.

#. On restart, the plugin explicitly restores the previously saved basement
   using ``FastScape_Set_Basement``.

#. In the ASPECT parameter file, ``sediment_thick`` is the sixth compositional
   field.

#. The expression ``if(z>140e3, DZ - SeaLevel - z, 0)`` is the boundary
   prescription for that sixth field.

#. ``z`` is the third Cartesian spatial coordinate in the 3-D model. It is the
   input coordinate to the function, not the sediment-thickness field itself.

#. At the top of the original 150-km-high box, ``z=150 km``, so the prescribed
   ``sediment_thick`` value is 2 km.

#. At the bottom, ``z=0``, the prescribed ``sediment_thick`` value is zero.

#. The ``1`` associated with the top boundary belongs to ``sediment``, while
   the ``1`` at the bottom belongs to ``asthenosphere``.

#. The Boundary composition model is a boundary condition for the ASPECT
   composition-advection problem. It does not itself calculate FastScape's
   basement.

Next source-level question
--------------------------

The next unresolved question is not the meaning of the ASPECT boundary
function. That part is now clear.

The next question is:

   **Exactly how does FastScapeLib initialize and subsequently update its
   internal basement array after ``FastScape_Init_H``?**

That requires tracing the FastScapeLib implementation of initialization,
erosion, deposition, uplift, and sediment-transport routines rather than
inferring the basement from the ASPECT ``Sea level`` or ``sediment_thick``
parameters.
