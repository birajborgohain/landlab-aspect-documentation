Landlab meeting: Sediment Component Development in Landlab (Oct 2, 2026, MFD Day1) 
======================================================================================

Purpose and context
-------------------

This document records the detailed technical discussion about developing a new
sediment-routing and sediment-process capability in Landlab, with particular
attention to multiple-flow-direction (MFD) routing and compatibility with
existing erosion components.

The discussion focused on how to move from governing equations and existing
Fortran/source-code knowledge to a simple, testable Landlab implementation.
The main recommendation was to proceed incrementally rather than attempting to
implement the complete sediment model at once.

1. Central technical problem
----------------------------

The principal issue is a mismatch between MFD flow routing and erosion or
sediment components that expect a single downstream direction.

In an MFD system, one node may have several receivers. Water can therefore be
partitioned among several downstream directions. Existing stream-power-style
components, however, may expect:

* one receiver per node;
* one steepest slope per node; and
* one direction along which the erosion process is evaluated.

The discussion described two possible levels of MFD support.

Simplified MFD adaptation
~~~~~~~~~~~~~~~~~~~~~~~~

Water can be allowed to split among multiple directions while the erosion
calculation continues to use the steepest slope and its corresponding receiver.

In this case the routing is multiple-directional, but the erosion process is
still effectively a single-direction calculation.

Full MFD sediment partitioning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sediment itself is divided among all valid downstream receivers according to
the flow-routing proportions.

For node ``i`` and receiver ``j``, the conceptual sediment flux is

.. math::

   Q_{s,i\rightarrow j} = w_{ij} Q_{s,i}^{out}.

The sediment influx at node ``j`` is the sum of contributions from upstream
nodes:

.. math::

   Q_{s,j}^{in} = \sum_i w_{ij}Q_{s,i}^{out}.

The routing weights should satisfy

.. math::

   \sum_j w_{ij}=1.

This is the more complete physical treatment, but it requires substantially
more work.

2. The steepest-slope problem
----------------------------

A key discussion point was the difference between the single-flow and MFD
representations.

A single-flow representation can be viewed as:

.. code-block:: text

   N nodes
      |
      +--> one slope per node
      |
      +--> one receiver per node

An MFD representation can be viewed as:

.. code-block:: text

   N nodes
      |
      +--> multiple slopes per node
      |
      +--> multiple receivers per node
      |
      +--> receiver proportions
```

Conceptually, the MFD slope and receiver arrays may therefore have dimensions
``N x M``, whereas existing components may expect an ``N``-element steepest
slope and receiver field.

The important design issue is that simply changing an established one-
dimensional field into a two-dimensional field could break existing code.

3. Backward compatibility
-------------------------

Backward compatibility was one of the main software-design concerns.

Several possible approaches were discussed.

Approach A: Add a flag
~~~~~~~~~~~~~~~~~~~~~~

The existing component could receive a flag selecting single-flow or MFD
behavior.

For example:

.. code-block:: python

   if single_flow:
       use_existing_method()
   else:
       use_mfd_method()

This avoids creating a second public component, but it increases branching,
complexity, and testing requirements.

Approach B: Create a new component
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A copy of an existing component could be given a new name and modified for the
new behavior.

Advantages:

* the existing component remains unchanged;
* existing workflows remain compatible;
* the new implementation can be developed independently; and
* working directly with the copied component provides an opportunity to learn
  the existing implementation in detail.

The disadvantage is duplicated code and the technical debt that may result.

Approach C: Refactor using inheritance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Common functionality could be placed in a base class, with separate
single-flow and MFD implementations inheriting from it.

This could reduce duplication but would introduce additional abstraction and
could make the code harder to understand.

No final decision was made among these three approaches.

The general preferences expressed were:

* avoid unnecessary flags;
* avoid large amounts of duplicated code;
* avoid unnecessarily complicated inheritance; and
* preserve compatibility where practical.

It was also recognized that backward-incompatible changes can be acceptable in
major software releases if they are deliberate and accompanied by appropriate
migration guidance.

4. The adapter idea
-------------------

A simpler alternative was proposed: insert an adapter between the MFD flow
accumulator and existing erosion components.

The workflow would be:

.. code-block:: text

   MFD flow routing
          |
          | multiple slopes + receivers
          v
   MFD-to-steepest adapter
          |
          | one slope + one receiver
          v
   Existing erosion component
          |
          v
   sediment / topographic evolution
```

