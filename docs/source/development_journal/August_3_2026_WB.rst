August 3, 2026, Running the Denial Ada Lovelace Extension Model without World Builder on macOS
================================================================================================

Objective
---------

The original Denial's ``original_II.prm`` model depends on the ASPECT World Builder plugin for initializing the geological model. Since World Builder is currently unavailable on macOS, a modified version of the parameter file was created to allow the benchmark to run without the World Builder dependency.

In addition, several nonlinear and linear solver parameters were relaxed in an attempt to improve convergence. Despite these modifications, the simulation ultimately terminated with a mesh mapping exception during the reaction computation stage.

Modifications to the Original Parameter File
--------------------------------------------

The following changes were introduced relative to the original parameter file.

1. Removal of World Builder
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The World Builder initialization was disabled.

Original:

.. code-block:: text

   set World builder file = ada_lovelace.wb

Modified:

.. code-block:: text

   # set World builder file = ada_lovelace.wb

Similarly, the initial composition model was changed from

.. code-block:: text

   set List of model names = function, world builder
   set List of model operators = add, add

to

.. code-block:: text

   set Model name = function
   set List of model operators = add

This allows the model to initialize using only the analytical function instead of requiring World Builder.

2. Landlab Script
~~~~~~~~~~~~~~~~~

The Landlab driver script was replaced.

Original

.. code-block:: text

   set Script name = landlab_script_ada_lovelace

Modified

.. code-block:: text

   set Script name = original_landlab

This change was made to use the available Landlab implementation compatible with the local setup.

3. Output Directory
~~~~~~~~~~~~~~~~~~~

Original

.. code-block:: text

   landlab_250m_resolution

Modified

.. code-block:: text

   outputs/no_web_test_1

to keep the modified experiment separate from the original benchmark outputs.

4. Solver Parameter Modifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Several solver parameters were relaxed in an attempt to improve nonlinear convergence.

.. list-table:: Solver parameter modifications
   :header-rows: 1
   :widths: 50 20 20

   * - Parameter
     - Original
     - Modified
   * - Cut back factor
     - ``0.5``
     - ``0.25``
   * - Linear solver tolerance
     - ``1e-8``
     - ``1e-7``
   * - GMRES restart length
     - ``100``
     - ``150``
   * - Newton switch tolerance
     - ``1e-5``
     - ``1e-3``
   * - Maximum linear Stokes solver tolerance
     - ``1e-8``
     - ``1e-6``

The remaining physical model parameters were kept identical to the benchmark.

Observed Solver Behavior
------------------------

The simulation successfully completed several timesteps and repeatedly solved:

* Temperature
* Stokes
* Viscoelastic stress
* Plastic strain
* Compositional fields

The solver switched from Picard iterations to Newton iterations as expected:

.. code-block:: text

   Switching from defect correction form of Picard
   to the Newton solver scheme.

Throughout the run, the Stokes system converged with approximately 75--135 AMG iterations per nonlinear iteration.

Although convergence improved significantly during each nonlinear solve, the nonlinear residual never reached the requested tolerance before the maximum number of nonlinear iterations (40) was exhausted.

Near the end of timestep 10, the solver reported

.. code-block:: text

   WARNING:
   The nonlinear solver in the current timestep
   failed to converge.

   Continuing to the next timestep even though
   solution is not fully converged.

This behavior is expected because the parameter

.. code-block:: text

   set Nonlinear solver failure strategy =
       continue with next timestep

explicitly instructs ASPECT to continue even when nonlinear convergence is not achieved.

Simulation Progress
-------------------

The simulation nevertheless advanced to timestep 11.

The reported state was

.. code-block:: text

   Timestep 11
   t = 100741 years
   dt = 741 years

Landlab successfully produced a new surface mesh

.. code-block:: text

   Writing output VTK file...

and ASPECT began solving the next timestep.

Fatal Error
-----------

The simulation ultimately terminated with

.. code-block:: text

   Exception:
   Mapping<2>::ExcTransformationFailed()

The important diagnostic message is

.. code-block:: text

   Computing the mapping between a real space point
   and a point in reference space failed,
   typically because the given point lies outside
   the cell where the inverse mapping is not unique.

The stack trace shows the failure occurred in

.. code-block:: text

   MappingQ::transform_real_to_unit_cell()

during

.. code-block:: text

   StrainDependent::fill_reaction_outputs()

called by

.. code-block:: text

   ViscoPlastic::evaluate()

