August 12, 2026 – Badlands (Day 2): Alluvial and Marine Deposition and landlab_vis Documentation Development (Day 5)
======================================================================================================================

Main Activities
----------------

1. Badlands – Day 2: Website, Documentation, and Algorithm Review
--------------------------------------------------------------------

Continued studying Badlands as part of the second day of the Badlands
review. The focus was mainly on the Badlands website and documentation,
with additional attention to understanding the underlying algorithms and
overall model workflow.

The goal was to develop a clearer understanding of how the Badlands model
is structured, how its major components work together, and how the
algorithms are implemented. 




I continued going through the Badlands documentation and source-code
structure, with particular attention to the description of **deposition
processes**.

The section that particularly caught my attention was the discussion of
**alluvial plain forced deposition** and the separate treatment of
**marine deposition**.

.. seealso::

    Badlands documentation: Section: XML input parameters: Alluvial plain forced deposition and Marine deposition
    `<https://badlands.readthedocs.io/en/latest/xml.html>`__


.. .. seealso::

..    Figure 4: *Model space for stream power-based incision laws*.
..    `Click for details <https://badlands.readthedocs.io/en/latest/proc.html>`__

This made me realize that deposition in a landscape-evolution model may not
be represented by a single formulation. Instead, different depositional
environments may require different physical or numerical treatments.

The main question that emerged during this reading was:

   Are alluvial/fluvial deposition and marine deposition represented by
   fundamentally different formulations in Badlands, and how do these
   approaches compare with the corresponding implementations in FastScape
   and Landlab?

Alluvial plain forced deposition
--------------------------------

The Badlands documentation points out an important limitation of the
detachment-limited incision law.

The advantage of the detachment law over transport-limited approaches is the
relatively small restriction it places on computational time steps. However,
the detachment formulation is more appropriate for mountainous regions and
does not by itself account for deposition on alluvial plains.

To address this limitation, Badlands provides an **alluvial plain forced
deposition** mechanism.

The basic idea is that when a river reaches a sufficiently low or critical
slope, deposition can be forced.

Two parameters are particularly important:

``<slp_cr>``
   Critical slope at which forced deposition is activated.

``<perc_dep>``
   Percentage of the maximum deposition that can occur while ensuring that
   the local slope does not reverse.

Conceptually, the process can be represented as:

.. code-block:: text

   Mountainous region
          |
          v
   Detachment-limited erosion
          |
          v
   Sediment production
          |
          v
   Downstream sediment transport
          |
          v
   River reaches low / critical slope
          |
          v
   Forced alluvial deposition
          |
          v
      Alluvial plain

This caught my attention because the deposition is not simply being treated
as a generic consequence of sediment transport capacity.

Instead, Badlands introduces a specific condition associated with the
development of an **alluvial plain**.

This raises an important question:

   Is this forced deposition intended as a numerical treatment for a
   limitation of the detachment-limited formulation, or does it represent
   an additional physical approximation for alluvial-plain development?

This distinction is something I want to investigate further by examining the
Badlands source code.

Alluvial deposition versus transport-limited deposition
--------------------------------------------------------

The discussion of forced deposition also made me reconsider the distinction
between several possible ways of representing deposition.

One possibility is that deposition emerges naturally from the relationship
between sediment supply and transport capacity:

.. math::

   Q_s > Q_t
   \quad \Rightarrow \quad
   \text{sediment accumulation / deposition}.

Another possibility is a **forced deposition rule**, in which deposition is
activated when a geomorphic condition such as a critical channel slope is
reached.

Therefore, Badlands appears to provide at least two conceptually different
ways of thinking about deposition:

1. deposition associated with sediment transport and transport capacity;
2. forced deposition used to represent alluvial-plain development when a
   critical slope condition is reached.

I want to distinguish these carefully rather than treating them as the same
deposition mechanism.

Marine deposition
-----------------

The Badlands documentation then introduces a separate section on
**marine deposition**.

Once sediment reaches the marine environment, rivers no longer transport it
in the same way as they do within the fluvial system. The documentation
describes sediment as generally being deposited close to the shoreline.

