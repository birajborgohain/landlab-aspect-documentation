Deposition and Rift Basin Evolution
===================================

This benchmark tests the implementation of sediment deposition within the
**Landlab--ASPECT** framework by reproducing the published
**FastScape--ASPECT** model. Reproducing the published implementation
provides a validation benchmark for the Landlab-based framework before it
is extended to investigate sediment deposition, landscape evolution, and
rift basin development in a broader range of tectonic settings.

**Reference**

| Xue, L., Moucha, R., Scholz, C. A., & Naliboff, J. (2025).
| *Sedimentation and deformation in oblique continental rifts: The role of climate--tectonic interactions*.
| *Earth and Planetary Science Letters*, **657**, 119565.
| DOI: https://doi.org/10.1016/j.epsl.2025.119565


Table of FastScape--ASPECT to Landlab--ASPECT Mapping
------------------------------------------------------

.. .. list-table:: FastScape--ASPECT to Landlab--ASPECT mapping
..    :header-rows: 1
..    :widths: 15 24 40 10 26

..    * - Parameter for
..      - FastScape--ASPECT Parameter setup
..      - Landlab--ASPECT Implementation setup
..      - Status
..      - Notes

..    * - Time step per ASPECT time step
..      - ::

..           Number of FastScape timesteps 
..           per ASPECT timestep = 5
..      - ::

..           n_substeps = 10
..           sub_dt = dt / n_substeps
..      - Implemented
..      - The ASPECT timestep is subdivided into multiple Landlab substeps using operator splitting.

..    * - Maximum timestep length
..      - ::
      
..         Maximum timestep length = 5000 (Years)
..      - Not explicittly but
..        ::
        
..           dt = end_time - self.current_time
..           (it is controlled by sub_dt)
..      - Partial
..      - Controlled by ASPECT. No explicit maximum timestep limiter is implemented in Landlab.

..    * - Uplift and Advection
..      - ::
          
..           Uplift and advect with fastScape = true
..      - Uplift (in loop)
..         ::

..           vertical_velocity = self.determine_uplift_velocity(..)
..           self.elevation += vertical_velocity * sub_dt
       
..        Advection (Not in Loop)
..         ::

..           self.horizontal_velocity = \
..               self.determine_horizontal_velocity(...)

..           self.horizontal_surface_advector = \
..               AdvectionSolverTVD(...)
..      - Implemented
..      - Surface uplift is applied explicitly before each erosion and diffusion step.

  
..    * - Flow routing
..      - Implicit (built-in)
..      - Explicit (FlowAccumulator)
..        ::

..           "FlowAccumulator": {
..               "flow_director": "D8",
..           }

..           self.flow_accumulator = FlowAccumulator(
..               self.model_grid,
..               flow_director="D8",
..           )
..      - Implemented
..      - Drainage directions and drainage area are computed using the D8 algorithm.

..    * - Erosion & Deposition
..      - Erosional parameters (fastcape)
..        ::
..           Drainage area exponent = 0.5
..           Slope exponent = 1.0
..           Bedrock river incision rate = 1e-6
..           Bedrock diffusivity = 1e-2

..           Bedrock deposition coefficient = 1
..           Sediment deposition coefficient = 1
..           Sediment river incision rate = 1e-6
..           Sediment diffusivity = -1
..      - ErosionDeposition(...) (``initialize_landlab_components``)

..       ::

..         def initialize_landlab_components(...):

..             "ErosionDeposition": {
..                 "m_sp": 0.5,
..                 "n_sp": 1.0,
..                 "K": 1e-6,
..             }

..             "LinearDiffuser": {
..                 "D": 1e-2,
..             }

..       **Bedrock deposition coefficient:** Missing

..       ::

..         def update_until(...):

..             self.erosion_deposition = ErosionDeposition(...)
..       - Implemented
..       - Stream-power erosion with sediment deposition.

..    * - 
..      - Drainage area exponent
..      - ``m_sp = 0.5``
..      - Implemented
..      - Direct correspondence with the FastScape drainage area exponent.

..    * - 
..      - Slope exponent
..      - ``n_sp = 1.0``
..      - Implemented
..      - Direct correspondence with the FastScape slope exponent.

