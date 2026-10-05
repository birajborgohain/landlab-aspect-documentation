Sept 26-27, 2026, Monolithic and Moduar Component MFD Sediment Routing in Landlab
======================================================================================

Summary: Monolithic vs. Non-Monolithic Coupling and the Planned MFD
Sediment-Routing Component
-------------------------------------------------------------------

Purpose
-------

This note summarizes the concepts discussed about **monolithic and
non-monolithic numerical coupling** and documents the planned development
of a modular **MFD sediment-routing component** for Landlab.

The immediate goal is to develop a small, testable component that uses
Landlab's existing multiple-flow-direction (MFD) infrastructure to route
sediment through multiple downstream pathways. More complex processes,
including erosion, sand/silt partitioning, and deposition, can then be
added progressively.

1. Monolithic and Non-Monolithic Concepts
-----------------------------------------

1.1 Coupled does not mean monolithic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Consider two unknowns:

* ``x`` = elevation
* ``y`` = sediment thickness

Suppose the physics gives two coupled equations::

    2x + y = 10
    x + 3y = 12

These can be written as one matrix system::

    [ 2  1 ] [ x ] = [ 10 ]
    [ 1  3 ] [ y ]   [ 12 ]

This is a **monolithic formulation** because the unknowns are assembled
into one combined system and solved together.

The important idea is::

    coupling  = how the physical variables influence each other
    monolithic = how the numerical problem is assembled and solved

Therefore, a problem can be physically coupled without being solved by a
monolithic solver.

1.2 Component-based or non-monolithic approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of assembling one large system containing both ``x`` and ``y``,
the problem can be separated into components.

For example::

    Elevation component
          |
          | calculates/updates x
          |
          v
       shared fields
          ^
          |
          | calculates/updates y
          |
    Sediment component

The components communicate through shared fields and can be executed
sequentially or iteratively.

Conceptually, the equations might be represented as::

    A_x x = b_x(y)

and::

    A_y y = b_y(x)

There can still be matrices ``A_x`` and ``A_y`` inside the individual
components. The difference is that the entire ``x-y`` problem is not
necessarily assembled into one global block matrix.

1.3 The global monolithic representation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a more general coupled elevation-sediment problem, a monolithic
formulation could look like::

    [ A_zz  A_zH ] [ dz ] = [ b_z ]
    [ A_Hz  A_HH ] [ dH ]   [ b_H ]

Here:

* ``A_zz`` describes elevation-to-elevation relationships.
* ``A_HH`` describes sediment-to-sediment relationships.
* ``A_zH`` represents the influence of sediment on elevation.
* ``A_Hz`` represents the influence of elevation on sediment.

The off-diagonal blocks represent the coupling between the fields.

For ``N`` grid nodes, ``z`` and ``H`` each contain ``N`` unknowns, so the
combined system has approximately ``2N`` unknowns.

1.4 Non-monolithic does not mean uncoupled
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A component-based model can still have feedback::

    sediment H
        |
        v
    elevation z
        |
        v
      slope S
        |
        v
    sediment flux Qs
        |
        v
    deposition D
        |
        v
    sediment H

Thus the system can be strongly coupled even if the software is organized
as separate components.

A typical sequential or iterative structure is::

    calculate flow
        ->
    calculate erosion
        ->
    route sediment
        ->
    calculate deposition
        ->
    update topography
        ->
    repeat

This is non-monolithic in organization, but it can still represent
coupled physics.

2. Why This Matters for Landlab
-------------------------------

Landlab is a component-based framework. It is therefore better not to
describe "Landlab" as inherently monolithic or inherently non-monolithic.
Different components and workflows can use different numerical methods.

For the planned development, the initial strategy is **component-based and
non-monolithic**:

* use existing Landlab flow-routing infrastructure;
* create a dedicated sediment-routing component;
* exchange information through Landlab grid fields;
* progressively add erosion, sand/silt partitioning, deposition, and
  sediment storage;
* only investigate a monolithic coupled solver later if the scientific
  equations require simultaneous solution.

3. Planned MFD Sediment-Routing Architecture
--------------------------------------------

