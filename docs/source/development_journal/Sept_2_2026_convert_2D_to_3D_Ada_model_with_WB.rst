September 2, 2026: Converting 2D T-Model to 3D ASPECT Model Conversion, Ada model with World Builder
=====================================================================================================

Overview
--------

The original ASPECT--Landlab T-Model was developed as a two-dimensional
(2D) model. The goal of the present modification was to convert the
T-Model into a three-dimensional (3D) ASPECT model while retaining the
main physical formulation and the existing ASPECT--Landlab coupling.

The conversion required more than changing the model dimension from
``2`` to ``3``. Several parts of the ASPECT parameter file depend directly
on the spatial dimension, the number of velocity components, the number
of stress components, and the number of compositional fields.

The major modifications were made to:

* model dimension;
* model geometry;
* coordinate variables;
* viscoelastic stress fields;
* total number of compositional fields;
* initial composition;
* boundary composition;
* initial temperature;
* boundary velocity;
* mesh deformation boundaries;
* composition-threshold mesh refinement;
* compositional heating.

Several errors appeared during the conversion because portions of the
original 2D parameter file still contained 2D assumptions or lists with
the old number of entries.

The purpose of this document is to record the complete conversion
process, including the changes made, the reasons for those changes, and
the errors encountered.


1. Changing the Model Dimension
-------------------------------

The first and most fundamental change was to change the model dimension
from 2D to 3D.

The 3D model uses:

.. code-block:: text

   set Dimension = 3

In the 2D model, the spatial coordinate system was based on two
coordinates:

.. math::

   (x,y)

The 3D model uses three coordinates:

.. math::

   (x,y,z)

The coordinate meanings in the new model are:

.. list-table:: Coordinate system
   :header-rows: 1
   :widths: 15 30 45

   * - Coordinate
     - Direction
     - Physical meaning
   * - ``x``
     - Horizontal
     - Horizontal model length
   * - ``y``
     - Horizontal
     - Second horizontal direction
   * - ``z``
     - Vertical
     - Vertical/depth direction

This change affects every function in the parameter file that uses
spatial coordinates.


2. Converting the Geometry from 2D to 3D
----------------------------------------

The geometry was changed to an ASPECT ``box`` geometry.

The new configuration is:

.. code-block:: text

   subsection Geometry model
     set Model name = box

     subsection Box
       set X repetitions = 110
       set Y repetitions = 40
       set Z repetitions = 50

       set X extent      = 320e3
       set Y extent      = 80e3
       set Z extent      = 100e3
     end
   end

The resulting physical domain is:

.. math::

   L_x = 320~\mathrm{km}

.. math::

   L_y = 80~\mathrm{km}

.. math::

   L_z = 100~\mathrm{km}

The geometry can be summarized as follows.

.. list-table:: 3D box geometry
   :header-rows: 1
   :widths: 20 25 20 35

   * - Direction
     - Extent
     - Repetitions
     - Approximate base spacing
   * - ``x``
     - ``320 km``
     - ``110``
     - ``2.91 km``
   * - ``y``
     - ``80 km``
     - ``40``
     - ``2.00 km``
   * - ``z``
     - ``100 km``
     - ``50``
     - ``2.00 km``

The approximate base-cell spacing is calculated as

.. math::

   \Delta x = \frac{320~\mathrm{km}}{110}
            \approx 2.91~\mathrm{km},

.. math::

   \Delta y = \frac{80~\mathrm{km}}{40}
            = 2~\mathrm{km},

and

.. math::

   \Delta z = \frac{100~\mathrm{km}}{50}
            = 2~\mathrm{km}.

Therefore, the computational domain is now

.. math::

   0 \leq x \leq 320~\mathrm{km},

.. math::

   0 \leq y \leq 80~\mathrm{km},

and

.. math::

   0 \leq z \leq 100~\mathrm{km}.


3. Why the Geometry Change Affects Other Parts of the Model
------------------------------------------------------------

Changing the geometry introduces a new spatial direction. This means
that several quantities that were vectors or tensors in 2D must now be
represented in 3D.

For example, a velocity vector changes from

.. math::

   \mathbf{v}_{2D} = (v_x,v_y)

to