..    * - 
..      - Bedrock river incision rate
..      - ::

..           K = 1e-6

..           K = ed["K"] / self.s2yr
..      - Implemented
..      - Converted from yr⁻¹ to SI units before initializing ``ErosionDeposition``.

..    * - 
..      - Bedrock diffusivity
..      - ::

..           "LinearDiffuser": {
..               "D": 1e-2,
..           }

..           D = landlab_component_parameters[
..               "LinearDiffuser"]["D"] / self.s2yr

..           self.linear_diffuser = LinearDiffuser(
..               self.model_grid,
..               linear_diffusivity=self.Diffusivity,
..           )
..      - Implemented
..      - Hillslope diffusion using ``LinearDiffuser``.

..    * - 
..      - Marine transport
..      - ::

..           "SimpleSubmarineDiffuser": {
..               "K": 1e-2,
..               "tidal_range": 0.0,
..               "sea_level": 0.0,
..           }

..           self.submarine_diffuser =
..               SimpleSubmarineDiffuser(...)
..      - Basic implementation
..      - Approximates marine sediment diffusion.

..    * - 
..      - Sea level
..      - ``sea_level = 0.0``
..      - Implemented
..      - Passed directly to ``SimpleSubmarineDiffuser``.

..    * - 
..      - Marine diffusivity
..      - ::

..           shallow_water_diffusivity =
..               sd["K"] / self.s2yr
..      - Approximate
..      - Similar role to FastScape marine diffusivity but uses a different numerical formulation.

..    * - 
..      - Boundary conditions
..      - Landlab boundary status
..      - Missing
..      - FastScape fixed and reflective boundary conditions are not yet mapped to Landlab boundary conditions.

..    * - 
..      - Ghost nodes
..      - ::

..           ghost_nodes = 2

..           nrows = int(y_extent / spacing) + 1 + ghost_nodes
..           ncols = int(x_extent / spacing) + 1 + ghost_nodes
..      - Implemented
..      - The RasterModelGrid is enlarged by two ghost nodes surrounding the physical domain.

..    * - 
..      - Node tolerance
..      - Coupling interpolation
..      - Missing
..      - Current implementation assumes one-to-one correspondence between ASPECT and Landlab nodes.

..    * - 
..      - Additional mesh refinement
..      - ``RasterModelGrid`` resolution
..      - Missing
..      - Surface refinement is currently determined during grid construction.

..    * - 
..      - Vertical exaggeration
..      - —
..      - Not required
..      - Visualization parameter only.

..    * - 
..      - Random seed
..      - —
..      - Missing
..      - Not currently required.

..    * - 
..      - Sediment diffusivity
..      - —
..      - Missing
..      - Separate sediment diffusivity is not represented.

..    * - 
..      - Bedrock deposition coefficient
..      - ``v_s = 1000.0``
..      - Needs investigation
..      - ``v_s`` represents settling velocity and is not directly equivalent to the FastScape deposition coefficient.

..    * - 
..      - Sediment deposition coefficient
..      - —
..      - Missing
..      - No direct Landlab equivalent currently exists.

..    * - 
..      - Sand/silt transport
..      - —
..      - Missing
..      - Requires additional Landlab components or custom implementation.

..    * - 
..      - Porosity evolution
..      - —
..      - Missing
..      - No equivalent implementation currently exists.

..    * - 
..      - Sand/silt ratio
..      - —
..      - Missing
..      - No equivalent implementation currently exists.

..    * - 
..      - Marine compaction
..      - —
..      - Missing
..      - Not currently available in Landlab.


.. .. list-table:: FastScape--ASPECT to Landlab--ASPECT mapping
..    :header-rows: 1
..    :widths: 15 24 40 10 26

..    * - Parameter for
..      - FastScape--ASPECT Parameter setup
..      - Landlab--ASPECT Implementation setup
..      - Status
..      - Notes

..    * - Time step per ASPECT time step
..      - ::

..           Number of FastScape timesteps
..           per ASPECT timestep = 5

..      - ::

..           n_substeps = 10
..           sub_dt = dt / n_substeps

