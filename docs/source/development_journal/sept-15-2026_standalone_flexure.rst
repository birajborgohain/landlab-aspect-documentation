September, 15,2026, FastScape–ASPECT vs. Landlab–ASPECT: Sediment Thickness Comparison, Landlab Flexure
==========================================================================================================

Starting hypothesis
--------------------

The starting point was a comparison of the ``sediment_thick`` field in
FastScape–ASPECT and Landlab–ASPECT.

The initial profiles were nearly identical. After approximately 800 kyr,
noticeable spatial fluctuations developed in Landlab–ASPECT, while
FastScape–ASPECT remained comparatively smooth.

The main question was whether this difference could be related to how the two
models transport and redistribute sediment.

Both simulations were intended to use the same ASPECT configuration,
geometry, initial conditions, and ``set Compositional field methods = field``.
The main difference for this investigation was the sediment-transport
formulation:

* FastScape includes erosion, upstream sediment supply, transport, and
  deposition, with sediment thickness represented through the
  surface–basement relationship.
* The current Landlab implementation uses ``SimpleSubmarineDiffuser`` (SSD),
  which represents submarine sediment redistribution primarily as
  depth-dependent diffusion.

The initial hypothesis was that the richer FastScape sediment formulation
might redistribute or damp a feedback that becomes more pronounced in the
current Landlab formulation.

Objective of the standalone experiments
----------------------------------------

Rather than immediately modifying the full Landlab–ASPECT model, we isolated
two Landlab components:

* ``SimpleSubmarineDiffuser`` — sediment redistribution/deposition.
* ``Flexure1D`` — lithospheric response to sediment loading.

The purpose was to determine whether increasing sediment thickness produces
flexure, whether flexure can modify accommodation and subsequently affect
sediment redistribution, and whether this feedback could plausibly produce
behavior similar to the spatial variability observed in Landlab–ASPECT.

The experiments were deliberately arranged as a progression from simple
single-component tests to sediment-state and feedback experiments.

Experiment progression
----------------------

Level 1 — SimpleSubmarineDiffuser reference
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SSD was first run by itself to establish the baseline behavior of the current
Landlab submarine sediment-transport formulation.

The closed-boundary experiment approximately conserved sediment. Importantly,
``sediment_deposit__thickness`` was recognized as a timestep diagnostic rather
than a persistent sediment reservoir.

Level 2 — Prescribed sediment load -> Flexure1D
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A prescribed sediment-thickness distribution was converted to pressure using

.. math::

   P = rho_s g H.

This tested whether a sufficiently large sediment load can generate a
measurable flexural response.

For a maximum prescribed sediment thickness of about 2000 m, the setup
produced a flexural response of approximately 1762 m. The important result was
that substantial accumulated sediment loading can generate a large flexural
response.

Level 3 — SSD -> incremental load -> Flexure1D
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SSD sediment change was converted into an incremental load and passed to
Flexure1D.

The flexural increments were extremely small. This showed that the
instantaneous SSD sediment change can be far too small to generate meaningful
flexure, even though the accumulated sediment thickness may eventually be
large.

Level 4 — Closed SSD–Flexure feedback
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Flexure was allowed to modify the surface seen by the next SSD timestep:

    sediment redistribution
        -> sediment load
        -> flexure
        -> accommodation/surface
        -> sediment redistribution

The feedback remained extremely weak under the incremental-load formulation.
This was the first strong indication that simple ``dH -> load -> flexure``
feedback was not sufficient to explain the Landlab–ASPECT fluctuations.

Level 5 — Persistent sediment state + flexure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The surface was explicitly decomposed as

.. math::

   z = R + H,

where ``z`` is surface elevation, ``R`` is bedrock elevation, and ``H`` is
persistent sediment thickness.

The state-consistency relation was maintained throughout the experiment.
However, flexure remained very small because loading was still based on
timestep sediment change rather than total accumulated sediment load.

Level 6 — Persistent sediment state + mass conservation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The next experiment focused on sediment state representation and mass
conservation without flexural feedback.

The model explicitly maintained ``z = R + H`` while SSD redistributed
persistent sediment.

The sediment volume changed by only about ``4e-4 m^2`` in the 1-D volume proxy,
showing excellent numerical mass closure in the closed system.

This demonstrated that an explicit persistent sediment state can be introduced
while maintaining a mass-conserving relationship between surface, bedrock,
and sediment thickness.

Level 7 — Persistent sediment state + external source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An external sediment source was added and the sediment budget was explicitly
tracked as

.. math::

   M(t) = M(0) + M_external(t).

This separated internally redistributed sediment from externally supplied
sediment and provided a framework for later mass-balance experiments.