.. math::

   \mathbf{v}_{3D} = (v_x,v_y,v_z).

Similarly, the stress tensor becomes a full three-dimensional symmetric
tensor with six independent components:

.. math::

   \boldsymbol{\sigma}
   =
   \begin{pmatrix}
   \sigma_{xx} & \sigma_{xy} & \sigma_{xz}\\
   \sigma_{xy} & \sigma_{yy} & \sigma_{yz}\\
   \sigma_{xz} & \sigma_{yz} & \sigma_{zz}
   \end{pmatrix}.

The six independent stress components are

.. math::

   \sigma_{xx},
   \sigma_{yy},
   \sigma_{zz},
   \sigma_{xy},
   \sigma_{xz},
   \sigma_{yz}.

This is the main reason that the compositional-field structure had to
be changed substantially.


4. Increasing the Number of Compositional Fields
------------------------------------------------

The 3D model uses:

.. code-block:: text

   set Number of fields = 20

This increase was required by the viscoelastic formulation.

During the conversion, ASPECT produced the following important error:

.. code-block:: text

   Rheology model Elasticity requires 3+3 in 2D or 6+6 in 3D
   fields of type stress.

This error indicates that the 3D elasticity formulation requires six
current stress components and six previous/old stress components.

Therefore:

.. math::

   6 + 6 = 12

stress fields are required.

The remaining fields are used for strain quantities and material or
sediment-related quantities.


5. Final 20 Compositional Fields
--------------------------------

The final compositional-field configuration is:

.. code-block:: text

   subsection Compositional fields
     set Number of fields = 20

     set Names of fields = ve_stress_xx, \
                           ve_stress_yy, \
                           ve_stress_zz, \
                           ve_stress_xy, \
                           ve_stress_xz, \
                           ve_stress_yz, \
                           ve_stress_xx_old, \
                           ve_stress_yy_old, \
                           ve_stress_zz_old, \
                           ve_stress_xy_old, \
                           ve_stress_xz_old, \
                           ve_stress_yz_old, \
                           plastic_strain, \
                           noninitial_plastic_strain, \
                           viscous_strain, \
                           crust, \
                           mantle_lithosphere, \
                           sediment_age, \
                           deposition_depth, \
                           sediment

     set Types of fields = stress, \
                           stress, \
                           stress, \
                           stress, \
                           stress, \
                           stress, \
                           stress, \
                           stress, \
                           stress, \
                           stress, \
                           stress, \
                           stress, \
                           strain, \
                           strain, \
                           strain, \
                           chemical composition, \
                           chemical composition, \
                           generic, \
                           generic, \
                           chemical composition
   end

The complete field ordering is:

.. list-table:: 20 compositional fields
   :header-rows: 1
   :widths: 8 32 25 35

   * - No.
     - Field
     - Type
     - Purpose
   * - 1
     - ``ve_stress_xx``
     - ``stress``
     - Current normal stress
   * - 2
     - ``ve_stress_yy``
     - ``stress``
     - Current normal stress
   * - 3
     - ``ve_stress_zz``
     - ``stress``
     - Current normal stress
   * - 4
     - ``ve_stress_xy``
     - ``stress``
     - Current shear stress
   * - 5
     - ``ve_stress_xz``
     - ``stress``
     - Current shear stress
   * - 6
     - ``ve_stress_yz``
     - ``stress``
     - Current shear stress
   * - 7
     - ``ve_stress_xx_old``
     - ``stress``
     - Previous normal stress
   * - 8
     - ``ve_stress_yy_old``
     - ``stress``
     - Previous normal stress
   * - 9
     - ``ve_stress_zz_old``
     - ``stress``
     - Previous normal stress
   * - 10
     - ``ve_stress_xy_old``
     - ``stress``
     - Previous shear stress
   * - 11
     - ``ve_stress_xz_old``
     - ``stress``
     - Previous shear stress
   * - 12
     - ``ve_stress_yz_old``
     - ``stress``
     - Previous shear stress
   * - 13
     - ``plastic_strain``
     - ``strain``
     - Plastic strain
   * - 14
     - ``noninitial_plastic_strain``
     - ``strain``
     - Non-initial plastic strain
   * - 15
     - ``viscous_strain``
     - ``strain``
     - Viscous strain
   * - 16
     - ``crust``
     - ``chemical composition``
     - Crust material
   * - 17
     - ``mantle_lithosphere``
     - ``chemical composition``
     - Mantle lithosphere
   * - 18
     - ``sediment_age``
     - ``generic``
     - Sediment age
   * - 19
     - ``deposition_depth``
     - ``generic``
     - Deposition depth
   * - 20
     - ``sediment``
     - ``chemical composition``
     - Sediment material