This immediately suggests that the model changes the way sediment is treated
once it crosses from the terrestrial/fluvial environment into the marine
environment.

The Badlands documentation also states that a **diffusion law**, defined
within the hillslope structure, can be used to redistribute marine sediment.

Conceptually:

.. code-block:: text

   Fluvial system
        |
        | sediment delivery
        v
   Coastal environment
        |
        v
   Initial marine deposition
        |
        v
   Marine sediment redistribution
        |
        +--------------------+
        |                    |
        v                    v
   Diffusive transport   Further marine transport
                         based on coastal/marine
                         slope and sediment delivery

The documentation also describes two additional parameters for transporting
sediment farther into the marine realm:

``<diffnb>``
   Divides the initial sediment volume into several equal parts that are
   distributed iteratively over the model timestep.

``<diffprop>``
   Controls the proportion of the maximum thickness that can be deposited
   at a node based on surrounding elevations.

This is particularly interesting because it suggests that marine deposition
is not simply the same fluvial deposition algorithm operating below sea
level.

Instead, there appears to be a separate **marine sediment redistribution
process**.

The broader picture emerging from Badlands
------------------------------------------

At this stage, my interpretation is that the Badlands sediment system can be
thought of as a sequence of environments:

.. code-block:: text

   Uplands / mountains
          |
          | erosion
          v
   Fluvial channels
          |
          | sediment transport
          v
   Alluvial plain
          |
          | deposition / storage
          v
   Coastal zone
          |
          | marine deposition
          v
   Marine environment
          |
          | diffusion / marine redistribution
          v
   Offshore sediment accumulation

This provides a more useful framework for understanding basin development.

Rather than asking only:

   "How does Badlands calculate deposition?"

I now want to ask:

   "How does Badlands move sediment between different depositional
   environments, and does the mathematical formulation change as sediment
   moves from the fluvial system to the marine system?"

This distinction is important for understanding how the model can simulate a
complete **source-to-sink system**.

Comparison with FastScape
-------------------------

This observation immediately reminded me of the FastScape implementation I
have been working with.

In the ASPECT--FastScape parameter file, the FastScape component contains a
specific option:

.. code-block:: text

   set Use marine component = false

The FastScape configuration also contains separate parameters for bedrock
and sediment:

.. code-block:: text

   set Bedrock deposition coefficient   = 1
   set Sediment deposition coefficient = 1

and separate erosion and diffusion parameters:

.. code-block:: text

   set Bedrock river incision rate      = 1e-5
   set Sediment river incision rate     = 1e-5

   set Bedrock diffusivity              = 1e-2
   set Sediment diffusivity             = 1e-2

The presence of a separate **Marine parameters** subsection is especially
interesting:

.. code-block:: text

   subsection Marine parameters

      set Sea level = 0
      set Sand porosity = 0
      set Silt porosity = 0
      set Sand e-folding depth = 1e3
      set Silt e-folding depth = 1e3
      set Depth averaging thickness = 1e2
      set Sand transport coefficient = 50
      set Silt transport coefficient = 50

   end

This makes me suspect that FastScape also distinguishes between the
terrestrial/fluvial sediment system and the marine sediment system.

However, I do **not** want to conclude yet that the FastScape formulation is
the same as the Badlands formulation.

The configuration only demonstrates that FastScape has a distinct marine
component and marine parameters. The actual equations and implementation
still need to be traced.

FastScape therefore raises several questions:

* What happens to sediment when it crosses sea level?
* How is terrestrial/alluvial deposition calculated?
* How is marine deposition calculated?
* What role do the ``Sand`` and ``Silt`` parameters play?
* What is the physical meaning of the e-folding depth?
* How are marine transport coefficients used?
* Does the marine component solve a diffusion equation?
* How does the marine component interact with the fluvial sediment flux?
* Is the FastScape deposition formulation related to Yuan et al. (2019)?

These questions should be investigated directly from the FastScape source
and equations.

Comparison with Landlab
-----------------------

