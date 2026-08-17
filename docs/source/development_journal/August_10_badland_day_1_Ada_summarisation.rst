August 10, 2026 – Badlands (Day 1) and Ada ASPECT–Landlab Analysis
===================================================================

Main Activities

I mainly worked on two tasks:

1. Badlands
-------------

I read through the Badlands documentation, source-code structure, and
website to better understand the model, its implementation, and overall
organization.

Badlands: Initial Notes on Fluvial Incision, Sediment Flux, and Basin Sedimentation
----------------------------------------------------------------------------------------
Initial observation
-------------------

While going through the Badlands website and documentation, one of the figures
that particularly caught my attention was **Fig. 4: Model space for stream
power-based incision laws**. The figure shows how the river incision rate
depends on sediment flux and illustrates the different possible relationships
between sediment transport and bed incision.

.. seealso::

   Figure 4: *Model space for stream power-based incision laws*.
   `Click for details <https://badlands.readthedocs.io/en/latest/proc.html>`__

This figure made me interested in understanding not only how Badlands calculates
river incision, but also how the resulting sediment flux is subsequently used
to model **sediment transport, deposition, and ultimately sedimentary basin
development**.

The central question I want to investigate is:

   How do the sediment-flux-dependent incision equations in Badlands
   contribute to the development of sedimentation in a basin, and how does
   this formulation differ from the deposition approaches implemented in
   FastScape and Landlab?

Badlands fluvial formulation
----------------------------

The Badlands documentation describes several formulations of river incision,
ranging from **detachment-limited** to **transport-limited** behavior.

In the basic detachment-limited formulation, incision is controlled primarily
by the resistance of the bed to erosion. In contrast, the transport-limited
formulation introduces a sediment transport capacity, :math:`Q_t`, and
compares the actual sediment flux, :math:`Q_s`, with this capacity.

The important quantity therefore becomes

.. math::

   \frac{Q_s}{Q_t}.

This ratio provides a useful way of thinking about the transition between
erosion and deposition:
* :math:`Q_s \ll Q_t` corresponds approximately to detachment-limited
behavior;

* :math:`Q_s \approx Q_t` approaches transport-limited behavior;

* :math:`Q_s > Q_t` indicates that the supplied sediment exceeds the local transport capacity and deposition can occur.

Badlands therefore does not treat sediment flux simply as a passive output of
erosion. Sediment flux can also modify the rate at which the river incises its
bed.

This is particularly interesting in the context of basin evolution because
the same sediment generated upstream can subsequently become the material
that is transported and deposited downstream.

Sediment flux as a control on incision
--------------------------------------

Badlands introduces a sediment-flux-dependent modification to the stream-power
incision law:

.. math::

   \dot{\epsilon}
   =
   \kappa f(Q_s)(PA)^m S^n,

where :math:`f(Q_s)` represents the dependence of incision on sediment flux.

The documentation describes several possible formulations, including:

* a linear decline or under-capacity formulation;
* an almost-parabolic tool-and-cover formulation;
* a Turowski-type formulation;
* a saltation-abrasion formulation.

This is one of the aspects that caught my attention because sediment has a
dual role in the river system.

At relatively low sediment flux, sediment can enhance erosion through a
**tool effect**, in which transported grains contribute to bed abrasion or
plucking.

At higher sediment flux, sediment can begin to cover and protect the bed,
producing a **cover effect** and reducing bedrock incision.

Thus, sediment flux is not simply a quantity that is transported downstream.
It can actively modify the erosion rate of the river itself.

This creates a feedback:

.. code-block:: text

   erosion
      |
      v
   sediment production
      |
      v
   sediment flux Qs
      |
      +--------------------+
      |                    |
      v                    v
   transport          modification of
   downstream         incision rate
      |
      v
   deposition
      |
      v
   basin sedimentation

This feedback appears particularly relevant for understanding how a landscape
evolves into a sedimentary basin.

From incision to basin sedimentation
-------------------------------------

