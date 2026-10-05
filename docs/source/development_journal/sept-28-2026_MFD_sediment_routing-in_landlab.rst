
Sept 28, 2026, Why MFD Sediment Routing Belongs in Landlab
Rather Than in ``ASPECT/source/mesh_deformation/landlab.cc``
=======================================================================

Purpose
-------

This document summarizes the reasoning that led us to the conclusion that
**multiple-flow-direction (MFD) sediment routing should be developed as a
Landlab-side capability rather than implemented inside ASPECT's
``landlab.cc`` coupling code**.

The conclusion emerged from tracing the ASPECT--Landlab coupling architecture,
examining the existing Landlab MFD infrastructure, examining the sediment
components that currently do not support route-to-multiple flow, and
distinguishing the responsibilities of the ASPECT C++ coupling layer from
those of the Landlab surface-process model.

The central conclusion is:

.. important::

   **ASPECT's ``landlab.cc`` should remain the coupling/interface layer.
   MFD sediment routing should be implemented in Landlab, where the flow
   network, sediment processes, fields, and surface-process state already
   live.**

The goal is therefore not to put a new MFD algorithm into ASPECT. Instead,
ASPECT should provide the geodynamic forcing and receive the resulting
surface-elevation change, while Landlab performs the surface-process
calculation.

1. We first identified what ``landlab.cc`` actually does
--------------------------------------------------------

The first step was to trace the historical ASPECT--Landlab coupling code.

The important discovery was that ``landlab.cc`` is **not a sediment-routing
module** and is not intended to be the place where Landlab surface-process
algorithms are implemented.

It is an ASPECT-side coupling plugin.

Its responsibility is approximately:

::

    ASPECT
       |
       | ASPECT solution fields
       v
    landlab.cc
       |
       v
    Python / Landlab
       |
       | topographic change
       v
    landlab.cc
       |
       v
    ASPECT mesh deformation

The historical ``Landlab`` class derives from ``ExternalToolInterface<dim>``
and loads a Python script. The external-tool interface provides the generic
mechanism for:

* evaluating ASPECT fields at external evaluation points;
* passing those fields to the external model;
* receiving updated surface velocities or deformation information;
* mapping the external result back to ASPECT surface degrees of freedom;
* creating the ASPECT mesh-velocity constraints.

Therefore, ``landlab.cc`` is fundamentally an **adapter/interface** between
ASPECT and the Python/Landlab surface-process model.

2. We traced the ASPECT-side data pathway
-----------------------------------------

The coupling pathway was reconstructed as:

::

    ASPECT solution
          |
          v
    RemotePointEvaluation
          |
          v
    ASPECT fields at Landlab nodes
          |
          v
       update_until()
          |
          v
    Landlab surface-process model
          |
          v
       Delta z
          |
          v
    ASPECT surface velocity
          |
          v
    mesh velocity constraints
          |
          v
    MeshDeformationHandler
          |
          v
    vector-Laplacian mesh deformation
          |
          v
    ALE correction
          |
          v
    next ASPECT solution

This showed that the surface-process physics is intended to occur on the
Landlab/Python side.

The C++ coupling code transfers information; it does not need to know the
details of every surface-process algorithm.

3. We examined ``update_until()``
---------------------------------

The Python interface reinforced the same conclusion.

The coupling template defines an ``update_until()`` function that advances the
Landlab model for the duration of an ASPECT timestep.

Conceptually:

::

    ASPECT timestep
          |
          v
    update_until(...)
          |
          v
    advance Landlab
          |
          v
    calculate change in topography
          |
          v
    return Delta z to ASPECT

The test implementation demonstrated this architecture by advancing a
Landlab diffusion model through substeps and accumulating the resulting
topographic change.

Therefore, a sediment-routing algorithm naturally belongs inside the
Landlab evolution performed by ``update_until()`` or inside a Landlab
component called from it.

4. We examined the existing Landlab MFD capability
--------------------------------------------------

The next important discovery was that **Landlab already has MFD flow
routing**.

Landlab's MFD infrastructure can determine:

* multiple receiver nodes;
* the proportion of flow routed to each receiver;
* the upstream-node ordering required to process the drainage network;
* drainage area and related flow-routing quantities.

Therefore, we do NOT need to develop a new MFD hydrologic routing algorithm.

The existing Landlab MFD machinery can provide the network:

::

    Topography
        |
        v
    FlowDirectorMFD
        |
        +------------------+
        |                  |
        v                  v
    receiver nodes     receiver proportions
        |                  |
        +--------+---------+
                 |
                 v
          sediment routing

This changed the problem substantially.

The problem is not:

::

    "How do we implement MFD?"