..      - Implemented
..      - The ASPECT timestep is subdivided into multiple Landlab substeps using operator splitting.

..    * - Maximum timestep length
..      - ::

..           Maximum timestep length = 5000 (Years)

..      - Not explicitly controlled in Landlab.

..        ::

..           dt = end_time - self.current_time

..      - Partial
..      - Controlled by ASPECT. No explicit maximum timestep limiter is implemented in Landlab.

..    * - Uplift and Advection
..      - :: 

..           Uplift and advect with FastScape = true

..      - **Uplift**

..        ::

..           vertical_velocity = self.determine_uplift_velocity(...)
..           self.elevation += vertical_velocity * sub_dt

..        **Horizontal advection**

..        ::

..           self.determine_horizontal_velocity(...)

..           self.horizontal_surface_advector.run_one_step(sub_dt)

..      - Implemented
..      - Surface uplift is applied explicitly before erosion and diffusion.

..    * - Flow routing
..      - Implicit (built-in)

..      - Explicit via ``FlowAccumulator``

..        ::

..           "FlowAccumulator": {
..               "flow_director": "D8",
..           }

..           self.flow_accumulator = FlowAccumulator(
..               self.model_grid,
..               flow_director="D8",
..           )

..      - Implemented
..      - Drainage directions and drainage area are computed using the D8 algorithm.

..    * - Erosion & Deposition

..      - ::

..           Drainage area exponent = 0.5
..           Slope exponent = 1.0
..           Bedrock river incision rate = 1e-6
..           Bedrock diffusivity = 1e-2

..           Bedrock deposition coefficient = 1
..           Sediment deposition coefficient = 1
..           Sediment river incision rate = 1e-6
..           Sediment diffusivity = -1

..      - **Initialization**

..        ::

..           "ErosionDeposition": {
..               "m_sp": 0.5,
..               "n_sp": 1.0,
..               "K": 1e-6,
..           }

..           "LinearDiffuser": {
..               "D": 1e-2,
..           }

..        **Update**

..        ::

..           self.erosion_deposition.run_one_step(sub_dt)

..        **Bedrock deposition coefficient:** Missing

..      - Implemented
..      - Stream-power erosion with sediment deposition.

.. list-table:: FastScape--ASPECT to Landlab--ASPECT mapping
   :header-rows: 1
   :widths: 18 28 12 42

   * - FastScape parameter
     - Landlab implementation
     - Status
     - Notes

   * - Time step per ASPECT time step
     - ``n_substeps``
     - Implemented
     - ASPECT timestep is subdivided into multiple Landlab substeps.

   * - Maximum timestep length
     - ``dt = end_time - self.current_time``
     - Partial
     - Controlled by ASPECT. No explicit timestep limiter.

   * - Uplift
     - ``determine_uplift_velocity()``
     - Implemented
     - Vertical velocity from ASPECT updates the surface elevation.

   * - Horizontal advection
     - ``AdvectionSolverTVD``
     - Implemented
     - Uses the ASPECT horizontal velocity stored in ``advection__velocity``.

   * - Flow routing
     - ``FlowAccumulator(flow_director="D8")``
     - Implemented
     - Explicit in Landlab, implicit in FastScape.

   * - Stream-power erosion
     - ``ErosionDeposition``
     - Implemented
     - Uses drainage area and slope.

   * - Hillslope diffusion
     - ``LinearDiffuser``
     - Implemented
     - Linear diffusion.

   * - Marine transport
     - ``SimpleSubmarineDiffuser``
     - Basic implementation
     - Approximates marine sediment transport.

   * - Ghost nodes
     - RasterModelGrid buffer
     - Implemented
     - Two ghost nodes surrounding the physical domain.

   * - Boundary conditions
     - Landlab boundary status
     - Missing
     - No direct FastScape mapping.

   * - Node tolerance
     - Coupling interpolation
     - Missing
     - One-to-one node mapping currently assumed.

   * - Additional refinement
     - RasterModelGrid resolution
     - Missing
     - Fixed during grid construction.

   * - Vertical exaggeration
     - —
     - Not required
     - Visualization only.

   * - Random seed
     - —
     - Missing
     - Not currently required.

   * - Sediment diffusivity
     - —
     - Missing
     - Not represented.

   * - Bedrock deposition coefficient
     - —
     - Missing
     - No equivalent currently.

   * - Sediment deposition coefficient
     - —
     - Missing
     - No equivalent currently.

   * - Sand/silt transport
     - —
     - Missing
     - Requires additional implementation.

   * - Porosity evolution
     - —
     - Missing
     - Not implemented.

   * - Sand/silt ratio
     - —
     - Missing
     - Not implemented.

   * - Marine compaction
     - —
     - Missing
     - Not implemented.


