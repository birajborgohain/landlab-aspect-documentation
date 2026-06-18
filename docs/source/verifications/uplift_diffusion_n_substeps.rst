
Verification of the ``n_substeps`` Coupling Algorithm
=======================================================
-----------------------
Objective
-----------------------


We are investigating the reliability and numerical consistency of the ``n_substeps`` 
implementation within the coupled algorithm. This effort was motivated by an 
observed discrepancy whereby the coupled simulations fail to reproduce 
the topographic evolution obtained from the prescribed standalone 
benchmark across a range of ``n_substeps`` values. The present experimental 
design aims to isolate the source of this discrepancy and determine 
whether it arises from the coupling strategy, timestep partitioning, 
or another aspect of the implementation.

During the development of an uplift–diffusion benchmark for the coupled ASPECT–Landlab framework based on an existing 
standalone Landlab setup, discrepancies were observed between coupled and standalone simulations when the 
temporal coupling parameter ``n_substeps`` was increased beyond 1. The parameter ``n_substeps`` is a numerical coupling 
parameter rather than a physical model parameter. It controls the temporal resolution of the coupling by dividing 
each ASPECT–Landlab coupling timestep into multiple substeps. In the coupling algorithm, ``n_substeps`` is decleared as following 
``sub_dt = dt / n_substeps``, where ``dt`` represents the ASPECT time. 



.. math::
   dt = t_{n+1}^{\mathrm{ASPECT}} - t_n^{\mathrm{ASPECT}}

where:

* :math:`t_n^{\mathrm{ASPECT}}` is the current ASPECT simulation time.
* :math:`t_{n+1}^{\mathrm{ASPECT}}` is the next ASPECT simulation time.


 **Code snippet -1:** *Snippet of the coupling algorithm.*

.. code-block:: python
   :linenos:
   

   def set_mesh_information(self, ..):

      self.model_grid = landlab.RasterModelGrid()
      self.uplift_rate = (
      self.model_grid.node_y[self.model_grid.core_cells]/ 1e5
      )
   def update_until(self,..):
         
      dt = end_time - self.current_time
      if dt > 0:
         n_substeps = N
         sub_dt = dt / n_substeps
            for i in range(n_substeps):
               self.linear_diffuser.run_one_step(sub_dt)
               self.model_grid.at_node["topographic__elevation"]
               [self.model_grid.core_nodes] += (self.uplift_rate * sub_dt)


Although the coupling timestep ``dt`` is subdivided into smaller timesteps according to

.. math::

   \mathrm{sub\_dt} = \frac{\mathrm{dt}}{\mathrm{n\_substeps}}

the total elapsed simulation time over a coupling interval remains unchanged. Since ``n_substeps`` 
is a numerical coupling parameter rather than a physical model parameter, varying its value should 
not substantially alter the model solution for a benchmark with constant uplift rate and constant 
diffusivity. In principle, the same amount of uplift is applied over the interval ``dt``, and diffusion 
acts over the same total physical time regardless of how that interval is partitioned.
However, the predicted topography varied systematically as ``n_substeps`` 
increased. This indicates that the solution is sensitive to the temporal splitting of uplift and diffusion 
within a coupling timestep. The experiments presented below investigate 
the origin of these differences and identify suitable range of ``n_substeps`` values for coupled 
ASPECT–Landlab simulations in which surface uplift is prescribed from ASPECT-derived velocity fields.

--------------------------------
How discrepancy was identified?
--------------------------------
When uplift is prescribed directly within the Landlab component of the coupling algorithm (code snippet-1 line number 5), 
the coupled ASPECT–Landlab model reproduces the standalone Landlab benchmark only for ``n_substeps = 1``. 
Increasing ``n_substeps`` to ``2``, ``3``, ``9``, ``15``, ``20``, and ``40`` results in progressively lower 
topography relative to the standalone solution, despite all simulations using identical uplift and diffusion parameters.

-------------------------------------------------------------
Method applied to investigate the origin of the discrepancy
-------------------------------------------------------------
To investigate the origin of this discrepancy, tracer statements were inserted immediately before and 
after the diffusion and uplift operations within each coupling substep (code snippet 2 shows the tracer implimentation). The tracer output records the 
maximum surface elevation at three stages of the update sequence: (1) before diffusion, (2) after diffusion, 
and (3) after uplift. By tracking the elevation change associated with each process independently, 
it is possible to determine how repeated diffusion–uplift interactions introduced by increasing ``n_substeps`` 
influence the final topographic evolution.

.. **Code Snippet 2.** Tracer instrumentation used to record elevation changes before diffusion, after diffusion, and after uplift during each coupling substep.

**Code Snippet 2.** *Tracer instrumentation used to record elevation changes before diffusion, after diffusion, and after uplift during each coupling substep.*


.. raw:: html

   <div style="
      background:#f8f9fa;
      padding:12px;
      border-radius:5px;
      border:1px solid #ddd;
      margin:10px 0;
      font-size:0.95em;">

   <pre style="
      margin-top:10px;
      font-size:0.9em;
      line-height:1.4;
      font-family:'Courier New', monospace;">

    1  for i in range(n_substeps):

    2      trace(f"Starting substep {i}")

    3      <span style="
             background:#fff3cd;
             color:#856404;
             font-weight:bold;">
    4      # TRACE: elevation before diffusion
    5      trace(f"Before diffusion = {np.max(self.elevation)}")
           </span>

    6      self.linear_diffuser.run_one_step(sub_dt)

    7      <span style="
             background:#d4edda;
             color:#155724;
             font-weight:bold;">
    8      # TRACE: elevation after diffusion
    9      trace(f"After diffusion = {np.max(self.elevation)}")
           </span>

   10      self.model_grid.at_node["topographic__elevation"][
   11          self.model_grid.core_nodes
   12      ] += self.uplift_rate * sub_dt

   13      <span style="
             background:#cce5ff;
             color:#004085;
             font-weight:bold;">
   14      # TRACE: elevation after uplift
   15      trace(f"After uplift = {np.max(self.elevation)}")
           </span>

   </pre>

   </div>

-------------
Model Setup
-------------
To evaluate the numerical behavior of the ASPECT–Landlab coupling framework, we constructed a 
benchmark experiment based on the standalone Landlab linear diffusion test case. The objective  
was to determine whether the coupled framework could reproduce the reference 
solution as given in tandalone Landlab linear diffusion test. Two scenarios were tested 
in coupled framework:

- Uplift triggered from Landlab by declearing in ``inport-template.py``
- Uplift driven from ASPECT velocity field by declearing in ``.prm``

Case 1 : Landlab induced uplift configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**ASPECT parameter file** ``.prm`` :


The geodynamic component was implemented using ASPECT in a three-dimensional 
rectangular domain with dimensions of 900 × 1900 × 1 units in the x-, y-, and z-directions,
respectively. The domain was discretized using a structured mesh consisting of 9 and 19 horizontal 
repetitions in the x- and y-directions and a single element in the vertical direction, 
resulting in a horizontal node spacing of 100 units. No additional global mesh refinement 
was applied. Simulations were performed for a total model time of 3 time units (which is in 
second by setting ``set Use years instead of seconds = false``) using a 
maximum timestep of 1.