The same distinction becomes even clearer when looking at the Landlab
implementation.

There appear to be at least two relevant components that should not be
treated as one model.

The first is the **fluvial erosion-deposition component**:

``ErosionDeposition``

The second is the **marine sediment redistribution component**:

``SimpleSubmarineDiffuser``

These two components represent different processes.

Landlab ``ErosionDeposition``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Landlab ``ErosionDeposition`` component is described as an
erosion-deposition model in the style of **Davy and Lague (2009)**.

It uses a mass-balance approach involving sediment both in the bed and in
transport, with an explicit sediment transport length scale.

The source code describes the erosion term as:

.. math::

   E = K q^{m_{sp}} S^{n_{sp}} - \omega.

The model then calculates sediment influx and deposition rate.

The source code contains:

.. code-block:: python

   self._depo_rate[positive_q] = self._qs[positive_q] * (
       v_s[positive_q] / self._q[positive_q]
   )

and subsequently updates the surface elevation through:

.. code-block:: python

   dzdt = self._depo_rate - self._erosion_term
   self._topographic__elevation[cores] += dzdt[cores] * dt

This is an important implementation detail because it explicitly shows that
the elevation change is calculated from the difference between deposition
and erosion.

The Landlab source also describes ``v_s`` as an effective settling velocity
and explains that the ratio between ``v_s`` and the runoff ratio controls the
transition between detachment-limited and transport-limited response styles.
:contentReference[oaicite:0]{index=0}

Therefore, the Landlab fluvial erosion-deposition component is conceptually
different from simply applying a generic diffusion process.

Landlab ``SimpleSubmarineDiffuser``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The marine component is different.

``SimpleSubmarineDiffuser`` is explicitly described as a model for transporting
marine sediment using a **water-depth-dependent diffusion model**.

Its diffusion coefficient is:

.. math::

   D(h) = D_0 f_1(h) f_2(h).

Here the transport coefficient changes with water depth.

The first function accounts for the decrease in transport efficiency below
the wave-base depth:

.. math::

   f_1(h) =
   \exp\left(-\frac{h-h_w}{h_w}\right)

for depths below the wave base.

The second function accounts for the transition around the shoreline:

.. math::

   f_2(h)
   =
   \frac{\tanh(-h/R_t)+1}{2}.

Thus, the marine Landlab component is fundamentally a
**depth-dependent diffusion model**.

The source code calculates water depth as:

.. code-block:: python

   self._depth[:] = (
       sea_level
       - self._grid.at_node["topographic__elevation"]
   )

and calculates the diffusion coefficient using:

.. code-block:: python

   k[:] = self._shallow_water_diffusivity * self.depth_function(self._depth)

with an additional reduction below the wave base.

The component then calls the inherited diffusion solver:

.. code-block:: python

   super().run_one_step(dt)

and records the resulting topographic change as sediment deposition or
erosion:

.. code-block:: python

   depo[:] = (
       self.grid.at_node["topographic__elevation"] - z_before
   )

The uploaded source therefore gives a clear indication that
``SimpleSubmarineDiffuser`` is not simply another implementation of the
fluvial ``ErosionDeposition`` model. :contentReference[oaicite:1]{index=1}

A conceptual comparison
-----------------------

The distinction that is beginning to emerge can be summarized as:

.. list-table:: Preliminary comparison of depositional processes
   :header-rows: 1
   :widths: 22 28 28 22

   * - Model / process
     - Environment
     - Main mechanism
     - Question to investigate

   * - Badlands alluvial forced deposition
     - Alluvial plain
     - Critical-slope-based forced deposition
     - How does ``slp_cr`` and ``perc_dep`` determine deposition?

   * - Badlands marine deposition
     - Marine
     - Deposition near shoreline + diffusion / marine redistribution
     - How are ``diffnb`` and ``diffprop`` implemented?

   * - FastScape fluvial
     - Terrestrial / fluvial
     - Bedrock and sediment erosion/deposition parameters
     - What is the exact governing formulation?

   * - FastScape marine component
     - Marine
     - Separate marine parameterization
     - How are sand/silt transport and depth dependence calculated?

   * - Landlab ``ErosionDeposition``
     - Fluvial
     - Sediment mass balance + transport length scale
     - How does ``v_s`` control the response?

   * - Landlab ``SimpleSubmarineDiffuser``
     - Marine
     - Water-depth-dependent diffusion
     - How does marine diffusion redistribute sediment?