Time stepping
-------------

FastScape

.. code-block:: text

   Number of FastScape timesteps per ASPECT timestep = 5

Landlab

.. code-block:: python

   n_substeps = 10
   sub_dt = dt / n_substeps

Uplift
------

FastScape

.. code-block:: text

   Uplift and advect with FastScape = true

Landlab

.. code-block:: python

   vertical_velocity = self.determine_uplift_velocity(
       ASPECT_dim,
       ASPECT_fields_at_Landlab_nodes_dict,
   )

   self.elevation += vertical_velocity * sub_dt

Horizontal advection
--------------------

FastScape performs horizontal advection internally.

Landlab computes the horizontal velocity from ASPECT and stores it
in the ``advection__velocity`` field.

.. code-block:: python

   self.determine_horizontal_velocity(
       ASPECT_dim,
       ASPECT_fields_at_Landlab_nodes_dict,
   )

   self.horizontal_surface_advector.run_one_step(sub_dt)


Flow routing
------------

FastScape

* Implicit (built into FastScape)

Landlab

.. code-block:: python

   self.flow_accumulator = FlowAccumulator(
       self.model_grid,
       flow_director="D8",
   )


Erosion and deposition
----------------------

FastScape parameters

.. code-block:: text

   Drainage area exponent = 0.5
   Slope exponent = 1.0
   Bedrock river incision rate = 1e-6
   Bedrock diffusivity = 1e-2

   Bedrock deposition coefficient = 1
   Sediment deposition coefficient = 1
   Sediment river incision rate = 1e-6
   Sediment diffusivity = -1

Common Erosional Parameter Mapping
----------------------------------

.. list-table:: FastScape erosional parameters and their Landlab equivalents
   :header-rows: 1
   :widths: 35 30 35

   * - FastScape parameter
     - Landlab parameter
     - Remarks

   * - ``Drainage area exponent = 0.5``
     - ``m_sp = 0.5``
     - Numerically identical.

   * - ``Slope exponent = 1.0``
     - ``n_sp = 1.0``
     - Numerically identical.

   * - ``Bedrock river incision rate = 1e-6``
     - ``K = 1e-6``
     - Numerically identical. Erodibility coefficient.

   * - ``Bedrock diffusivity = 1e-2``
     - ``D = 1e-2``
     - Numerically identical.

.. note::

  **Unit consistency:** The FastScape parameters

  * `Bedrock river incision rate = 1e-6`
  * `Bedrock diffusivity = 1e-2`

  are already expressed in **per year** units (m/yr and m²/yr, respectively).
  Landlab also expects these quantities in per-year units. Therefore, these
  values should be passed directly as

  * `K = 1e-6`
  * `D = 1e-2`

  **without dividing by** `self.s2yr = 60 * 60 * 24 * 365.25`.

  Dividing by `self.s2yr` would incorrectly convert the parameters from
  per year to per second, resulting in values that are too small by a factor
  of approximately :math:`3.16 \times 10^7`.


.. list-table:: Typical ranges of bedrock incision/uplift rates and linear hillslope diffusivities
   :header-rows: 1
   :widths: 35 30 30

   * - Scenario
     - Incision/Uplift
     - Diffusivity

   * - Low-relief landscapes
     - :math:`10^{-7}`–:math:`10^{-6}` m/yr
     - :math:`10^{-2}`–:math:`10^{-1}` m²/yr

   * - Moderate relief
     - :math:`10^{-6}`–:math:`10^{-5}` m/yr
     - :math:`10^{-1}`–:math:`1` m²/yr

   * - Active mountain belts
     - :math:`10^{-5}`–:math:`10^{-4}` m/yr
     - :math:`1`–:math:`10` m²/yr

   * - Regional-scale numerical models
     - :math:`10^{-6}`–:math:`10^{-5}` m/yr
     - :math:`1`–:math:`100` m²/yr