``no Stokes, no Advection`` non-linear solver used. The initial temperature field 
was prescribed as a linear depth-dependent function between a lower boundary temperature 
of 1600 K and an upper boundary temperature of 273 K. Gravity was applied vertically with 
a magnitude of 1, and the incompressible Boussinesq approximation was employed. Material 
properties were represented using ASPECT's simple material model with a reference density 
of 2700 kg m\ :sup:`-3`, a thermal expansion coefficient of 3 × 10\ :sup:`-5` K\ :sup:`-1`, 
a thermal conductivity of 3 W m\ :sup:`-1` K\ :sup:`-1`, a specific heat capacity of 800 J kg\ :sup:`-1` K\ :sup:`-1`, 
and a constant viscosity of 10\ :sup:`22` Pa s.


Surface evolution was coupled to ASPECT through the mesh deformation
framework. The top boundary of the ASPECT domain was assigned to the
``Landlab`` mesh deformation plugin, allowing surface displacements
computed by Landlab to be transferred directly to the ASPECT mesh.
To maintain mesh quality during surface motion, tangential mesh
velocities were permitted along the lateral boundaries.

The coupling was activated in the ASPECT parameter file using:

.. code-block:: text

   subsection Mesh deformation
     set Mesh deformation boundary indicators = top: Landlab
     set Additional tangential mesh velocity boundary indicators = left, right, front, back

     subsection Landlab
       set MPI ranks for Landlab = 1
       set Script name = import-template
     end
   end

Here, the top surface is controlled by the Landlab mesh deformation
plugin, while one MPI rank is allocated to execute the Landlab model.
The Python script ``import-template.py`` defines the Landlab grid,
surface-process components, and the data exchange routines used by the
ASPECT--Landlab coupling framework.



**Landlab parameter file** ``import-template.py`` :

The surface-process component was implemented using the Landlab landscape evolution framework. 
The Landlab domain covers an area of 900 m × 1900 m and is represented by a raster grid with a 
spacing of 100 m, resulting in 20 rows and 10 columns of nodes. All four boundaries were assigned
fixed-elevation boundary conditions. The initial topography consisted of a nearly planar surface
with an elevation of 0 m. To ensure reproducibility and consistency with the original Landlab 
benchmark, a small-amplitude random perturbation generated using a fixed random seed was added
to the surface elevation field.

Surface transport was simulated using Landlab's linear diffusion component. A constant linear 
diffusivity was applied uniformly across the domain:

.. math::

   D = 5 \times 10^{4}\ \mathrm{m^2\, ASPECT time^{-1}}

The model was advanced using a timestep of 1 year for a total simulation duration of 3 years.

In the standalone Landlab benchmark, uplift was prescribed as

.. math::

   U(y) = \frac{y}{10^5}

where :math:`y` denotes the northward coordinate of each core node. During each timestep, 
diffusion was applied and uplift was subsequently added to the interior nodes. This benchmark 
produces a known reference topography and is commonly used to verify the correctness of the 
diffusion implementation.

In the coupled ASPECT–Landlab framework, all benchmark parameters, including domain geometry, 
grid spacing, boundary conditions, diffusivity, timestep, simulation duration, and initial 
topography, were retained unchanged. 

Surface evolution was handled through the ASPECT–Landlab coupling interface, where vertical surface 
displacement from ASPECT was communicated to Landlab at every global timestep. To investigate the 
effect of coupling timescales, the Landlab timestep could be subdivided into multiple substeps 
according to

.. math::

   \Delta t_{\mathrm{sub}}
   =
   \frac{\Delta t}
        {n_{\mathrm{substeps}}}

where :math:`\Delta t` is the global ASPECT timestep and :math:`n_{\mathrm{substeps}}` is the 
number of Landlab substeps executed within each coupling interval.

Case 2 : ASPECT induced uplift configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This experiment was designed to isolate the effect of transferring uplift from the ASPECT
to the coupling interface. All model parameters, domain geometry, mesh resolution, boundary 
conditions, diffusivity, and simulation duration were kept identical to the 
``case 1`` above. The only modifications were:

1. The uplift term previously prescribed directly within Landlab was disabled.
2. Surface uplift was instead imposed through ASPECT using a prescribed vertical velocity boundary condition.
3. The ``Single Stokes and Single Advection`` nonlinear solver was activated to compute the velocity field used by the mesh deformation framework.

The prescribed velocity boundary condition was defined in the ASPECT parameter file as:

.. code-block:: text

   subsection Boundary velocity model

    set Prescribed velocity boundary indicators =
      left: function, right: function, bottom: function

    subsection Function
      set Coordinate system = cartesian
      set Variable names = x,y,z,t
      set Function expression = 0; 0; y/1e5
    end
   end

This configuration imposes zero horizontal velocity and a spatially varying vertical velocity,

.. math::
   
   v_z = \frac{y}{10^5},

which produces uplift that increases linearly in the positive :math:`y` direction. 
The resulting velocity field is incorporated into the ASPECT mesh deformation 
framework and communicated to Landlab through the coupling interface.

Unlike the previous benchmark, where uplift was applied directly to 
Landlab nodes, surface elevation changes are now induced by ASPECT 
through mesh deformation. Consequently, the benchmark evaluates 
the ability of the coupling framework to transfer ASPECT-generated 
surface motion to Landlab while preserving the expected uplift--diffusion behavior.



-------------------------------------------------------------
Results
-------------------------------------------------------------

.. raw:: html

   <div style="
      background:#e8f5e9;
      border-left:6px solid #2e7d32;
      padding:12px;
      margin:10px 0;
      border-radius:4px;
      line-height:1.7;">



   <b></b> As <code>n_substeps</code> increases, tracer analysis reveals two distinct behaviours:

   <br><br>

   <b style="color:#1565C0;">Constant Uplift:</b>
   The magnitude of elevation change produced by the uplift code line
   <code>self.uplift_rate * sub_dt</code> (Code Snippet 2, line 10)
   remains essentially constant across all <code>n_substeps</code> scenarios (Figure C10 to C14).

   <br><br>

   <b style="color:#EF6C00;">Diffusion Response Increased Nonlinearly and Reached a Plateau:</b>
   The magnitude of elevation change produced by the diffusion code line
   <code>self.linear_diffuser.run_one_step(sub_dt)</code> (Code Snippet 2, line 6)
   increases nonlinearly with increasing <code>n_substeps</code> before gradually approaching a plateau (Figure C10 to C14).

   </div>


-------------------------------------------------------------
Interpretation
-------------------------------------------------------------
As ``n_substeps`` value increases, The effect of diffusion code line ``self.linear_diffuser.run_one_step(sub_dt)`` 
becomes more pronounced, resulting in a lower topography relative to the standalone Landlab benchmark 
and it stoped lowering upon further increase in ``n_substeps`` values.

**Interpretation 1:**

**Substepping reduces operator-splitting error** (indicate ``n_substeps`` is working as intented).

The agreement between the coupled and standalone solutions with
increasing ``n_substeps`` suggests that substepping is functioning
as intended (as shown in Figure 5 bellow). 


**Interpretation 2:**

**Residual discrepancies likely originate from the coupling strategy itself.**

Although increasing ``n_substeps`` improves agreement with the reference
solution, a small mismatch remains, even for the best-performing case
(Figure 6, ASPECT-driven uplift case with ``n_substeps = 3``). Because the
ASPECT and Landlab grids are geometrically identical at the coupling
interface, the discrepancy cannot be attributed to interpolation or grid
mismatch. Instead, it most likely reflects the numerical characteristics of
the coupled framework, including mesh deformation, temporal coupling, and model synchronization.


