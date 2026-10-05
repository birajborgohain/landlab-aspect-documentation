Oct 3, 2026, Multi-flow Routing and Marine Sediment Deposition in Landlab — (MFD Day 2)
=========================================================================================

3 October 2026
--------------

Development Morning Notes
-------------------------

Understanding ``np.argmax(slopes, axis=1)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



The central issue discussed today was the interface between **multiple-flow-
direction (MFD) routing** and existing Landlab erosion or sediment components
that may expect one downstream receiver and one steepest slope per node.

In a single-flow system, there is one slope and one receiver per node. These
are naturally represented as ``N``-element arrays.

In an MFD system, a node can have several possible receivers. Conceptually,
slopes, receivers, and routing proportions can therefore be represented as
``N x M`` arrays, where ``N`` is the number of nodes and ``M`` is the maximum
number of flow directions/receivers.

The distinction is:

.. code-block:: text

   Single flow:
       N x 1 slope
       N x 1 receiver

   MFD:
       N x M slopes
       N x M receivers
       N x M receiver proportions
```

What ``np.argmax(slopes, axis=1)`` does
---------------------------------------

For an MFD slope array, the expression

.. code-block:: python

   steepest_index = np.argmax(slopes, axis=1)

finds the position of the maximum slope for every node.

For example:

.. code-block:: python

   slopes = np.array([
       [0.10, 0.25, 0.15],
       [0.30, 0.12, 0.20],
       [0.08, 0.11, 0.20],
   ])

   steepest_index = np.argmax(slopes, axis=1)

gives

.. code-block:: text

   [1, 0, 2]
```

meaning:

.. code-block:: text

   node 0 → receiver 2 is steepest
   node 1 → receiver 1 is steepest
   node 2 → receiver 3 is steepest
```

``argmax`` returns the **index**, not the slope value.

The corresponding slope can then be selected using the same index. Most
importantly, the **same index must be used to select the receiver** so that the
slope and receiver remain paired.

Conceptually:

.. code-block:: text

   N x M slopes       N x M receivers
          \                /
           \              /
            → steepest index
                    |
                    v
          N x 1 slope + receiver
```

Effect on sediment flux
-----------------------

This is where an important distinction arises.

Suppose one node has three MFD receivers:

.. code-block:: text

   receiver A   slope = 0.20   proportion = 0.50
   receiver B   slope = 0.15   proportion = 0.30
   receiver C   slope = 0.10   proportion = 0.20
```

If the outgoing sediment flux is 10 units, full MFD routing gives:

.. math::

   Q_{s,A}=0.50(10)=5,

.. math::

   Q_{s,B}=0.30(10)=3,

and

.. math::

   Q_{s,C}=0.20(10)=2.

Therefore:

.. math::

   5+3+2=10.

All three downstream paths carry sediment.

If ``argmax`` is instead used to select the steepest receiver and **all
sediment is sent through that receiver**, the result becomes:

.. code-block:: text

   receiver A = 10
   receiver B = 0
   receiver C = 0
```

Thus ``argmax`` by itself does not preserve MFD sediment partitioning.

For sediment routing, it effectively collapses the MFD network to a
single-flow path.

Why this matters for the FastScape marine model
-----------------------------------------------

The FastScape marine workflow uses multiple receivers and routing weights to
distribute sediment through the marine domain.

The important purpose of MFD here is therefore not simply to obtain a better
estimate of the steepest slope. It is to allow **spatial redistribution of
sediment**.

Conceptually:

.. code-block:: text

                    Coast
                      |
                      v
                  sediment
                      |
                      ●
                    / |                    /  |                    ↓   ↓   ↓
                 A    B    C
               40%  35%  25%
```

This allows sediment to spread laterally across the marine domain rather than
being forced into a single downstream path.

Consequently, replacing full MFD sediment routing with a steepest-direction
``argmax`` approach can change:

* sediment flux at downstream nodes;
* spatial deposition patterns;
* sediment thickness;
* locations of maximum accumulation;
* shelf sediment distribution; and
* subsequent topographic evolution when deposition changes elevation.

Therefore, **yes, it can affect the final sediment field**.

The critical distinction: erosion versus sediment routing
----------------------------------------------------------

The discussion identified two different problems that should not be conflated.

### Problem A — Choosing a slope for erosion

An existing stream-power erosion component may require one slope per node:

.. math::

   E=K A^m S^n.

An MFD-to-steepest adapter can provide a single steepest slope:

.. code-block:: text

   MFD slopes
        |
        v
   maximum slope
        |
        v
   N-element steepest slope
        |
        v
   existing erosion component
```

This can be a useful compatibility solution.

### Problem B — Routing the sediment produced by erosion