Deposition Parameter Mapping
----------------------------

.. list-table:: FastScape deposition parameters and their Landlab equivalents
   :header-rows: 1
   :widths: 35 30 35

   * - FastScape parameter
     - Landlab parameter
     - Remarks

   * - ``Bedrock deposition coefficient = 1``
     - ``v_s = 1000.0``
     - Approximate mapping. ``v_s`` is the sediment settling velocity in ``ErosionDeposition`` and is **not** a direct equivalent of the FastScape bedrock deposition coefficient. The settling velocity parameter (dimensionless if drainage area is used instead of discharge).

     
   * - ``Sediment deposition coefficient = 1``
     - —
     - No equivalent parameter in ``ErosionDeposition``.

   * - ``Sediment river incision rate = 1e-6``
     - —
     - ``ErosionDeposition`` uses a single incision coefficient ``K`` for both erosion and deposition processes.

   * - ``Sediment diffusivity = -1``
     - —
     - No separate sediment diffusivity is implemented. Hillslope diffusion is represented by ``LinearDiffuser`` using a single diffusivity ``D``.

Marine Parameter Mapping
------------------------

.. list-table:: FastScape marine parameters and their Landlab equivalents
   :header-rows: 1
   :widths: 35 30 35

   * - FastScape parameter
     - Landlab parameter
     - Remarks

   * - ``Sea level = -2000``
     - ``sea_level = 0``
     - Passed directly to ``SimpleSubmarineDiffuser``.

   * - ``Sand transport coefficient = 200``
     - —
     - Not implemented.

   * - ``Silt transport coefficient = 200``
     - —
     - Not implemented.
   * - ``Sand porosity = 0``
     - —
     - Not implemented.

   * - ``Silt porosity = 0``
     - —
     - Not implemented.

   * - ``Sand e-folding depth = 1e3``
     - —
     - Not implemented.

   * - ``Silt e-folding depth = 1e3``
     - —
     - Not implemented.

   * - ``Sand-silt ratio = 1``
     - —
     - Not implemented.

   * - ``Depth averaging thickness = 1e2``
     - —
     - Not implemented.

Mesh Geometry & Boundaries
------------------------------

The following table summarizes the commonly used FastScape parameters, their
closest equivalent in Landlab (when available), and their purpose.

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - **FastScape Parameter**
     - **Landlab Equivalent**
     - **Description**

   * - ``Vertical exaggeration = -1``
     - —
     - Controls the vertical scaling used internally by FastScape. A value of
       ``-1`` disables vertical exaggeration (default behavior) and does not
       affect the physical simulation.

   * - ``Additional fastscape refinement = 1``
     - ``RasterModelGrid`` resolution (``xy_spacing``)
     - Refines the FastScape surface grid above the highest ASPECT surface
       resolution. Increasing this value produces a finer erosion/deposition
       grid. Landlab instead uses a fixed grid resolution specified during
       grid creation.

   * - ``Fastscape seed = 1000``
     - ``numpy.random.seed()``
     - Sets the random seed for stochastic processes, ensuring reproducible
       simulations whenever random initialization is used.

   * - ``Maximum surface refinement level = 1``
     - None
     - Specifies the highest adaptive mesh refinement level permitted at the
       ASPECT surface. This parameter has no equivalent in Landlab because
       Landlab uses a fixed-resolution grid.

   * - ``Surface refinement difference = 0``
     - None
     - Limits the allowable difference between the minimum and maximum surface
       refinement levels to maintain smooth mesh transitions. This parameter is
       not applicable to Landlab.

   * - ``Use marine component = true``
     - .. code-block:: python

        self.submarine_diffuser = SimpleSubmarineDiffuser(
              self.model_grid,
              tidal_range=sd["tidal_range"],
              shallow_water_diffusivity=sd["K"] / self.s2yr,
              sea_level=sd["sea_level"],
          )
     - Enables marine sediment transport and deposition below sea level.
       Landlab does not provide a built-in marine sedimentation component.

   * - ``Uplift and advect with fastscape = true``
     - User-defined uplift and advection
     - Allows FastScape to apply tectonic uplift and horizontal advection in
       addition to erosion and deposition. In Landlab, uplift is typically
       imposed by the user, while advection requires additional components or
       custom implementation.

   * - ::

          subsection Box
            set X repetitions = 30
            set Y repetitions = 12
            set Z repetitions = 15

            set X extent = 300e3
            set Y extent = 120e3
            set Z extent = 150e3

     - ::

          x_extent = 300e3
          y_extent = 120e3
          spacing = 2500.0

          ghost_nodes = 2

          nrows = int(y_extent / spacing) + 1 + ghost_nodes
          ncols = int(x_extent / spacing) + 1 + ghost_nodes

       
     - Uses ghost nodes outside the computational domain to simplify boundary
       condition calculations. Landlab instead handles boundaries using node
       status flags.

   * - ``Node tolerance = 0.001``
     - None
     - Defines the maximum allowable distance between an ASPECT surface node
       and the corresponding FastScape node when transferring data between the
       two models. This parameter is specific to the ASPECT--FastScape
       coupling.