For every node, the adapter would identify the maximum available slope and then
select the receiver associated with exactly the same index.

Conceptually:

.. code-block:: python

   steepest_index = np.argmax(slopes, axis=1)

The same ``steepest_index`` must then be used to obtain the corresponding
receiver. This is important because the selected slope and receiver must remain
paired.

The conversion is conceptually:

.. code-block:: text

   slopes:       N x M
   receivers:    N x M
        |
        v
   choose maximum slope
        |
        +----> steepest slope: N
        |
        +----> corresponding receiver: N
```

This was identified as potentially the quickest path to a working system.

5. Why the adapter is attractive
--------------------------------

The adapter allows the MFD flow-routing system to retain its existing
multi-receiver information while supplying the one-dimensional fields expected
by an existing erosion component.

This avoids immediately modifying every erosion component.

The main unresolved issue is whether existing erosion components are hard-wired
to particular field names such as the steepest-slope field. If they are, the
adapter may need to populate the expected field or the erosion component may
need an optional way to specify which slope field it should use.

One possible interface would be conceptually:

.. code-block:: python

   eroder = SomeEroder(
       grid,
       slope_field="topographic__steepest_slope",
   )

The default would preserve current behavior, while an MFD workflow could pass
the field created by the adapter.

6. Full MFD sediment routing
----------------------------

The adapter is not the final MFD sediment solution.

For full MFD routing, sediment must be explicitly partitioned among receivers.

For example, if a source has a sediment flux of 10 units, a simple test could
split it into:

.. code-block:: text

   source
     |
     +---- 5
     |
     +---- 3
     |
     +---- 2
```

The total downstream sediment should remain

.. math::

   5+3+2=10.

This provides a very simple conservation test.

A second test should include several upstream sources contributing sediment to
the same downstream node.

The full implementation must account for:

* multiple sediment receivers;
* receiver proportions;
* sediment influx from multiple upstream nodes;
* erosion and deposition;
* sediment conservation;
* receiver indexing; and
* upstream ordering.

7. Recommended incremental development plan
--------------------------------------------

The discussion strongly favored starting with a small, understandable problem.

Step 1: Learn how to create a Landlab component
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Begin with a minimal component and learn:

* initialization;
* input fields;
* output fields;
* user parameters;
* ``run_one_step``;
* documentation;
* units;
* field validation; and
* testing conventions.

The first component does not need to contain the complete sediment physics.

Step 2: Study the existing flow-routing implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Work directly with a small experimental version of the relevant flow-routing
code.

The goal is to understand:

* receiver arrays;
* receiver proportions;
* upstream ordering;
* donor lists;
* downstream accumulation; and
* differences between single-flow and MFD routing.

Using a very small grid makes it possible to inspect every array manually.

Step 3: Build the MFD-to-steepest adapter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement the simplest conversion:

.. code-block:: text

   multiple slopes
        +
   multiple receivers
        |
        v
   maximum slope
        |
        +--> steepest slope
        |
        +--> matching receiver
```

Step 4: Test the adapter
~~~~~~~~~~~~~~~~~~~~~~~~

Use synthetic topography with a known set of slopes and receivers.

Verify that:

* the maximum slope is selected;
* the receiver at the same index is selected;
* the resulting arrays have the expected one-dimensional shape; and
* single-flow cases remain unchanged.

Step 5: Connect to an existing erosion component
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the adapter output as input to an existing erosion component.

The purpose is to demonstrate that existing erosion physics can operate in an
MFD-routing workflow without immediately rewriting the erosion component.

Step 6: Implement standalone MFD sediment routing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before coupling everything together, create a small sediment-routing module.

Start with known sediment inputs and known receiver proportions.

Verify sediment conservation at every node and after every routing step.

Step 7: Connect erosion to sediment transport
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once routing is verified, connect sediment generated by fluvial erosion to the
sediment-routing framework.

Then add:

* downstream transport;
* deposition;
* sediment influx;
* sediment outflux; and
* topographic change.

Step 8: Extend toward terrestrial-to-marine transport
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The longer-term workflow can then become:

.. code-block:: text

   fluvial erosion
        |
        v
   terrestrial sediment flux
        |
        v
   MFD sediment routing
        |
        v
   coast / shoreline
        |
        v
   marine sediment transport
        |
        v
   marine deposition
        |
        v
   topographic evolution
```

