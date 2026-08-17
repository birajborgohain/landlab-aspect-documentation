August 16, 2026, Badland (Day 5) Rift setting and Topographic relaxation versus continental collision
========================================================================================================





The paper uses two important experiments with fundamentally different
purposes:

* topographic relaxation (TR);
* continental collision (CC).

Topographic relaxation
----------------------

The relaxation experiment begins with an existing sinusoidal topographic
perturbation.

There is no active plate convergence responsible for creating the initial
topography.

Conceptually::

    initial topography
            |
            v
    gravitational/viscous relaxation
            |
            v
    topographic decay
            |
            v
        equilibrium

The basic conceptual relaxation form is:

.. math::

    h(t) = h_0 e^{-t/t^*}

The TR experiment is primarily a numerical benchmark. The question is whether
the numerical method can reproduce the expected relaxation of an initial
topographic perturbation and correctly handle the free surface.

The paper reports that, without surface processes, the topography relaxes over
roughly 300 ka and that the ALE-IB solution agrees well with the analytical
solution.

Continental collision
---------------------

The continental-collision experiment is an actively forced tectonic problem.

The model includes:

* continental crust;
* a pre-existing weak zone;
* convergence;
* visco-plastic deformation; and
* surface processes.

The paper uses a convergence velocity of approximately
``5 cm yr^-1``.

Conceptually::

    plate convergence
            |
            v
       shortening
            |
            v
     crustal thickening
            |
            v
       mountain growth
            |
            v
     erosion/deposition
            |
            v
      tectonic feedback

Thus, collision is not simply relaxation of an existing topographic
perturbation. It is an active mountain-building problem.

Fundamental difference
----------------------

The distinction can be summarized as:

.. list-table:: Topographic relaxation versus continental collision
   :header-rows: 1
   :widths: 30 35 35

   * - Property
     - Topographic relaxation
     - Continental collision
   * - Main process
     - Gravitational/viscous relaxation
     - Tectonic convergence
   * - Active convergence
     - No
     - Yes
   * - Crustal shortening
     - No
     - Yes
   * - Crustal thickening
     - No
     - Yes
   * - Mountain building
     - Not actively produced
     - Actively produced
   * - Topographic response
     - Mainly decay
     - Growth and deformation
   * - Main purpose
     - Numerical benchmark
     - Coupled tectonic application
   * - Analytical solution
     - Available for the benchmark
     - No simple analytical solution

The simplest conceptual distinction is:

    **Topographic relaxation is a "mountain decays" experiment, whereas
    continental collision is a "mountain grows while being eroded"
    experiment.**

Why both experiments are useful
-------------------------------

The two experiments test different aspects of the coupling framework.

TR asks:

    Can the numerical framework correctly handle a moving free surface and
    surface processes when the initial topographic perturbation is allowed
    to relax?

Because an analytical solution exists, the numerical solution can be
quantitatively benchmarked.

CC asks:

    What happens when tectonic deformation actively builds topography while
    erosion and deposition modify the evolving surface?

The second experiment is therefore primarily a scientific application rather
than an analytical benchmark.

Rift setting as a possible third experiment
-------------------------------------------------

A rift setting with topographic growth can, in principle, be tested using the
same general coupled geodynamic–surface-process framework.

A conceptual rift experiment would be:

.. math::

    \text{extension}
    \rightarrow
    \text{faulting}
    +
    \text{crustal thinning}
    +
    \text{isostatic response}
    \rightarrow
    \text{uplift and subsidence}

followed by:

.. math::

    \text{uplift}
    \rightarrow
    \text{erosion}

and:

.. math::

    \text{subsidence}
    \rightarrow
    \text{sediment accommodation and deposition}

Why rifting is different
-------------------------

Rifting is not simply the extensional equivalent of collision.

Collision has a relatively direct relationship:

.. math::

    \text{convergence}
    \rightarrow
    \text{shortening}
    \rightarrow
    \text{crustal thickening}
    \rightarrow
    \text{uplift}