Boundary Conditions
---------------------

The following table summarizes the available FastScape boundary conditions and
their closest equivalents in Landlab.

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - **FastScape Boundary Condition**
     - **Landlab Equivalent**
     - **Description**

   * - Numerically identical

       .. code-block:: python

        subsection Boundary conditions
          set Front = 1
          set Right = 1
          set Back  = 1
          set Left  = 1

     - Numerically identical

       .. code-block:: python

        self.model_grid.set_closed_boundaries_at_grid_edges(
            right_is_closed=True,
            left_is_closed=True,
            top_is_closed=True,
            bottom_is_closed=True,
        )

     - **Boundary condition definitions**

       .. note::

        In FastScape, boundary condition values have the following meaning:

        - ``1``: Fixed-height boundary. The boundary elevation is fixed,
          although it can still be modified by an imposed uplift velocity.

        - ``0``: Reflective boundary. No flux crosses the boundary,
          producing a mirror symmetry about the boundary.

        During testing of the ASPECT–Landlab coupling, reflective
        boundaries (``0``) resulted in **no river incision within the
        rift valley**. Therefore, fixed-height boundaries (``1``) are
        used in the examples presented here.
    
    
   * - ``Boundary = 0`` (Not used)
     - —
     - Specifies a reflective (no-flux) boundary that prevents sediment from
       leaving the domain. Opposing reflective boundaries can produce special
       behavior in FastScape.

   * - ``Left mass flux`` (Not used)
     - —
     - Prescribes sediment flux through the left boundary
       (:math:`\mathrm{m^2/yr}`).

   * - ``Front mass flux`` (Not used)
     - —
     - Prescribes sediment flux through the front boundary
       (:math:`\mathrm{m^2/yr}`).

   * - ``Back mass flux`` (Not used)
     - —
     - Prescribes sediment flux through the back boundary
       (:math:`\mathrm{m^2/yr}`).

   * - ``Back front ghost nodes periodic`` (Not used)
     - —
     - Treats ghost nodes as periodic in the front--back direction even when
       the physical boundaries are fixed.

   * - ``Left right ghost nodes periodic`` (Not used)
     - —
     - Treats ghost nodes as periodic in the left--right direction even when
       the physical boundaries are fixed.


.. note:: 

  * Several FastScape parameters (for example,
    ``Maximum surface refinement level``,
    ``Surface refinement difference``, and ``Node tolerance``) are specific to
    the ASPECT--FastScape coupling and therefore have **no direct equivalent**
    in Landlab.

  * FastScape operates on an adaptively refined surface mesh provided by ASPECT,
    whereas Landlab uses a fixed structured grid such as
    ``RasterModelGrid`` or ``HexModelGrid``.

  * Boundary handling also differs between the two frameworks:

    * **FastScape:** Fixed (``1``), reflective (``0``), optional ghost nodes,
      and prescribed sediment flux boundaries.

    * **Landlab:** Open, closed, fixed-value, or fixed-gradient boundaries
      controlled through node status flags.