What particularly caught my attention
-------------------------------------

The main thing that caught my attention on this second day is the possibility
that **sediment deposition is not one single physical or numerical process**.

Instead, the model may need different formulations for different
environments.

I am beginning to think about the sediment system as:

.. code-block:: text

   SOURCE
     |
     v
   Bedrock erosion
     |
     v
   Fluvial sediment production
     |
     v
   Fluvial sediment transport
     |
     +-------------------------+
     |                         |
     v                         v
   Alluvial deposition     Continued transport
     |                         |
     |                         v
     |                    Coastal delivery
     |                         |
     +------------+------------+
                  |
                  v
          Marine deposition
                  |
                  v
          Marine redistribution
                  |
                  v
              SINK / BASIN

This perspective is particularly useful for thinking about **source-to-sink
systems**.

The important issue is that the governing process may change as sediment
moves through the system:

.. code-block:: text

   erosion
      |
      v
   transport
      |
      v
   alluvial deposition
      |
      v
   coastal transfer
      |
      v
   marine deposition
      |
      v
   marine redistribution
      |
      v
   basin accumulation

This is now making me interested in determining whether Badlands, FastScape,
and Landlab are actually implementing the same conceptual source-to-sink
system using different numerical formulations, or whether they make
fundamentally different assumptions about sediment storage and redistribution.

Questions for the next stage
----------------------------

The following questions emerged from this second day of reading.

Badlands
~~~~~~~~

* How exactly is forced alluvial deposition implemented?
* What is the mathematical role of ``slp_cr``?
* How is ``perc_dep`` used to prevent slope reversal?
* Is forced deposition applied only when using the detachment-limited law?
* How does it interact with transport-limited deposition?
* How is sediment thickness or sediment storage represented?
* How does sediment move from the alluvial system into the marine system?

Badlands marine system
~~~~~~~~~~~~~~~~~~~~~~

* Is marine deposition a separate equation from fluvial deposition?
* How is shoreline deposition calculated?
* What exactly does ``diffnb`` control numerically?
* What exactly does ``diffprop`` represent?
* How does the marine diffusion law interact with hillslope diffusion?

FastScape
~~~~~~~~~

* What is the exact formulation associated with the FastScape deposition
  parameters?
* Is the non-marine formulation related to Yuan et al. (2019)?
* What changes when ``Use marine component = true``?
* How are sand and silt represented?
* What are the e-folding depths?
* How is marine transport coupled to the fluvial sediment flux?

Landlab
~~~~~~~

* How does ``ErosionDeposition`` differ mathematically from Badlands?
* How does the Davy and Lague formulation determine deposition?
* What is the precise role of ``v_s``?
* How does ``ErosionDeposition`` handle alluvial sediment storage?
* How does ``SimpleSubmarineDiffuser`` differ from the fluvial
  ``ErosionDeposition`` component?
* Is the marine component intended to represent the same physical process
  as the marine component in FastScape?

Coupled ASPECT--Landlab
~~~~~~~~~~~~~~~~~~~~~~~

* If the surface-process model contains separate terrestrial and marine
  components, how should these be coupled to ASPECT?
* How is sea level represented?
* How is sediment thickness transferred back to the ASPECT surface?
* How should deposition be mapped when the Landlab surface crosses the
  shoreline?
* Does the coupling need separate treatment for fluvial and marine
  sediment fields?

Current interpretation
----------------------

At this stage, I do **not** want to claim that Badlands, FastScape, and
Landlab use equivalent deposition formulations.

Instead, the second day of Badlands reading has identified a more fundamental
question:

   **How does a landscape-evolution model represent the transition from
   bedrock erosion, through fluvial sediment transport and alluvial storage,
   to coastal and marine deposition?**