Rifting involves a more spatially complex combination:

.. math::

    \text{extension}
    \rightarrow
    \text{normal faulting}
    +
    \text{crustal thinning}
    +
    \text{isostatic response}

This can produce both positive and negative topographic changes:

* uplifted rift shoulders and footwalls;
* steep fault scarps;
* subsiding hanging walls;
* fault-bounded basins; and
* sediment accumulation within the basins.

The surface process model therefore experiences simultaneously:

.. math::

    U_{\rm tectonic} > 0
    \quad\text{in uplifted regions}

and:

.. math::

    U_{\rm tectonic} < 0
    \quad\text{in subsiding regions}

This creates a spatially heterogeneous system of erosional sources and
depositional sinks.

Potential sedimentary feedback in a rift
----------------------------------------

A rift provides an especially interesting feedback:

.. math::

    \text{extension}
    \rightarrow
    \text{subsidence}
    \rightarrow
    \text{sedimentation}
    \rightarrow
    \text{surface loading}
    \rightarrow
    \text{additional deformation}

At the same time:

.. math::

    \text{extension}
    \rightarrow
    \text{rift-shoulder uplift}
    \rightarrow
    \text{erosion}
    \rightarrow
    \text{mass removal}
    \rightarrow
    \text{isostatic response}

This makes a rift experiment a potentially strong test of two-way
tectonic–surface-process coupling.

Why the paper did not include rifting
-------------------------------------

The paper does not explicitly state that rifting was excluded because of a
specific technical incompatibility.

Therefore, it should not be concluded that the ALE-IB framework cannot handle
rift settings.

The safer interpretation is that the authors chose topographic relaxation and
continental collision as their benchmark/application suite.

The paper also discusses previous coupled modelling studies involving rift
systems, indicating that coupled surface-process/geodynamic modelling is
relevant to rifting.

The authors emphasize other limitations, including the use of two-dimensional
models because of computational cost and the simplification of real
three-dimensional geological structures.

Therefore:

    **The absence of a rift experiment should be interpreted primarily as a
    scope choice rather than evidence that rifting is incompatible with the
    coupling framework.**

Why a rift experiment would be scientifically useful
------------------------------------------------------

A rift case would add a different type of tectonic–surface-process feedback
to the experiments.

A useful three-experiment sequence would be:

.. list-table:: Possible experiment suite
   :header-rows: 1
   :widths: 25 35 40

   * - Experiment
     - Tectonic forcing
     - Main process being tested
   * - Topographic relaxation
     - Relaxation of initial perturbation
     - Free-surface numerical benchmark
   * - Continental collision
     - Compression
     - Mountain building and erosion feedback
   * - Continental rifting
     - Extension
     - Faulting, uplift, subsidence, erosion, and basin sedimentation

For ASPECT–Landlab, rifting would be especially useful because the tectonic
vertical velocity field could contain both uplift and subsidence:

.. math::

    U_{\rm tectonic}(x,y,t)
    =
    u_z(x,y,t)

with:

.. math::

    U_{\rm tectonic} > 0
    \quad\text{for uplift}

and:

.. math::

    U_{\rm tectonic} < 0
    \quad\text{for subsidence}

The Landlab surface evolution could then be represented conceptually as:

.. math::

    \frac{\partial h}{\partial t}
    =
    U_{\rm tectonic}
    -
    E
    +
    D

where ``E`` represents erosion and ``D`` represents deposition.

This would provide a strong test of whether the ASPECT–Landlab coupling correctly
transfers spatially heterogeneous tectonic vertical motion to the surface
process model.

The word "inevitable" in the paper
-----------------------------------

The paper concludes that its work aims to facilitate the **"inevitable
evolution"** of geodynamic modelling toward more holistic and accurate
coupling simulations of Earth's dynamical surface and interior.

Meaning of "inevitable"
-----------------------

Here, **inevitable** means difficult to avoid or expected to happen as the
field develops.

The authors are making a strong statement about the future direction of
geodynamic modelling.

