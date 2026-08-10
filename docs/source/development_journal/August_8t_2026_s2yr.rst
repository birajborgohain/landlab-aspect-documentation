August 8, 2026, Clarification of Units in the ASPECT--Landlab Coupling
========================================================================


I am trying to clarify the units of the erosion and diffusion parameters in our ASPECT--Landlab coupling.

In the current coupling code, I have:

.. code-block:: python

   s2yr = 60 * 60 * 24 * 365.25

   D_val = 1e-2 / s2yr
   K_val = 1e-5 / s2yr
   K_sub = 1e-2 / s2yr

Based on the literature ranges we have been using, typical values are approximately:

.. list-table:: Typical parameter ranges
   :header-rows: 1
   :widths: 35 30

   * - Parameter
     - Typical range
   * - Linear hillslope diffusivity
     - :math:`10^{-2}`--:math:`10^{2}\ {\rm m^2/yr}`
   * - Incision/erosion rate
     - :math:`10^{-7}`--:math:`10^{-4}\ {\rm m/yr}`

These values depend, of course, on the particular landscape and modeling scenario.

Unit conversion
----------------

My main question is about the ``/s2yr`` conversion.

If

.. math::

   D = 10^{-2}\ {\rm m^2/yr}

and

.. math::

   K = 10^{-5}\ {\rm m/yr},

are literature values expressed per year, then dividing by ``s2yr`` converts them to per-second units:

.. math::

   D = \frac{10^{-2}}{s2yr}
     \approx 3.17\times10^{-10}\ {\rm m^2/s}

and

.. math::

   K = \frac{10^{-5}}{s2yr}
     \approx 3.17\times10^{-13}\ {\rm m/s}.

Therefore, the ``/s2yr`` operation is appropriate **only if the rest of the calculation is being carried out using seconds as the time unit**.

Landlab and units
-----------------

Just as a point of background for the discussion below, my understanding is that Landlab is generally **unit-agnostic**; that is, it does not prescribe a particular choice of time or length units. Rather, the quantities supplied to the Landlab components need to be internally consistent.

For example, if the calculation is being carried out with time in years, then a diffusivity of :math:`10^{-2}` would correspond to :math:`10^{-2}\ {\rm m^2/yr}`. If time is instead represented in seconds, the corresponding value would need to be expressed in :math:`{\rm m^2/s}`.

I mention this mainly to provide some context for my question below. I am trying to understand what time unit is being used consistently in the current ASPECT--Landlab coupling, particularly for the timestep passed to the Landlab components and for the values of ``D_val``, ``K_val``, and ``K_sub``.


Current coupling question
--------------------------

This is where I am uncertain about our current implementation.

In the coupling calculation, I think we may actually be using the numerical values

.. math::

   D = 10^{-2}

and

.. math::

   K = 10^{-5}

without dividing by ``s2yr`` in some calculations.

If so, there is a very large difference between the two interpretations:

.. math::

   1\ {\rm yr} = 31,557,600\ {\rm s}
   \approx 3.15\times10^7\ {\rm s}.

Therefore, using ``10^-5`` directly when the calculation is interpreted as seconds is different by approximately :math:`3.15\times10^7` from using

.. math::

   \frac{10^{-5}}{s2yr}
   \approx 3.17\times10^{-13}\ {\rm m/s}.

This makes me wonder whether we should interpret the parameters in one of the following ways:

#. Use the literature values directly as
   :math:`10^{-2}\ {\rm m^2/yr}` and :math:`10^{-5}\ {\rm m/yr}`,
   if the coupled surface-process calculation is being carried out with
   time measured in years.

#. Convert the values using ``/s2yr`` if the Landlab calculation is
   actually receiving and using time in seconds.

#. If the much smaller values are intentional, determine whether they are
   being used as numerical-stability parameters rather than as direct
   representations of the physical literature values.

Numerical stability versus physical parameter values
-----------------------------------------------------

I would particularly like to distinguish between these two possibilities.

If a parameter is deliberately reduced for numerical stability, then it would be useful to document this explicitly as a **numerical modeling choice**, rather than interpreting the reduced value as the physical value from the literature.

For example, using

.. code-block:: python

   K_val = 1e-5 / s2yr

has a clear physical interpretation as approximately

