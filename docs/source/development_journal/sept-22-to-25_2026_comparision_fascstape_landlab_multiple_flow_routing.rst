September 22 to 25, 2026, FastScape--Landlab Sediment-State Comparison, Multple flow routing
==============================================================================================

Date
----
25 September 2026

Focus
-----
Comparison of existing Landlab components with corresponding FastScape Fortran
implementations to identify the implementation gap in representing and
evolving sediment as an explicit spatial state for ASPECT--Landlab coupling.

Time spent on the focused comparison
-------------------------------------
The focused FastScape--Landlab comparison work began on 22 September 2026 and
continued through 25 September 2026, including today's discussion with the
Landlab developers.

This corresponds to approximately **4 calendar days** of focused comparison
work (22--25 September, inclusive). This focused period was built on earlier
FastScape source-code exploration and sediment/erosion-deposition work.

What was compared
-----------------
Five main comparisons were carried out:

1. ``FastScape Marine.f90`` vs. ``Landlab SimpleSubmarineDiffuser``
2. ``FastScape StreamPowerLaw.f90`` vs. ``Landlab FastscapeEroder``
3. ``FastScape find_receiver()`` vs. ``Landlab FlowDirectorD8``
4. ``FastScape find_mult_rec()`` vs. ``Landlab FlowDirectorMFD``
5. ``Landlab ErosionDeposition`` vs. ``Landlab SpaceLargeScaleEroder``

Main findings
-------------
The comparison showed that the issue is not simply the absence of individual
numerical components in Landlab.

Landlab already provides:

* single-flow routing through components such as ``FlowDirectorD8``;
* multiple-flow-direction (MFD) routing through ``FlowDirectorMFD``;
* drainage accumulation through ``FlowAccumulator``;
* FastScape-compatible implicit stream-power erosion through
  ``FastscapeEroder``;
* sediment erosion/deposition through ``ErosionDeposition``;
* SPACE-based sediment and bedrock erosion/deposition through
  ``SpaceLargeScaleEroder``; and
* submarine diffusion through ``SimpleSubmarineDiffuser``.

The important difference identified through the comparison is the way these
capabilities are connected into an integrated sediment state.

FastScape's marine implementation connects terrestrial sediment production,
sediment flux, terrestrial routing, marine transfer, marine multiple-flow
routing, sediment fractions, marine transport, deposition, and sediment
thickness/composition evolution within a connected workflow.

In contrast, the current Landlab workflow used in the ASPECT coupling calls
the surface-process components sequentially:

.. code-block:: python

   flow_accumulator.run_one_step()

   erosion_deposition.run_one_step(sub_dt)

   linear_diffuser.run_one_step(sub_dt)

   submarine_diffuser.run_one_step(sub_dt)

This provides the individual surface processes, but does not yet provide the
same integrated terrestrial--marine sediment-state workflow found in
FastScape.

MFD finding
-----------
A particularly important part of the investigation was the distinction
between the availability of MFD routing and its use by downstream sediment
components.

Landlab already has ``FlowDirectorMFD`` and ``FlowAccumulator`` can use
multiple-flow routing. Therefore, the development gap is not the absence of
an MFD flow-routing algorithm itself.

The comparison instead raised the question of whether route-to-multiple
information is propagated into the sediment-transport and sediment-state
components.

The current ``ErosionDeposition`` and ``SpaceLargeScaleEroder`` implementations
were found to check for route-to-multiple flow and currently do not support
that workflow because compatibility has not been verified.

Discussion with Landlab developers
-----------------------------------
On 25 September 2026, the findings were presented to the Landlab developers.

The developers verified that **multiple-flow routing is not currently used
within the relevant sediment-processing framework**. This supports the
central observation from the comparison: Landlab has MFD flow-routing
infrastructure, but the existing sediment-process framework does not
currently propagate/use that MFD information in the way required for the
proposed integrated sediment workflow.

The developers considered this a potential development gap that could be
addressed to further refine and extend the Landlab framework.

Proposed development direction
------------------------------
The proposed work is not to replace existing Landlab components or to
reproduce FastScape algorithms unnecessarily.

Instead, the development would investigate an integrated sediment-state
framework that reuses existing Landlab capabilities and connects them through
explicit sediment fields.

The conceptual workflow is:

.. code-block:: text

   flow routing
        |
        v
   erosion
        |
        v
   sediment generation
        |
        v
   sediment routing
        |
        v
   marine transfer
        |
        v
   marine routing
        |
        v
   deposition
        |
        v
   sediment thickness H(x,y,t)

Potential development components include:

* integration of MFD routing with sediment transport;
* explicit sediment influx and outflux;
* terrestrial-to-marine sediment transfer;
* sediment storage in depressions and lakes;
* marine sediment routing;
* optional silt and sand fractions;
* explicit evolving sediment thickness;
* sediment mass-conservation diagnostics; and
* exchange of the sediment state within the ASPECT--Landlab coupling.

Key conclusion
--------------
The comparison and developer discussion shifted the interpretation of the
original problem from a primarily numerical implementation issue toward a
potential **framework integration and sediment-state architecture gap**.

The central development question is now:

   How can existing Landlab flow-routing, erosion, deposition, and marine
   components be connected so that multiple-flow sediment routing produces
   a consistent, spatially evolving sediment state suitable for
   terrestrial--marine surface-process modeling and ASPECT coupling?

This provides a concrete direction for the next stage of development while
preserving and reusing the substantial functionality already present in
Landlab.
