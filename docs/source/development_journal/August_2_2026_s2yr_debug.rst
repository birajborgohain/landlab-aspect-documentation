August 2, 2026, Investigation of Unit Conversion and Solver Failure in the ASPECT–Landlab Coupling
---------------------------------------------------------------------------------------------------

**Objective**

Today's work focused on investigating a numerical instability encountered
after replacing the original FastScape coupling with the new Landlab
implementation while preserving the same parameter values from the original
ASPECT FastScape model.

The main objective was to determine whether the instability originated from

* incorrect unit conversion,
* differences between FastScape and Landlab,
* the ASPECT–Landlab coupling,
* or the newly introduced ghost-node implementation.

**Background**

Originally, the Landlab implementation converted several parameters from
per-year units to per-second units before passing them to Landlab:

.. code-block:: python

   D = 1e-2 / self.s2yr
   K = 1e-6 / self.s2yr
   shallow_water_diffusivity = 1e-2 / self.s2yr

The motivation for changing this was based on the ASPECT parameter file,
which contains

.. code-block:: text

   set Use years in output instead of seconds = true

Since the original FastScape parameters are documented in units of
:meth:`m/year` and :math:`m^2/year`, it appeared more natural to pass the
same parameter values directly into Landlab:

.. code-block:: python

   D = 1e-2
   K = 1e-6
   shallow_water_diffusivity = 1e-2

This modification was expected to make the Landlab implementation consistent
with the original FastScape implementation.

**Observed Error**

Immediately after removing the ``/ self.s2yr`` conversions, the coupled model
failed.

The ASPECT log first reported

.. code-block:: text

   RuntimeWarning:
   divide by zero encountered in divide

   RuntimeWarning:
   overflow encountered in divide

Immediately afterwards, the topography became

.. code-block:: text

   Max elevation = 51837293163

   Min elevation = -17681406182

These elevations are physically impossible and indicate that the numerical
solution became unstable during the very first timestep.

Following this instability, ASPECT terminated with

.. code-block:: text

   The iterative advection solver in
   Simulator::solve_advection did not converge.

Finally, MPI aborted the simulation.

**Interpretation of the Error**

Initially it appeared that the ASPECT temperature solver was responsible for
the crash.

However, after carefully reading the error log, the sequence of events became
clear:

1. Landlab produces runtime warnings.
2. The surface elevation becomes numerically unstable.
3. Topography grows to approximately :math:`10^{10}` m.
4. ASPECT attempts to deform the surface.
5. The temperature advection solver fails to converge.
6. MPI aborts the simulation.

Therefore, the ASPECT solver failure is not the root cause. Instead, it is a
consequence of an earlier numerical instability occurring inside the
landscape evolution model.

**Initial Hypothesis**

The first hypothesis was that removing

.. code-block:: python

   / self.s2yr

increased the diffusivities and erosion coefficients by a factor of

.. math::

   365.25 \times 24 \times 60 \times 60
   \approx
   3.16 \times 10^7

This would make diffusion and erosion approximately thirty million times
stronger than before and therefore provide a straightforward explanation for
the numerical instability.

**Inspection of LandLabTemplate**

The next step was to inspect the implementation of
``LandLabTemplate``.

The objective was to determine whether ASPECT or the coupling framework was
already performing hidden conversions between years and seconds.

The following functions were examined:

* ``determine_uplift_velocity()``
* ``determine_horizontal_velocity()``
* ``dimensional_deposition_erosion()``
* initialization of ``self.s2yr``

**Findings**

No unit conversions were found.

Specifically,

* uplift velocities are copied directly from ASPECT,
* horizontal velocities are copied directly from ASPECT,
* ``dimensional_deposition_erosion()`` only averages values for 2-D models,
* ``self.s2yr`` is simply defined and never used inside the template.

This eliminated the possibility that the coupling framework was silently
converting between years and seconds.

**Inspection of Landlab Components**

The next stage was to inspect the source code of the individual Landlab
components to determine their expected time units.

**LinearDiffuser**

The first important observation was

.. code-block:: python

   _unit_agnostic = True

The documentation specifies

.. code-block:: text

   linear_diffusivity : m² / time

rather than

.. code-block:: text

   m²/s