.. math::

   3.17\times10^{-13}\ {\rm m/s},

provided that the original :math:`10^{-5}` value is intended to represent
:math:`{\rm m/yr}`.

On the other hand, using ``K_val = 1e-5`` in a seconds-based calculation
would represent a completely different physical rate.

What I would like to clarify
----------------------------

Could you please let me know how you think we should interpret these parameters in the current ASPECT--Landlab coupling?

In particular, I would like to establish:

* What time unit is actually being used by the coupled Landlab calculation?
* Should ``D_val``, ``K_val``, and ``K_sub`` be supplied in per-year or
  per-second units?
* Is the ``/s2yr`` conversion currently necessary?
* Are the smaller parameter values being used intentionally for numerical
  stability, or are they intended to represent the physical literature
  values?
* If the latter, are we unintentionally using values that differ from the
  intended physical parameters by approximately :math:`10^7`?

I want to make sure that the units are internally consistent between ASPECT,
the coupling layer, and the Landlab surface-process components, and that we
can clearly distinguish **physical parameter values** from any
**numerical-stability adjustments**.

Comparison between FastScape--ASPECT and Landlab--ASPECT
----------------------------------------------------------

The following figure shows a comparison between the **FastScape--ASPECT**
coupling presented by Xue et al. (2025, EPSL) and the current
**Landlab--ASPECT** coupling.

In the Landlab--ASPECT experiments, the coupled model ran successfully when
the erosion, diffusion, and shallow-water diffusivity parameters were
converted using ``self.s2yr``. Specifically, the following forms were used:

.. code-block:: python

   K = ed["K"] / self.s2yr

   self.Diffusivity[:] = D / self.s2yr

   shallow_water_diffusivity = sd["K"] / self.s2yr

In contrast, when the same parameter values were used **without** dividing
by ``self.s2yr``, the Landlab--ASPECT coupled model did not run successfully.

Observed numerical instability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Immediately after removing the ``/ self.s2yr`` conversions, the coupled
model became numerically unstable. The ASPECT log first reported:

.. code-block:: text

   RuntimeWarning:
   divide by zero encountered in divide

   RuntimeWarning:
   overflow encountered in divide

Immediately following these warnings, the topographic elevation became
extremely large in magnitude:

.. code-block:: text

   Max elevation = 51837293163
   Min elevation = -17681406182

These values are clearly inconsistent with the expected physical scale of
the model and indicate that the numerical solution became unstable during
the early stage of the simulation.

Following this instability, ASPECT reported that the advection solver could
not converge:

.. code-block:: text

   The iterative advection solver in
   Simulator::solve_advection did not converge.

The simulation subsequently terminated and MPI aborted the run.

Interpretation
~~~~~~~~~~~~~~

At this stage, the results indicate that the Landlab--ASPECT coupling is
stable for the tested parameter values when the ``/ self.s2yr`` conversion
is applied, whereas removing this conversion leads to numerical instability
and failure of the ASPECT advection solver.

This observation raises an important question regarding the effective time
units used in the ASPECT--Landlab coupling. In particular, it is necessary
to determine whether the ``/ self.s2yr`` operation is representing a
required conversion between the time units used by the physical parameters
and those used by the coupled calculation, or whether the conversion is
also affecting the numerical stability of the surface-process calculation.

The comparison therefore motivates a closer examination of the units and
scaling of ``K``, ``D``, and the shallow-water diffusivity in the
Landlab--ASPECT coupling before interpreting the parameter values directly
as physical literature values.

Figures
--------
.. figure:: /_images/deposition/depo_drainage_topo_combine_Landlab_Fastscape.png
   :width: 100%
   :align: center

Landlab--ASPECT Coupling Implementation
----------------------------------------

The following code shows    Landlab ``.py``
``original_landlab.py`` model used for the Landlab--ASPECT coupling.