-------------------------------------------------------------
Discussion
-------------------------------------------------------------

The progressive lowering of topography as ``n_substeps`` increases and then
no further lowering with further increasing ``n_substeps``, 
can be understood as the interaction of two temporal subdivision 
mechanisms acting within the coupled framework. 

**In Landlab induced uplift secenario:**

In this benchmark recreation, the closest agreement with the standalone
Landlab reference solution is obtained when ``n_substeps = 1``. This behavior
can be understood by considering that Landlab's ``LinearDiffuser`` component
already contains an internal timestep subdivision mechanism through
`self._tstep_ratio = dt/self._dt` (`diffusion.py`, line 445), where
`self._dt` is the CFL-limited stable diffusion timestep. Whenever the
user-specified timestep exceeds the stability limit, the diffusion solver
automatically advances the solution using multiple stable internal
substeps. Consequently, diffusion is already temporally well resolved
within a single Landlab timestep.

In the coupled ASPECT--Landlab framework, an additional level of temporal
subdivision can be introduced through ``n_substeps > 1``, which further
partitions the ASPECT coupling timestep into smaller intervals. Unlike
Landlab's internal diffusion substepping, which is required for numerical
stability, ``n_substeps`` is intended to improve the temporal resolution of
the interaction between uplift and diffusion. Increasing ``n_substeps``
causes diffusion and uplift to interact more frequently during a coupling
interval, allowing sediment transport to respond to intermediate uplifted
topographies rather than only the final uplifted state.

As a result, increasing ``n_substeps`` modifies the temporal coupling
behavior relative to the original standalone Landlab benchmark. Therefore,
for the specific purpose of reproducing the standalone Landlab diffusion
benchmark within the coupled framework, ``n_substeps = 1`` provides the most
appropriate comparison because it preserves the original benchmark's
timestep structure. This recommendation should not be interpreted as a
general guideline for coupled simulations, where larger values of
``n_substeps`` may be beneficial for reducing operator-splitting errors and
improving temporal coupling accuracy.

**In ASPECT induced uplift secenario:**

In the ASPECT-defined uplift case, uplift is generated indirectly from the
surface velocity field computed by ASPECT through the Stokes and advection
solution. Under the simple material-model configuration used in this study,
the coupled solution exhibited a noticeable dependence on the temporal
coupling parameter ``n_substeps``. Among the tested values, ``n_substeps = 3``
produced the closest agreement with the reference topography (Figure 6,
second row, middle panel). This observation suggests that multiple coupling
substeps may be required to adequately resolve the transfer of ASPECT-derived
surface motion to the Landlab surface-process model.

---------
Summary
---------

.. raw:: html

   <div style="background-color:#E8F4FD; border-left:6px solid #1F77B4; padding:15px; border-radius:6px; line-height:1.8;">

   The coupled ASPECT–Landlab framework contains multiple levels of temporal discretization. ASPECT controls its timestep according to the requirements of the geodynamic solver, while Landlab's <code>LinearDiffuser</code> component internally subdivides the requested diffusion timestep through <code>self._tstep_ratio = dt/self._dt</code> to satisfy the CFL stability condition. These mechanisms are primarily responsible for the stability and accuracy of their respective numerical solvers.

   The parameter <code>n_substeps</code> serves a different purpose. Rather than stabilizing either solver, it improves the temporal accuracy of the uplift–diffusion coupling by subdividing the ASPECT timestep into smaller coupling intervals. This allows diffusion to respond more frequently to intermediate uplifted topographies and reduces the temporal discretization error associated with the operator-split coupling procedure.

   Consequently, increasing <code>n_substeps</code> progressively lowers the predicted topography relative to simulations with fewer coupling substeps because diffusion interacts more frequently with evolving uplifted surfaces. The resulting topography approaches a limiting solution as <code>n_substeps</code> increases, indicating convergence of the coupling algorithm. Therefore, the observed lowering should not be interpreted as a consequence of numerical stabilization, but rather as the result of improved temporal resolution of the coupled uplift–diffusion system.

   </div>