Level 8–9 — Sediment source + flexural feedback
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Persistent sediment, external sediment supply, and flexural feedback were
combined and compared with a no-flexure control.

The incremental-load formulation again produced negligible flexural effects.
The control and feedback sediment-thickness evolutions were essentially
indistinguishable.

Level 10 — Resolution sensitivity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The paired control/feedback experiment was repeated at approximately 2 km,
1 km, and 0.5 km resolution.

The sediment-thickness solutions remained effectively identical between
control and flexural cases. The dominant wavelength was also much larger than
the grid spacing.

Thus, the weak flexural effect was not explained simply by the tested spatial
resolution.

Level 11 — Direct large sediment perturbation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A localized perturbation of approximately 1000 m was introduced to provide a
stronger forcing.

Even with this large perturbation, the flexural displacement under the
incremental-load formulation was approximately ``1e-9 m``.

The sediment-thickness difference remained small and could not be explained by
a meaningful flexural response.

This highlighted the fundamental distinction between total sediment
thickness ``H`` and timestep sediment change ``dH``.

Level 12 — Total sediment load -> static Flexure1D
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A controlled static test used the total sediment load,

.. math::

   P = rho_s g H.

For a maximum sediment thickness of approximately 2000 m, the corrected test
gave approximately:

* Airy response: 1762.1 m;
* elastic response: 1762.6 m;
* Airy analytical error: zero;
* elastic/Airy ratio: approximately 1.0003.

This verified that Flexure1D responds correctly to a substantial total
sediment load in the controlled static experiment.

This was a diagnostic test, not the final time-dependent coupling
formulation. Flexure1D uses ``lithosphere__increment_of_overlying_pressure``,
so repeatedly treating total accumulated load as an increment would
artificially accumulate the flexural response.

Level 13 — Naive total-load feedback
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Total sediment load was combined with SSD in a time-dependent feedback and
the absolute flexural response was repeatedly added to the bedrock.

This generated an unrealistic flexural accumulation of approximately 66.7 km.

The experiment was rejected as a physical coupling formulation, but it clearly
identified the accumulation artifact.

Level 14 — Quasi-static total-load feedback
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The formulation was corrected by preserving an unloaded reference bedrock
surface ``R0`` and calculating the flexural response from the current total
sediment load:

.. math::

   R = R0 + w(H),

   z = R + H.

This removed the artificial accumulation.

The maximum flexural displacement was approximately 266 m in the chosen
experiment, demonstrating that the accumulated sediment load can produce a
substantial accommodation response.

However, the sediment response remained weak:

* maximum sediment-thickness difference: about 0.10 m;
* RMS sediment-thickness difference: about 0.0115 m;
* control and feedback sediment distributions: nearly identical.

Thus, even a substantial flexural response did not reproduce the strong
sediment-thickness variability observed in Landlab–ASPECT.

Level 15 — Prescribed accommodation sensitivity + source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Accommodation was prescribed directly, with amplitudes from 0 to 1000 m,
while an external sediment source remained active.

The sediment response remained weak. The maximum sediment-thickness
difference stayed close to 0.10 m even though accommodation increased by a
factor of 20.

Level 16 — Pure accommodation sensitivity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The accommodation experiment was repeated without an external sediment
source.

Again, the response was weak. Increasing prescribed accommodation from 50 to
1000 m did not produce a proportionally large increase in sediment
redistribution.

This further weakened the idea that a simple sediment-loading/flexural
accommodation feedback is the primary explanation for the Landlab–ASPECT
spatial fluctuations.

Main findings
-------------

Finding 1 — Sediment loading can generate substantial flexure
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The static loading experiments demonstrate that sufficiently large sediment
thickness can generate substantial flexural response.

For example, a prescribed 100 m sediment thickness produced approximately
1.63 m of flexural response in the tested setup.

Therefore, sediment loading is physically capable of generating accommodation.

Finding 2 — Total sediment load and timestep sediment change are different
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The early feedback experiments used ``dH`` to calculate pressure and produced
almost no flexure.

The later static experiments showed that the accumulated thickness ``H`` can
produce a much larger response.

This distinction is fundamental for designing the eventual dynamic coupling.

Finding 3 — Flexure alone did not reproduce the Landlab–ASPECT behavior
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Even when a substantial total-load flexural response was imposed, the SSD
sediment response remained weak.

Therefore, the current experiments do not support simple
``sediment accumulation -> loading -> flexure -> accommodation`` as the main
explanation for the strong Landlab–ASPECT fluctuations.

Finding 4 — The 100–200 m range became an important diagnostic
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Landlab–ASPECT results suggest that stronger spatial changes occur not
only around approximately 800 kyr, but also after sediment thickness becomes
roughly 100–200 m.