.. code-block:: python
   :linenos:

   from mpi4py import MPI
   import importlib.util
   import os
   import sys
   import numpy as np
   import landlab
   from landlab.components import (
       LinearDiffuser,
       AdvectionSolverTVD,
       FlowAccumulator,
       ErosionDeposition,
       SimpleSubmarineDiffuser,
       DepressionFinderAndRouter,
   )

   # ---------------------------------------------------------------------------
   # Import LandLabTemplate base class, which is located in
   # contrib/python/scripts/.
   # ---------------------------------------------------------------------------

   from landlab_template import LandLabTemplate

   # ---------------------------------------------------------------------------
   # Custom model — override only the methods you want to change.
   # ---------------------------------------------------------------------------

   class MyAspectLandlabModel(LandLabTemplate):

       def update_until(
           self,
           end_time,
           ASPECT_dim,
           ASPECT_fields_at_Landlab_nodes_dict,
       ):
           dt = end_time - self.current_time
           self.timestep += 1

           deposition_erosion = np.zeros(
               self.model_grid.number_of_nodes
           )

           vertical_velocity = self.determine_uplift_velocity(
               ASPECT_dim,
               ASPECT_fields_at_Landlab_nodes_dict,
           )

           self.horizontal_velocity = (
               self.determine_horizontal_velocity(
                   ASPECT_dim,
                   ASPECT_fields_at_Landlab_nodes_dict,
               )
           )

           self.horizontal_surface_advector = AdvectionSolverTVD(
               self.model_grid,
               fields_to_advect=self.elevation,
           )

           # Extract compositions along the ASPECT surface.
           # slice_weak_composition = (
           #     ASPECT_fields_at_Landlab_nodes_dict["weak"]
           # )
           # slice_strong_composition = (
           #     ASPECT_fields_at_Landlab_nodes_dict["strong"]
           # )

           # Project composition values from y=0 to all Landlab nodes.
           # strong_composition = np.zeros(
           #     self.model_grid.number_of_nodes
           # )
           # weak_composition = np.zeros(
           #     self.model_grid.number_of_nodes
           # )

           # unique_x_values = np.unique(
           #     self.model_grid.x_of_node
           # )
           #
           # for x in unique_x_values:
           #     strong_composition[
           #         self.model_grid.x_of_node == x
           #     ] = slice_strong_composition[
           #         unique_x_values == x
           #     ]
           #
           #     weak_composition[
           #         self.model_grid.x_of_node == x
           #     ] = slice_weak_composition[
           #         unique_x_values == x
           #     ]

           # Modify diffusivity based on composition.
           # self.Diffusivity[
           #     strong_composition >= 0.5
           # ] = 1e-10 / self.s2yr
           #
           # self.Diffusivity[
           #     weak_composition >= 0.5
           # ] = 10 / self.s2yr

           if dt > 0:
               n_substeps = 10
               sub_dt = dt / n_substeps

               for _ in range(n_substeps):
                   elevation_before = self.elevation.copy()

                   self.elevation += (
                       vertical_velocity * sub_dt
                   )

                   self.horizontal_surface_advector.run_one_step(
                       sub_dt
                   )

                   self.flow_accumulator.run_one_step()

                   self.erosion_deposition.run_one_step(
                       sub_dt
                   )

                   self.linear_diffuser.run_one_step(
                       sub_dt
                   )

                   self.submarine_diffuser.run_one_step(
                       sub_dt
                   )

                   deposition_erosion += (
                       self.elevation - elevation_before
                   )

           self.current_time = end_time

           print(
               "Max elevation:",
               np.max(self.elevation),
               "Min elevation:",
               np.min(self.elevation),
           )

           # Return the change in topography along y=0,
           # where the ASPECT mesh is located.
           dimensional_deposition_erosion = (
               self.dimensional_deposition_erosion(
                   ASPECT_dim,
                   deposition_erosion,
               )
           )

           # Save Landlab output for each timestep.
           # In .prm, Output directory should be set to
           # outputs/name_of_the_run.
           self.save_landlab_output()

           return dimensional_deposition_erosion

       def set_mesh_information(self, grid_dictionary):
           if self.model_grid is not None:
               return

           print("* Creating RasterModelGrid ...")

           x_extent = 300e3
           y_extent = 120e3
           spacing = 2500.0

           # Compute the number of grid nodes.
           #
           # A domain with N = L/dx intervals requires N+1
           # physical nodes because both endpoints are included.
           # We then add one extra boundary (ghost/buffer) node
           # on each side (+2 total).
           #
           # Total nodes = intervals + 1 + 2
           #             = physical nodes + ghost nodes

           ghost_nodes = 2

           nrows = (
               int(y_extent / spacing)
               + 1
               + ghost_nodes
           )

           ncols = (
               int(x_extent / spacing)
               + 1
               + ghost_nodes
           )

           # Shift the grid origin by one grid spacing so that
           # the first node lies outside the physical domain
           # using xy_of_lower_left=(-spacing, -spacing).
           #
           # Combined with the extra rows and columns, this
           # provides one boundary (ghost/buffer) node on each
           # side of the grid.

           self.model_grid = landlab.RasterModelGrid(
               (nrows, ncols),
               xy_spacing=(spacing, spacing),
               xy_of_lower_left=(-spacing, -spacing),
           )

           print("* Creating topographic elevation ...")

           self.elevation = self.model_grid.add_zeros(
               "topographic__elevation",
               at="node",
           )

           self.horizontal_velocity = (
               self.model_grid.add_zeros(
                   "advection__velocity",
                   at="link",
               )
           )

           # # Triangular mountain in the centre of the domain.
           # topo_height = 20e3
           # left_x_arr = np.array([25e3, 50e3])
           # left_y_arr = np.array([0.0, topo_height])
           # right_x_arr = np.array([50e3, 75e3])
           # right_y_arr = np.array([topo_height, 0.0])
           #
           # left_m, left_b = np.polyfit(
           #     left_x_arr,
           #     left_y_arr,
           #     deg=1,
           # )
           #
           # right_m, right_b = np.polyfit(
           #     right_x_arr,
           #     right_y_arr,
           #     deg=1,
           # )
           #
           # self.elevation[
           #     self.model_grid.x_of_node <= 50e3
           # ] = (
           #     left_m
           #     * self.model_grid.x_of_node[
           #         self.model_grid.x_of_node <= 50e3
           #     ]
           #     + left_b
           # )
           #
           # self.elevation[
           #     self.model_grid.x_of_node > 50e3
           # ] = (
           #     right_m
           #     * self.model_grid.x_of_node[
           #         self.model_grid.x_of_node > 50e3
           #     ]
           #     + right_b
           # )
           #
           # self.elevation[
           #     self.model_grid.x_of_node
           #     < np.min(left_x_arr)
           # ] = 0.0
           #
           # self.elevation[
           #     self.model_grid.x_of_node
           #     > np.max(right_x_arr)
           # ] = 0.0

           self.model_grid.set_closed_boundaries_at_grid_edges(
               right_is_closed=True,
               left_is_closed=True,
               top_is_closed=True,
               bottom_is_closed=True,
           )

           print(
               "\tnumber of nodes:",
               self.model_grid.number_of_nodes,
           )

           self.initialize_landlab_components()

           print("* Done")

           return self.model_grid

       def initialize_landlab_components(self):

           landlab_component_parameters = {

               "LinearDiffuser": {
                   "D": 1e-2,  # m2/year
               },

               "FlowAccumulator": {
                   "flow_director": "D8",
               },

               "ErosionDeposition": {
                   "K": 1e-6,  # m/year
                   "v_s": 1000.0,
                   "m_sp": 0.5,
                   "n_sp": 1.0,
                   "sp_crit": 0.0,
               },

               "SimpleSubmarineDiffuser": {
                   "K": 1e-2,  # m2/year
                   "tidal_range": 0.0,
                   "sea_level": 0.0,
               },
           }

           # LinearDiffuser
           D = landlab_component_parameters[
               "LinearDiffuser"
           ]["D"]

           self.Diffusivity = self.model_grid.add_zeros(
               "linear_diffusivity",
               at="node",
           )

           self.Diffusivity[:] = D / self.s2yr

           self.linear_diffuser = LinearDiffuser(
               self.model_grid,
               linear_diffusivity=self.Diffusivity,
           )

           # FlowAccumulator
           self.flow_accumulator = FlowAccumulator(
               self.model_grid,
               flow_director=(
                   landlab_component_parameters[
                       "FlowAccumulator"
                   ]["flow_director"]
               ),
           )

           # ErosionDeposition
           ed = landlab_component_parameters[
               "ErosionDeposition"
           ]

           self.erosion_deposition = ErosionDeposition(
               self.model_grid,
               K=ed["K"] / self.s2yr,
               v_s=ed["v_s"],
               m_sp=ed["m_sp"],
               n_sp=ed["n_sp"],
               sp_crit=ed["sp_crit"],
           )

           # SimpleSubmarineDiffuser
           sd = landlab_component_parameters[
               "SimpleSubmarineDiffuser"
           ]

           self.submarine_diffuser = (
               SimpleSubmarineDiffuser(
                   self.model_grid,
                   tidal_range=sd["tidal_range"],
                   shallow_water_diffusivity=(
                       sd["K"] / self.s2yr
                   ),
                   sea_level=sd["sea_level"],
               )
           )

           self.horizontal_surface_advector = (
               AdvectionSolverTVD(
                   self.model_grid,
                   fields_to_advect=self.elevation,
               )
           )


   # ---------------------------------------------------------------------------
   # Module-level instance — ASPECT calls these functions by name.
   # ---------------------------------------------------------------------------

   model = MyAspectLandlabModel()

   model.export_aspect_callbacks(model, globals())