.. code-block:: ini

   subsection Fastscape
     set Number of fastscape timesteps per aspect timestep = 5

     # Maximum timestep for FastScape
     set Maximum timestep length = 5000

     set Vertical exaggeration = -1

     # How many levels FastScape should be refined above the maximum ASPECT surface resolution.
     set Additional fastscape refinement = 1

     set Fastscape seed = 1000

     # As the highest resolution at the surface is 3 in the mesh refinement function,
     # we set this the same.
     set Maximum surface refinement level = 1

     # The difference between the lowest and highest refinement level at the surface.
     set Surface refinement difference = 0

     set Use marine component = true

     # Flag for having FastScape advect/uplift the surface.
     set Uplift and advect with fastscape = true

     # Because no boundaries are periodic, no flux is prescribed,
     # and no advection occurs in FastScape,
     # we do not need ghost nodes.
     set Use ghost nodes = true

     # Node tolerance for how close an ASPECT node must be
     # to the FastScape node for the value to be transferred.
     set Node tolerance = 0.001

     # BC 1 is fixed and 0 is reflective
     subsection Boundary conditions

       set Front = 1
       set Right = 1
       set Back = 1
       set Left = 1

       # Flux per unit length through left boundary.
       # set Left mass flux = 0
       # set Front mass flux = 0
       # set Back mass flux = 0

       # Whether to set the ghost nodes periodic.
       # set Back front ghost nodes periodic = false
       # set Left right ghost nodes periodic = false

     end

     subsection Erosional parameters

       set Drainage area exponent = 0.5
       set Slope exponent = 1

       # A negative value indicates varied flow.
       # set Multi-direction slope exponent = -1

       # Bedrock deposition coefficient.
       set Bedrock deposition coefficient = 1

       # Deposition coefficient for sediment.
       set Sediment deposition coefficient = 1

       # River incision rate for bedrock.
       set Bedrock river incision rate = 1e-6

       # River incision rate for sediment.
       set Sediment river incision rate = 1e-6

       # Bedrock diffusivity.
       set Bedrock diffusivity = 1e-2

       # Sediment diffusivity.
       set Sediment diffusivity = -1

       # Use a fixed erosional base level.
       # set Use a fixed erosional base level = true

       # set Erosional base level = 0

     end

     subsection Marine parameters

       # FastScape sea level (m)
       set Sea level = -2000

       set Sand porosity = 0
       set Silt porosity = 0

       set Sand e-folding depth = 1e3
       set Silt e-folding depth = 1e3

       set Sand-silt ratio = 1
       set Depth averaging thickness = 1e2

       set Sand transport coefficient = 200
       set Silt transport coefficient = 200

     end

   end

Landlab component initialization
--------------------------------

All Landlab components are initialized in
``initialize_landlab_components()``.

.. code-block:: python

   def initialize_landlab_components(self):

       landlab_component_parameters = {

           "LinearDiffuser": {
               "D": 1e-2,
           },

           "FlowAccumulator": {
               "flow_director": "D8",
           },

           "ErosionDeposition": {
               "K": 1e-6,
               "v_s": 1000.0,
               "m_sp": 0.5,
               "n_sp": 1.0,
               "sp_crit": 0.0, # erosion threshold
           },

           "SimpleSubmarineDiffuser": {
               "K": 1e-2,
               "tidal_range": 0.0,
               "sea_level": 0.0,
           },
       }

       # LinearDiffuser
       D = landlab_component_parameters["LinearDiffuser"]["D"] / self.s2yr

       self.Diffusivity = self.model_grid.add_zeros(
           "linear_diffusivity",
           at="node",
       )
       self.Diffusivity[:] = D

       self.linear_diffuser = LinearDiffuser(
           self.model_grid,
           linear_diffusivity=self.Diffusivity,
       )

       # FlowAccumulator
       self.flow_accumulator = FlowAccumulator(
           self.model_grid,
           flow_director=landlab_component_parameters[
               "FlowAccumulator"]["flow_director"],
       )

       # ErosionDeposition
       ed = landlab_component_parameters["ErosionDeposition"]

       self.erosion_deposition = ErosionDeposition(
           self.model_grid,
           K=ed["K"] / self.s2yr,
           v_s=ed["v_s"],
           m_sp=ed["m_sp"],
           n_sp=ed["n_sp"],
           sp_crit=ed["sp_crit"],
       )

       # SimpleSubmarineDiffuser
       sd = landlab_component_parameters["SimpleSubmarineDiffuser"]

       self.submarine_diffuser = SimpleSubmarineDiffuser(
           self.model_grid,
           tidal_range=sd["tidal_range"],
           shallow_water_diffusivity=sd["K"] / self.s2yr,
           sea_level=sd["sea_level"],
       )

       # Horizontal advection
       self.horizontal_surface_advector = AdvectionSolverTVD(
           self.model_grid,
           fields_to_advect=self.elevation,
       )