This changes the useful question from

    Why does the behavior change at approximately 800 kyr?

to

    Does increasing sediment thickness eventually produce enough sediment
    loading to modify the coupled surface evolution?

The 100 m prescribed-load experiment showed that this thickness range can
produce meter-scale flexural response in the controlled setup.

However, 100–200 m should not yet be called a critical threshold. The current
experiments have not established a threshold in the coupled Landlab–ASPECT
system.

Finding 5 — The broader FastScape hypothesis remains plausible
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The experiments weakened one specific interpretation:

    FastScape is smoother because its richer sediment formulation damps a
    sediment-loading/flexural feedback.

The Landlab standalone tests did not show a strong version of that particular
feedback.

However, the broader hypothesis remains reasonable:

    The different sediment-transport and deposition formulations in FastScape
    and Landlab may respond differently to surface perturbations and
    geodynamic forcing. One formulation may redistribute or damp spatial
    perturbations that are amplified by the other.

The investigation should therefore shift toward sediment-transport
formulation, sediment-state representation, numerical operators, and coupling
order rather than flexure alone.

What the experiments changed scientifically
--------------------------------------------

The smoother FastScape result should not automatically be interpreted as more
physical.

Two possibilities remain:

#. FastScape's richer sediment transport and deposition formulation genuinely
   redistributes sediment in a way that suppresses spatial amplification.
#. The two models solve different sediment-transport problems, so their
   different patterns reflect different model formulations rather than one
   model being intrinsically more physical.

The standalone experiments provide the controlled route for separating these
possibilities.

Refined working hypothesis
--------------------------

The working hypothesis is now:

    Does the difference in sediment transport and deposition formulations
    between FastScape and Landlab alter the amplification or redistribution
    of surface perturbations during geodynamic coupling, leading to the
    stronger spatial variability observed in Landlab–ASPECT?

This is more defensible than assuming that the difference is caused by
flexural feedback.

Next experiments
----------------

### Matched standalone Landlab versus FastScape

The next decisive experiment is a matched standalone comparison of Landlab
and FastScape before ASPECT coupling.

Use the same:

* initial surface;
* sediment distribution;
* spatial resolution;
* timestep;
* model duration;
* boundary conditions;
* sea level;
* forcing.

Track not only sediment thickness but also sediment redistribution and
spatial variability.

If the difference already appears in standalone runs, the sediment
formulation is the leading explanation.

If the standalone models behave similarly but diverge after ASPECT coupling,
then the coupling or feedback is the more likely source.

### Explicit 100–200 m sensitivity test

Run controlled cases through approximately

.. math::

   0, 25, 50, 75, 100, 125, 150, 175, 200, 250 m.

For each case record maximum sediment thickness, sediment load, maximum and
RMS flexural response, sediment-thickness change, and spatial wavelength.

The key question is whether the apparent 100–200 m transition corresponds to a
real change in response.

### Compare sediment thickness with flexure

For an evolving Landlab experiment, plot:

* maximum sediment thickness versus time;
* flexural response versus time;
* flexural response versus maximum sediment thickness;
* sediment-thickness variability versus maximum sediment thickness.

The last two plots are especially important because they test whether
sediment thickness, rather than elapsed model time, controls the transition.

### Separate transport effects from coupling effects

The eventual controlled matrix should contain:

* Landlab standalone;
* FastScape standalone;
* one-way Landlab–ASPECT;
* one-way FastScape–ASPECT;
* two-way Landlab–ASPECT;
* two-way FastScape–ASPECT.

This separates sediment-transport effects from ASPECT feedback effects.

### Test numerical sensitivity

For the Landlab–ASPECT fluctuations, examine:

* spatial resolution;
* timestep;
* diffusivity;
* coupling interval;
* coupling order;
* sediment transport magnitude;
* erosion/deposition balance;
* mass conservation;
* characteristic wavelength relative to grid spacing.

This will help distinguish physical amplification from a numerical artifact.

Overall conclusion
-------------------

The experiments moved the investigation from a qualitative observation to a
controlled hypothesis test.

The key result is:

    Large accumulated sediment loads can produce substantial flexural
    response, but the current SimpleSubmarineDiffuser configuration did not
    show a comparably strong sediment-redistribution response to that
    accommodation.

Therefore, the strong spatial variability developing in Landlab–ASPECT after
sediment thickness becomes large is not yet explained by simple
sediment-loading/flexural feedback.

The investigation should now focus more strongly on the differences between
the sediment-transport formulations and state representations of Landlab and
FastScape, while using the 100–200 m sediment-thickness range as a targeted
diagnostic.

The next decisive test is a matched standalone Landlab versus standalone
FastScape sediment-evolution experiment, followed by controlled one-way and
two-way coupling experiments.