The aspect I want to understand more deeply is how the incision formulation is
connected to **basin sedimentation**.

A river eroding an upstream landscape generates sediment. That sediment is
transported through the drainage network. As the transport capacity changes
with discharge, slope, and other parameters, sediment can either continue to
be transported or begin to accumulate.

Therefore, basin sedimentation can be viewed as the downstream consequence of
the coupled evolution of:

1. bedrock erosion;
2. sediment production;
3. sediment transport;
4. sediment storage;
5. sediment deposition.

This raises an important modeling question:

   Is Badlands primarily calculating deposition as a consequence of the
   difference between sediment supply and transport capacity, or is there
   an additional formulation controlling where and how sediment is deposited?

This is something I want to examine directly in the Badlands implementation
rather than assuming that all models use the same mathematical treatment.

Comparison with FastScape
-------------------------

Another point that caught my attention is the comparison with **FastScape**.

My current understanding is that the deposition implementation in FastScape
may be related to the formulation discussed by **Yuan et al. (2019)**.
However, this is still a working hypothesis and needs to be verified by
examining the FastScape equations and source code.

.. seealso::

   Braun and Willett, 2013: *A very efficient O(n), implicit and parallel
   method to solve the stream power equation governing fluvial incision and
   landscape evolution* -- *Geomorphology*, 170--179,
   `doi:10.1016/j.geomorph.2012.10.008`_.

   Yuan, X. P., Braun, J., Guerit, L., Rouby, D., & Cordonnier, G. (2019):
   *A new efficient method to solve the stream power law model taking into
   account sediment deposition* -- *Journal of Geophysical Research: Earth
   Surface*, 124, 1346--1365,
   `doi:10.1029/2018JF004867`_.

.. _doi:10.1016/j.geomorph.2012.10.008: https://doi.org/10.1016/j.geomorph.2012.10.008

.. _doi:10.1029/2018JF004867: https://doi.org/10.1029/2018JF004867


The question I want to investigate is therefore:

   Does FastScape calculate deposition using the same type of sediment-flux
   versus transport-capacity relationship used by Badlands, or does it use
   a fundamentally different mass-conservation/deposition formulation?

In particular, I want to compare:

* how sediment flux is calculated;
* how transport capacity is defined;
* how erosion and sediment production are coupled;
* how deposition is triggered;
* whether deposition is calculated explicitly or through flux divergence;
* whether sediment thickness/storage is explicitly tracked;
* how sediment is routed downstream; and
* how these formulations affect basin-scale sediment accumulation.


Comparison with Landlab / SPACE
-------------------------------

The third comparison that interests me is with the **SPACE model implemented
in Landlab**.

SPACE was specifically developed to simultaneously model bedrock erosion,
sediment transport, and the evolution of an alluvial layer. The model
conserves sediment in two reservoirs: the sediment stored on the bed and the
sediment contained in the water column. It explicitly calculates erosion,
entrainment, deposition, and sediment flux.

This makes SPACE particularly interesting for comparison with Badlands.

.. seealso:: 

   Shobe, C. M., Tucker, G. E., & Barnhart, K. R. (2017):
   *The SPACE 1.0 model: A Landlab component for 2-D calculation of sediment
   transport, bedrock erosion, and landscape evolution* — Geoscientific Model
   Development, 10, 4577–4604.

The SPACE formulation can be summarized conceptually as:

.. code-block:: text

   bedrock erosion
         |
         v
   sediment entrainment
         |
         v
   sediment in water column
         |
         +---------> downstream transport
         |
         v
      deposition
         |
         v
   alluvial layer thickness

The important difference is that SPACE explicitly evolves the sediment
reservoir and alluvial thickness. The governing equations conserve sediment
mass both in the water column and on the channel bed.

In particular, SPACE writes the sediment-flux balance in terms of entrainment,
bedrock erosion, deposition, and downstream sediment-flux divergence:

.. math::

   \frac{\partial (Q_s/w)}{\partial x}
   =
   E_s + (1-F_f)E_r - D_s.

The evolution of sediment thickness is then described by

.. math::

   \frac{\partial H}{\partial t}
   =
   \frac{D_s-E_s}{1-\phi}.

This explicit treatment of sediment thickness is one of the features I want
to compare carefully with the Badlands implementation.

The SPACE paper emphasizes that the model uses an
**erosion--deposition framework**, rather than relying only on an Exner-type
flux-divergence formulation. It explicitly calculates sediment entrainment
and deposition and allows the system to transition between
detachment-limited, transport-limited, and mixed behavior.

The paper also states that SPACE was designed to simultaneously evolve an
alluvial layer and a bedrock bed and to operate over landscape-evolution
spatial and temporal scales. This is directly relevant to the comparison I
want to make with Badlands and FastScape.


The paper describes SPACE as a model for simultaneous sediment transport and
bedrock erosion, with explicit conservation of sediment mass and evolution
of an alluvial layer. :contentReference[oaicite:0]{index=0}

Current working comparison
--------------------------

At this stage, I do **not** want to conclude that Badlands, FastScape, and
SPACE use the same deposition algorithm. Instead, I see three potentially
different approaches that need to be examined.

.. list-table:: Initial comparison to investigate
   :header-rows: 1
   :widths: 20 27 27 26

   * - Model
     - Main question
     - Sediment representation
     - Deposition question

   * - Badlands
     - How does :math:`Q_s/Q_t` control incision and deposition?
     - Sediment flux and transport capacity
     - How is excess sediment converted into deposition?

   * - FastScape
     - What formulation controls sediment deposition?
     - To be investigated
     - Is the formulation related to Yuan et al. (2019)?

   * - Landlab / SPACE
     - How are sediment and bedrock simultaneously conserved?
     - Water-column sediment + alluvial layer + bedrock
     - Explicit entrainment and deposition

What particularly catches my attention
---------------------------------------

The most interesting aspect for me is that **sediment is not simply the
product of erosion**.

Instead, sediment can participate in a feedback system:

.. math::

   \text{erosion}
   \rightarrow
   \text{sediment production}
   \rightarrow
   Q_s
   \rightarrow
   \text{incision modification}
   \rightarrow
   \text{transport}
   \rightarrow
   \text{deposition}
   \rightarrow
   \text{basin filling}.

This suggests that understanding basin sedimentation requires understanding
the coupling between **erosion, sediment flux, transport capacity, and
deposition**, rather than examining the deposition equation in isolation.

This is the direction I want to follow next: trace the equations from the
Badlands stream-power incision formulation through the actual implementation
of sediment transport and deposition, and then compare that implementation
with FastScape and Landlab/SPACE.

Badlands flow-network implementation
-------------------------------------

Another part of the Badlands documentation that is relevant to this
investigation is the flow-network implementation.

Badlands computes the stream network over a **TIN** and uses a
**single-flow-direction (SFD)** approximation in which water follows the
steepest downslope path. The nodes are ordered using the
:math:`O(n)` method of Braun and Willett (2013).

The documentation provides the following function:

.. code-block:: python

   SFD_receivers(fillH, elev, neighbours, edges, distances, globalIDs)

This function determines the downslope receiver of each TIN node by
examining neighboring elevations and selecting the steepest downslope
connection.

The resulting flow network and node ordering are important because sediment
flux must subsequently be routed through the drainage network.

The Badlands source documentation shows that the flow-network implementation
operates directly on the TIN and constructs an ordered stack of nodes for
flow routing.


2. Ada ASPECT–Landlab Coupling
--------------------------------

I continued investigating the Ada Lovelace Workshop ASPECT–Landlab
coupling, focusing particularly on the ``s2yr`` conversion and the
differences between runs with and without the conversion.

I summarized the observed issues, including the numerical instability
and parameter/unit-conversion differences, and communicated the findings
to Daniel to get his feedback and comments on the setup.