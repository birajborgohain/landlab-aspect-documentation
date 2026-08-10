August 7, 2026 Denial Ada error, case 1 with ``s2yr`` and case 2 without s2yr
==============================================================================


**Error Summary case 1, k/s2yr, d/s2yr**
------------------------------------------

The simulation did not complete successfully. The main problem occurred at
**Timestep 9**.

1. **Evaluation points outside the model domain**

   The following warning was reported:

   .. code-block:: text

      WARNING: not all evaluation points were found inside the domain!
      Point 0: -500 80000
      Point 1: -250 80000
      Point 883: 220250 80000
      Point 884: 220500 80000

   Some requested evaluation points were outside the computational domain.

2. **Nonlinear solver became unstable**

   At Timestep 9, the nonlinear residual initially was:

   .. code-block:: text

      1.19269

   The residual then increased dramatically:

   .. code-block:: text

      16.6717
      54.3931
      104493
      8.15752e+11

   This indicates strong divergence of the nonlinear solution.

3. **Linear solver iterations became very large**

   Several systems required approximately 90--120 iterations. For example:

   .. code-block:: text

      ve_stress_xx system ... 114 iterations
      plastic_strain system ... 114 iterations
      viscous_strain system ... 114 iterations

4. **Solver required a different preconditioner**

   The solver eventually reported:

   .. code-block:: text

      Solving ve_stress_xx system ...
      retrying linear solve with different preconditioner...

**Overall Observation**
~~~~~~~~~~~~~~~~~~~~~~~~

The simulation was stable through Timestep 8, but numerical instability
developed during Timestep 9. The instability was characterized by evaluation
points outside the domain, rapidly increasing nonlinear residuals, large
linear-solver iteration counts, and the need to retry the linear solve with a
different preconditioner.

The simulation therefore did not complete successfully for this case.


Error Summary case 2: Without ``s2yr``
----------------------------------------------------

This run corresponds to the case where the Landlab parameters were used
**without dividing by ``s2yr``**.

The simulation did not show the same immediate ``divide by zero`` and
``overflow`` warnings observed in the other ``no_s2yr`` run. Instead, the
model successfully completed the initial timestep and then progressed to
the first physical timestep.

Observed behavior
~~~~~~~~~~~~~~~~~

1. **Evaluation-point warning**

   At the beginning of the simulation, ASPECT reported that some Landlab
   evaluation points were outside the ASPECT domain:

   .. code-block:: text

      WARNING: not all evaluation points were found inside the domain!

      Evaluation points not found:
      Point 0: -500 80000
      Point 1: -250 80000
      Point 883: 220250 80000
      Point 884: 220500 80000

   The same warning appeared repeatedly during the run.

   This is a warning about the location of Landlab evaluation points and
   should be distinguished from the subsequent termination of the run.

2. **Timestep 0 completed successfully**

   ASPECT successfully solved the initial Stokes problem and reached
   postprocessing.

   The initial topography remained:

   .. code-block:: text

      Topography min/max: 0 m, 0 m

   The velocity solution at this stage was:

   .. code-block:: text

      RMS, max velocity:
      0.00158 m/year, 0.0028 m/year

   Therefore, the simulation did not fail during initialization or
   timestep 0.

3. **The simulation reached timestep 1**

   The log then shows:

   .. code-block:: text

      *** Timestep 1:  t=10000 years, dt=10000 years

   This indicates that timestep 0 was completed and ASPECT advanced to the
   first physical timestep.

4. **SSH connection was lost**

   The last messages recorded in the log were:

   .. code-block:: text

      Read from remote host nmthpc.id.nmt.edu: Operation timed out
      Connection to nmthpc.id.nmt.edu closed.
      client_loop: send disconnect: Broken pipe

   The provided log therefore ends with an SSH connection timeout rather
   than an ASPECT solver error.


Landlab Coupling Script
-----------------------

The following code shows the Landlab surface-process implementation used
in the ASPECT--Landlab coupling.