6. Initial Composition Model
----------------------------

The original 2D model used two coordinate variables.

The 3D model now uses:

.. code-block:: text

   set Variable names = x,y,z

The active initial composition function is:

.. code-block:: text

   set Function expression = 0; 0; 0; 0; 0; 0; \
                             0; 0; 0; 0; 0; 0; \
                             0; 0; 0; \
                             if (z>=50.e3, 1, 0); \
                             if (z<50.e3, 1, 0); \
                             0; 0; 0

There are exactly 20 expressions.

The mapping is:

.. list-table:: Initial composition mapping
   :header-rows: 1
   :widths: 15 35 50

   * - Field
     - Expression
     - Initial condition
   * - 1--12
     - ``0``
     - All stress fields initially zero
   * - 13--15
     - ``0``
     - Strain fields initially zero
   * - 16
     - ``if(z>=50.e3,1,0)``
     - Crust above the 50 km interface
   * - 17
     - ``if(z<50.e3,1,0)``
     - Mantle-lithosphere region below the interface
   * - 18--20
     - ``0``
     - Sediment-related fields initially zero

The important 3D change is the use of ``z`` to define the vertical
material structure.


7. Error Related to the Initial Composition
--------------------------------------------

When the number of compositional fields was increased, the initial
composition function also had to be expanded.

If ASPECT has:

.. code-block:: text

   set Number of fields = 20

then the initial composition function must provide the corresponding
number of expressions.

Keeping the old shorter 2D expression after increasing the field count
causes a field-number mismatch.

Therefore, the following must be kept consistent:

.. code-block:: text

   Number of fields
           =
   Number of initial composition expressions

For the current model:

.. code-block:: text

   20 = 20


8. Boundary Composition Model
-----------------------------

The boundary composition model was also changed to use the 3D
coordinate system.

The configuration is:

.. code-block:: text

   subsection Boundary composition model
     set Model name = function
     set Fixed composition boundary indicators = top, bottom
     set Allow fixed composition on outflow boundaries = true

     subsection Function
       set Coordinate system   = cartesian
       set Variable names      = x,y,z,t
       set Function constants  = DZ = 100e3, SeaLevel = 0

       set Function expression = 0; 0; 0; 0; 0; 0; \
                                 0; 0; 0; 0; 0; 0; \
                                 0; 0; 0; \
                                 if(z<1e3, 1, 0); \
                                 if(z>75e3, t/1e6, 0); \
                                 if(z>75e3, DZ - SeaLevel - z, 0); \
                                 if(z>75e3, 1, 0); \
                                 0
     end
   end

The variables changed from the 2D form to:

.. code-block:: text

   x,y,z,t

The addition of ``z`` is required because the boundary composition
conditions now operate on the 3D geometry.


9. Boundary Composition Field Count
------------------------------------

The boundary composition function contains 20 expressions.

The first fifteen expressions correspond to the stress and strain
fields:

.. code-block:: text

   0; 0; 0; 0; 0; 0;
   0; 0; 0; 0; 0; 0;
   0; 0; 0;

The remaining expressions correspond to the material and sediment
fields.

This was necessary because the original boundary composition function
had fewer expressions based on the original field count.

A key rule during the conversion is therefore:

.. code-block:: text

   20 compositional fields
            ->
   20 boundary-composition expressions


10. Initial Temperature Model
-----------------------------

The original 2D temperature model used:

.. code-block:: text

   set Variable names = x,y

and calculated depth using:

.. code-block:: text

   h-y

In the 3D model, the vertical direction is ``z``. Therefore, the
temperature function was changed to:

.. code-block:: text

   set Variable names = x,y,z

and:

.. code-block:: text

   h-z

The new vertical model uses:

.. code-block:: text

   set Function constants = h=100e3, ts1=273, ts2=683, ts3=993, \
                            A1=1.e-6, A2=0.25e-6, A3=0.0, \
                            k1=2.5, k2=2.5, k3=2.5, \
                            qs1=0.06125, qs2=0.04125, qs3=0.03625

The complete expression is:

.. code-block:: text

   set Function expression = if( (h-z)<=30.e3, \
                                 ts1 + (qs1/k1)*(h-z) - (A1*(h-z)*(h-z))/(2.0*k1), \
                                 if( (h-z)>30.e3 && (h-z)<=50.e3, \
                                     ts2 + (qs2/k2)*(h-z-30.e3) - (A2*(h-z-30.e3)*(h-z-30.e3))/(2.0*k2), \
                                     ts3 + (qs3/k3)*(h-z-50.e3) - (A3*(h-z-50.e3)*(h-z-50.e3))/(2.0*k3) ) );


11. Temperature Model Changes
-----------------------------

The main changes to the temperature model are:

.. list-table:: 2D-to-3D temperature changes
   :header-rows: 1
   :widths: 30 30 40

   * - Original 2D model
     - New 3D model
     - Reason
   * - ``x,y``
     - ``x,y,z``
     - Three-dimensional coordinate system
   * - ``h-y``
     - ``h-z``
     - ``z`` is the vertical coordinate
   * - ``h=80e3``
     - ``h=100e3``
     - New vertical extent
   * - 2D temperature profile
     - 3D temperature profile
     - Temperature varies vertically through the 3D volume

The temperature function does not explicitly depend on ``x`` or ``y``.
It therefore produces a vertically varying temperature profile that is
applied throughout the horizontal extent of the 3D model.


12. Correction to the Original Temperature Condition
------------------------------------------------------

The original temperature function contained an intermediate condition
of the form:

.. code-block:: text

   (h-y)>30.e3 && (h-y)<=30.e3

This condition cannot be satisfied because the same quantity cannot be
simultaneously greater than 30 km and less than or equal to 30 km.

The 3D version uses:

.. code-block:: text

   (h-z)>30.e3 && (h-z)<=50.e3

This defines an intermediate interval between 30 km and 50 km.

The three depth intervals are therefore:

.. list-table:: Temperature intervals
   :header-rows: 1
   :widths: 25 25 50

   * - Depth
     - Temperature branch
     - Meaning
   * - ``0--30 km``
     - First expression
     - Upper thermal layer
   * - ``30--50 km``
     - Second expression
     - Intermediate thermal layer
   * - ``>50 km``
     - Third expression
     - Deeper thermal layer


13. Boundary Velocity Model
---------------------------

The boundary velocity model was another location where the 2D
configuration could not be used directly.

The original 2D expression was:

.. code-block:: text

   if (x < w/2 , -v, v) ; v*2*d/w

This contains two velocity components.

A 3D velocity vector requires three components:

.. math::

   \mathbf{v} = (v_x,v_y,v_z).

The expression was therefore changed to:

.. code-block:: text

   set Function expression = if (x < w/2 , -v, v); \
                             0; \
                             v*2*d/w

The three components are:

.. list-table:: 3D boundary velocity
   :header-rows: 1
   :widths: 15 45 40

   * - Component
     - Expression
     - Meaning
   * - ``v_x``
     - ``if(x < w/2,-v,v)``
     - Opposing horizontal velocity
   * - ``v_y``
     - ``0``
     - No velocity in the second horizontal direction
   * - ``v_z``
     - ``v*2*d/w``
     - Vertical velocity component

The essential change was:

.. code-block:: text

   2D:
   vx ; vy

   3D:
   vx ; vy ; vz


14. Boundary Velocity Parsing Error
-----------------------------------

During the conversion, ASPECT produced an error associated with the
boundary velocity function:

.. code-block:: text

   ERROR: FunctionParser failed to parse
   'Boundary velocity model.Function'

The problematic expression was:

.. code-block:: text

   if (x < w/2 , -v, v) ; v*2*d/w

The problem was that this was still a two-component expression while
the model had been changed to 3D.

The correction was to add the missing third component:

.. code-block:: text

   if (x < w/2 , -v, v); 0; v*2*d/w