ASPECT Parameter File
---------------------

The following ``.prm`` parameter file was used for the Landlab--ASPECT coupled
simulation.

.. code-block:: text
   :linenos:

   *###############  Global parameters###############*
   set Dimension                              = 3
   set Start time                             = 0
   set End time                               = 1e6
   set Resume computation                     = auto
   set Use years instead of seconds           = true
   set Nonlinear solver scheme                = single Advection, iterated Newton Stokes
   set Nonlinear solver tolerance             = 1e-4
   set Max nonlinear iterations               = 50
   set Max nonlinear iterations in pre-refinement = 10
   set CFL number                             = 0.5
   set Maximum time step                      = 20e3
   set Output directory                       = outputs/7_test64_landlab_ada_denial_2.5_km-spacing_ghost_node_2_self_horizontal_surface_advector_YES_s2yr_DIFF_ERO_DEPO_n_substep_10
   set Timing output frequency                = 1
   set Pressure normalization                 = no
   set Adiabatic surface temperature          = 1517

   *############### Solver parameters ###############*
   subsection Solver parameters

   subsection Stokes solver parameters
   set Stokes solver type                  = block AMG
   set Number of cheap Stokes solver steps = 4000
   set Linear solver tolerance             = 1e-7
   set GMRES solver restart length         = 100
   set Use full A block as preconditioner  = true
   end

   subsection Newton solver parameters
   set Max pre-Newton nonlinear iterations      = 10
   set SPD safety factor                        = 0.9
   set Nonlinear Newton solver switch tolerance = 1e-4
   set Max Newton line search iterations        = 5
   set Maximum linear Stokes solver tolerance   = 1e-5
   set Use Newton residual scaling method       = false
   set Use Newton failsafe                      = true
   set Stabilization preconditioner             = SPD
   set Stabilization velocity block             = SPD
   set Use Eisenstat Walker method for Picard iterations = false
   end

   subsection Advection solver parameters
   set GMRES solver restart length = 50
   end
   end

   *############### Governing equations ###############*
   subsection Formulation
   set Formulation       = Boussinesq approximation
   set Mass conservation = incompressible
   end

   *################ Model geometry ###############*
   subsection Geometry model
   set Model name = box

   subsection Box
   set X repetitions = 30
   set Y repetitions = 12
   set Z repetitions = 15
   set X extent      = 300e3
   set Y extent      = 120e3
   set Z extent      = 150e3
   end
   end

   *############### mesh refinement ###############*
   subsection Mesh refinement
   set Initial global refinement          = 0
   set Initial adaptive refinement        = 1
   set Time steps between mesh refinement = 0
   set Strategy = minimum refinement function, maximum refinement function

   subsection Minimum refinement function
   set Coordinate system = cartesian
   set Variable names = x,y,z
   set Function expression = if(z>=140e3, 3, if(z>120e3, 2, if(z>100e3, 1, 0)))
   end

   subsection Maximum refinement function
   set Coordinate system = cartesian
   set Variable names = x,y,z
   set Function expression = if(z>=140e3, 3, if(z>120e3, 2, if(z>100e3, 1, 0)))
   end
   end

   *############### discretization ###############*
   subsection Discretization
   set Composition polynomial degree = 2
   set Stokes velocity polynomial degree = 2
   set Temperature polynomial degree = 2
   end

   *############### mesh deformation Using Landlab ###############*

   subsection Mesh deformation
   set Mesh deformation boundary indicators = top : Landlab
   set Additional tangential mesh velocity boundary indicators = left, right, front, back

   subsection Landlab
   set MPI ranks for Landlab = 1
   set Script name = original_landlab
   set Script path = .
   set Script argument =
   end
   end

   *############### boundary velocity ###############*
   subsection Boundary velocity model
   set Prescribed velocity boundary indicators = left x: function, right x: function, bottom z: function
   end

   subsection Boundary velocity model
   set Tangential velocity boundary indicators = front, back
   end

   subsection Boundary velocity model
   subsection Function
   set Variable names = x,y,z
   set Function constants = out_vel=0.5, cm=0.01, yr=1, depth=150.e3, width=300.e3
   set Function expression = if (x<width/2., -1*out_vel/2*cm/yr, 1*out_vel/2*cm/yr); \
                             0; \
                             (out_vel*depth)/width*cm/yr;
   end
   end

   *############### compositional fields ###############*
   subsection Compositional fields
   set Number of fields = 10
   set Names of fields = sediment_age, \
                         noninitial_plastic_strain, \
                         plastic_strain, \
                         viscous_strain, \
                         sediment, \
                         sediment_thick, \
                         crust_upper, \
                         crust_lower, \
                         mantle_lithosphere, \
                         asthenosphere

   set Types of fields = generic, \
                         strain, \
                         strain, \
                         strain, \
                         chemical composition, \
                         generic, \
                         chemical composition, \
                         chemical composition, \
                         chemical composition, \
                         chemical composition

   set Compositional field methods = particles

   set Mapped particle properties = sediment_age: initial sediment_age, \
                                    noninitial_plastic_strain: noninitial_plastic_strain, \
                                    plastic_strain: plastic_strain, \
                                    viscous_strain: viscous_strain, \
                                    sediment: initial sediment, \
                                    sediment_thick: initial sediment_thick, \
                                    crust_upper: initial crust_upper, \
                                    crust_lower: initial crust_lower, \
                                    mantle_lithosphere: initial mantle_lithosphere, \
                                    asthenosphere: initial asthenosphere
   end

   *################ Temperature boundary conditions ###############*
   subsection Boundary temperature model
   set Fixed temperature boundary indicators = bottom, top
   set List of model names = box

   subsection Box
   set Bottom temperature = 1592.
   set Top temperature    = 273
   end
   end

   *################ Gravity model ################*
   subsection Gravity model
   set Model name = vertical

   subsection Vertical
   set Magnitude = 9.81
   end
   end

   *################ Post processing ################*
   subsection Particles
   set Minimum particles per cell = 50
   set Maximum particles per cell = 200
   set Load balancing strategy = remove and add particles
   set List of particle properties = initial composition, \
                                     viscoplastic strain invariants, \
                                     pT path, \
                                     position
   set Interpolation scheme = quadratic least squares

   subsection Interpolator
   subsection Quadratic least squares
   set Use quadratic least squares limiter = true
   set Use boundary extrapolation = true
   end
   end

   set Update ghost particles = true
   set Particle generator name = reference cell

   subsection Generator
   subsection Reference cell
   set Number of particles per cell per direction = 5
   end
   end
   end

   subsection Postprocess
   set List of postprocessors = basic statistics, \
                                composition statistics, \
                                heat flux densities, \
                                heat flux statistics, \
                                mass flux statistics, \
                                material statistics, \
                                matrix statistics, \
                                memory statistics, \
                                particles, \
                                pressure statistics, \
                                temperature statistics, \
                                topography, \
                                velocity statistics, \
                                visualization

   subsection Particles
   set Time between data output = 30e6
   set Data output format = vtu
   end

   subsection Visualization
   set Interpolate output = true
   set Output format = vtu
   set List of output variables = adiabat, material properties, heat flux map, named additional outputs, strain rate, \
                                  principal stress, surface stress, maximum horizontal compressive stress, heating
   set Time between graphical output = 2e6
   set Number of grouped files = 6
   set Point-wise stress and strain = true
   end
   end

   *# Checkpointing*
   subsection Checkpointing
   set Steps between checkpoint = 10
   end