The problem is:

::

    "How do we use Landlab's existing MFD flow network
     to route sediment through multiple receivers?"

5. We separated flow routing from sediment routing
--------------------------------------------------

This distinction became central.

Landlab already provides the hydrologic MFD structure:

::

    topography
        |
        v
    MFD flow direction
        |
        +--> receiver 1
        +--> receiver 2
        +--> receiver 3
        ...
        |
        +--> receiver proportions

Our proposed development operates on that existing network.

For sediment flux, if node ``i`` has outgoing sediment flux ``Qs_i_out`` and
routes to receiver ``j`` with proportion ``w_ij``, then

::

    Qs_(i -> j) = w_ij * Qs_i_out

The downstream sediment influx is the sum of all upstream contributions:

::

    Qs_j_in = sum( w_ij * Qs_i_out )

Thus, the sediment-routing layer consumes the MFD information generated by
Landlab rather than recalculating it.

6. We examined the existing sediment components
-----------------------------------------------

We then looked at Landlab's sediment-processing components, particularly:

* ``ErosionDeposition``
* ``SpaceLargeScaleEroder``

These components already provide substantial sediment-process functionality.

They calculate erosion, deposition, sediment influx/outflux, and related
surface-process quantities.

This was another important reason not to place a new sediment algorithm in
ASPECT.

The relevant Landlab components already contain the scientific concepts and
data structures needed for sediment processing.

However, both components currently check whether route-to-multiple flow has
been used and raise ``NotImplementedError`` because compatibility with
route-to-multiple methods has not been verified.

The important point is therefore not that Landlab lacks sediment modeling.

Instead:

::

    Landlab has

        MFD flow routing
        +
        sediment erosion/deposition components

    but the two pieces are not yet integrated for
    route-to-multiple sediment processing.

This identifies a much more precise development opportunity.

7. The actual development gap
-----------------------------

The development gap can therefore be represented as:

::

        EXISTING LANDLAB
------------------------

        Topography
             |
             v
        FlowDirectorMFD
             |
             +------------------------+
             |                        |
             v                        v
        receivers              proportions
             |                        |
             +-----------+------------+
                         |
                         v
                  Flow accumulation


        EXISTING LANDLAB
------------------------

        Erosion
        Deposition
        Sediment flux
        Sediment fields


        MISSING INTEGRATION
---------------------------

        MFD sediment routing
                 |
                 v
        multiple-receiver
        sediment transport
                 |
                 v
        downstream sediment
        accumulation
                 |
                 v
        deposition / storage

The scientific-software problem is therefore an **integration problem**, not
a missing MFD-flow problem.

8. Why putting MFD sediment routing in ``landlab.cc`` is the wrong layer
------------------------------------------------------------------------

Putting the algorithm in ``landlab.cc`` would mix two fundamentally different
responsibilities.

The responsibilities of ``landlab.cc`` are:

* communication between ASPECT and Python;
* transfer of ASPECT solution fields;
* evaluation-point handling;
* return of surface deformation information;
* ASPECT mesh-velocity constraints.

The responsibilities of Landlab are:

* flow routing;
* drainage-network representation;
* erosion;
* sediment transport;
* deposition;
* topographic evolution;
* persistent surface-process state.

MFD sediment routing belongs to the second group.

A C++ implementation inside ``landlab.cc`` would therefore place a
surface-process algorithm inside an ASPECT coupling adapter, even though the
same information and data structures already exist on the Landlab side.

9. It would also make the coupling less modular
-----------------------------------------------

The desired architecture is:

::

                    ASPECT
                      |
             geodynamic forcing
                      |
                      v
              Landlab coupling
                      |
                      v
                  Landlab
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
      flow          erosion      sediment
     routing                     deposition
        |             |             |
        +-------------+-------------+
                      |
                      v
                 Delta z
                      |
                      v
                    ASPECT

The alternative would be:

::

                    ASPECT
                      |
                      v
                landlab.cc
                      |
             +--------+--------+
             |                 |
             v                 v
       coupling logic     sediment MFD
             |             algorithm
             |                 |
             +--------+--------+
                      |
                      v
                   Landlab

The second architecture makes ``landlab.cc`` responsible for knowledge of
a particular surface-process algorithm.

That would make the coupling layer more tightly coupled to the scientific
implementation.

10. The existing Landlab architecture gives us the correct abstraction
----------------------------------------------------------------------

The MFD sediment algorithm can instead consume fields already produced by
Landlab.

Conceptually:

::

    FlowDirectorMFD
          |
          +--> flow__receiver_node
          |
          +--> flow__receiver_proportions
          |
          +--> upstream ordering
          |
          v
    MFD sediment-routing component
          |
          +--> sediment influx
          +--> sediment outflux
          +--> deposition
          +--> sediment storage
          |
          v
    updated topography
          |
          v
       Delta z
          |
          v
       ASPECT

This means the new component can remain useful independently of ASPECT.

It could first be tested as a normal Landlab component and only later be
called through the ASPECT--Landlab coupling.

11. The development sequence became clear
-----------------------------------------

Stage 1 -- Use existing Landlab MFD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Do not write another flow-direction algorithm.

Use:

::

    FlowDirectorMFD
        |
        v
    receiver nodes
    receiver proportions
    upstream ordering

Stage 2 -- Implement MFD sediment transport
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Develop the sediment-specific operation:

::

    sediment outflux
           |
           +--> w1 * Qs
           +--> w2 * Qs
           +--> w3 * Qs
           ...

and accumulate these contributions at downstream nodes.

Stage 3 -- Couple sediment routing to erosion/deposition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Conceptually:

::

    sediment influx
          +
    local erosion
          -
    deposition
          =
    sediment outflux

The resulting sediment flux is then distributed among the MFD receivers.

Stage 4 -- Add persistent sediment state
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the broader terrestrial--marine model, maintain quantities such as:

* sediment thickness;
* sediment fractions;
* sediment flux;
* deposition;
* erosion;
* potentially silt/sand fractions.

Stage 5 -- Couple to ASPECT
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Only after the Landlab component is independently validated should it be
called from the ASPECT--Landlab ``update_until()`` workflow.

The ASPECT side then remains conceptually simple:

::

    ASPECT
       |
       | uplift / velocity / fields
       v
    Landlab
       |
       | erosion + MFD sediment routing + deposition
       v
    Delta z
       |
       v
    ASPECT

12. Why this is especially important for the proposed FastScape-compatible work
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The broader goal is not simply to reproduce FastScape's MFD routing.

FastScape already contains its own flow-routing and marine sediment-routing
implementations.

The proposed Landlab development is better described as:

::

    FastScape formulations
             +
    existing Landlab capabilities
             +
    MFD-compatible sediment processing
             +
    terrestrial--marine coupling
             +
    ASPECT coupling
             |
             v
    integrated Landlab workflow

Landlab's existing capabilities should therefore be reused wherever
possible.

In particular, we should not duplicate:

* MFD flow direction;
* drainage-area accumulation;
* FastScape stream-power erosion;
* general Landlab erosion/deposition functionality.

Instead, the development should focus on the missing interfaces and
integration required to move sediment through an MFD network and ultimately
into the terrestrial--marine workflow.

13. The final architectural conclusion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The reasoning can be summarized in one diagram:

::

                     ASPECT
                       |
                       | geodynamic fields
                       v
              +------------------+
              |   landlab.cc     |
              |                  |
              | ASPECT/Python    |
              | coupling layer   |
              +--------+---------+
                       |
                       | Python interface
                       v
              +------------------+
              |     Landlab      |
              |                  |
              | Existing MFD     |
              | Existing erosion |
              | Existing fields  |
              |                  |
              | +--------------+ |
              | | NEW MFD      | |
              | | sediment     | |
              | | routing      | |
              | +--------------+ |
              |                  |
              +--------+---------+
                       |
                       | Delta z
                       v
                     ASPECT

The conclusion is:

.. important::

   **MFD sediment routing should be developed as a Landlab capability, not
   embedded in ``landlab.cc``.**

``landlab.cc`` should remain the ASPECT--Landlab coupling layer.

Landlab should own the surface-process algorithm.

ASPECT should provide geodynamic forcing and receive the resulting surface
deformation.

14. The key scientific-software principle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The final principle behind the decision is:

::

    Put an algorithm where the data,
    physical processes, and software abstractions
    that define that algorithm already live.

For MFD sediment routing:

::

    MFD receivers
        +
    receiver proportions
        +
    upstream ordering
        +
    sediment flux
        +
    erosion/deposition
        +
    sediment state

are all fundamentally Landlab-side concepts.

Therefore the sediment-routing algorithm belongs in Landlab.

The ASPECT ``landlab.cc`` layer should expose the coupling interface, not
become a second implementation of Landlab's surface-process model.

15. One-sentence conclusion for the book
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A concise statement suitable for the computational book is:

::

    Because Landlab already provides the MFD flow network while its sediment
    processing components do not yet support route-to-multiple sediment
    transport, the appropriate development is an MFD-compatible sediment
    routing component in Landlab; ASPECT's ``landlab.cc`` should remain the
    coupling layer that transfers geodynamic fields to Landlab and returns
    the resulting surface deformation.