This illustrates an important conversion rule:

.. code-block:: text

   Dimension = 3
          ->
   velocity function requires three components


15. Mesh Deformation
--------------------

The ASPECT--Landlab coupling is performed through mesh deformation of
the top surface.

The 3D configuration contains:

.. code-block:: text

   subsection Mesh deformation
     set Mesh deformation boundary indicators = top: Landlab
     set Additional tangential mesh velocity boundary indicators = left, right, front, back

     subsection Landlab
       set MPI ranks for Landlab = 1
       set Script name = p_3_ada_lla_wb_landlab
       set Script argument =
       set Script path =
     end
   end

The important change is the addition of:

.. code-block:: text

   front, back

to the tangential mesh-velocity boundaries.


16. Why Front and Back Were Added
---------------------------------

A 2D model has two side boundaries.

A 3D box has four vertical side faces.

The 3D boundaries are:

.. list-table:: 3D ASPECT boundaries
   :header-rows: 1
   :widths: 20 25 55

   * - Boundary
     - Coordinate
     - Location
   * - ``left``
     - Minimum ``x``
     - ``x = 0``
   * - ``right``
     - Maximum ``x``
     - ``x = L_x``
   * - ``front``
     - Minimum ``y``
     - ``y = 0``
   * - ``back``
     - Maximum ``y``
     - ``y = L_y``
   * - ``bottom``
     - Minimum ``z``
     - ``z = 0``
   * - ``top``
     - Maximum ``z``
     - ``z = L_z``

Therefore, the new 3D geometry requires both ``front`` and ``back`` to
be included when specifying tangential mesh velocity boundaries.


17. Composition-Threshold Mesh Refinement
-----------------------------------------

The composition-threshold mesh refinement also had to be updated.

The final configuration is:

.. code-block:: text

   subsection Composition threshold
     set Compositional field thresholds = 1e50, 1e50, 1e50, 1e50, 1e50, 1e50, \
                                          1e50, 1e50, 1e50, 1e50, 1e50, 1e50, \
                                          1.0,  1e50, 1e50, 1e50, 1e50, 1e50, \
                                          1e50, 1e50
   end

There are exactly 20 threshold values.


18. Meaning of the Composition Thresholds
------------------------------------------

The threshold list corresponds directly to the 20 compositional fields.

The mapping is:

.. list-table:: Composition-threshold mapping
   :header-rows: 1
   :widths: 10 35 20 35

   * - No.
     - Field
     - Threshold
     - Role
   * - 1--12
     - Stress fields
     - ``1e50``
     - Effectively prevents these fields from normally triggering refinement
   * - 13
     - ``plastic_strain``
     - ``1.0``
     - Active refinement criterion
   * - 14
     - ``noninitial_plastic_strain``
     - ``1e50``
     - Effectively disabled
   * - 15
     - ``viscous_strain``
     - ``1e50``
     - Effectively disabled
   * - 16
     - ``crust``
     - ``1e50``
     - Effectively disabled
   * - 17
     - ``mantle_lithosphere``
     - ``1e50``
     - Effectively disabled
   * - 18
     - ``sediment_age``
     - ``1e50``
     - Effectively disabled
   * - 19
     - ``deposition_depth``
     - ``1e50``
     - Effectively disabled
   * - 20
     - ``sediment``
     - ``1e50``
     - Effectively disabled

The ``1.0`` threshold is therefore assigned to field 13,
``plastic_strain``, while the other fields have a very large threshold.


19. Composition-Threshold Error
-------------------------------

ASPECT produced the following error:

.. code-block:: text

   The number of thresholds given here must be equal to the number of
   compositional fields.

The internal condition reported by ASPECT was:

.. code-block:: text

   composition_thresholds.size() == this->n_compositional_fields()

The model has:

.. code-block:: text

   20 compositional fields

Therefore the threshold list must contain:

.. code-block:: text

   20 thresholds

A previous version contained the wrong number of threshold values.

The important distinction is that the composition-threshold list does
not include a separate background entry.

Thus:

.. code-block:: text

   Compositional fields = 20
   Composition thresholds = 20


20. Compositional Heating
-------------------------

The compositional heating model also had to be updated because the
number of compositional fields changed.