Step 9: Couple with the broader ASPECT-Landlab workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Only after the individual pieces are verified should the sediment workflow be
integrated into the larger ASPECT-Landlab coupling framework.

8. Sediment conservation as a primary test
-------------------------------------------

Sediment conservation should be one of the first numerical tests.

For a node with outgoing sediment flux ``Q_s`` and receiver weights ``w_ij``:

.. math::

   Q_s^{out} = \sum_j Q_{s,i\rightarrow j}.

With

.. math::

   Q_{s,i\rightarrow j}=w_{ij}Q_s^{out},

the split should conserve the total flux when

.. math::

   \sum_j w_{ij}=1.

This test is valuable because it can isolate errors in:

* receiver indexing;
* receiver weights;
* upstream ordering;
* donor construction;
* accumulation; and
* sediment splitting.

A very small synthetic network is therefore more useful at the beginning than
a large landscape simulation.

9. Reuse existing Landlab capabilities
--------------------------------------

The development should not unnecessarily duplicate existing Landlab
functionality.

Where appropriate, the new work should reuse existing capabilities for:

* flow routing;
* drainage-area accumulation;
* stream-power erosion;
* terrestrial erosion and deposition;
* hillslope processes; and
* marine or submarine processes.

The primary development problem is the integration of these capabilities,
especially where MFD routing conflicts with single-receiver assumptions.

10. GitHub issue and collaborative development
----------------------------------------------

The discussion recommended creating a Landlab GitHub issue to document the
high-level problem and development plan.

The issue can record:

* the MFD-routing problem;
* the sediment-routing problem;
* possible designs;
* implementation milestones;
* design decisions;
* test results; and
* future work.

This was preferred to relying only on email because the discussion and design
decisions remain accessible to the development community.

A small collaborative coding session or mini-hackathon was also suggested.

A useful session would include:

1. opening the relevant flow-routing source code;
2. inspecting the MFD data structures;
3. identifying the exact fields required by erosion components;
4. implementing the MFD-to-steepest conversion;
5. constructing a minimal sediment-routing example;
6. testing conservation;
7. deciding whether the adapter should be a function or component; and
8. defining the smallest useful pull request.

11. Pull-request workflow
-------------------------

The recommended workflow is to develop through a **draft pull request**.

Before moving toward full review, the implementation should include:

* documentation;
* tests;
* a clear interface;
* a readable implementation;
* examples;
* completed PR checklist items; and
* a clear explanation of compatibility implications.

A draft PR allows design and implementation feedback before the code is treated
as ready for final review.

12. Immediate coding roadmap
----------------------------

The most practical immediate sequence is:

1. Create a minimal Landlab component.
2. Learn its field and ``run_one_step`` structure.
3. Reproduce a small portion of the flow-routing logic.
4. Inspect MFD receivers, slopes, proportions, and upstream ordering.
5. Implement an MFD-to-steepest adapter.
6. Test the adapter on a tiny synthetic grid.
7. Verify sediment conservation using a prescribed flux split.
8. Connect the adapter to an existing erosion component.
9. Implement full MFD sediment partitioning.
10. Add deposition and sediment mass-balance tests.
11. Extend the workflow toward terrestrial-to-marine sediment transport.
12. Integrate the verified components into the ASPECT-Landlab coupling workflow.

13. Main lesson from the discussion
-----------------------------------

The major challenge is not initially translating the sediment equations into
Python. The first challenge is understanding the **software interface between
Landlab's flow-routing data structures and the assumptions of existing erosion
and sediment components**.

The development can therefore be organized into layers:

.. code-block:: text

   Landlab component architecture
              |
              v
   flow routing and MFD structures
              |
              v
   MFD-to-single-flow adapter
              |
              v
   sediment flux routing
              |
              v
   erosion and deposition
              |
              v
   terrestrial-to-marine transport
              |
              v
   ASPECT-Landlab coupling
```

Starting at the bottom of this sequence makes the implementation easier to
understand, test, and review.

The overall recommendation from the discussion was therefore an incremental,
test-driven development strategy: first understand the existing component and
routing architecture, then establish a minimal MFD conversion and sediment
conservation test, then connect existing erosion processes, and finally build
the integrated terrestrial-marine sediment capability.

Source note
-----------

This document is a detailed organization of the supplied discussion transcript.
It preserves the technical ideas and unresolved design questions raised during
that discussion rather than treating any particular architectural option as a
final decision.