Similarly, the timestep documentation specifies only

.. code-block:: text

   dt : time

The internal CFL stability criterion is computed as

.. math::

   \Delta t
   \propto
   \frac{\Delta x^2}{D}

which remains dimensionally consistent regardless of whether the time unit is

* seconds,
* years,
* kyr,
* or Myr,

provided both ``D`` and ``dt`` use the same unit.

**Conclusion**

``LinearDiffuser`` is genuinely unit agnostic.

**SimpleSubmarineDiffuser**

Unlike ``LinearDiffuser``, the submarine diffuser explicitly documents its
time units.

Its constructor specifies

.. code-block:: text

   shallow_water_diffusivity (m² / y)

Its timestep documentation specifies

.. code-block:: text

   dt : Time-step duration (y)

The component also defines

.. code-block:: python

   _time_units = "y"

**Conclusion**

``SimpleSubmarineDiffuser`` is explicitly designed to operate using years.

**ErosionDeposition**

The erosion-deposition component documents its parameters using generic units

.. code-block:: text

   L / T

and

.. code-block:: text

   dt : Model timestep [T]

rather than seconds.

**Conclusion**

``ErosionDeposition`` is also unit agnostic provided all quantities are
internally consistent.

**Current Understanding**

After inspecting both the coupling framework and the Landlab source code, the
original hypothesis became significantly weaker.

The investigation now indicates that

* ASPECT is operating in years.
* ``LandLabTemplate`` performs no hidden unit conversions.
* ``LinearDiffuser`` is unit agnostic.
* ``ErosionDeposition`` is unit agnostic.
* ``SimpleSubmarineDiffuser`` explicitly expects years.

Therefore, using

.. code-block:: python

   D = 1e-2
   K = 1e-6
   shallow_water_diffusivity = 1e-2

appears to be the more internally consistent implementation.

This naturally raises the following question:

**If the units are now internally consistent, why does the simulation still
become unstable?**

**Current Leading Hypotheses**

The instability is now believed to originate from something other than the
simple removal of ``/ self.s2yr``.

The leading possibilities are

1. interaction between the newly introduced ghost nodes and one of the
   Landlab components,

2. a mismatch between FastScape parameter definitions and the equivalent
   Landlab parameters,

3. numerical instability within one specific Landlab component.

**Planned Debugging Strategy**

Rather than modifying the unit conversions again, the next debugging stage
will isolate the component responsible for the instability.

The components will be enabled sequentially.

**Stage 1**

.. code-block:: python

   self.flow_accumulator.run_one_step()

**Stage 2**

.. code-block:: python

   self.flow_accumulator.run_one_step()
   self.linear_diffuser.run_one_step(sub_dt)

**Stage 3**

.. code-block:: python

   self.flow_accumulator.run_one_step()
   self.linear_diffuser.run_one_step(sub_dt)
   self.erosion_deposition.run_one_step(sub_dt)

**Stage 4**

.. code-block:: python

   self.flow_accumulator.run_one_step()
   self.linear_diffuser.run_one_step(sub_dt)
   self.erosion_deposition.run_one_step(sub_dt)
   self.submarine_diffuser.run_one_step(sub_dt)

After each component call, the following diagnostic checks will be added:

.. code-block:: python

   print(
       np.nanmin(self.elevation),
       np.nanmax(self.elevation),
       np.any(np.isnan(self.elevation)),
       np.any(np.isinf(self.elevation))
   )

This should identify exactly which component first produces invalid
elevations.

**Next Steps**

The immediate objectives for the next development session are

* isolate the first Landlab component that generates unstable elevations,
* determine whether ghost nodes participate correctly in all Landlab
  calculations,
* verify that the FastScape parameters have identical physical meanings in
  their corresponding Landlab implementations,
* investigate the origin of the divide-by-zero warning inside Landlab,
* determine whether the numerical instability originates before or after the
  first diffusion calculation.

**Status**

The unit-conversion investigation substantially improved the understanding of
the ASPECT–Landlab coupling.

At present, there is no clear evidence that the instability is caused solely
by using years instead of seconds.

Instead, the evidence increasingly suggests that the instability originates
from a numerical issue within one of the coupled Landlab components or from
its interaction with the modified grid containing ghost nodes.