The final configuration is:

.. code-block:: text

   subsection Heating model
     set List of model names = compositional heating

     subsection Compositional heating
       set Use compositional field for heat production averaging = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                                                                   0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1

       set Compositional heating values = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, \
                                          0, 0, 0, 0, 0, 0, 1.0e-6, 0.0, 0.0, 0.0, 1.0e-6
     end
   end


21. Why the Heating Lists Have 21 Entries
------------------------------------------

Although the model has 20 compositional fields, the heating lists
contain 21 values.

This is because the heating list includes the background material in
addition to the 20 compositional fields.

Therefore:

.. math::

   1 + 20 = 21.

The first entry corresponds to the background material.

The remaining entries correspond to the 20 compositional fields.

The mapping is:

.. list-table:: Heating list
   :header-rows: 1
   :widths: 10 30 20 20

   * - Position
     - Field/material
     - Averaging
     - Heating value
   * - 1
     - Background
     - ``0``
     - ``0``
   * - 2--13
     - Stress fields
     - ``0``
     - ``0``
   * - 14
     - ``plastic_strain``
     - ``0``
     - ``0``
   * - 15
     - ``noninitial_plastic_strain``
     - ``0``
     - ``0``
   * - 16
     - ``viscous_strain``
     - ``0``
     - ``0``
   * - 17
     - ``crust``
     - ``1``
     - ``1.0e-6``
   * - 18
     - ``mantle_lithosphere``
     - ``0``
     - ``0.0``
   * - 19
     - ``sediment_age``
     - ``0``
     - ``0.0``
   * - 20
     - ``deposition_depth``
     - ``0``
     - ``0.0``
   * - 21
     - ``sediment``
     - ``1``
     - ``1.0e-6``

Therefore, the current configuration assigns nonzero heat production to
the ``crust`` and ``sediment`` entries.


22. Heating List Error
----------------------

An error occurred when the heating averaging list contained 20 values.

ASPECT reported:

.. code-block:: text

   Length of Use compositional field for heat production averaging list
   must be either one or 21.
   Currently it is 20.

This error is different from the composition-threshold error.

For composition thresholds:

.. code-block:: text

   20 compositional fields
   ->
   20 thresholds

For the heating list:

.. code-block:: text

   background + 20 compositional fields
   ->
   21 values

Therefore, the number of entries must be checked separately for each
ASPECT parameter.


23. Summary of All Major Changes
--------------------------------

The complete conversion is summarized below.

.. list-table:: 2D T-Model to 3D model conversion
   :header-rows: 1
   :widths: 25 30 45

   * - Component
     - 2D
     - 3D modification
   * - Dimension
     - ``2``
     - ``3``
   * - Coordinates
     - ``x,y``
     - ``x,y,z``
   * - Geometry
     - 2D
     - 3D ``box``
   * - X extent
     - Original T-Model extent
     - ``320 km``
   * - Y extent
     - Original 2D vertical/depth direction
     - ``80 km`` horizontal dimension
   * - Z extent
     - Not present
     - ``100 km`` vertical dimension
   * - X repetitions
     - 2D configuration
     - ``110``
   * - Y repetitions
     - 2D configuration
     - ``40``
   * - Z repetitions
     - Not present
     - ``50``
   * - Stress representation
     - 2D
     - Full 3D stress tensor
   * - Stress fields
     - Fewer fields
     - ``6 + 6 = 12``
   * - Total fields
     - Original field count
     - ``20``
   * - Initial composition
     - 2D coordinate function
     - 3D ``x,y,z`` function
   * - Boundary composition
     - Original number of expressions
     - ``20`` expressions
   * - Temperature
     - ``h-y``
     - ``h-z``
   * - Temperature height
     - ``80 km``
     - ``100 km``
   * - Boundary velocity
     - Two components
     - Three components
   * - Mesh deformation
     - 2D side boundaries
     - ``left,right,front,back``
   * - Composition thresholds
     - Original number
     - ``20``
   * - Heating list
     - Original number
     - ``21`` including background


24. Error Summary
-----------------

The errors encountered during the conversion can be summarized as
follows.