while ASPECT was computing composition reactions.

Interpretation
--------------

The failure is **not** a linear solver failure.

Likewise, it is **not** simply caused by the nonlinear solver reaching the maximum number of iterations.

Instead, the exception indicates that ASPECT attempted to map a physical point back into a finite element cell, but the point no longer belonged to the expected cell.

This generally occurs when one of the following situations develops:

* excessive mesh deformation,
* invalid mesh geometry,
* highly distorted cells,
* surface displacement becoming inconsistent with the computational mesh,
* or a point generated during the reaction computation lies outside the deformed element.

The fact that the error occurs inside

.. code-block:: text

   transform_real_to_unit_cell()

rather than inside the Stokes or temperature solver strongly suggests that the mesh geometry (or the particle/reaction evaluation locations) became invalid after the mesh deformation step.

Relationship to Solver Changes
------------------------------

Relaxing the solver tolerances allowed the simulation to progress further than the original configuration.

Specifically,

* larger linear solver tolerances,
* a looser Newton switching criterion,
* and a larger maximum linear Stokes tolerance

reduced the computational cost of each nonlinear solve and prevented early solver failure.

However, these changes did **not** eliminate the underlying instability responsible for the mapping exception.

Consequently, although the modified parameter file enabled the benchmark to advance beyond earlier timesteps without World Builder, the simulation still terminated because of an invalid geometric mapping during the reaction computation.

Conclusion
----------

The modified parameter file successfully removed the World Builder dependency, allowing the Ada Lovelace benchmark to run on macOS. Relaxing several nonlinear solver parameters enabled the simulation to advance through multiple timesteps despite repeated nonlinear convergence warnings.

Nevertheless, the simulation ultimately failed with a ``MappingQ::transform_real_to_unit_cell()`` exception during the visco-plastic reaction computation. This indicates that the primary issue is not the nonlinear solver tolerance itself, but rather an invalid geometric mapping caused by mesh deformation or inconsistent evaluation points during the reaction stage. Further investigation should therefore focus on the mesh deformation, Landlab surface update, and reaction evaluation workflow rather than additional adjustments to the solver tolerances.

Possible Relationship to Removing World Builder
------------------------------------------------

The modified benchmark differs from the original benchmark by disabling World Builder and replacing it with a simplified analytical initial composition. In addition, several solver parameters and the Landlab driver script were also modified to allow execution on macOS.

Because multiple changes were introduced simultaneously, it is **not possible to conclude** that the ``MappingQ::transform_real_to_unit_cell()`` exception is a direct consequence of removing World Builder.

Nevertheless, removing World Builder changes the initial material distribution used by the visco-plastic model. This can alter the evolution of deformation, strain localization, and surface topography, which may indirectly influence mesh quality during later timesteps.

Therefore, the observed mapping failure should be regarded as occurring **after** the World Builder removal, but **not necessarily because of** the World Builder removal. Additional controlled tests are required to isolate the cause, for example by varying one modification at a time (World Builder, Landlab script, or solver parameters).

.. note::

   The modified test was executed using:

   .. code-block:: bash

      /opt/homebrew/bin/mpirun -np 14 /Users/biraj/software/landlab_ASPECT_test_2/aspect/build/aspect-release original_ll.prm

   with all outputs written to ``/Users/biraj/cookbook_biraj/denial_ada_prm/outputs/no_web_test_1``.


Write up to contribute to Denial AGU abstract (if in case)
------------------------------------------------------------
Current work is focused on developing and validating a coupled continental
rift–deposition benchmark by reproducing an existing ASPECT–FastScape model
within the ASPECT–LandLab framework. The objective is not only to reproduce
published results, but also to systematically investigate where solutions
begin to diverge and whether those differences arise from numerical
implementation, coupling methodology, surface-process formulations, mesh
representations, or parallel execution.

The benchmark is being used as a diagnostic framework to understand how
geodynamic and surface-process models interact across different temporal and
spatial scales. Through controlled benchmark experiments, we are evaluating
the influence of temporal coupling, operator splitting, mesh deformation,
and data exchange between ASPECT and LandLab on sediment transport,
deposition, and surface evolution. In particular, the benchmark is helping
to identify the numerical strengths and current limitations of the coupling
framework, including its fidelity, scalability, robustness, and parallel
performance. These efforts will establish best practices for coupling
geodynamic and landscape evolution models while providing a foundation for
more realistic simulations of sedimentary basin development and continental
rift evolution.