They are not merely saying:

    coupling is useful

or:

    coupling is one possible modelling strategy.

Instead, they suggest that geodynamic modelling is necessarily moving toward
increasingly integrated simulations.

The underlying argument is:

.. math::

    \text{Earth's surface and interior are physically coupled}

therefore:

.. math::

    \text{separate surface and interior models}
    \rightarrow
    \text{increasingly incomplete representation}

and consequently:

.. math::

    \text{geodynamic modelling}
    \rightarrow
    \text{more integrated surface--interior coupling}

Why use such a strong word?
---------------------------

The word **"inevitable"** emphasizes the authors' belief that coupled modelling
is more than one optional modelling philosophy.

Their broader vision is that future models will increasingly need to represent
interacting processes including:

* mantle and lithospheric deformation;
* crustal deformation;
* topographic evolution;
* erosion;
* sediment transport;
* deposition; and
* feedbacks between Earth's surface and interior.

There is an important difference between:

    "natural evolution"

and:

    "inevitable evolution"

"Natural evolution" would be a softer statement that coupling is a logical
progression.

"Inevitable evolution" makes the stronger claim that the field is expected or
bound to move in this direction.

Relation to the paper's motivation
----------------------------------

The statement reflects the central motivation of the paper: reducing the
traditional separation between geodynamic processes and surface processes.

The authors envision a modelling framework in which:

.. math::

    \boxed{
    \text{geodynamics}
    \leftrightarrow
    \text{surface processes}
    }

are treated as interacting components of one dynamical Earth system.

Thus, the sentence can be interpreted as:

    The authors believe that increasingly integrated simulations of Earth's
    interior and surface represent the future direction of geodynamic
    modelling, and that their coupling framework is intended to help enable
    that transition.

Scientific result versus authors' vision
----------------------------------------

"Inevitable" should not be interpreted as a result proven by the numerical
experiments.

There is an important distinction:

* **Scientific result:** the paper demonstrates a particular framework for
  coupling geodynamics and surface processes.
* **Broader claim or vision:** the authors argue that geodynamic modelling will
  inevitably move toward more holistic surface–interior coupling.

Therefore, "inevitable" is best understood as a **statement of scientific
vision or prediction about the direction of the field**, rather than a
quantitative result demonstrated by the experiments.

Connection to the ASPECT–Landlab ``n_substeps`` investigation
-----------------------------------------------------------------

The spatial coupling discussed today can also be viewed together with the
ongoing ``n_substeps`` investigation.

The coupled process can be represented schematically as:

.. math::

    \mathcal{I}_{A\rightarrow L}
    \rightarrow
    \mathcal{E}_{Landlab}
    \rightarrow
    \mathcal{I}_{L\rightarrow A}

where:

* ``I_A->L`` = ASPECT finite-element point evaluation at Landlab points;
* ``E_Landlab`` = Landlab surface-process evolution;
* ``I_L->A`` = closest-point transfer back to ASPECT.

Temporal substepping controls how frequently these spatial-transfer and
surface-evolution operations occur during a tectonic time step.

This helps distinguish two potentially different numerical effects:

* **spatial-transfer effects**, caused by how the two discretizations exchange
  information;
* **temporal operator-splitting effects**, caused by how frequently the
  coupled operators interact.

Key conclusions
------------------

#. Topographic relaxation is primarily a free-surface/numerical benchmark,
   whereas continental collision is an actively forced mountain-building
   experiment.
#. A rift setting can also be studied with the same general coupling
   framework, but it introduces simultaneous uplift, subsidence, faulting,
   erosion, and basin sedimentation.
#. The paper does not identify rifting as technically incompatible with the
   framework; its absence is better interpreted as a scope choice.
#. The word "inevitable" expresses the authors' vision that geodynamic
   modelling will increasingly move toward holistic coupling of Earth's
   surface and interior.
#. "Inevitable" is therefore a prediction or scientific vision about the
   direction of the field, not a numerical result demonstrated by the paper.
