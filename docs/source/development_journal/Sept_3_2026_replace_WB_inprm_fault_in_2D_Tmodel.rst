September 3, 2026: Replacing the World Builder Fault Definition with an ASPECT Function
=========================================================================================

Overview
--------

The original model used the World Builder (WB) file to initialize a fault-related
composition structure. The purpose of this modification is to remove the dependency
on the World Builder file and reproduce the same intended fault structure directly
inside the ASPECT ``.prm`` file.

The original World Builder configuration defined a fault feature and used a smooth
composition model to modify two compositional fields. The corresponding fault
geometry and a linear composition transition are now expressed analytically using
ASPECT's ``Initial composition model`` with the ``function`` model.

After this modification, the World Builder file is no longer required to initialize
the fault-related compositional fields. The ``.prm`` file contains the complete
initial composition definition needed to initialize the fault structure.


Original World Builder Configuration
------------------------------------

The original World Builder file contained the following fault definition:

.. code-block:: json

   {
       "version":"1.0",
       "cross section":[[0,0.8e5],[3.2e5,0.8e5]],
       "features":
       [
           {
               "model":"fault",
               "name":"fault1",
               "dip point":[3.2e5,2e5],
               "min depth":0,
               "max depth":1e5,
               "coordinates":[[110e3,4e5],[110e3,0]],
               "segments":
               [
                   {
                       "length":0.7e5,
                       "thickness":[8000],
                       "angle":[60]
                   }
               ],
               "temperature models":
               [
                   {
                       "model":"uniform",
                       "temperature":273
                   }
               ],
               "composition models":
               [
                   {
                       "model":"smooth",
                       "compositions":[6,8],
                       "operation":"add",
                       "side distance fault center":4000,
                       "center fractions":[1.5,1.5],
                       "side fractions":[0.5,0.5]
                   }
               ]
           }
       ]
   }


Important World Builder Parameters
-----------------------------------

The parameters relevant to the composition-based fault initialization are:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - World Builder parameter
     - Meaning used in the translation
   * - ``coordinates`` at ``x = 110e3``
     - Fault reference position at ``x = 110 km``.
   * - ``angle = 60``
     - Fault dip angle of 60 degrees.
   * - ``length = 0.7e5``
     - Fault segment length of 70 km.
   * - ``thickness = 8000``
     - World Builder fault thickness parameter. This value is not explicitly used in the analytical function below.
   * - ``compositions = [6,8]``
     - Modify compositional fields 6 and 8.
   * - ``center fractions = [1.5,1.5]``
     - Composition at the fault center is 1.5 for both selected fields.
   * - ``side fractions = [0.5,0.5]``
     - Composition away from the fault is 0.5 for both selected fields.
   * - ``side distance fault center = 4000``
     - The linear transition is applied over 4 km perpendicular distance from the fault centerline.
   * - ``operation = add``
     - World Builder applies the fault composition model as an additive composition model.


Compositional Fields Affected by the Fault
-------------------------------------------

The ASPECT model contains 14 compositional fields. The relevant field numbering is:

.. list-table::
   :header-rows: 1
   :widths: 15 40 45

   * - Field
     - Name
     - Role in the fault replacement
   * - 0
     - ``ve_stress_xx``
     - Unchanged; initialized to zero.
   * - 1
     - ``ve_stress_yy``
     - Unchanged; initialized to zero.
   * - 2
     - ``ve_stress_xy``
     - Unchanged; initialized to zero.
   * - 3
     - ``ve_stress_xx_old``
     - Unchanged; initialized to zero.
   * - 4
     - ``ve_stress_yy_old``
     - Unchanged; initialized to zero.
   * - 5
     - ``ve_stress_xy_old``
     - Unchanged; initialized to zero.
   * - 6
     - ``plastic_strain``
     - Modified by the fault function.
   * - 7
     - ``noninitial_plastic_strain``
     - Unchanged; initialized to zero.
   * - 8
     - ``viscous_strain``
     - Modified by the fault function.
   * - 9
     - ``crust``
     - Unchanged; initialized using the original horizontal-layer function.
   * - 10
     - ``mantle_lithosphere``
     - Unchanged; initialized using the original horizontal-layer function.
   * - 11
     - ``sediment_age``
     - Unchanged; initialized to zero.
   * - 12
     - ``deposition_depth``
     - Unchanged; initialized to zero.
   * - 13
     - ``sediment``
     - Unchanged; initialized to zero.

The World Builder composition model specifically references fields 6 and 8.
Therefore, these are the two fields that need to be replaced by analytical
expressions in the ASPECT parameter file.


Why a Function-Based Replacement Can Be Used
---------------------------------------------

The cookbook demonstrates that an initial composition structure can be defined
directly in ASPECT using the ``function`` initial composition model.

For example, the cookbook uses an ``if`` expression to define an initially
localized strain region:

.. code-block:: prm

   subsection Initial composition model
     set Model name = function

     subsection Function
       set Variable names = x,y
       set Function expression = 0; \
                                 if(x>50.e3 && x<150.e3 && y>50.e3, 0.5 + rand_seed(1), 0); \
                                 if(y>=80.e3, 1, 0); \
                                 if(y<80.e3 && y>=60.e3, 1, 0); \
                                 if(y<60.e3, 1, 0);
     end
   end

The important principle is that the initial composition does not have to be supplied
by World Builder. It can instead be written as a mathematical function of the
coordinates ``x`` and ``y``.

The cookbook therefore provides the basis for replacing the World Builder
initialization with an analytical ASPECT function. It does not, however, provide
the exact function for this particular fault. The fault-specific function below is
constructed from the geometry and composition parameters of the original World
Builder configuration.

The cookbook supplied for this model uses this same function-based approach for
prescribing an initial strain/weak zone. The present conversion applies that
approach to the specific dipping fault in the World Builder model.


Defining the Fault Geometry Mathematically
-------------------------------------------

The World Builder fault is referenced at ``x = 110 km`` and has a dip angle of
60 degrees.

The fault origin is therefore taken as

.. math::

   (x_0,y_0)=(110000,0).

For a 60 degree dip,

.. math::

   \cos(60^\circ)=0.5

and

.. math::

   \sin(60^\circ)=0.8660254.

Instead of describing the fault directly in terms of ``x`` and ``y``, the
coordinates are transformed into two coordinates relative to the dipping fault.

The first coordinate is the distance measured along the fault:

.. math::

   s = (x-110000)\cos(60^\circ) + y\sin(60^\circ).

Using the numerical values gives

.. math::

   s = 0.5(x-110000)+0.8660254y.

The second coordinate is the perpendicular distance from the fault centerline:

.. math::

   d = -(x-110000)\sin(60^\circ)+y\cos(60^\circ).

Therefore,

.. math::

   d=-0.8660254(x-110000)+0.5y.

These two coordinates are useful because ``s`` describes where a point lies along
the fault, while ``d`` describes how far the point is from the fault.


Restricting the Function to the 70-km Fault Segment
---------------------------------------------------

The World Builder fault segment has a length of

.. math::

   L=0.7\times10^5=70000\ {\rm m}=70\ {\rm km}.

Therefore, the point is considered to be along the fault segment only when

.. math::

   0\leq s\leq70000.

In the ASPECT function this becomes:

.. code-block:: text

   0.5*(x-110.e3)+0.8660254*y>=0 &&
   0.5*(x-110.e3)+0.8660254*y<=70.e3

The ``&&`` operator means logical ``AND``. Both conditions must therefore be
true.

This prevents the dipping fault function from extending indefinitely beyond the
70-km fault segment.


Defining the 4-km Composition Transition
-----------------------------------------

The World Builder composition model specifies:

.. code-block:: text

   center fractions = [1.5,1.5]
   side fractions   = [0.5,0.5]
   side distance fault center = 4000

For the replacement, the transition is intentionally chosen to be linear.

At the fault center,

.. math::

   |d|=0,

so the composition is

.. math::

   C=1.5.

At a distance of 4 km,

.. math::

   |d|=4000,

the composition reaches

.. math::

   C=0.5.

A linear function connecting these two values is

.. math::

   C(d)=1.5-\frac{|d|}{4000}.

Thus the resulting values are:

.. list-table::
   :header-rows: 1
   :widths: 30 30

   * - Distance from fault center
     - Composition
   * - 0 km
     - 1.50
   * - 1 km
     - 1.25
   * - 2 km
     - 1.00
   * - 3 km
     - 0.75
   * - 4 km
     - 0.50
   * - Greater than 4 km
     - 0.50

The use of ``abs(d)`` makes the transition symmetric on both sides of the fault
centerline.


Combining the Fault Geometry and Composition
---------------------------------------------

The three conditions used in the final function are therefore:

1. The point is after the beginning of the fault: ``s >= 0``.
2. The point is before the end of the fault: ``s <= 70.e3``.
3. The point is within 4 km of the fault centerline: ``abs(d) < 4.e3``.

When all three conditions are true, the function returns

.. math::

   1.5-\frac{|d|}{4000}.

When any of the conditions is false, the function returns ``0.5``.

In compact form, the function is

.. code-block:: text

   if(s>=0 && s<=70.e3 && abs(d)<4.e3,
      1.5-abs(d)/4.e3,
      0.5)


Final ASPECT Initial Composition Model
--------------------------------------

The resulting ``Initial composition model`` can therefore be written directly
in the ASPECT ``.prm`` file:

.. code-block:: prm

   subsection Initial composition model
     set Model name = function

     subsection Function
       set Coordinate system = cartesian
       set Variable names = x,y

       set Function expression = 0; \
                                 0; \
                                 0; \
                                 0; \
                                 0; \
                                 0; \
                                 if(0.5*(x-110.e3)+0.8660254*y>=0 && \
                                    0.5*(x-110.e3)+0.8660254*y<=70.e3 && \
                                    abs(-0.8660254*(x-110.e3)+0.5*y)<4.e3, \
                                    1.5-abs(-0.8660254*(x-110.e3)+0.5*y)/4.e3, \
                                    0.5); \
                                 0; \
                                 if(0.5*(x-110.e3)+0.8660254*y>=0 && \
                                    0.5*(x-110.e3)+0.8660254*y<=70.e3 && \
                                    abs(-0.8660254*(x-110.e3)+0.5*y)<4.e3, \
                                    1.5-abs(-0.8660254*(x-110.e3)+0.5*y)/4.e3, \
                                    0.5); \
                                 if(y>=50.e3, 1, 0); \
                                 if(y<50.e3, 1, 0); \
                                 0; \
                                 0; \
                                 0
     end
   end


How the 14 Expressions Correspond to the Fields
------------------------------------------------

The semicolon-separated expressions correspond to the 14 compositional fields
in the same order in which they are listed in the ``Compositional fields``
subsection.

The resulting mapping is:

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Field
     - ASPECT field
     - Initial function
   * - 0
     - ``ve_stress_xx``
     - ``0``
   * - 1
     - ``ve_stress_yy``
     - ``0``
   * - 2
     - ``ve_stress_xy``
     - ``0``
   * - 3
     - ``ve_stress_xx_old``
     - ``0``
   * - 4
     - ``ve_stress_yy_old``
     - ``0``
   * - 5
     - ``ve_stress_xy_old``
     - ``0``
   * - 6
     - ``plastic_strain``
     - Linear dipping-fault function
   * - 7
     - ``noninitial_plastic_strain``
     - ``0``
   * - 8
     - ``viscous_strain``
     - Linear dipping-fault function
   * - 9
     - ``crust``
     - ``if(y>=50.e3, 1, 0)``
   * - 10
     - ``mantle_lithosphere``
     - ``if(y<50.e3, 1, 0)``
   * - 11
     - ``sediment_age``
     - ``0``
   * - 12
     - ``deposition_depth``
     - ``0``
   * - 13
     - ``sediment``
     - ``0``

The same fault expression is used for fields 6 and 8 because the World Builder
configuration assigns identical center and side fractions to both fields.


Removing the World Builder Dependency
-------------------------------------

The original parameter file contains:

.. code-block:: prm

   set World builder file = ada_lovelace.wb

and the initial composition model contains:

.. code-block:: prm

   subsection Initial composition model
     set List of model names = function, world builder
     set List of model operators = add, add

The standalone model no longer requires either of these World Builder components.

The initial composition model is instead:

.. code-block:: prm

   subsection Initial composition model
     set Model name = function

     subsection Function
       ...
     end
   end

The following line can therefore be removed from the global parameters:

.. code-block:: prm

   set World builder file = ada_lovelace.wb

The ``world builder`` entry can also be removed from the initial composition
model because the fault-related initialization is now contained entirely in the
ASPECT function.


Resulting Model Dependency
--------------------------

Before the modification, the initialization sequence was conceptually:

.. code-block:: text

   ASPECT .prm
       |
       +---- Initial composition function
       |
       +---- World Builder file
                    |
                    +---- Fault geometry
                    |
                    +---- Fault composition
                              |
                              +---- fields 6 and 8

After the modification, the sequence becomes:

.. code-block:: text

   ASPECT .prm
       |
       +---- Initial composition function
                    |
                    +---- Fault geometry expressed analytically
                    |
                    +---- Linear composition transition
                              |
                              +---- field 6: plastic_strain
                              |
                              +---- field 8: viscous_strain

Thus the fault initialization no longer depends on an external World Builder
file.


Interpretation and Scope of the Replacement
--------------------------------------------

This conversion reproduces the intended fault geometry using an analytical
description: a 60-degree dipping fault beginning at ``x = 110 km`` and extending
70 km along the fault, with a symmetric 4-km composition transition on either
side of the fault centerline.

The composition transition has deliberately been chosen to be linear from 1.5
at the fault center to 0.5 at 4 km distance. This is the prescribed
approximation used in this standalone formulation.

The World Builder ``thickness = 8000`` parameter is not explicitly included in
the analytical expression. The effective 8-km-wide transition region instead
comes from applying the 4-km distance on both sides of the fault centerline.

Therefore, the standalone function should be understood as a direct analytical
translation of the specified fault geometry and the selected linear
composition behavior, rather than a claim that every internal detail of the
World Builder ``smooth`` implementation is mathematically identical.

The resulting ``.prm`` can consequently be initialized without loading the
World Builder fault file, provided that no other part of the parameter file
depends on World Builder.