The initial evidence suggests that different environments may be represented
using different numerical formulations:

.. code-block:: text

   FLUVIAL / ALLUVIAL
   ------------------

   stream power
        +
   sediment transport
        +
   erosion / deposition
        +
   alluvial storage


   MARINE
   ------

   shoreline sediment delivery
        +
   water-depth-dependent transport
        +
   diffusion / redistribution
        +
   marine sediment accumulation

This distinction will be important for the next stage of the Badlands,
FastScape, and Landlab comparison.

The next step is therefore not simply to compare parameter names between
Badlands, FastScape, and Landlab. I need to trace the **governing equations
and source-code implementation** for each environment and determine how
sediment mass is transferred between them.

See also
--------

`Badlands documentation: XML input parameters <https://badlands.readthedocs.io/en/latest/xml.html>`__

`Badlands documentation: Simulated Processes <https://badlands.readthedocs.io/en/latest/proc.html>`__

Shobe, C. M., Tucker, G. E., & Barnhart, K. R. (2017):
*The SPACE 1.0 model: A Landlab component for 2-D calculation of sediment
transport, bedrock erosion, and landscape evolution* --
*Geoscientific Model Development*, 10, 4577--4604.

Yuan, X. P., Braun, J., Guerit, L., Rouby, D., & Cordonnier, G. (2019):
*A new efficient method to solve the stream power law model taking into
account sediment deposition* --
*Journal of Geophysical Research: Earth Surface*, 124, 1346--1365,
`doi:10.1029/2018JF004867 <https://doi.org/10.1029/2018JF004867>`__.

Davy, P. & Lague, D. (2009):
*Fluvial erosion/transport equation of landscape evolution models revisited* --
*Journal of Geophysical Research: Earth Surface*, 114, F03007,
`doi:10.1029/2008JF001146 <https://doi.org/10.1029/2008JF001146>`__.

Braun, J. & Willett, S. D. (2013):
*A very efficient O(n), implicit and parallel method to solve the stream
power equation governing fluvial incision and landscape evolution* --
*Geomorphology*, 170--179,
`doi:10.1016/j.geomorph.2012.10.008 <https://doi.org/10.1016/j.geomorph.2012.10.008>`__.

2. landlab_vis – Day 5: Source Code and Documentation
--------------------------------------------------------

Continued development of the ``landlab_vis`` documentation, with a focus
on connecting the documentation more closely to the source code and
establishing a consistent structure for explaining the software.

The overall documentation structure was organized into:

.. code-block:: text

    Introduction
    Getting Started
    Installation
    Python / Coding Basics
    Cookbook
    API Documentation
    Detailed API Guide
    Developer Guide

A clear distinction was established between the concise **API
Documentation** and the more explanatory **Detailed API Guide**. The API
documentation describes what the public classes, methods, properties, and
functions provide, while the Detailed API Guide explains how the classes
work internally and why particular Python structures are used.

Work also continued on documenting the ``Dataset`` class, including its
relationship with ``Frame``, loading Landlab ``.vtk`` output, frame
selection and navigation, data-location handling, properties and methods,
class methods, Python special methods, and practical examples.

A ``python_basics`` section was also established to explain fundamental
Python concepts used throughout ``landlab_vis``. In particular,
``paths.rst`` documents ``pathlib.Path``, relative and absolute paths,
operating-system-specific paths, and specifying Landlab output
directories.

The documentation philosophy was further refined into the following
structure:

.. code-block:: text

    Concept
        |
        v
    Example
        |
        v
    Example output
        |
        v
    Python / Coding Basics
        |
        v
    Concise API
        |
        v
    Detailed API
        |
        v
    Automatically generated API

This structure provides a consistent separation between what the
software provides, how it works internally, why the underlying Python
concepts are used, how the software is used, and how it can be developed.

The same documentation approach will be applied to the remaining
``landlab_vis`` components, including ``Frame``, ``DatasetReader``,
``Profile``, ``ProfileExtractor``, and ``ProfilePlotter``.