Once erosion produces sediment, the sediment can still be distributed among all
valid receivers:

.. math::

   Q_{s,i
   ightarrow j}=w_{ij}Q_{s,i}^{out}.

Thus an intermediate architecture is possible:

.. code-block:: text

             MFD flow routing
                    |
          +---------+---------+
          |                   |
          v                   v
   steepest slope       all receivers
          |                   |
          v                   v
       erosion          sediment routing
          |                   |
          +---------+---------+
                    |
                    v
              sediment flux
                    |
                    v
                 deposition
```

This is fundamentally different from sending all sediment to the ``argmax``
receiver.

Does ``argmax`` make MFD equivalent to single-flow?
----------------------------------------------------

For **sediment routing**, yes, if the selected steepest receiver receives 100%
of the sediment.

The MFD flow-routing component may still contain multiple receivers and
proportions internally, but if the sediment component discards those
alternatives and uses only the ``argmax`` receiver, the sediment process is
effectively single-flow.

Therefore:

.. code-block:: text

   MFD flow routing
          |
          v
   choose steepest receiver
          |
          v
       one receiver
          |
          v
   single-flow sediment routing
```

This should be called an **MFD-to-single-flow compatibility operation**, not a
full MFD sediment-routing implementation.

Why the adapter is still useful
--------------------------------

The adapter solves a software-interface problem.

It can translate:

.. code-block:: text

   MFD information
        |
        +--> N x M slopes
        +--> N x M receivers
        |
        v
   choose steepest direction
        |
        +--> N-element slope
        +--> N-element receiver
        |
        v
   existing single-flow erosion component
```

This allows existing erosion code to be used while the complete MFD sediment
routing is developed separately.

Full MFD sediment routing
-------------------------

A true MFD sediment-routing implementation must retain:

* all valid receivers;
* receiver proportions;
* sediment flux at each node;
* sediment contribution to each receiver;
* sediment influx from multiple upstream nodes; and
* sediment conservation.

The basic operation is:

.. math::

   Q_{s,i
   ightarrow j}=w_{ij}Q_{s,i}^{out}.

The downstream influx is then accumulated from all upstream contributions:

.. math::

   Q_{s,j}^{in}=\sum_i Q_{s,i
   ightarrow j}.

For a conservative split:

.. math::

   \sum_j w_{ij}=1,

and therefore:

.. math::

   \sum_j Q_{s,i
   ightarrow j}=Q_{s,i}^{out}.

This conservation relation should be one of the first numerical tests of the
new sediment-routing implementation.

Recommended development sequence
---------------------------------

The discussion leads to the following incremental plan.

1. **Understand MFD routing.**

   Inspect receivers, receiver proportions, slopes, upstream ordering, and
   donor relationships.

2. **Build the steepest-direction adapter.**

   Use ``np.argmax(slopes, axis=1)`` to obtain the steepest direction and its
   corresponding receiver.

3. **Use the adapter only for erosion compatibility.**

   Do not interpret it as full MFD sediment routing.

4. **Build a standalone MFD sediment-routing test.**

   Prescribe a known sediment flux and known receiver proportions.

5. **Verify conservation.**

   For example, route 10 units as 5 + 3 + 2 and verify that the total remains
   10.

6. **Connect erosion to sediment routing.**

   Reuse existing erosion capabilities where appropriate.

7. **Add deposition.**

   Track sediment influx, outflux, deposition, and topographic change.

8. **Extend toward the marine domain.**

   Preserve multiple receivers and routing weights so that sediment can spread
   spatially across the marine domain.

9. **Validate the final sediment field.**

   Compare total sediment, spatial distribution, sediment thickness, deposition
   locations, and sensitivity to routing proportions.

Main conclusion
---------------

The key lesson from Day 2 is that

.. code-block:: python

   np.argmax(slopes, axis=1)
```

answers:

**"Which flow direction is steepest for each node?"**

It does **not** answer:

**"How should sediment flux be distributed among all MFD receivers?"**

Therefore these operations should remain conceptually separate.

For compatibility with an existing single-flow erosion component:

.. code-block:: text

   N x M slopes
       |
       v
   np.argmax(..., axis=1)
       |
       v
   N-element steepest slope
```

For true MFD sediment transport:

.. code-block:: text

   N x M receivers
   N x M proportions
          +
   sediment flux
          |
          v
   sediment partitioning
          |
          v
   multiple downstream sediment fluxes
```

This distinction is central to the planned Landlab sediment-component
development.

The practical strategy is therefore to use the steepest-index adapter, if
needed, for the **erosion-component compatibility problem**, while developing
the **full MFD sediment-flux routing problem** separately for realistic
terrestrial-to-marine sediment redistribution.