The planned architecture is::

                         EXISTING LANDLAB
                      +---------------------+
                      | topographic z       |
                      +----------+----------+
                                 |
                                 v
                       +----------------+
                       | FlowDirectorMFD|
                       +--------+-------+
                                |
                                v
                 +----------------------------+
                 | receiver nodes r_ij       |
                 | proportions w_ij          |
                 | slopes S_ij               |
                 | links                     |
                 +-------------+--------------+
                               |
                               v
                       +----------------+
                       | FlowAccumulator|
                       +--------+-------+
                                |
                                v
                 +----------------------------+
                 | Q, drainage area, stack   |
                 +-------------+--------------+
                               |
                               v
                 +----------------------------+
                 | NEW COMPONENT              |
                 |                            |
                 | MFD Sediment Router        |
                 | + erosion                  |
                 | + sand/silt partition      |
                 | + deposition               |
                 +-------------+--------------+
                               |
                               v
                 +----------------------------+
                 | sediment__influx            |
                 | sediment__outflux           |
                 | sand__influx/outflux        |
                 | silt__influx/outflux        |
                 | deposition                  |
                 | erosion                     |
                 +-------------+--------------+
                               |
                               v
                         update z / H

The first version should deliberately be smaller than this final diagram.
The initial component should concentrate on the core MFD sediment-routing
operation before all erosion and deposition physics are added.

4. How the Existing Landlab MFD Fields Are Used
------------------------------------------------

The existing ``FlowDirectorMFD`` supplies the MFD network information.
The important conceptual fields are:

* ``flow__receiver_node``

  The downstream receiver nodes. For route-to-many methods this is a
  two-dimensional node field.

* ``flow__receiver_proportions``

  The fraction of flow assigned to each receiver.

* ``flow__link_to_receiver_node``

  Links associated with the receiver pathways.

* ``topographic__steepest_slope``

  Downhill slope associated with each receiver pathway.

``FlowAccumulator`` supplies additional information such as:

* ``drainage_area``
* ``surface_water__discharge``
* ``flow__upstream_node_order``

The planned sediment component should consume these existing fields rather
than recreate the MFD flow-direction algorithm.

5. Core MFD Sediment-Routing Equation
-------------------------------------

Suppose node ``i`` has sediment outflux

.. math::

   Q_{s,i}.

If node ``i`` has receivers ``j`` with MFD proportions

.. math::

   w_{ij},

then the sediment flux sent from node ``i`` to receiver ``j`` is

.. math::

   Q_{s,i\rightarrow j}
   =
   w_{ij} Q_{s,i}.

The receiver proportions satisfy

.. math::

   \sum_j w_{ij}=1.

Therefore the sediment arriving at downstream node ``j`` is

.. math::

   Q_{s,j}^{in}
   =
   \sum_i w_{ij} Q_{s,i}.

This is the fundamental operation of the proposed MFD sediment router.

6. Simple Example
-----------------

Suppose one node has 100 m3/yr of sediment leaving it and MFD gives two
receivers:

* receiver A: 60 percent
* receiver B: 40 percent

Then::

    Q_s = 100 m3/yr

    Q_s -> A = 0.60 x 100 = 60 m3/yr

    Q_s -> B = 0.40 x 100 = 40 m3/yr

and therefore::

    60 + 40 = 100 m3/yr

The routing conserves sediment.

This is analogous to the existing MFD water-routing structure, but the new
component applies the receiver proportions to sediment flux.

7. Adding Sand and Silt
-----------------------

Once bulk sediment routing works, the sediment can be separated into two
fractions::

    Q_s = Q_sand + Q_silt

Define a sand fraction ``F_s``:

.. math::

   Q_{\rm sand}=F_s Q_s,

and

.. math::

   Q_{\rm silt}=(1-F_s)Q_s.

The same MFD routing can then be applied separately::

   Q_{\rm sand,i\rightarrow j}
   =
   w_{ij}Q_{\rm sand,i}

and::

   Q_{\rm silt,i\rightarrow j}
   =
   w_{ij}Q_{\rm silt,i}.

This provides the basic structure needed for later sand-silt deposition and
marine sediment coupling.

8. Progressive Development Strategy
------------------------------------

Stage 1 -- MFD sediment routing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement only the transfer of sediment from a node to multiple receivers::

    Q_s,i -> w_ij Q_s,i

No complicated erosion or deposition physics is required initially.

Stage 2 -- Sediment conservation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verify that sediment is conserved::

    incoming sediment + generated sediment
    =
    outgoing sediment + deposited sediment + boundary loss.

For a closed routing test, the expected total mass balance should be
verified numerically.

Stage 3 -- Erosion
~~~~~~~~~~~~~~~~~~

Add a sediment-generation law, for example a stream-power-type relation::

    E = K Q^m S^n

The exact erosion formulation should be selected after the basic routing
component is validated.