.. raw:: html

   <div style="
      background: linear-gradient(135deg, #E8F8FF, #F0FFF4);
      border: 3px solid #4A90E2;
      border-radius: 12px;
      padding: 15px 20px;
      margin: 15px 0;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
      line-height: 1.6;
      font-size: 1.05em;">

   <span style="font-si
   ze:1.2em;"> <b>Main Finding</b></span><br><br>

   <span style="color:#1F4E79;">
   Increasing <code>n_substeps</code> improves the temporal accuracy of uplift–diffusion coupling. The resulting lower topography reflects a more faithful representation of uplift–diffusion interactions and convergence toward the numerically consistent coupled solution.
   </span>

   </div>

--------
Figures
--------

Figure 1: Problem defintion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Discrepancy in Topographic Response for  Between Coupled ASPECT–Landlab and Standalone Landlab in ``n_substeps > 1``   ``(Greater then 1)`` Scenarios
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _fig_n_steps_problem_definition:

.. figure:: /_images/inkscape_readthedoc/n_substeps_problem_defination_intro_ppt.png
   :align: center


Figure 2: ``n_substeps`` Purpose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Coupling Larger Time with Shorter Time frame
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. _fig_n_steps_problem_definiti:

.. figure:: /_images/benchmark_test_1/n_steps_rate_comparision_geodynamic_landscape_processes.png
   :align: center




Figure 3 Hypothesis
^^^^^^^^^^^^^^^^^^^^^^^^^^
Increasing ``n_substeps`` Should Not Change the Solution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _fig_n_steps_problem_defin:

.. figure:: /_images/inkscape_readthedoc/n_step_problem_definition.png
   :align: center

.. Schematic representation of temporal subdivision in the ASPECT–Landlab 
.. coupling algorithm. Increasing ``n_substeps`` decreases the size of 
.. individual coupling timesteps while keeping the total simulated time 
.. constant. Based on this conservation of total uplift and diffusion time, 
.. the final topography was initially expected to be independent of ``n_substeps``.

Figure 4: Thumbnail
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Uplift-Diffusion Algorithm in coupled Landlab-ASPECT framework 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^



**Code snippet -1:** *Snippet of the coupling algorithm.*

.. code-block:: python
   :linenos:
   

   def set_mesh_information(self, ..):

      self.model_grid = landlab.RasterModelGrid()
      self.uplift_rate = (
      self.model_grid.node_y[self.model_grid.core_cells]/ 1e5
      )
   def update_until(self,..):
         
      dt = end_time - self.current_time
      if dt > 0:
         n_substeps = N
         sub_dt = dt / n_substeps
            for i in range(n_substeps):
               self.linear_diffuser.run_one_step(sub_dt)
               self.model_grid.at_node["topographic__elevation"]
               [self.model_grid.core_nodes] += (self.uplift_rate * sub_dt)

.. figure:: /_images/benchmark_test_1/import-landlab_algo_sequence.png
   :align: center

Figure 5: Operator Splitting Error (or Non-Simultaneous Process Interaction)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Isolation of Diffusion and Uplift Effects Using Elevation Tracers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. figure:: /_images/inkscape_readthedoc/n_sub_steps_tracer_cross-section.png
   :align: center


Figure 6: Summary 
^^^^^^^^^^^^^^^^^^^

.. figure:: /_images/inkscape_readthedoc/n_subsets_summary.png
   :align: center

.. admonition:: Key Inetrpretation
   :class: orange-box

   **Increasing** ``n_substeps`` **improves convergence, but exact reproduction of a standalone benchmark solution should not necessarily be expected.**

   The coupled solution is sensitive to the choice of ``n_substeps`` because uplift and diffusion are applied as separate discrete operations. Increasing ``n_substeps`` reduces operator-splitting errors and generally improves convergence toward a temporally better-resolved coupled solution.

   However, exact agreement with a standalone benchmark cannot necessarily be expected. Standalone benchmarks are typically formulated and verified within a single numerical framework, whereas the coupled ASPECT--Landlab system combines multiple numerical methods, solution procedures, and data-exchange operations. Consequently, even when the same physical process is represented, differences may arise from the numerical pathways through which information is generated, transferred, and applied within the coupled framework.

   Therefore, verification of coupled models ultimately requires benchmark problems that are explicitly designed for coupled geodynamic--surface process systems. Such benchmarks should test the numerical behavior of the coupling strategy itself, including temporal coupling, data exchange, mesh deformation, and process interactions. Developing benchmark problems with analytical or otherwise independently verifiable coupled solutions remains an important direction for future work.


--------------------------
Complementary Experiments
--------------------------

Figure C1: Diffusion first ``THEN`` Uplift
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/figures/landlab/bug_landlab_folder/ASPECT_driven_uplift_mismatch_Standalone_Landlab_debuging/Landlab_driven_uplift_operator_splitting_error_diffrent_sequence_uplift_diffusion_diffrent_node_overlaping/outputs/diffusion_first_uplift_opertor_spliting_error_n_substeps-1/results_benchmark/cross_section_all_times.png
   :align: center

Figure C2: Uplift first ``THEN`` Diffusion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/figures/landlab/bug_landlab_folder/ASPECT_driven_uplift_mismatch_Standalone_Landlab_debuging/Landlab_driven_uplift_operator_splitting_error_diffrent_sequence_uplift_diffusion_diffrent_node_overlaping/outputs/uplift_first_diffusion_opertor_spliting_error/results_benchmark/cross_section_all_times.png
   :align: center


Figure C3: Ideal case scenario
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. figure:: /_static/figures/landlab/bug_landlab_folder/ASPECT_driven_uplift_mismatch_Standalone_Landlab_debuging/Landlab_driven_uplift_operator_splitting_error_diffrent_sequence_uplift_diffusion_diffrent_node_overlaping/outputs/diffusion_first_uplift_opertor_spliting_error_n_substeps-1/results_benchmark/cross_section_all_times.png
   :align: center

Figure C4: Coupled Landlab defined uplift (No difusion) uniform Uplift
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. figure:: /_static/figures/landlab/bug_landlab_folder/ASPECT_driven_uplift_mismatch_Standalone_Landlab_debuging/Landlab_driven_uplift_operator_splitting_error_diffrent_sequence_uplift_diffusion_diffrent_node_overlaping/outputs/Only_uplift_No_diffusion_random_initial_Topo_opertor_spliting_error_n_substeps-1/results_benchmark/cross_section_all_times.png
   :align: center

Figure C5: ASPECT defined uplift (No difusion) uniform Uplift
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. figure:: /_static/figures/landlab/bug_landlab_folder/ASPECT_driven_uplift_mismatch_Standalone_Landlab_debuging/ASPECT_driven_uplift_case/outputs/ASPECT_defined_uplift_No_Diffusion_subset_1_global_velocity_boundary_refin-0_x_9_y_19-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_x-900_y-1900_z-1000_single_Advection_single_Stokes/results_benchmark/cross_section_all_times.png
   :align: center


Figure C7: Uplift Implementation difference
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_images/test_3/test_3_Raster_topography_eq_no_of_ncols_nrows.eps.png
  :width: 1000px
  :align: center

.. important::

   **Most Plausible Explanation: Uplift Implementation Differences**

   The most likely explanation for the remaining discrepancy between the
   standalone Landlab benchmark and the coupled ASPECT--Landlab solution
   is the fundamentally different manner in which uplift is introduced
   into the two modeling frameworks.

   In the standalone Landlab benchmark, uplift is prescribed explicitly
   and applied directly at individual grid nodes. The imposed uplift field
   therefore enters the surface-evolution calculation without any
   intermediate numerical processes.

   In contrast, within the coupled ASPECT--Landlab framework, uplift is
   generated indirectly through the geodynamic solution. Surface motion is
   first prescribed through the boundary velocity model and then propagated
   through the ASPECT solution procedure, which involves the Stokes and
   advection equations and depends on the evolving pressure, temperature,
   density, and viscosity fields. The resulting surface displacement is
   subsequently transferred to Landlab through the mesh-deformation
   interface.

   Consequently, even when the prescribed boundary velocity is designed to
   reproduce the same uplift pattern, the uplift reaches the landscape
   model through a substantially different numerical pathway. Therefore,
   the remaining mismatch is more likely to reflect differences in uplift
   generation and transfer within the coupled framework than errors arising
   from projection, interpolation, or node-to-node mapping between ASPECT
   and Landlab.



.. raw:: html

   <div style="
      background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
      border-left: 8px solid #FF6F00;
      border-radius: 10px;
      padding: 18px 22px;
      margin: 15px 0;
      box-shadow: 0 3px 8px rgba(0,0,0,0.12);">

   <h3 style="
      margin-top:0;
      color:#E65100;
      font-size:1.25em;">
      Open Questions
   </h3>

   <ol style="line-height:1.8; font-size:1.05em; color:#4E342E;">

   <li>
   <b>Does the coupled solution converge to a unique solution as
   <code>n_substeps</code> increases?</b>
   <br>
   Determining whether the ASPECT–Landlab solution approaches a
   limiting topography with increasing temporal resolution would
   provide direct evidence that <code>n_substeps</code> functions as a
   convergence parameter rather than introducing numerical artifacts.
   </li>

   <br>

   <li>
   <b>What <code>n_substeps</code> value is sufficient for practical
   coupled simulations?</b>
   <br>
   Identifying the smallest value of <code>n_substeps</code> that
   produces a converged solution would provide a useful guideline for
   future ASPECT–Landlab studies by balancing numerical accuracy and
   computational cost.
   </li>

   </ol>

   </div>


Figure C8: ``n_substeps = 10`` scenario: Crosssection of each time step (total of 4)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/figures/landlab/bug_landlab_folder/outputs/Landlab_defined_uplift_subset_10_global_refin-0_x_9_y_19-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_x-900_y-1900_z-1000_no_Advection_no_Stokes/results_benchmark/cross_section_all_times.png
   :align: center

Figure C9: ``n_substeps = 1`` scenario: Crosssection of each time step (total of 4)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/figures/landlab/bug_landlab_folder/outputs/Landlab_defined_uplift_subset_1_global_refin-0_x_9_y_19-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_x-900_y-1900_z-1000_no_Advection_no_Stokes/results_benchmark/cross_section_all_times.png
   :align: center






Figure C10: ``n_substeps = 1`` scenario: Diffusion and Uplift effect on Elevation Changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/figures/landlab/bug_landlab_folder/n_substeps_issue_analysis/test_template_ADV_GEO_Project_placeholder/analysis_substeps_figures/loop_vs_max_uplift_diffusion_change_n_substeps_1.png
   :align: center





Figure C11: ``n_substeps = 2`` scenario: Diffusion and Uplift effect on Elevation Changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/figures/landlab/bug_landlab_folder/n_substeps_issue_analysis/test_template_ADV_GEO_Project_placeholder/analysis_substeps_figures/loop_vs_max_uplift_diffusion_change_n_substeps_2.png
   :align: center

Figure C12: ``n_substeps = 3`` scenario: Diffusion and Uplift effect on Elevation Changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/figures/landlab/bug_landlab_folder/n_substeps_issue_analysis/test_template_ADV_GEO_Project_placeholder/analysis_substeps_figures/loop_vs_max_uplift_diffusion_change_n_substeps_3.png
   :align: center

Figure C13: ``n_substeps = 6`` scenario: Diffusion and Uplift effect on Elevation Changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/figures/landlab/bug_landlab_folder/n_substeps_issue_analysis/test_template_ADV_GEO_Project_placeholder/analysis_substeps_figures/loop_vs_max_uplift_diffusion_change_n_substeps_6.png
   :align: center

Figure C14: ``n_substeps = 20`` scenario: Diffusion and Uplift effect on Elevation Changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: /_static/figures/landlab/bug_landlab_folder/n_substeps_issue_analysis/test_template_ADV_GEO_Project_placeholder/analysis_substeps_figures/loop_vs_max_uplift_diffusion_change_n_substeps_20.png
   :align: center

.. by 
.. ASPECT and exchanged with Landlab only at discrete coupling intervals. 
.. When `n_substeps = 1`, diffusion responds only once to the total uplift 
.. accumulated over an ASPECT timestep. Increasing `n_substeps` introduces 
.. intermediate uplift–diffusion interactions, allowing diffusion to act on 
.. partially uplifted surfaces rather than waiting until the end of the coupling interval.

.. Consequently, the coupled model contains two levels of temporal subdivision: 
.. an internal diffusion subcycling mechanism within Landlab and an external 
.. coupling subcycling mechanism introduced by `n_substeps`. The additional 
.. coupling subdivision improves the temporal representation of uplift–diffusion 
.. interactions and increases the cumulative effect of diffusion relative to 
.. simulations with fewer coupling substeps. This produces progressively lower 
.. topography and brings the coupled solution closer to the standalone Landlab 
.. reference solution. Beyond approximately `n_substeps ≈ 3–6`, further subdivision 
.. produces only negligible changes because the temporal discretization error 
.. associated with the uplift–diffusion coupling has become sufficiently small 
.. and the solution has effectively converged.




.. Other possible mechanisms which are less likely.

.. The first possibility is that diffusion progressively lowered 
.. the landscape until topographic curvature becomes negligible (plateau formation). However, 
.. experiments performed with diffusivity reduced by two orders of 
.. magnitude show that substantial curvature and steep slopes remain 
.. in the landscape even after the solution reaches a plateau with 
.. increasing ``n_substeps``. Therefore, lowering of landscape and the plateau cannot be explained 
.. by exhaustion of curvature or by diffusion reaching a physical transport limit.

.. The second possibility is that increasing ``n_substeps`` 
.. increases the frequency with which the diffusion solver 
.. is executed, since effect of diffusion solver also increases nonlinearly, 
.. thereby causing more material to 
.. be removed leads to lowering of topography with increasing ``n_substeps``. While this explanation is initially appealing, it is 
.. not sufficient because the total simulated time remains constant. 

.. .. A physically and numerically consistent diffusion solver should 
.. .. converge toward a limiting solution as the timestep is reduced, 
.. .. rather than continue producing unlimited additional erosion simply 
.. .. because it is evaluated more frequently.

.. .. The most plausible explanation is that the plateau reflects convergence 
.. .. of the uplift–diffusion coupling scheme. As `n_substeps` increases, the 
.. .. oupling timestep decreases and the temporal interaction between uplift and 
.. .. diffusion is resolved more accurately. This reduces the temporal discretization 
.. .. error associated with the uplift-diffusion coupling. Initially, 
.. .. increasing `n_substeps` produces noticeable changes in topography because 
.. .. this coupling error is significant. However, beyond approximately `n_substeps ≈ 6`, 
.. .. the error becomes sufficiently small that further subdivision of the coupling 
.. .. timestep produces only negligible changes in the solution.

.. Therefore, the observed plateau is unlikely to result from either increased 
.. diffusion frequency or exhaustion of topographic curvature. Instead, it 
.. indicates that the computed solution has become insensitive to further 
.. increases in `n_substeps`. Physically, this means that increasing the 
.. frequency of uplift–diffusion interactions beyond this threshold does 
.. not significantly alter the predicted topography. Numerically, it 
.. indicates that the dominant temporal discretization error associated 
.. with the coupling algorithm has been reduced to a negligible level and 
.. that the solution has effectively converged with respect to `n_substeps`.


.. A conceptually similar mechanism exists within Landlab's `LinearDiffuser` component through the variable

.. `self._tstep_ratio = dt / self._dt`

.. (`diffusion.py`, line 445), where `dt` is the user-specified timestep and `self._dt` is the internally computed 
.. stability-limited diffusion timestep. This ratio represents the number of CFL-stable diffusion timesteps required 
.. to advance the solution over the requested timestep. Consequently, both `n_substeps` in the coupled framework 
.. and `self._tstep_ratio` in standalone Landlab act as temporal subdivision mechanisms that 
.. increase the number of diffusion updates performed within a given model timestep, although they 
.. arise from different numerical considerations.




.. .. raw:: html

..    <div style="
..       background:#eef7ff;
..       border-left:6px solid #1976d2;
..       padding:15px;
..       margin:15px 0;
..       border-radius:5px;">

..    <h3 style="margin-top:0;">
..    Appendix 1. Tracer Analysis of Diffusion and Uplift Response for Different <code>n_substeps</code>
..    </h3>

..    <p>
..    The tracer analysis reveals a fundamental difference between the behaviour of the uplift and diffusion terms as
..    <code>n_substeps</code> increases. In all simulations, the maximum uplift change recorded after each uplift operation
..    (Code Snippet 2, line 15) remains constant throughout the coupling loops because uplift is applied as
..    </p>

.. .. math::

..    \Delta z_{\mathrm{uplift}} = U \, \Delta t_{\mathrm{loop}}

.. .. raw:: html

..    <p>
..    where <code>U</code> is fixed and <code>\Delta t_{loop}</code> is constant within a given
..    <code>n_substeps</code> configuration. Consequently, the maximum uplift change remains equal to
..    <code>0.014</code> for <code>n_substeps = 1</code>, <code>0.004667</code> for
..    <code>n_substeps = 3</code>, and <code>0.0007</code> for <code>n_substeps = 20</code>
..    throughout all loops.
..    </p>

..    <p>
..    In contrast, the maximum diffusion change recorded after the diffusion operation
..    (Code Snippet 2, line 9) exhibits a strongly nonlinear evolution. For
..    <code>n_substeps = 1</code>, the diffusion change increases from
..    <code>0</code> in the first loop to approximately <code>0.0134</code> in the second loop
..    and reaches <code>0.0138</code> by the third loop, becoming nearly equal in magnitude to
..    the uplift change of <code>0.014</code>. This rapid increase occurs because diffusion
..    initially acts on a nearly flat surface and therefore has little effect, but becomes
..    progressively stronger as uplift-generated topographic gradients develop.
..    </p>

..    <p>
..    A similar pattern is observed for <code>n_substeps = 3</code>. The maximum diffusion
..    change increases rapidly from <code>0</code> in the first loop to <code>0.0040</code>
..    in the second loop, <code>0.0043</code> in the third loop, and subsequently approaches
..    a nearly constant value of approximately <code>0.0046</code> after about six to seven loops.
..    At this stage the diffusion and uplift magnitudes become nearly equal, indicating that
..    diffusion is removing almost the same amount of elevation that uplift adds during each substep.
..    </p>

..    <p>
..    For <code>n_substeps = 20</code>, the same behaviour occurs but over a larger number of loops.
..    The diffusion change increases from <code>0</code> to approximately <code>0.00030</code>
..    after the second loop, <code>0.00054</code> after the fifth loop, <code>0.00062</code>
..    after the tenth loop, and gradually converges toward <code>0.000695</code> by loops
..    <code>50–60</code>. This value is nearly identical to the uplift increment of
..    <code>0.0007</code> applied during each loop. Once this state is reached, the diffusion
..    and uplift contributions become approximately balanced and the elevation change per loop
..    becomes very small.
..    </p>

..    <p>
..    The results therefore demonstrate that increasing <code>n_substeps</code> does not change
..    the magnitude of the uplift increment applied during each substep, but it does increase
..    the number of opportunities for diffusion to act on newly created topography within a
..    single ASPECT timestep. As <code>n_substeps</code> increases, diffusion repeatedly removes
..    a portion of the uplift-generated relief before the next uplift increment is applied.
..    Consequently, a larger fraction of the uplift is dissipated during the coupling interval,
..    leading to progressively lower maximum elevations and explaining why the coupled
..    ASPECT–Landlab simulations produce lower topography than the standalone Landlab benchmark
..    for <code>n_substeps &gt; 1</code>.
..    </p>

..    <p>
..    An additional observation is that the diffusion change approaches a steady-state value that
..    is nearly equal to the uplift increment for each <code>n_substeps</code> configuration.
..    Once this balance is reached, further increases in loop number produce only minor changes
..    in elevation. The stabilization occurs after approximately <code>2–3</code> loops for
..    <code>n_substeps = 1</code>, <code>6–8</code> loops for <code>n_substeps = 3</code>,
..    and roughly <code>40–50</code> loops for <code>n_substeps = 20</code>. This convergence
..    behaviour is consistent with the flattening of the diffusion curves and indicates that
..    the system approaches a dynamic balance between uplift and diffusion within the
..    substepping cycle.
..    </p>

..    </div>







.. In the 
.. coupled ASPECT–Landlab framework, the ASPECT timestep 


.. However, the observed 
.. discrepancy initially suggested that increasing ``n_substeps`` might 
.. be introducing additional uplift or additional diffusion, leading 
.. to a divergence from the standalone Landlab benchmark,as shown in the figure below.



.. Initially, this behavior appeared to suggest a flaw in the coupling
.. implementation, leading to the hypothesis that increasing
.. ``n_substeps`` might inadvertently introduce additional uplift or
.. additional diffusion into the system.

.. Through a systematic investigation involving execution tracing,
.. diagnostic logging, convergence analysis, process-magnitude analysis,
.. and topographic comparison against benchmark solutions, it was
.. demonstrated that the implementation is mathematically correct.

.. The observed discrepancies arise not from additional uplift or
.. additional diffusion, but from changes in the temporal frequency of
.. interaction between uplift and diffusion operators.

.. This report documents the reasoning process that transformed an
.. apparent numerical bug into a deeper understanding of temporal
.. coupling in multi-process Earth surface models.

.. Introduction
.. ^^^^^^^^^^^^^^

.. Over the past several months, I have had the privilege of working
.. within a group of scientists whose research has significantly shaped
.. our understanding of coupled geodynamic and Earth-surface systems.

.. As a young researcher entering this field, I found myself listening
.. carefully during group meetings, trying to understand not only the
.. scientific results being discussed, but also the way experienced
.. scientists approach complex numerical problems.

.. One lesson gradually became clear:

..     In computational geoscience, the most challenging problems are
..     often not coding errors. More frequently, they arise from
..     misunderstandings of what a numerical algorithm is actually doing.

.. The investigation presented here emerged from one such situation.

.. At first glance, the problem appeared simple.

.. A coupled ASPECT–Landlab simulation reproduced a standalone Landlab
.. benchmark when ``n_substeps = 1``, but began to diverge from the
.. benchmark when larger values were used.

.. The immediate interpretation seemed obvious:

..     Increasing the number of substeps must be adding more uplift or
..     more diffusion.

.. As the investigation progressed, however, this explanation began to
.. unravel.

.. What followed was a detailed effort to understand not only the
.. observed behavior, but also the mathematical and physical meaning of
.. temporal coupling within the ASPECT–Landlab framework.

.. Initial Observation and Source of Confusion
.. -------------------------------------------

.. The investigation began with a seemingly contradictory observation.

.. For a diffusion coefficient of

.. .. math::

..    D = 5\times10^4 \; \mathrm{m^2/year}

.. the coupled ASPECT–Landlab simulation reproduced the standalone
.. Landlab benchmark almost perfectly when

.. .. code-block:: python

..    n_substeps = 1

.. and in some cases also when

.. .. code-block:: python

..    n_substeps = 2

.. However, increasing

.. .. code-block:: python

..    n_substeps = 10

.. produced a noticeably lower topography.

.. The immediate interpretation was:

..     Increasing ``n_substeps`` appears to introduce more uplift and
..     more diffusion than the standalone benchmark.

.. This raised concerns that the substepping implementation itself
.. might be incorrect.

.. The central question became:

..     Does increasing ``n_substeps`` unintentionally add extra
..     physical uplift or extra physical diffusion?

.. Original Hypothesis
.. -------------------

.. The original mental model was:

.. ::

..    n_substeps = 1
..        → 1 diffusion event
..        → 1 uplift event

..    n_substeps = 10
..        → 10 diffusion events
..        → 10 uplift events

.. which naturally suggests:

.. ::

..    More loops
..        ↓
..    More uplift
..        ↓
..    More diffusion
..        ↓
..    Different topography

.. Under this interpretation, disagreement with the benchmark would
.. indicate a flaw in the implementation.

.. Examination of the Actual Code
.. ------------------------------

.. The critical section of the coupling code is:

.. .. code-block:: python

..    n_substeps = N

..    sub_dt = dt / n_substeps

..    for i in range(n_substeps):

..        self.linear_diffuser.run_one_step(sub_dt)

..        self.model_grid.at_node[
..            "topographic__elevation"
..        ][self.model_grid.core_nodes] += (
..            self.uplift_rate * sub_dt
..        )

.. .. code-block:: python
..    :linenos:

..    n_substeps = N

..    sub_dt = dt / n_substeps

..    for i in range(n_substeps):

..        self.linear_diffuser.run_one_step(sub_dt)

..        self.model_grid.at_node["topographic__elevation"][self.model_grid.core_nodes] += (self.uplift_rate * sub_dt)

.. .. admonition:: Coupling Algorithm
..    :class: note

..    .. code-block:: python
..       :linenos:

..       n_substeps = N

..       sub_dt = dt / n_substeps

..       for i in range(n_substeps):

..           self.linear_diffuser.run_one_step(sub_dt)

..           self.model_grid.at_node[
..               "topographic__elevation"
..           ][self.model_grid.core_nodes] += (
..               self.uplift_rate * sub_dt
..           )


.. .. card:: Coupling Algorithm

..    .. code-block:: python
..       :linenos:

..       n_substeps = N

..       sub_dt = dt / n_substeps

..       for i in range(n_substeps):

..           self.linear_diffuser.run_one_step(sub_dt)

..           self.model_grid.at_node[
..               "topographic__elevation"
..           ][self.model_grid.core_nodes] += (
..               self.uplift_rate * sub_dt
..           )


.. Algorithm
.. ^^^^^^^^^

.. The ASPECT timestep :math:`dt` is subdivided into

.. .. math::

..    sub\_dt = \frac{dt}{n_{substeps}}

.. The coupling loop is implemented as:

.. .. code-block:: python
..    :linenos:
..    :caption: Temporal substepping algorithm

..    n_substeps = N

..    sub_dt = dt / n_substeps

..    for i in range(n_substeps):

..        self.linear_diffuser.run_one_step(sub_dt)

..        self.model_grid.at_node[
..            "topographic__elevation"
..        ][self.model_grid.core_nodes] += (
..            self.uplift_rate * sub_dt
..        )
.. At first glance, it appears that increasing ``n_substeps`` increases
.. the number of uplift and diffusion operations.

.. However, a closer inspection reveals an important detail:

.. .. math::

..    sub\_dt = \frac{dt}{n_{substeps}}

.. Thus every uplift increment becomes smaller as the number of
.. substeps increases.

.. Mathematical Verification
.. -------------------------

.. For one substep:

.. .. math::

..    \Delta z_{uplift} = U \cdot sub\_dt

.. where

.. .. math::

..    U = uplift\_rate

.. Since there are :math:`n_{substeps}` loops:

.. .. math::

..    Total\ uplift
..    =
..    n_{substeps}
..    \times
..    (U \cdot sub\_dt)

.. Substituting

.. .. math::

..    sub\_dt
..    =
..    \frac{dt}{n_{substeps}}

.. gives

.. .. math::

..    Total\ uplift
..    =
..    n_{substeps}
..    \times
..    U
..    \times
..    \frac{dt}{n_{substeps}}

.. which simplifies to

.. .. math::

..    Total\ uplift = Udt

.. Therefore

.. .. math::

..    \boxed{
..    Total\ uplift\ is\ independent\ of\ n_{substeps}
..    }

.. The same argument applies to diffusion time:

.. .. math::

..    n_{substeps} \times sub\_dt = dt

.. Thus

.. .. math::

..    \boxed{
..    Total\ diffusion\ time\ is\ independent\ of\ n_{substeps}
..    }

.. This result immediately invalidated the original hypothesis.

.. Increasing ``n_substeps`` does **not** add more uplift.

.. Increasing ``n_substeps`` does **not** add more diffusion time.

.. Revised Interpretation
.. ----------------------

.. Once the conservation properties were established, the question changed.

.. If neither uplift nor diffusion time increases, why does the
.. topography change?

.. The answer lies in the order and frequency of interaction.

.. Case: ``n_substeps = 1``
.. ^^^^^^^^^^^^^^^^^^^^^^^^

.. ::

..    Diffuse for dt
..    Uplift for dt

.. Case: ``n_substeps = 2``
.. ^^^^^^^^^^^^^^^^^^^^^^^^

.. ::

..    Diffuse for dt/2
..    Uplift for dt/2

..    Diffuse for dt/2
..    Uplift for dt/2

.. Case: ``n_substeps = 10``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^

.. ::

..    Diffuse
..    Uplift
..    Diffuse
..    Uplift
..    ...
..    10 times

.. Thus:

.. .. math::

..    n_{substeps}

.. controls the **interaction frequency**

.. rather than the physical magnitude of uplift or diffusion.

.. Detailed Verification Using Simple Examples
.. --------------------------------------------

.. To fully understand the effect of ``n_substeps``, it is useful to
.. examine a few simple examples.

.. Let

.. .. math::

..    U = uplift\_rate

.. and let

.. .. math::

..    dt

.. represent the ASPECT timestep.

.. Case 1: ``n_substeps = 1``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Then:

.. .. math::

..    sub\_dt = dt

.. The loop runs once:

.. .. code-block:: python

..    elevation += uplift_rate * dt

.. Total uplift added:

.. .. math::

..    Udt

.. Case 2: ``n_substeps = 2``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Then:

.. .. math::

..    sub\_dt = \frac{dt}{2}

.. First loop:

.. .. math::

..    U\frac{dt}{2}

.. Second loop:

.. .. math::

..    U\frac{dt}{2}

.. Total uplift:

.. .. math::

..    U\frac{dt}{2}
..    +
..    U\frac{dt}{2}
..    =
..    Udt

.. Case 3: ``n_substeps = 10``
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Then:

.. .. math::

..    sub\_dt = \frac{dt}{10}

.. Each loop contributes:

.. .. math::

..    U\frac{dt}{10}

.. There are ten loops:

.. .. math::

..    10
..    \times
..    U\frac{dt}{10}
..    =
..    Udt

.. General Case
.. ^^^^^^^^^^^^

.. Each loop contributes:

.. .. math::

..    U \cdot sub\_dt

.. and there are

.. .. math::

..    n_{substeps}

.. loops.

.. Therefore, total uplift over the entire ASPECT timestep is:

.. .. math::

..    Total\ uplift
..    =
..    n_{substeps}
..    \times
..    (U \cdot sub\_dt)

.. Substituting

.. .. math::

..    sub\_dt
..    =
..    \frac{dt}{n_{substeps}}

.. gives

.. .. math::

..    Total\ uplift
..    =
..    n_{substeps}
..    \times
..    U
..    \times
..    \frac{dt}{n_{substeps}}

.. The factor :math:`n_{substeps}` cancels:

.. .. math::

..    Total\ uplift
..    =
..    Udt

.. Therefore,

.. .. math::

..    \boxed{
..    Total\ uplift\ is\ independent\ of\ n_{substeps}
..    }

.. Why This Matters
.. ^^^^^^^^^^^^^^^^

.. This result proves something fundamental about the implementation.

.. Increasing ``n_substeps`` does **not** increase the total uplift
.. applied during a timestep.

.. Instead, it partitions the same total uplift into smaller increments.

.. The same reasoning applies to diffusion time.

.. The following table summarizes the result:

.. +--------------+----------------+-----------------+--------------+
.. | n_substeps   | Uplift/Loop    | Number of Loops | Total Uplift |
.. +==============+================+=================+==============+
.. | 1            | Udt            | 1               | Udt          |
.. +--------------+----------------+-----------------+--------------+
.. | 2            | Udt/2          | 2               | Udt          |
.. +--------------+----------------+-----------------+--------------+
.. | 10           | Udt/10         | 10              | Udt          |
.. +--------------+----------------+-----------------+--------------+
.. | 40           | Udt/40         | 40              | Udt          |
.. +--------------+----------------+-----------------+--------------+

.. Regardless of the number of substeps, the total uplift applied over
.. the ASPECT timestep remains identical.

.. The same argument applies to diffusion:

.. .. math::

..    n_{substeps}
..    \times
..    sub\_dt
..    =
..    dt

.. Therefore,

.. .. math::

..    \boxed{
..    Total\ diffusion\ time\ is\ independent\ of\ n_{substeps}
..    }

.. This realization represented the first major turning point in the
.. investigation.

.. The discrepancy between the coupled model and the benchmark could no
.. longer be explained by additional uplift or additional diffusion.

.. Instead, attention shifted toward understanding how the frequency of
.. interaction between uplift and diffusion changes as
.. ``n_substeps`` increases.

.. Process Magnitude Analysis
.. --------------------------

.. To investigate this effect, detailed execution traces were added.

.. The following quantities were tracked:

.. Diffusion Change
.. ^^^^^^^^^^^^^^^^

.. .. math::

..    \Delta z_{diffusion}
..    =
..    z_{after\ diffusion}
..    -
..    z_{before\ diffusion}

.. Uplift Change
.. ^^^^^^^^^^^^^

.. .. math::

..    \Delta z_{uplift}
..    =
..    z_{after\ uplift}
..    -
..    z_{before\ uplift}

.. Additional diagnostics included:

.. * Maximum elevation
.. * Deposition/erosion magnitude
.. * Cumulative terrain modification

.. Observations from Magnitude Analysis
.. ------------------------------------

.. For

.. .. math::

..    D = 50000

.. the results showed that increasing ``n_substeps`` causes

.. .. math::

..    \Delta z_{uplift}

.. and

.. .. math::

..    \Delta z_{diffusion}

.. to decrease for each individual update.

.. However, more interaction cycles occur during the same physical
.. time interval.

.. The cumulative result is a smoother terrain.

.. Consequently:

.. .. math::

..    Max\ Elevation \downarrow

.. with increasing ``n_substeps``.

.. Convergence Analysis
.. --------------------

.. A convergence metric was introduced:

.. .. math::

..    Error(n)
..    =
..    \|z_n - z_{40}\|

.. where

.. .. math::

..    z_{40}

.. served as the most refined available solution.

.. The resulting convergence curves showed:

.. * Monotonic error reduction
.. * No oscillations
.. * Diminishing returns with increasing substeps

.. This behavior indicates:

.. .. math::

..    z_n \rightarrow z^*

.. for increasing :math:`n`.

.. Meaning of the Limiting Coupled Solution
.. ----------------------------------------

.. The convergence study revealed an important concept.

.. As

.. .. math::

..    n_{substeps} \rightarrow \infty

.. the coupled solution approaches

.. .. math::

..    z^*

.. which can be interpreted as

..     the continuously interacting uplift–diffusion solution.

.. This is referred to as the **limiting coupled solution**.

.. Comparison with Standalone Landlab
.. ----------------------------------

.. The benchmark comparison introduced an interesting observation.

.. For

.. .. code-block:: python

..    n_substeps = 1

.. the coupled model closely reproduced the standalone Landlab benchmark.

.. For

.. .. code-block:: python

..    n_substeps = 10

.. the coupled model deviated from the benchmark.

.. Initially this appeared to indicate an error.

.. However, after understanding the role of substepping, the
.. interpretation changed.

.. The discrepancy is not caused by:

.. ::

..    Extra uplift
..    Extra diffusion

.. but by:

.. ::

..    More frequent interaction
..    between uplift and diffusion

.. during the same physical interval.

.. What Was Learned
.. ----------------

.. The investigation revealed that the original concern stemmed from an
.. incorrect mental model of the algorithm.

.. The code does not behave as:

.. ::

..    More substeps
..        =
..    More uplift
..        =
..    More diffusion

.. Instead it behaves as:

.. ::

..    More substeps
..        =
..    More frequent coupling
..        =
..    Different interaction pathway

.. while conserving:

.. * Total uplift
.. * Total diffusion time
.. * Total simulation time

.. Scientific Implications
.. -----------------------

.. The study establishes that the substepping implementation is
.. mathematically correct.

.. The observed sensitivity is physical and numerical rather than a
.. coding error.

.. The parameter ``n_substeps`` acts as a temporal coupling-resolution
.. parameter.

.. It determines how frequently tectonic uplift and surface diffusion
.. interact within a single ASPECT timestep.

.. Remaining Scientific Question
.. -----------------------------

.. The original debugging question has now evolved into a scientific
.. modeling question:

..     What value of ``n_substeps`` best represents the real interaction
..     between tectonic uplift and surface diffusion?

.. Several possibilities exist.

.. Option A
.. ^^^^^^^^

.. Use:

.. .. code-block:: python

..    n_substeps = 1

.. because it reproduces the standalone benchmark.

.. Option B
.. ^^^^^^^^

.. Use larger values:

.. .. code-block:: python

..    n_substeps = 10
..    n_substeps = 20
..    n_substeps = 40

.. because they more closely approximate continuous interaction between
.. processes.

.. Option C
.. ^^^^^^^^

.. Determine an optimal value through convergence studies and physical
.. timescale analysis.

.. Conclusions
.. -----------

.. The discrepancy between standalone Landlab and coupled
.. ASPECT–Landlab simulations was initially interpreted as evidence that
.. increasing ``n_substeps`` introduced additional uplift or additional
.. diffusion.

.. Detailed analysis demonstrated that this interpretation was incorrect.

.. The implementation conserves both total uplift and total diffusion
.. time regardless of the number of substeps.

.. Increasing ``n_substeps`` simply partitions the same physical interval
.. into smaller interaction cycles, allowing uplift and diffusion to
.. influence one another more frequently.

.. The resulting differences in topography arise from changes in temporal
.. coupling resolution rather than changes in process magnitude.

.. Convergence analysis further demonstrated the existence of a limiting
.. coupled solution, indicating that the implementation is numerically
.. sound.

.. The focus of future work should therefore shift from validating the
.. implementation to determining which temporal coupling strategy most
.. accurately represents the physical interaction between tectonic uplift
.. and surface processes within the ASPECT–Landlab framework.


.. Synthesis
.. -----------

.. The Landlab LinearDiffuser internally performs 
.. CFL-based timestep subdivision to satisfy the 
.. stability requirements of the explicit diffusion solver. 
.. In addition, the ASPECT–Landlab coupling employs 
.. operator-splitting substeps, where uplift and 
.. diffusion are applied repeatedly over smaller 
.. intervals within each ASPECT timestep, reducing 
.. splitting error and improving temporal coupling accuracy.

.. self._tstep_ratio = dt/self._dt as:
.. Automatic CFL-based subcycling of an 
.. explicit diffusion solver to satisfy 
.. the stability condition of the Forward 
.. Euler time integration scheme.

.. | Mechanism                         | Purpose                                        |
.. | --------------------------------- | ---------------------------------------------- |
.. | `self._tstep_ratio = dt/self._dt` | Diffusion stability                            |
.. | `sub_dt = dt/n_substeps`          | Coupling accuracy between uplift and diffusion |