.. list-table:: Errors encountered during 2D-to-3D conversion
   :header-rows: 1
   :widths: 30 35 35

   * - Error
     - Cause
     - Solution
   * - Elasticity requires ``6+6`` stress fields in 3D
     - Too few stress fields were available for 3D viscoelasticity
     - Added six current and six old stress fields
   * - Initial composition mismatch
     - Function contained fewer expressions than required
     - Updated to 20 expressions
   * - Boundary composition mismatch
     - Original 2D expression list was retained
     - Updated to 20 expressions
   * - Boundary velocity ``FunctionParser`` error
     - Only two velocity components were supplied
     - Added the third component
   * - Composition threshold length error
     - Threshold list did not contain 20 values
     - Changed to exactly 20 values
   * - Heating-list length error
     - 20 values were supplied instead of 21
     - Added the background entry
   * - Temperature coordinate mismatch
     - Original function used ``y`` as vertical coordinate
     - Changed to ``z``
   * - Temperature interval error
     - Original condition used an impossible interval
     - Changed upper interval boundary from 30 km to 50 km


25. Important Difference Between 20 and 21
------------------------------------------

One of the most important lessons from the conversion is that not every
ASPECT list uses the same counting convention.

The following values must be distinguished.

.. list-table:: Required list lengths
   :header-rows: 1
   :widths: 40 20 40

   * - Parameter
     - Number
     - Reason
   * - ``Number of fields``
     - ``20``
     - Twenty compositional fields
   * - Initial composition expressions
     - ``20``
     - One expression for each field
   * - Boundary composition expressions
     - ``20``
     - One expression for each field
   * - Composition thresholds
     - ``20``
     - One threshold for each field
   * - Boundary velocity components
     - ``3``
     - ``x``, ``y``, and ``z`` velocity
   * - Heating averaging list
     - ``21``
     - Background + 20 fields
   * - Heating values
     - ``21``
     - Background + 20 fields


26. Why the 3D Conversion Required So Many Changes
---------------------------------------------------

The conversion demonstrates that a dimensional change affects the
mathematical structure of the entire model.

The relationship can be summarized as:

.. code-block:: text

   Dimension = 3
          |
          +----> 3D box geometry
          |
          +----> x, y, z coordinates
          |
          +----> 3-component velocity
          |
          +----> 3D stress tensor
          |
          +----> 6 current stress components
          |
          +----> 6 old stress components
          |
          +----> 12 stress fields
          |
          +----> 20 total compositional fields
          |
          +----> 20 initial-composition expressions
          |
          +----> 20 boundary-composition expressions
          |
          +----> 20 composition thresholds
          |
          +----> 3D mesh boundaries
          |
          +----> z-based temperature function
          |
          +----> updated heating lists


27. Relationship Between ASPECT and Landlab
-------------------------------------------

The ASPECT model is now three-dimensional, while Landlab continues to
represent the evolving surface as a two-dimensional grid.

ASPECT represents the volume:

.. math::

   (x,y,z)

while Landlab operates on the surface:

.. math::

   (x,y).

The coupling can therefore be conceptually represented as:

.. code-block:: text

                     LANDLAB
                 2D surface grid
                    (x,y)
                       |
                       | surface elevation
                       v
             +---------------------+
             |    ASPECT TOP       |
             |                     |
             |                     |
             |    3D volume        |
             |    (x,y,z)          |
             |                     |
             |                     |
             +---------------------+
                    ASPECT
                 bottom boundary

The additional ASPECT dimension does not mean that Landlab itself must
become a 3D volumetric grid. Instead, Landlab supplies the evolving
surface information that is coupled to the top boundary of the
three-dimensional ASPECT domain.


28. Geometry Consistency with World Builder
--------------------------------------------

The 3D ASPECT geometry must also remain consistent with the World
Builder configuration.

The current ASPECT geometry has:

.. code-block:: text

   X extent = 320e3
   Y extent = 80e3
   Z extent = 100e3

The corresponding vertical dimension used in functions such as the
boundary composition model is:

.. code-block:: text

   DZ = 100e3

This is consistent with the current ASPECT vertical extent.

Whenever the box size is changed, quantities that depend explicitly on
the box dimensions must also be checked.

For example:

.. code-block:: text

   ASPECT Z extent
   World Builder depth
   DZ
   temperature height h
   Landlab coupling dimensions