Stage 4 -- Deposition
~~~~~~~~~~~~~~~~~~~~~

Add a deposition law that converts transported sediment flux into a local
deposition rate::

    D = f(Q_s, Q, S, ...)

Then update the surface according to the chosen sediment-mass formulation.

Stage 5 -- Sand/silt partition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Introduce separate sand and silt fluxes::

    Q_s = Q_sand + Q_silt.

Track their routing and deposition separately.

Stage 6 -- Persistent sediment state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Introduce sediment thickness fields, for example::

    H = H_sand + H_silt

and, where appropriate,

.. math::

   z = z_{\rm bedrock} + H.

This turns sediment into an explicit state variable rather than only a
diagnostic change in elevation.

Stage 7 -- Marine sediment routing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use an MFD network in the marine domain to distribute sediment among
multiple downslope pathways.

Stage 8 -- Coupled terrestrial-marine evolution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The eventual feedback loop is::

    H -> z -> S -> Q_s -> D -> H

At this stage the model becomes a genuinely coupled sediment-topography
system. A more strongly coupled or monolithic numerical formulation can be
considered only if the governing equations and timestep requirements make
it necessary.

9. Implementation Philosophy
----------------------------

The first implementation should be a **modular Python Landlab component**,
not an immediate rewrite of the entire Landlab MFD infrastructure.

The preferred progression is::

    Pure Python reference implementation
                 |
                 v
          unit tests
                 |
                 v
      mass-conservation tests
                 |
                 v
       FastScape comparison
                 |
                 v
          Numba optimization
                 |
                 v
            benchmark
                 |
                 v
      C++ only if justified

The purpose of the pure-Python implementation is to make the numerical
algorithm transparent and easy to inspect. Performance optimization should
come after the mathematical and conservation properties are demonstrated.

10. Proposed Initial Component Interface
-----------------------------------------

A conceptual component might eventually look like::

    class MFDSedimentRouter(Component):

        def __init__(self, grid, ...):
            # read existing Landlab MFD fields
            # create sediment input/output fields
            # store model parameters

        def run_one_step(self, dt):
            # obtain MFD receiver network
            # obtain receiver proportions
            # process nodes in the appropriate flow order
            # route sediment to multiple receivers
            # update sediment influx/outflux
            # later: erosion, deposition, sand/silt, sediment thickness

The first implementation should remain small enough that every operation
can be checked by hand.

11. Validation Plan
-------------------

Before adding complicated physics, construct simple tests.

Test 1 -- Single receiver
~~~~~~~~~~~~~~~~~~~~~~~~~

If only one receiver exists and::

    w = 1

the new MFD sediment router should reproduce ordinary single-flow
sediment routing.

Test 2 -- Two-way split
~~~~~~~~~~~~~~~~~~~~~~~

For::

    w_1 = 0.6
    w_2 = 0.4

and::

    Q_s = 100

verify::

    Q_s,1 = 60
    Q_s,2 = 40

and::

    Q_s,1 + Q_s,2 = Q_s.

Test 3 -- Multiple upstream donors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verify that the downstream node receives the sum of all incoming sediment
contributions.

Test 4 -- Mass conservation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verify that total sediment is conserved except for explicitly represented
deposition, storage, or boundary export.

Test 5 -- Topographic feedback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After sediment deposition changes ``z``, rerun the flow direction and verify
that the MFD network responds consistently to the new topography.

Test 6 -- FastScape comparison
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the basic algorithm is correct, compare selected routing and sediment
results with the corresponding FastScape formulation.

12. Overall Research Direction
------------------------------

The immediate research/software-development goal is therefore:

**Build a modular MFD sediment-routing component inside Landlab that reuses
the existing MFD flow network and provides a clean sediment-flux interface.**

The development is intentionally incremental:

.. math::

   \text{MFD flow network}
   \rightarrow
   \text{sediment routing}
   \rightarrow
   \text{erosion}
   \rightarrow
   \text{deposition}
   \rightarrow
   \text{sand/silt}
   \rightarrow
   \text{sediment storage}
   \rightarrow
   \text{marine routing}
   \rightarrow
   \text{coupled topography}.

The important architectural principle is::

    Existing Landlab FlowDirectorMFD
                  +
    Existing Landlab FlowAccumulator
                  +
    New MFD sediment-routing component
                  =
    modular MFD sediment framework

This approach allows the new scientific capability to be developed,
tested, validated, and optimized independently before it is integrated
into the larger terrestrial-marine erosion and deposition framework.