Missing FastScape Features in the Current Landlab--ASPECT Implementation
------------------------------------------------------------------------

The following FastScape parameters do not currently have a direct
equivalent in the present Landlab--ASPECT implementation.

Erosional parameters
~~~~~~~~~~~~~~~~~~~~

* **Sediment river incision rate**
  - FastScape supports separate incision rates for bedrock and sediment.
  - ``ErosionDeposition`` uses a single stream-power coefficient (``K``).

* **Sediment deposition coefficient**
  - No equivalent parameter currently exists.

* **Sediment diffusivity**
  - No separate sediment diffusivity is implemented.

* **Multi-direction slope exponent**
  - Landlab currently uses the D8 flow-routing algorithm.
  - No equivalent multi-direction weighting parameter is implemented.

* **Use a fixed erosional base level**
  - Not implemented.

* **Erosional base level**
  - Not implemented.

Marine parameters
~~~~~~~~~~~~~~~~~

* **Sand porosity**
  - Not implemented.

* **Silt porosity**
  - Not implemented.

* **Sand e-folding depth**
  - Not implemented.

* **Silt e-folding depth**
  - Not implemented.

* **Sand-silt ratio**
  - Not implemented.

* **Depth averaging thickness**
  - Not implemented.

* **Separate sand transport coefficient**
  - ``SimpleSubmarineDiffuser`` uses a single diffusivity and does not distinguish sand transport.

* **Separate silt transport coefficient**
  - ``SimpleSubmarineDiffuser`` uses a single diffusivity and does not distinguish silt transport.

* **Marine compaction**
  - Not implemented.

Figures
--------
.. figure:: /_images/deposition/depo_drainage_topo_combine_Landlab_Fastscape.png
   :width: 100%
   :align: center


Reproducing the Liang (2025) EPSL Landlab--ASPECT Test
------------------------------------------------------------------

This note records the locations of the input files, output directory,
and executable used for the Landlab--ASPECT coupling test based on the
Liang (2025) EPSL.

Input/Output Directory
----------------------

The parameter files and simulation outputs are stored in

.. code-block:: text

   /Users/biraj/cookbook_biraj/
   fastscape_cookbook_ASPECT-300_deal-970_fastscape-290_biraj/
   Liang_2025_EPSL_output_prm/
   prm_input/
   outputs/
   test64_landlab_ada_denial_2.5_km-spacing_ghost/

This directory contains:

* ASPECT ``.prm`` input files
* Landlab outputs
* ASPECT outputs
* VTK files
* Simulation logs

ASPECT Executable
-----------------

The simulation was run using the following ASPECT executable:

.. code-block:: text

   /Users/biraj/software/landlab_ASPECT_test_2/
   aspect/build/aspect-release

Run Command
-----------

The simulation was executed using MPI with 14 processes.

activate uv environment 

.. code-block:: bash
  
  source /Users/biraj/software/landlab_ASPECT_test_2/aspect/.venv/bin/activate


.. code-block:: bash

   /opt/homebrew/bin/mpirun -np 14 \
     /Users/biraj/software/landlab_ASPECT_test_2/aspect/build/aspect-release \
     3d_64c1t1s1ob1c1_copy_1_landlab_ada_denial.prm

.. code-block:: bash

  9 minute to complete

