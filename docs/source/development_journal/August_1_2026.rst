August 1, 2026, Varification - Deposition Implementation Tests - Deposition and Rift Basin
========================================================================================================================

FastScape–Landlab Integration: Horizontal Surface Advection, Parameter Mapping, and Code Refinement
-------------------------------------------------------------------------------------------------------
Major effort focused on reproducing the FastScape implementation within the
Landlab–ASPECT framework while improving consistency between the two models.

1. **Added horizontal surface advection**

   Added the horizontal surface advection step to the ``update_until()``
   workflow:

   .. code-block:: python

      self.horizontal_surface_advector.run_one_step(sub_dt)

   This step was not present in the earlier implementation from Daniel's
   Ada Lovelace poster code. It was added because ASPECT provides horizontal
   surface velocities, and the evolving topography should be transported by
   these velocities before erosion and deposition are computed. Including
   this process makes the coupling more physically consistent and better
   represents the behavior of FastScape.

2. **Mapped FastScape parameters to Landlab**

   Completed a detailed comparison between FastScape and the equivalent
   Landlab components. Every available parameter was mapped and documented,
   together with notes describing direct equivalents, implementation
   differences, and parameters that currently have no Landlab counterpart.
   This provides a roadmap for the remaining development work needed to
   achieve closer feature parity.

3. **Improved horizontal velocity handling**

   Refined the horizontal velocity update workflow to better reflect how the
   model operates. Previously, the code implied that the horizontal velocity
   field was being reassigned each timestep using

   .. code-block:: python

      self.horizontal_velocity = self.determine_horizontal_velocity(...)

   However, ``determine_horizontal_velocity()`` updates the existing velocity
   field in place rather than creating a new one. The misleading assignment
   was removed, and the method is now called directly to update the current
   velocity field.

   In addition, the ``AdvectionSolverTVD`` object was moved from the
   per-timestep workflow to ``initialize_landlab()`` so that it is created
   only once during model initialization and reused throughout the simulation.
   This makes the code clearer, avoids unnecessary object creation, and
   better separates model initialization from timestep updates.