.. code-block:: python
   :linenos:

   from mpi4py import MPI
   import json
   import os
   import numpy as np
   import landlab
   from landlab.components import LinearDiffuser
   from landlab.components import FlowAccumulator
   from landlab.components import DepressionFinderAndRouter
   from landlab.components import ErosionDeposition
   from landlab.components import SimpleSubmarineDiffuser
   from landlab.components import AdvectionSolverTVD

   from landlab.io.native_landlab import save_grid, load_grid

   from landlab.io.legacy_vtk import write_legacy_vtk

   comm = None

   model_grid = None
   elevation = None

   linear_diffuser = None
   flow_accumulator = None
   erosion_deposition = None
   surface_advector = None
   submarine_diffuser = None

   horizontal_velocity = None
   ux = None
   uy = None

   s2yr = 60 * 60 * 24 * 365.25
   timestep = 0
   vtks = []

   def override_boundary_values(boundary_ids, field):
       '''
       A function which takes a user-specified array of nodes on a LandLab
       model boundary and sets the corresponding 'field' value at these
       boundary nodes equal to an adjacent core node.

       boundary_ids: List of boundary ids on the LandLab model grid.
                     For example: model_grid.nodes_at_top_edge to run
                     this function on the top boundary.

       field:        The LandLab field that will apply to the boundary.
                     For example: elevation
       '''

       # Iterate over all the nodes on the bottom boundary
       for boundary_idx in boundary_ids:

           # Find the nodes which are adjacent to the current boundary
           # node. This will include two boundary nodes, and a single
           # core node (for a raster grid).
           neighbour_nodes = (
               model_grid.adjacent_nodes_at_node[boundary_idx]
           )

           # Iterate over the nodes that are neighbouring the current
           # boundary node.
           for neighbour_idx in range(len(neighbour_nodes)):

               # Check to see if the neighbouring node is a boundary
               # node. If it is not, then we want to proceed.
               if not model_grid.node_is_boundary(
                   neighbour_nodes[neighbour_idx]
               ):

                   # Set the elevation on the boundary equal to the
                   # elevation at the adjacent core node.
                   field[boundary_idx] = field[
                       neighbour_nodes[neighbour_idx]
                   ]


   def initialize(comm_handle):
       if not comm_handle is None:

           # Convert the handle back to an MPI communicator
           global comm
           comm = MPI.Comm.f2py(comm_handle)

           rank = comm.Get_rank()
           size = comm.Get_size()

           print(f"Python: Hello from Rank {rank} of {size}")

           data = 1
           globalsum = comm.allreduce(data, op=MPI.SUM)

           if comm.rank == 0:
               print(
                   f"\tPython: testing communication; sum {globalsum}"
               )

       else:
           print("Python: running sequentially!")


   def finalize():
       pass


   # Run the Landlab simulation from the current time to end_time and
   # return the new topographic elevation (in m) at each local node.
   #
   # dict_variable_name_to_value_in_nodes is a dictionary mapping
   # variables (x velocity, y velocity, temperature, etc.) to an
   # array of values in each node.

   def update_until(
       end_time,
       current_time,
       dict_variable_name_to_value_in_nodes,
   ):
       global elevation
       global linear_diffuser
       global submarine_diffuser
       global flow_accumulator
       global erosion_deposition
       global timestep
       global horizontal_velocity
       global surface_advector

       dt = end_time - current_time
       timestep += 1

       deposition_erosion = np.zeros(
           model_grid.number_of_nodes
       )

       # Extract the velocity along the ASPECT model, which is
       # located at y=0 on the Landlab mesh.
       slice_x_velocity = (
           dict_variable_name_to_value_in_nodes["x velocity"]
       )

       slice_y_velocity = (
           dict_variable_name_to_value_in_nodes["y velocity"]
       )

       # Create empty arrays to project the velocity and composition
       # values out from y=0 to all nodes on the Landlab mesh.
       vertical_velocity = np.zeros(
           model_grid.number_of_nodes
       )

       lateral_velocity = np.zeros(
           model_grid.number_of_nodes
       )

       unique_x_values = np.unique(
           model_grid.x_of_node
       )

       for x in unique_x_values:
           vertical_velocity[
               model_grid.x_of_node == x
           ] = slice_y_velocity[
               unique_x_values == x
           ]

           lateral_velocity[
               model_grid.x_of_node == x
           ] = slice_x_velocity[
               unique_x_values == x
           ]

       x_vel_at_links = (
           model_grid.map_mean_of_link_nodes_to_link(
               lateral_velocity
           )
       )

       y_vel_at_links = (
           model_grid.map_mean_of_link_nodes_to_link(
               np.zeros(model_grid.number_of_nodes)
           )
       )

       # y velocity is zero since the ASPECT model is 2D.

       horizontal_velocity[
           model_grid.horizontal_links
       ] = x_vel_at_links[
           model_grid.horizontal_links
       ]

       horizontal_velocity[
           model_grid.vertical_links
       ] = y_vel_at_links[
           model_grid.vertical_links
       ]

       surface_advector = AdvectionSolverTVD(
           model_grid,
           fields_to_advect=elevation,
       )

       # Substepping for surface processes
       if dt > 0:
           n_substeps = 10
           sub_dt = dt / n_substeps

           for _ in range(n_substeps):

               elevation_before = elevation.copy()

               elevation[
                   model_grid.core_nodes
               ] += (
                   vertical_velocity[
                       model_grid.core_nodes
                   ] * sub_dt
               )

               surface_advector.update(sub_dt)

               flow_accumulator.run_one_step()

               erosion_deposition.run_one_step(
                   sub_dt
               )

               linear_diffuser.run_one_step(
                   sub_dt
               )

               submarine_diffuser.run_one_step(
                   sub_dt
               )

               deposition_erosion += (
                   elevation - elevation_before
               )

           pass

       current_time = end_time

       print(
           "Min elevation",
           np.min(elevation),
           "Max elevation:",
           np.max(elevation),
       )

       output_directory = "./landlab_2km_resolution/"
       landlab_output_directory = os.path.join(
           output_directory,
           "landlab",
       )

       if not os.path.isdir(
           landlab_output_directory
       ):
           os.makedirs(
               landlab_output_directory,
               exist_ok=True,
           )

       filename = (
           f"{output_directory}landlab_"
           f"{str(timestep).zfill(3)}.vtk"
       )

       print(
           "Writing output VTK file...",
           filename,
       )

       vtk_file = write_legacy_vtk(
           path=filename,
           grid=model_grid,
           clobber=True,
       )

       vtks.append(
           (current_time, filename)
       )

       if True:

           # Write vtk.series file
           # ParaView supports legacy VTK in this format.
           with open(
               f"{output_directory}landlab.vtk.series",
               "w",
           ) as f:

               series = {
                   "file-series-version": "1.0",
                   "files": [
                       {
                           "name": os.path.basename(filename),
                           "time": (
                               time
                               / 60
                               / 60
                               / 24
                               / 365.25
                           ),
                       }
                       for time, filename in vtks
                   ],
               }

               json.dump(
                   series,
                   f,
                   indent=2,
               )

       deposition_erosion_2d = np.zeros(
           len(
               np.unique(
                   model_grid.x_of_node
               )
           )
       )

       for x in unique_x_values:

           # deposition_erosion_2d[
           #     unique_x_values == x
           # ] = np.average(
           #     deposition_erosion[
           #         model_grid.x_of_node == x
           #     ]
           # )

           deposition_erosion_2d = (
               deposition_erosion[
                   model_grid.y_of_node == 0
               ]
           )

       return deposition_erosion_2d


   def set_mesh_information(
       dict_grid_information,
   ):
       global model_grid
       global elevation
       global horizontal_velocity
       global ux
       global uy

       if not model_grid:

           print("* Creating RasterModelGrid ...")

           x_extent = 220e3
           y_extent = 100e3
           spacing = 250.0

           nrows = (
               int(y_extent / spacing)
               + 5
           )

           ncols = (
               int(x_extent / spacing)
               + 5
           )

           model_grid = landlab.RasterModelGrid(
               (nrows, ncols),
               xy_spacing=(
                   spacing,
                   spacing,
               ),
               xy_of_lower_left=(
                   -2 * spacing,
                   -y_extent / 2
                   - 2 * spacing,
               ),
           )

           print(
               "* Creating topographic elevation ..."
           )

           # Initialize topography array with zeros
           elevation = model_grid.add_zeros(
               "topographic__elevation",
               at="node",
           )

           # Close all boundaries
           model_grid.set_closed_boundaries_at_grid_edges(
               right_is_closed=True,
               left_is_closed=True,
               top_is_closed=True,
               bottom_is_closed=True,
           )

           print(
               "\tnumber of nodes:",
               model_grid.number_of_nodes,
           )

           node_id = model_grid.find_nearest_node(
               [
                   x_extent / 2,
                   -y_extent / 2
                   - spacing,
               ]
           )

           model_grid.status_at_node[
               node_id
           ] = (
               model_grid.BC_NODE_IS_FIXED_VALUE
           )

           elevation[node_id] = 0

           horizontal_velocity = (
               model_grid.add_zeros(
                   "advection__velocity",
                   at="link",
               )
           )

           ux = model_grid.add_zeros(
               "x_velocity",
               at="node",
           )

           uy = model_grid.add_zeros(
               "y_velocity",
               at="node",
           )

           initialize_landlab_components(
               None
           )

           print("* Done")


   # If the ASPECT mesh is 2D, then we only want to return the
   # unique values of x on the LandLab mesh. The logic here is
   # probably different if the LandLab mesh is not a raster.
   def get_grid_x(grid_dictionary):
       global model_grid

       return np.unique(
           model_grid.x_of_node
       )


   # If the ASPECT mesh is 2D, then we only return an array of
   # 0s for the y values, since this is where the ASPECT surface
   # is located.
   def get_grid_y(grid_dictionary):
       global model_grid

       return np.zeros(
           np.unique(
               model_grid.x_of_node
           ).shape
       )


   def initialize_landlab_components(
       landlab_component_parameters,
   ):
       global model_grid
       global elevation
       global linear_diffuser
       global flow_accumulator
       global erosion_deposition
       global submarine_diffuser

       D_val = 1e-2 / s2yr
       K_val = 1e-5 / s2yr
       K_sub = 1e-2 / s2yr

       print(
           "* Initializing Landlab components ..."
       )

       linear_diffuser = LinearDiffuser(
           model_grid,
           linear_diffusivity=D_val,
       )

       flow_accumulator = FlowAccumulator(
           model_grid,
           flow_director="D8",
       )

       erosion_deposition = ErosionDeposition(
           model_grid,
           K=K_val,
           v_s=1000.0,
           m_sp=0.5,
           n_sp=1.0,
           sp_crit=0,
       )

       submarine_diffuser = (
           SimpleSubmarineDiffuser(
               model_grid,
               tidal_range=0.0,
               shallow_water_diffusivity=K_sub,
               sea_level=0.0,
           )
       )

       print(
           "* Done initializing Landlab components"
       )

       pass


   def checkpoint(checkpoint_dict):
       global model_grid
       global checkpoint_index

       # Extract checkpointing information from the
       # checkpoint dictionary.
       checkpoint_index = checkpoint_dict[
           "Current checkpoint ID"
       ]

       output_directory = checkpoint_dict[
           "Output directory"
       ]

       # Create LandLab checkpoint directory within
       # the ASPECT output directory.
       output_directory = os.path.join(
           output_directory,
           "landlab_checkpoints",
       )

       os.makedirs(
           output_directory,
           exist_ok=True,
       )

       print(
           "Checkpointing the LandLab model grid..."
       )

       filename = os.path.join(
           output_directory,
           f"landlab_checkpoint_"
           f"{str(checkpoint_index).zfill(2)}.grid",
       )

       save_grid(
           model_grid,
           filename,
           clobber=True,
       )

       pass


   def resume_checkpoint(checkpoint_dict):
       global model_grid
       global elevation
       global checkpoint_index
       global horizontal_velocity
       global ux
       global uy

       restart_checkpoint_id = checkpoint_dict[
           "Resume checkpoint ID"
       ]

       # Extract checkpointing information from the
       # checkpoint dictionary.
       output_directory = checkpoint_dict[
           "Output directory"
       ]

       output_directory = os.path.join(
           output_directory,
           "landlab_checkpoints",
       )

       # Load the LandLab grid from the checkpoint file
       # corresponding to the checkpoint index.
       print(
           "Loading the LandLab model grid..."
       )

       filename = os.path.join(
           output_directory,
           f"landlab_checkpoint_"
           f"{str(restart_checkpoint_id).zfill(2)}.grid",
       )

       model_grid = load_grid(
           filename
       )

       elevation = model_grid.at_node[
           "topographic__elevation"
       ]

       horizontal_velocity = model_grid.at_link[
           "advection__velocity"
       ]

       ux = model_grid.at_node[
           "x_velocity"
       ]

       uy = model_grid.at_node[
           "y_velocity"
       ]

       # We need to initialize the components after
       # loading the LandLab grid, since these are not stored.
       initialize_landlab_components(
           None
       )

       pass


   # Return the initial topography along y=0,
   # where the ASPECT surface is located.
   def get_initial_topography(
       grid_dictionary,
   ):
       global elevation

       return elevation[
           model_grid.y_of_node == 0
       ]


   def write_output(timestep):

       # Write the grid to vtk
       print(
           "Writing output VTK file..."
       )

       vtk_file = write_legacy_vtk(
           path=(
               f"./output_"
               f"{str(timestep).zfill(3)}.vtk"
           ),
           grid=model_grid,
           clobber=True,
       )