must not be allowed to describe different physical domains.


29. Final 3D Model Checklist
----------------------------

Before running the converted 3D model, the following items should be
checked.

.. list-table:: 3D model validation checklist
   :header-rows: 1
   :widths: 8 47 45

   * - No.
     - Check
     - Expected value
   * - 1
     - Model dimension
     - ``3``
   * - 2
     - Geometry model
     - ``box``
   * - 3
     - X extent
     - ``320e3``
   * - 4
     - Y extent
     - ``80e3``
   * - 5
     - Z extent
     - ``100e3``
   * - 6
     - X repetitions
     - ``110``
   * - 7
     - Y repetitions
     - ``40``
   * - 8
     - Z repetitions
     - ``50``
   * - 9
     - Number of compositional fields
     - ``20``
   * - 10
     - Current stress fields
     - ``6``
   * - 11
     - Old stress fields
     - ``6``
   * - 12
     - Initial composition expressions
     - ``20``
   * - 13
     - Boundary composition expressions
     - ``20``
   * - 14
     - Composition thresholds
     - ``20``
   * - 15
     - Boundary velocity components
     - ``3``
   * - 16
     - Tangential mesh boundaries
     - ``left,right,front,back``
   * - 17
     - Temperature variables
     - ``x,y,z``
   * - 18
     - Temperature vertical variable
     - ``h-z``
   * - 19
     - Heating averaging entries
     - ``21``
   * - 20
     - Heating values
     - ``21``
   * - 21
     - Vertical height constant
     - ``h=100e3``
   * - 22
     - Boundary composition depth constant
     - ``DZ=100e3``


30. Final Conclusion
--------------------

The conversion of the 2D T-Model into a 3D ASPECT model required a
coordinated modification of several interconnected sections of the
parameter file.

The first change was:

.. code-block:: text

   set Dimension = 3

This required the geometry to become a three-dimensional box:

.. code-block:: text

   X = 320 km
   Y = 80 km
   Z = 100 km

The change to three dimensions also required a full 3D stress
representation. Because the viscoelastic formulation stores both the
current and previous stress states, twelve stress fields are required:

.. math::

   6 \text{ current stress fields}
   +
   6 \text{ old stress fields}
   =
   12 \text{ stress fields}.

Together with the strain, crust, mantle-lithosphere, and
sediment-related fields, this resulted in:

.. code-block:: text

   20 compositional fields

Once the number of fields was increased to 20, every parameter that
uses one entry per compositional field had to be checked.

The resulting requirements are:

.. code-block:: text

   Compositional fields              = 20
   Initial composition expressions   = 20
   Boundary composition expressions = 20
   Composition thresholds            = 20

The boundary velocity function had to change from a two-component
vector to a three-component vector:

.. code-block:: text

   if (x < w/2,-v,v); 0; v*2*d/w

The mesh deformation boundaries also had to include the two additional
3D side faces:

.. code-block:: text

   left, right, front, back

The temperature model was converted from the 2D vertical coordinate
representation

.. code-block:: text

   h-y

to the 3D vertical representation

.. code-block:: text

   h-z

and the vertical height was changed from ``80e3`` to ``100e3`` to match
the new geometry.

Finally, the compositional heating lists required special attention.
Unlike the composition-threshold list, which contains exactly one
entry per compositional field, the heating lists include the background
material. Therefore:

.. code-block:: text

   Composition thresholds = 20
   Heating values          = 21

The errors encountered during the conversion were primarily
consistency errors. They occurred when one section of the parameter
file had been updated for 3D while another section still reflected the
old 2D configuration or the old number of compositional fields.

The main lesson from the conversion is that changing an ASPECT model
from 2D to 3D requires a systematic review of every parameter that
depends on:

* spatial coordinates;
* spatial dimension;
* velocity components;
* tensor components;
* compositional-field count;
* boundary faces;
* vertical geometry;
* and field-dependent parameter lists.

The final 3D T-Model should therefore be considered a coordinated 3D
formulation in which the geometry, rheology, stress representation,
compositional fields, thermal structure, boundary conditions, mesh
refinement, and ASPECT--Landlab surface coupling must all remain
mutually consistent with the three-dimensional model.