ASPECT Parameter File
---------------------

The following ASPECT parameter file was used for the simulation.

.. code-block:: text
   :linenos:

   *#######  Global parameters#######*
   set World builder file                     = original.wb
   set Dimension                              = 2
   set Start time                             = 0
   set End time                               = 200e4
   set Use years instead of seconds           = true
   set Resume computation                     = auto
   set Nonlinear solver scheme                = iterated Advection and Newton Stokes
   set Nonlinear solver tolerance             = 1e-4
   set Max nonlinear iterations               = 40
   set Nonlinear solver failure strategy      = continue with next timestep
   set CFL number                             = 0.25
   set Maximum time step                      = 1e4
   set Output directory                       = outputs/ws1_ada
   set Pressure normalization                 = no
   set Use operator splitting                 = true

   subsection Time stepping
     subsection Repeat on nonlinear solver failure
       set Cut back factor = 0.5
     end
   end

   subsection Solver parameters

     subsection Stokes solver parameters
       set Stokes solver type = block AMG
       set Number of cheap Stokes solver steps = 4000
       set Linear solver tolerance = 1e-8
       set GMRES solver restart length = 100
       set Use full A block as preconditioner = true
     end

     subsection Newton solver parameters
       set Max pre-Newton nonlinear iterations = 10
       set SPD safety factor = 0.9
       set Nonlinear Newton solver switch tolerance = 1e-5
       set Max Newton line search iterations = 5
       set Maximum linear Stokes solver tolerance = 1e-8
       set Use Newton residual scaling method = true
       set Use Newton failsafe = true
       set Stabilization preconditioner = SPD
       set Stabilization velocity block = SPD
       set Use Eisenstat Walker method for Picard iterations = false
     end

     subsection Advection solver parameters
       set GMRES solver restart length = 150
     end

     subsection Operator splitting parameters
       set Reaction time step = 50000
       set Reaction time steps per advection step = 1
       set Reaction solver type = fixed step
     end
   end

   subsection Formulation
     set Formulation = Boussinesq approximation
     set Enable elasticity = true
   end

   subsection Discretization
     set Composition polynomial degree = 2
     set Stokes velocity polynomial degree = 2
     set Temperature polynomial degree = 2
     set Use discontinuous composition discretization = true
   end

   subsection Geometry model
     set Model name = box

     subsection Box
       set X repetitions = 110
       set Y repetitions = 40
       set X extent = 220e3
       set Y extent = 80e3
     end
   end

   subsection Mesh refinement
     set Initial adaptive refinement = 3
     set Initial global refinement = 0
     set Time steps between mesh refinement = 4
     set Strategy = composition threshold

     subsection Composition threshold
       set Compositional field thresholds = 1e50, 1e50, 1e50, 1e50, 1e50, 1e50, 1.0, 1e50, 1e50, 1e50, 1e50, 1e50, 1e50, 1e50
     end
   end

   subsection Mesh deformation
     set Mesh deformation boundary indicators = top: Landlab
     set Additional tangential mesh velocity boundary indicators = left, right

     subsection Landlab
       set MPI ranks for Landlab = 1
       set Script name = original_landlab
       set Script argument =
       set Script path =
     end
   end

   subsection Boundary velocity model
     set Prescribed velocity boundary indicators = left x: function, right x: function, bottom y: function

     subsection Function
       set Variable names = x,y
       set Function constants = v=0.0025, w=320.e3, d=80.e3
       set Function expression = if (x < w/2 , -v, v) ; v*2*d/w
     end
   end

   subsection Compositional fields
     set Number of fields = 14
     set Names of fields = ve_stress_xx, \
                           ve_stress_yy, \
                           ve_stress_xy, \
                           ve_stress_xx_old, \
                           ve_stress_yy_old, \
                           ve_stress_xy_old, \
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
                           strain, \
                           strain, \
                           strain, \
                           chemical composition, \
                           chemical composition, \
                           generic, \
                           generic, \
                           chemical composition

     set Compositional field methods = field
   end

   subsection Initial composition model
     set List of model names = function, world builder
     set List of model operators = add, add

     subsection Function
       set Variable names = x,y
       set Function expression = 0; 0; 0; 0; 0; 0; \
                                 0; 0; 0; \
                                 if (y>=50.e3, 1, 0); \
                                 if (y<50.e3, 1, 0); \
                                 0; 0; 0
     end
   end

   subsection Boundary composition model
     set Model name = function
     set Fixed composition boundary indicators = top, bottom
     set Allow fixed composition on outflow boundaries = true

     subsection Function
       set Coordinate system = cartesian
       set Variable names = x,y,t
       set Function constants = DZ = 80e3, SeaLevel = 0
       set Function expression = 0; 0; 0; 0; 0; 0; \
                                 0; \
                                 0; \
                                 0; \
                                 0; \
                                 if(y<1e3, 1, 0); \
                                 if(y>75e3, t/1e6, 0); \
                                 if(y>75e3, DZ - SeaLevel - y, 0); \
                                 if(y>75e3, 1, 0)
     end
   end

   subsection Boundary temperature model
     set Fixed temperature boundary indicators = bottom, top
     set List of model names = box

     subsection Box
       set Bottom temperature = 1573
       set Top temperature = 273
     end
   end

   subsection Initial temperature model
     set Model name = function

     subsection Function
       set Variable names = x,y
       set Function constants = h=80e3, ts1=273, ts2=683, ts3=993, \
                                A1=1.e-6, A2=0.25e-6, A3=0.0, \
                                k1=2.5, k2=2.5, k3=2.5, \
                                qs1=0.06125, qs2=0.04125, qs3=0.03625

       set Function expression = if( (h-y)<=30.e3, \
                                     ts1 + (qs1/k1)*(h-y) - (A1*(h-y)*(h-y))/(2.0*k1), \
                                     if( (h-y)>30.e3 && (h-y)<=30.e3, \
                                         ts2 + (qs2/k2)*(h-y-30.e3) - (A2*(h-y-30.e3)*(h-y-30.e3))/(2.0*k2), \
                                         ts3 + (qs3/k3)*(h-y-30.e3) - (A3*(h-y-30.e3)*(h-y-30.e3))/(2.0*k3) ) );
     end
   end

   subsection Heating model
     set List of model names = compositional heating

     subsection Compositional heating
       set Use compositional field for heat production averaging = 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1
       set Compositional heating values = 0, 0, 0, 0, 0, 0, 0., 0., 0., 0., 1.0e-6, 0.0, 0.0, 0.0, 1.0e-6
     end
   end

   subsection Material model
     set Model name = visco plastic
     set Material averaging = geometric average only viscosity

     subsection Visco Plastic
       set Reference temperature = 273
       set Minimum strain rate = 1.e-20
       set Reference strain rate = 1.e-16
       set Minimum viscosity = 1e18
       set Maximum viscosity = 1e26

       set Define thermal conductivities = true
       set Thermal conductivities = 2.0
       set Heat capacities = 1000.

       set Densities = background: 2700, \
                       crust: 2700, \
                       mantle_lithosphere: 3300, \
                       sediment: 2100

       set Thermal expansivities = 2e-5
       set Viscosity averaging scheme = geometric
       set Viscous flow law = dislocation

       set Prefactors for dislocation creep = background: 1.0378e-14, \
                                              crust: 1.4332e-14, \
                                              mantle_lithosphere: 1.0378e-14, \
                                              sediment: 1.37e-26

       set Stress exponents for dislocation creep = background: 3.5, \
                                                    crust: 3.0, \
                                                    mantle_lithosphere: 3.5, \
                                                    sediment: 4.0

       set Activation energies for dislocation creep = background: 480.e3, \
                                                      crust: 356.e3, \
                                                      mantle_lithosphere: 480.e3, \
                                                      sediment: 223.e3

       set Activation volumes for dislocation creep = background: 0., \
                                                      crust: 0, \
                                                      mantle_lithosphere: 0, \
                                                      sediment: 0

       set Angles of internal friction = 30
       set Cohesions = 30.e6

       set Strain weakening mechanism = plastic weakening with plastic strain and viscous weakening with viscous strain
       set Start plasticity strain weakening intervals = 0.5
       set End plasticity strain weakening intervals = 1.5
       set Cohesion strain weakening factors = 0.25
       set Friction strain weakening factors = 0.25
       set Start prefactor strain weakening intervals = 0.5
       set End prefactor strain weakening intervals = 1.5
       set Prefactor strain weakening factors = 0.1

       set Use plastic damper = true
       set Plastic damper viscosity = 1e21

       set Elastic shear moduli = 30.0e9
       set Use fixed elastic time step = false
     end
   end

   subsection Gravity model
     set Model name = vertical

     subsection Vertical
       set Magnitude = 9.81
     end
   end

   subsection Postprocess
     set List of postprocessors = basic statistics, composition statistics, heat flux densities, heat flux statistics, mass flux statistics, pressure statistics, temperature statistics, topography, velocity statistics, visualization

     subsection Visualization
       set List of output variables = heat flux map, material properties, named additional outputs, strain rate

       subsection Material properties
         set List of material properties = density, viscosity
       end

       set Output format = vtu
       set Time between graphical output = 100.e3
       set Interpolate output = true
       set Write higher order output = true
     end

     subsection Particles
       set Time between data output = 100.e3
       set Data output format = vtu
     end
   end

   subsection Checkpointing
     set Steps between checkpoint = 5
   end

World Builder Configuration
---------------------------

The following World Builder configuration defines the fault geometry,
temperature, and compositional structure used in the ASPECT model.

.. code-block:: json
   :linenos:

   {
       "version": "1.0",
       "cross section": [
           [0, 0.8e5],
           [3.2e5, 0.8e5]
       ],
       "features":
       [
           {
               "model": "fault",
               "name": "fault1",
               "dip point": [3.2e5, 2e5],
               "min depth": 0,
               "max depth": 1e5,
               "coordinates":
               [
                   [110e3, 4e5],
                   [110e3, 0]
               ],
               "segments":
               [
                   {
                       "length": 0.7e5,
                       "thickness": [8000],
                       "angle": [60]
                   }
               ],
               "temperature models":
               [
                   {
                       "model": "uniform",
                       "temperature": 273
                   }
               ],
               "composition models":
               [
                   {
                       "model": "smooth",
                       "compositions": [6, 8],
                       "operation": "add",
                       "side distance fault center": 4000,
                       "center fractions": [1.5, 1.5],
                       "side fractions": [0.5, 0.5]
                   }
               ]
           }
       ]
   }