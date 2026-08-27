August 19, 2026 -- Badlands (Day 7): Sediment Transport, Deposition, Stratigraphy, and Model Frameworks
=======================================================================================================

Comparative Analysis of Landscape-Evolution and Sedimentation Models
--------------------------------------------------------------------

After reviewing the following papers, the comparative analysis below examines
the common features and major differences among the models, with particular
emphasis on sediment transport, erosion, deposition, sediment storage,
stratigraphy, and tectonic--surface-process coupling.

* Gasparini & Brandon (2011);
* Davy & Lague (2009);
* Badlands / Salles et al.;
* SPACE / Shobe et al. in Landlab;
* Yuan et al. (2019);
* FastScape / FastScapeLib; and
* Terrainbento / Barnhart et al. (2019).

The important realization from this study is that these models should not be
viewed simply as different choices of coefficients or exponents in a
stream-power equation.

Instead, they represent different levels of representation of the sediment
system.

The central question is therefore:

   How did landscape-evolution models move from prescribing erosion with
   relatively simple empirical relationships toward explicitly representing
   sediment production, transport, deposition, storage, basin filling, and
   stratigraphic evolution?

For the planned ASPECT--Landlab application, this distinction is especially
important. The objective is not merely to reproduce topographic evolution.
The broader objective is to understand how tectonic deformation, erosion,
sediment transport, deposition, sediment loading, and basin development
interact.

The conceptual progression can be summarized as::

    empirical erosion law
            |
            v
    sediment-dependent erosion
            |
            v
    sediment conservation
            |
            v
    explicit erosion + transport + deposition
            |
            v
    alluvial sediment storage
            |
            v
    source-to-sink sediment routing
            |
            v
    marine redistribution
            |
            v
    stratigraphic basin evolution
            |
            v
    tectonic--surface-process coupling
            |
            v
    modular and multi-model experimentation


1. A common mathematical foundation
------------------------------------

Despite their differences, most of these models share several fundamental
ideas.

1.1 Topography evolves through competing processes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the simplest level, surface elevation can be represented conceptually as

.. math::

   \frac{\partial h}{\partial t}
   =
   U - E + D,

where:

* :math:`h` is surface elevation;
* :math:`U` is tectonic uplift or another vertical forcing;
* :math:`E` is erosion; and
* :math:`D` is deposition.

This equation is conceptually simple, but the meaning of :math:`E` and
:math:`D` differs substantially among LEMs.

In a simple detachment-limited model, erosion may be calculated directly from
topographic properties:

.. math::

   E = K A^m S^n.

In a sediment-aware model, erosion can instead depend on sediment flux:

.. math::

   E = f(A,S,Q_s).

In a sediment-conserving model, erosion and deposition become coupled through
sediment transport:

.. math::

   \frac{\partial Q_s}{\partial x}
   =
   E_s - D_s
   + \text{other sediment sources and sinks}.

Thus, the important evolution is not simply a change in the mathematical
expression for erosion. It is the introduction of sediment as an explicit
quantity that can be transported, stored, and deposited.

1.2 Sediment production and routing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sediment ultimately originates from erosion of:

* bedrock;
* soil;
* previously deposited sediment;
* hillslopes; or
* other sediment reservoirs.

A general conceptual pathway is::

    substrate
       |
       v
    erosion
       |
       v
    sediment production
       |
       v
    sediment transport
       |
       v
    deposition
       |
       v
    storage / export

The increasing sophistication of LEMs can therefore be understood partly in
terms of how many of these stages are explicitly represented.

1.3 Drainage and topographic gradients
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most fluvial LEMs use some representation of:

* drainage area;
* discharge;
* channel slope;
* flow direction; and
* sediment transport capacity.

A common stream-power relationship is

.. math::

   E = K_f A^m S^n,

where:

* :math:`K_f` represents fluvial erodibility;
* :math:`A` represents drainage area;
* :math:`S` represents local slope;
* :math:`m` is the area exponent; and
* :math:`n` is the slope exponent.

The stream-power relationship therefore remains important even in more
advanced models.

The major difference is what is added around it.


2. The most important distinction: erosion versus sediment routing
------------------------------------------------------------------

The central conceptual distinction among these models is whether sediment is
treated as:

#. an implicit consequence of erosion;
#. a control on erosion;
#. a transported quantity;
#. a conserved reservoir; or
#. part of a complete source-to-sink stratigraphic system.

A useful conceptual hierarchy is::

    LEVEL 1
    -------
    Erosion only

        E = f(A,S)


    LEVEL 2
    -------
    Sediment affects erosion

        E = f(A,S,Q_s)


    LEVEL 3
    -------
    Sediment is explicitly transported

        erosion
           |
           v
        Q_s
           |
           v
        downstream transport


    LEVEL 4
    -------
    Sediment is conserved

        erosion
           |
           +------> sediment reservoir
           |
           v
        transport
           |
           v
        deposition


    LEVEL 5
    -------
    Complete source-to-sink system

        tectonics
           |
           v
        erosion
           |
           v
        sediment production
           |
           v
        fluvial transport
           |
           v
        deposition
           |
           v
        marine redistribution
           |
           v
        basin
           |
           v
        stratigraphy


This hierarchy is useful when comparing models because it prevents the
different formulations from being treated as if they were merely different
parameterizations of the same equation.


3. Gasparini & Brandon: sediment as a control on incision
----------------------------------------------------------

Gasparini & Brandon represent an important conceptual step because sediment
is considered not only as the product of erosion but also as something that
can influence bedrock incision.

The classical formulation is

.. math::

   E = K A^m S^n.

A more physically detailed formulation can instead be represented
conceptually as

.. math::

   E = f(A,S,Q_s),

where :math:`Q_s` is sediment flux.

The important conceptual change is:

   sediment can modify erosion.

3.1 Tool effect
~~~~~~~~~~~~~~~

At relatively low to moderate sediment flux, sediment can enhance bedrock
erosion by providing tools that impact and abrade the bed.

The conceptual process is::

    sediment
       |
       v
    impacts on bedrock
       |
       v
    abrasion / plucking
       |
       v
    enhanced incision

3.2 Cover effect
~~~~~~~~~~~~~~~~

At sufficiently high sediment flux, sediment can cover the bed.

The conceptual process becomes::

    high sediment flux
           |
           v
    sediment cover
           |
           v
    reduced bedrock exposure
           |
           v
    reduced incision

This tool-and-cover interpretation is important because it demonstrates that
sediment can be an active control on erosion rather than simply a passive
product of erosion.

3.3 Why changing ``m`` and ``n`` is not the same thing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This distinction should be retained throughout the LEM literature study.

Changing

.. math::

   E = K A^m S^n

to

.. math::

   E = K' A^{m'} S^{n'}

changes the parameterization.

It does not necessarily introduce a new physical process.

By contrast,

.. math::

   E = f(A,S,Q_s)

introduces sediment flux as an explicit control.

Therefore, a model that has different effective values of :math:`m` and
:math:`n` does not necessarily represent fundamentally different erosion
physics.

.. note::

   Similar stream-power exponents do not necessarily imply identical
   underlying erosion physics.


4. Davy & Lague: sediment conservation and disequilibrium transport
-------------------------------------------------------------------

Davy & Lague (2009) represent a major conceptual development because the
sediment problem is treated explicitly as a transport and mass-balance
problem.

The model introduces concepts including:

* erosion;
* deposition;
* sediment flux;
* water discharge;
* slope; and
* sediment transport length.

The transport length represents the average distance travelled by sediment
before deposition.

Conceptually::

    erosion
       |
       v
    sediment enters flow
       |
       v
    sediment transport
       |
       | finite transport length
       v
    deposition

This introduces spatial disequilibrium between erosion and deposition.

Sediment produced in an uplifting region therefore does not necessarily have
to be deposited immediately adjacent to its source.

4.1 Transport length
~~~~~~~~~~~~~~~~~~~~

The transport length can be represented conceptually as

.. math::

   \xi = \text{mean sediment travel distance}.

The interpretation is:

* small :math:`\xi` -> sediment is deposited relatively close to its source;
* large :math:`\xi` -> sediment can travel farther downstream.

Thus the model introduces a spatial lag between erosion and deposition.

4.2 Relevance to tectonic landscapes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Consider a tectonically active region:

.. code-block:: text

    tectonic uplift
          |
          v
      steep slopes
          |
          v
       erosion
          |
          v
    sediment production
          |
          v
    downstream transport
          |
          v
       deposition
          |
          v
        basin

The location of maximum erosion therefore does not have to coincide with the
location of maximum deposition.

This is one of the fundamental requirements for understanding sedimentary
basins.


5. Badlands: from fluvial erosion to source-to-sink evolution
--------------------------------------------------------------

Badlands represents a broader source-to-sink modeling framework.

The framework can incorporate processes including:

* detachment-limited incision;
* transport-limited incision;
* sediment-flux-dependent incision;
* hillslope processes;
* sediment transport;
* deposition;
* tectonic forcing;
* sea-level forcing;
* marine sediment transport; and
* stratigraphic evolution.

The conceptual framework becomes::

    tectonic forcing
          |
          v
       landscape
          |
          v
       erosion
          |
          v
    sediment production
          |
          v
    fluvial transport
          |
          v
       coast
          |
          v
    marine transport
          |
          v
    sediment deposition
          |
          v
       stratigraphy

5.1 Alluvial-plain forced deposition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One feature that particularly caught my attention while studying the Badlands
documentation is the treatment of alluvial-plain deposition.

The detachment-limited incision law has the advantage of permitting relatively
large computational time steps. However, detachment-limited formulations are
more naturally suited to mountainous regions where bedrock incision is the
dominant process.

They do not automatically provide a complete representation of extensive
alluvial-plain deposition.

Badlands therefore includes a mechanism that can force deposition when river
beds reach a critical slope.

Conceptually::

    river approaches low / critical slope
                 |
                 v
       transport becomes insufficient
                 |
                 v
             deposition
                 |
                 v
        alluvial-plain aggradation

The amount of deposition is constrained by a percentage of the maximum
deposition that can occur without reversing the local slope.

This immediately raised an important question for my study:

   Is this formulation fundamentally the same kind of sediment conservation
   used in SPACE or FastScape, or is it a different mechanism designed to
   efficiently represent alluvial deposition within the broader Badlands
   framework?

This distinction is important and should be investigated directly from the
Badlands implementation rather than assuming that every use of the word
``deposition`` refers to the same physical formulation.

5.2 Marine deposition
~~~~~~~~~~~~~~~~~~~~~

Badlands also treats the marine environment separately from the terrestrial
fluvial system.

Once sediment reaches the marine environment, the river no longer transports
it in the same way as it does on land. Sediment can instead be deposited near
the shoreline and subsequently redistributed by marine processes.

The Badlands documentation describes a diffusion law for marine sediment and
additional parameters that allow sediment to be transported farther into the
marine domain.

Conceptually::

    terrestrial sediment
           |
           v
        shoreline
           |
           v
    initial marine deposition
           |
           v
    marine redistribution
           |
           v
    deeper-water deposition

This suggests that, in a basin-scale model, ``deposition`` should not be
treated as a single universal process.

There may be distinct formulations for:

* fluvial/alluvial deposition;
* coastal deposition;
* marine sediment redistribution; and
* deeper marine deposition.

This is one of the questions that should be followed carefully when comparing
Badlands with FastScape and Landlab.


6. SPACE: explicit bedrock and alluvial sediment evolution
----------------------------------------------------------

SPACE stands for **Stream Power with Alluvium Conservation and Entrainment**.

It represents another important development because it explicitly tracks two
major parts of the channel system:

* the bedrock surface; and
* the sediment/alluvial layer.

Conceptually::

        surface
    -----------------
        sediment
    =================
        bedrock
    -----------------

Let:

* :math:`R` = bedrock elevation;
* :math:`H` = sediment thickness; and
* :math:`\eta` = total surface elevation.

Then conceptually,

.. math::

   \eta = R + H.

This separation is extremely important for sedimentary-basin studies.

A model that tracks only :math:`\eta` cannot directly distinguish whether a
surface change occurred because:

* bedrock was eroded; or
* sediment was deposited.

SPACE explicitly separates these contributions.

6.1 Sediment conservation
~~~~~~~~~~~~~~~~~~~~~~~~~

SPACE explicitly considers sediment conservation in the water column and
channel bed.

Conceptually, sediment flux changes because of erosion, entrainment, and
deposition:

.. math::

   \frac{\partial Q_s}{\partial x}
   =
   E_s + E_r - D_s,

where:

* :math:`Q_s` is sediment flux;
* :math:`E_s` is sediment entrainment;
* :math:`E_r` is sediment generated by bedrock erosion; and
* :math:`D_s` is sediment deposition.

The exact governing formulation contains additional assumptions, but the
central idea is:

   sediment entering the transport system must be balanced by downstream
   transport, deposition, and other sinks.

6.2 Evolution of the alluvial layer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The sediment thickness evolves through the balance between deposition and
erosion/entrainment.

Conceptually,

.. math::

   \frac{\partial H}{\partial t}
   =
   \frac{D_s-E_s}{1-\phi},

where :math:`\phi` is sediment porosity.

Therefore::

    erosion > deposition
          |
          v
    sediment layer thins


    deposition > erosion
          |
          v
    sediment layer thickens

This is particularly relevant to a developing sedimentary basin.

6.3 Mixed bedrock--alluvial channels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SPACE naturally allows transitions among:

* bedrock channels;
* alluvial channels; and
* mixed bedrock--alluvial channels.

A rift basin does not consist of a permanently alluvial surface.

Instead, the landscape can evolve through::

    exposed bedrock
          |
          v
       erosion
          |
          v
    sediment production
          |
          v
    partial alluvial cover
          |
          v
       deposition
          |
          v
     thick sediment
          |
          v
      basin fill


7. Yuan et al. (2019): efficient solution of erosion--deposition equations
--------------------------------------------------------------------------

Yuan et al. (2019) are particularly important because they address the
computational difficulty of solving an erosion--deposition formulation
efficiently.

The important development is therefore not simply another deposition
parameterization.

It is the development of an efficient numerical solution to a physically
richer erosion--deposition system.

The method is designed to be:

* efficient;
* implicit; and
* suitable for relatively large time steps.

This is highly relevant to coupling with tectonic models.

A geodynamic simulation may require a large number of surface-process
updates. Therefore a sediment model needs not only a physically meaningful
formulation but also a computationally practical solution.

The conceptual development can be represented as::

    Davy & Lague
          |
          v
    erosion/deposition
    mass-conservation framework
          |
          v
    computational challenge
          |
          v
    Yuan et al. (2019)
          |
          v
    efficient numerical solution

Thus Yuan et al. should be viewed primarily as an important numerical
development of the erosion--deposition framework.


8. FastScape: efficient landscape evolution and sediment transport
------------------------------------------------------------------

FastScape is particularly interesting for the planned ASPECT coupling because
its design emphasizes computational efficiency and modularity.

FastScape consists of several layers of software.

At the high level, FastScape is closely connected to the Python scientific
ecosystem and uses Xarray-simlab as its modeling framework.

At the lower level, Fastscapelib provides efficient implementations of
landscape-evolution algorithms.

The software ecosystem can therefore be viewed conceptually as::

    Fastscape
       |
       +-- Xarray-simlab
       |
       +-- Python model components
       |
       +-- Fastscapelib
              |
              +-- efficient numerical algorithms
              |
              +-- Fortran / C++ implementations

This distinction is important when trying to locate the sediment-deposition
code.

The Python layer often defines the model structure, parameters, process
connections, and interface to the user.

The computationally intensive core algorithms may be implemented in lower-
level languages.

Therefore, when studying sediment deposition in FastScape, it is not enough
to look only at the high-level Python model definition.

The relevant process implementation may need to be traced through the Python
component into Fastscapelib.

8.1 The ``basic_model`` architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The FastScape ``basic_model`` demonstrates the modular structure clearly.

Conceptually, the model contains processes such as:

* grid;
* boundary conditions;
* tectonic uplift;
* initial topography;
* flow routing;
* drainage area;
* stream-power incision;
* hillslope diffusion;
* erosion;
* vertical motion; and
* topography.

A simplified representation is::

    grid
      |
      v
    boundary
      |
      v
    tectonics
      |
      v
    surface
      |
      +----------------+
      |                |
      v                v
    flow            diffusion
      |
      v
    drainage
      |
      v
    stream power
      |
      v
    erosion
      |
      v
    topography

This is an important conceptual connection to Landlab and Terrainbento:
processes are assembled into a larger model rather than being written as one
monolithic algorithm.

8.2 FastScape sediment model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FastScape also provides a ``sediment_model`` that extends the basic model.

The sediment model introduces processes representing:

* bedrock;
* an active sediment layer;
* sediment-aware stream-power incision and transport; and
* differential hillslope erosion/deposition.

Conceptually::

    basic landscape model
             |
             v
        + bedrock
             |
             + active sediment layer
             |
             + sediment transport
             |
             + deposition
             |
             v
       sediment-aware model

This is particularly relevant to the current ASPECT--Landlab work because it
demonstrates how a model can evolve from a basic erosion model into a model
that separately tracks bedrock and sediment.

8.3 FastScape marine model
~~~~~~~~~~~~~~~~~~~~~~~~~~

FastScape further extends the sediment model with a marine component.

Conceptually::

    sediment model
          |
          v
       sea level
          |
          v
    marine transport
          |
          v
    marine deposition
          |
          v
      stratigraphic /
      surface evolution

The important point is that the marine environment is represented through
additional processes rather than simply changing the fluvial deposition
coefficient.

This is similar to the observation from the Badlands study that terrestrial
and marine sediment redistribution can require different formulations.

8.4 FastScape language architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FastScape is not simply a Python-only model.

Its software architecture includes:

* Python for the high-level modeling framework;
* Xarray-simlab for process organization and model execution;
* lower-level numerical libraries for computationally intensive algorithms;
* Fortran implementations in Fastscapelib-Fortran; and
* newer C++ implementations in Fastscapelib.

This is important when studying the actual sediment-deposition implementation.

A useful strategy is therefore:

.. code-block:: text

    FastScape Python model
             |
             v
       model process
             |
             v
      process component
             |
             v
      Fastscapelib API
             |
             v
    numerical implementation
             |
             v
       Fortran / C++


9. Terrainbento: a framework for comparing landscape-evolution models
----------------------------------------------------------------------

Terrainbento 1.0, introduced by Barnhart et al. (2019), provides an important
perspective that is different from the process formulations discussed above.

Terrainbento is not primarily a new erosion or deposition equation.

Instead, it is a Python framework designed for **multi-model analysis of
long-term drainage-basin evolution**.

This distinction is important.

The earlier sections ask:

   How is sediment erosion, transport, and deposition mathematically
   represented?

Terrainbento asks a different question:

   How can different landscape-evolution model formulations be organized,
   executed, tested, compared, and analyzed within a common framework?

This makes Terrainbento particularly relevant to the software architecture
of the ASPECT--Landlab project.

9.1 Motivation
~~~~~~~~~~~~~~

Landscape-evolution models contain mathematical descriptions of processes
such as:

* hillslope transport;
* surface-water routing;
* fluvial erosion;
* sediment transport;
* and material properties.

There is generally more than one reasonable formulation for representing
these processes.

For example, hillslope transport can be represented with alternative
diffusion formulations. Hydrology and fluvial erosion can also be represented
using different assumptions.

Terrainbento addresses this problem by providing a common framework within
which different combinations of process formulations can be implemented and
compared.

The important idea is therefore not simply the individual equations used by
Terrainbento.

The important idea is the **framework architecture**.

9.2 Terrainbento and Landlab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Terrainbento is built on top of Landlab.

The relationship can be viewed conceptually as::

    Landlab
       |
       +-- grid and field infrastructure
       |
       +-- hydrology components
       +-- hillslope components
       +-- erosion components
       +-- other Earth-surface-process components
       |
       v
    Terrainbento
       |
       +-- common model infrastructure
       +-- boundary conditions
       +-- input/output
       +-- model configuration
       +-- process combinations
       +-- model comparison
       |
       v
    alternative landscape-evolution models

This architecture is particularly interesting because a process component can
be changed or substituted without rebuilding the entire modeling framework.

9.3 Multiple model formulations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Terrainbento was designed specifically to support multi-model analysis.

Instead of assuming that one landscape-evolution equation is universally
appropriate, different process formulations can be run under comparable
conditions.

This makes it possible to ask questions such as:

* How does the hillslope transport law affect topographic evolution?
* How does the hydrologic formulation affect drainage structure?
* How does the fluvial erosion law affect steady-state topography?
* How sensitive are predictions to uncertain process formulations?
* Which differences arise from model structure rather than parameter values?

This is an important methodological point for the sedimentation study.

A comparison should distinguish:

.. code-block:: text

    parameter change
          |
          v
    same physical formulation


from:

.. code-block:: text

    process change
          |
          v
    different physical formulation

The second type of comparison is often much more scientifically informative.

9.4 Terrainbento as a modular architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Terrainbento separates:

* common model infrastructure;
* process components; and
* model configuration.

The general structure can be represented as::

    common model infrastructure
              |
       +------+------+
       |             |
    process A     process B
       |             |
       +------+------+
              |
              v
        complete model

This is directly relevant to the design philosophy of the ASPECT--Landlab
framework.

9.5 Terrainbento and sediment modeling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Terrainbento should not be described as a sediment-deposition formulation
itself.

Its relevance to the current study is primarily architectural.

The individual Landlab components provide the process formulations, while
Terrainbento provides a framework for combining and comparing those
components.

Therefore, when studying sedimentation, it is useful to distinguish:

.. code-block:: text

    sediment physics
          |
          v
    Landlab component
          |
          v
    model framework
          |
          v
    Terrainbento

from:

.. code-block:: text

    sediment physics
          |
          v
    ASPECT--Landlab coupling
          |
          v
    tectonic + surface-process evolution


10. Terrainbento and ASPECT--Landlab
------------------------------------

The architecture of Terrainbento provides a useful conceptual precedent for
the ASPECT--Landlab framework.

The key similarity is the separation between:

* model infrastructure;
* process components; and
* experiment configuration.

In Terrainbento, Landlab provides Earth-surface-process components while
Terrainbento provides a higher-level framework for combining those
components.

In ASPECT--Landlab, this architecture can be extended by introducing a
three-dimensional geodynamic model.

The conceptual architecture becomes::

             ASPECT
               |
               | tectonic forcing
               | uplift / subsidence
               | deformation
               v
        coupling interface
               |
               v
             Landlab
               |
       +-------+-------+----------------+
       |               |                |
    hillslope       fluvial        deposition /
    transport       erosion        sediment transport
       |               |                |
       +---------------+----------------+
                       |
                       v
                 updated surface
                       |
                       v
                     ASPECT

This is a fundamental extension of the Terrainbento philosophy.

Terrainbento combines alternative surface-process models.

ASPECT--Landlab can combine surface processes with an independently computed
geodynamic evolution.

10.1 A major architectural lesson
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The coupling framework should avoid embedding every possible surface-process
formulation directly into the geodynamic model.

Instead, surface processes should remain modular wherever possible.

This would allow the same ASPECT simulation infrastructure to interact with
different Landlab surface-process formulations.

For example::

    ASPECT
       |
       v
    coupling interface
       |
       +--> diffusion
       |
       +--> fluvial erosion
       |
       +--> erosion + deposition
       |
       +--> sediment transport
       |
       +--> marine transport
       |
       +--> future grain-size model

This architecture makes it possible to compare alternative scientific
hypotheses without redesigning the entire geodynamic model.

10.2 Terrainbento versus ASPECT--Landlab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Terrainbento and ASPECT--Landlab
   :header-rows: 1
   :widths: 25 35 40

   * - Feature
     - Terrainbento
     - ASPECT--Landlab

   * - Primary purpose
     - Multi-model landscape-evolution analysis
     - Coupled geodynamics and surface-process modeling

   * - Core framework
     - Landlab + Terrainbento
     - ASPECT + Landlab

   * - Surface processes
     - Alternative formulations
     - Landlab components

   * - Geodynamics
     - Not the primary focus
     - ASPECT provides geodynamic evolution

   * - Model comparison
     - Central objective
     - Important possible application

   * - Coupling
     - Primarily surface-process model combinations
     - Exchange between geodynamics and surface processes

   * - Extensibility
     - New model programs and components
     - New surface processes and coupling variables


11. Testing philosophy: another important Terrainbento lesson
--------------------------------------------------------------

Terrainbento also emphasizes testing and reproducibility.

This is particularly important for ASPECT--Landlab because coupling introduces
additional numerical and software sources of error.

A useful testing hierarchy is:

.. list-table:: Testing hierarchy for ASPECT--Landlab
   :header-rows: 1
   :widths: 25 75

   * - Test level
     - Purpose

   * - Component test
     - Verify an individual Landlab surface-process component.

   * - Coupling-interface test
     - Verify transfer of topography, uplift, erosion, deposition, and other
       quantities between ASPECT and Landlab.

   * - Conservation test
     - Verify sediment volume or mass balance.

   * - Time-integration test
     - Determine how coupling time step and ``n_substeps`` affect the result.

   * - Benchmark test
     - Compare against analytical or established numerical solutions.

   * - End-to-end test
     - Verify a complete tectonic--surface-process experiment.

This is directly connected to the current ``n_substeps`` investigation.

Changing ``n_substeps`` does not necessarily change the analytical amount of
uplift applied over a total time interval. However, changing the frequency
with which processes interact can change the numerical solution through
operator splitting.

Therefore:

   coupling convergence must be distinguished from physical-model
   convergence.

This is an important principle for the future sediment-deposition module.


12. Common features among the LEMs
----------------------------------

Although the mathematical formulations differ, the following features are
common to most of the models.

.. list-table:: Common features
   :header-rows: 1
   :widths: 25 75

   * - Feature
     - Common characteristic

   * - Topographic evolution
     - Surface elevation changes through erosion, transport, deposition,
       and/or tectonic forcing.

   * - Fluvial transport
     - Rivers or drainage networks provide major pathways for sediment
       movement.

   * - Stream power
     - Many formulations retain a relationship between erosion, discharge or
       drainage area, and slope.

   * - Sediment flux
     - Sediment flux becomes increasingly important as models become more
       physically explicit.

   * - Transport limitation
     - Rivers cannot transport unlimited sediment.

   * - Deposition
     - Sediment can leave the transport system and become stored.

   * - Tectonic forcing
     - Several frameworks can be driven by uplift, subsidence, or deformation.

   * - Long timescales
     - The models are primarily intended for geological timescales.

   * - Reduced complexity
     - Detailed hydrodynamics are simplified to permit long-duration
       landscape simulations.

   * - Numerical efficiency
     - Efficient flow routing and process solvers are essential.


13. Major differences among the models
--------------------------------------

The most useful comparison is not simply:

   Which equation does the model use?

Instead ask:

#. Is sediment explicit?
#. Is sediment conserved?
#. Is sediment storage explicit?
#. Is deposition explicit?
#. Is transport capacity explicit?
#. Is bedrock distinguished from sediment?
#. Is marine transport included?
#. Is stratigraphy retained?
#. Can tectonic deformation be imposed?
#. Is the framework designed for efficient coupling?
#. Can alternative process formulations be substituted easily?

13.1 Major conceptual comparison
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table:: Major conceptual differences
   :header-rows: 1
   :widths: 20 16 16 16 16 16

   * - Model
     - Sediment role
     - Conservation
     - Sediment storage
     - Bedrock/alluvium
     - Main strength

   * - Gasparini & Brandon
     - Sediment modifies incision
     - Limited relative to later explicit routing models
     - Not primary focus
     - Not primary focus
     - Sediment-dependent incision and tool/cover behavior

   * - Davy & Lague
     - Explicit transported sediment
     - Yes
     - Through transport/deposition
     - Conceptually represented
     - Erosion--transport--deposition framework

   * - Badlands
     - Explicit sediment routing
     - Yes
     - Yes
     - Yes
     - Regional source-to-sink and stratigraphic evolution

   * - SPACE
     - Explicit sediment and alluvial layer
     - Yes
     - Explicit sediment thickness
     - Yes
     - Mixed bedrock--alluvial evolution

   * - Yuan et al.
     - Explicit erosion/deposition
     - Yes
     - Through erosion--deposition system
     - Compatible with sediment-aware formulations
     - Efficient numerical solution

   * - FastScape
     - Explicit sediment transport/deposition models
     - Yes
     - Sediment model available
     - Yes in sediment formulation
     - Computationally efficient landscape evolution

   * - Terrainbento
     - Depends on selected Landlab model
     - Depends on selected component/model
     - Depends on selected component/model
     - Depends on selected model
     - Multi-model organization, comparison, and testing


14. Deposition is not one universal process
-------------------------------------------

One of the most important lessons from studying Badlands, FastScape, SPACE,
and Landlab is that the word ``deposition`` can refer to several different
physical or numerical mechanisms.

14.1 Local deposition
~~~~~~~~~~~~~~~~~~~~

A simple model may calculate deposition from local conditions:

.. math::

   D = f(\text{local conditions}).

14.2 Supply versus transport capacity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A more general conceptual framework compares sediment supply with transport
capacity.

Let:

.. math::

   Q_s = \text{sediment supply}

and

.. math::

   Q_t = \text{transport capacity}.

Conceptually::

       Q_s < Q_t
          |
          v
      transport


       Q_s \approx Q_t
          |
          v
      near capacity


       Q_s > Q_t
          |
          v
      deposition

A useful diagnostic quantity is

.. math::

   \chi = \frac{Q_s}{Q_t}.

Interpretation:

.. list-table:: Sediment supply versus transport capacity
   :header-rows: 1
   :widths: 30 70

   * - Condition
     - Interpretation

   * - :math:`Q_s/Q_t \ll 1`
     - Transport capacity is much greater than supplied sediment.

   * - :math:`Q_s/Q_t \approx 1`
     - Sediment approaches transport capacity.

   * - :math:`Q_s/Q_t > 1`
     - Sediment supply exceeds transport capacity and deposition can occur.

However, this should not automatically be assumed to be the exact deposition
equation of every LEM.

The distinction between a supply-versus-capacity interpretation and an
explicit erosion--deposition mass balance must be investigated separately for
each implementation.

14.3 Terrestrial versus marine deposition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The study of Badlands and FastScape also suggests that ``deposition`` may
need to be separated into environmental regimes.

A useful conceptual division is::

    terrestrial
        |
        +--> hillslope deposition
        |
        +--> alluvial deposition
        |
        +--> fluvial deposition
        |
        v
    shoreline
        |
        +--> coastal deposition
        |
        +--> marine redistribution
        |
        v
    deeper marine deposition

This is important for basin studies because a sediment parcel may experience
different transport mechanisms as it moves from mountain source to marine
sink.


15. Why SPACE is particularly interesting for a rift-basin experiment
----------------------------------------------------------------------

For an ASPECT--Landlab rift experiment, SPACE has a particularly attractive
property:

   it separately evolves bedrock topography and sediment thickness.

This means that the model can distinguish:

.. code-block:: text

    tectonic subsidence
          |
          v
    accommodation creation
          |
          v
    sediment deposition
          |
          v
    alluvial thickness increases

from:

.. code-block:: text

    tectonic uplift
          |
          v
       erosion
          |
          v
    bedrock lowering

This distinction is scientifically valuable because a basin surface can rise
even while the underlying bedrock is being lowered, if sediment deposition
exceeds bedrock erosion.

That is exactly the type of distinction required for sedimentary-basin
evolution.


16. Why Badlands is particularly interesting for basin stratigraphy
-------------------------------------------------------------------

Badlands has a different strength.

Its major advantage is the broader source-to-sink framework.

It can connect:

.. code-block:: text

    tectonics
       |
       v
    landscape evolution
       |
       v
    erosion
       |
       v
    sediment routing
       |
       v
    coastal processes
       |
       v
    marine redistribution
       |
       v
    deposition
       |
       v
    stratigraphy

Therefore Badlands is particularly attractive when the scientific question is:

   How does tectonic forcing control the spatial and temporal architecture of
   sedimentary basins?

The ability to preserve depositional history makes the model particularly
interesting for stratigraphic questions.


17. Why FastScape is particularly interesting for geodynamic coupling
----------------------------------------------------------------------

FastScape has a different advantage.

Its major strength is computational efficiency.

For a geodynamic model, the coupling can be represented as::

    ASPECT timestep
          |
          v
    tectonic deformation
          |
          v
    transfer surface information
          |
          v
    FastScape
          |
          +--> erosion
          |
          +--> sediment transport
          |
          +--> deposition
          |
          v
    updated surface
          |
          v
    transfer back to ASPECT

The efficiency of the surface-process solver therefore becomes part of the
overall coupling problem.

This makes FastScape particularly relevant as a computational comparison for
the ASPECT--Landlab framework.


18. Why Terrainbento matters for the research strategy
-------------------------------------------------------

Terrainbento adds another dimension to the comparison.

Badlands, SPACE, and FastScape primarily help answer:

   How should the landscape and sedimentary system be modeled?

Terrainbento additionally helps answer:

   How can different model formulations be organized and compared
   systematically?

This is useful because the ASPECT--Landlab project may eventually contain
multiple possible sediment formulations.

For example::

    ASPECT
       |
       v
    coupling interface
       |
       v
    Landlab
       |
       +--> simple diffusion
       |
       +--> stream power
       |
       +--> SPACE-like sediment formulation
       |
       +--> FastScape-like formulation
       |
       +--> marine sediment component
       |
       +--> grain-size evolution
       |
       v
    comparison framework

The Terrainbento philosophy suggests that these alternatives should be
treated as modular hypotheses rather than permanently embedded into one
monolithic model.


19. What is best for studying a rift-setting sedimentary basin?
---------------------------------------------------------------

There is no single best model for every part of the problem.

The answer depends on the scientific question.

19.1 Best for understanding sediment erosion and deposition physics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Davy & Lague + SPACE**

These provide a strong conceptual foundation for understanding:

* sediment conservation;
* erosion;
* entrainment;
* deposition;
* sediment flux;
* transport;
* alluvial storage; and
* bedrock/alluvial transitions.

19.2 Best for basin-scale source-to-sink and stratigraphic evolution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Badlands**

Badlands is particularly attractive when the primary outputs are:

* basin stratigraphy;
* depositional architecture;
* shoreline migration;
* source-to-sink routing;
* marine redistribution;
* accommodation; and
* tectonically controlled sedimentary architecture.

19.3 Best for efficient geodynamic coupling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**FastScape / FastScapeLib**

FastScape is particularly attractive when the study requires many coupled
simulations and the surface-process calculation must remain computationally
efficient.

19.4 Best for comparing alternative formulations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Terrainbento / Landlab**

Terrainbento is especially useful as a conceptual and software framework for
comparing alternative surface-process formulations.

Its value is not that it provides one superior sediment equation. Its value
is that it demonstrates how different model structures can be assembled,
tested, and compared within a common framework.

19.5 Best combination for ASPECT--Landlab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the particular ASPECT--Landlab rift-basin problem, I would conceptually
place:

* **SPACE** at the center of the sediment-physics investigation;
* **Davy & Lague** as an important conceptual foundation;
* **Yuan et al. (2019)** as an important numerical-development reference;
* **FastScape** as an important computational and coupling comparison;
* **Badlands** as a source-to-sink and stratigraphic comparison; and
* **Terrainbento** as a modular model-comparison and software-architecture
  precedent.


20. Proposed staged development for ASPECT--Landlab
---------------------------------------------------

Rather than immediately implementing the most complicated sediment model, a
staged development would be scientifically stronger.

20.1 Stage 1: simple stream-power erosion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start with

.. math::

   E = K A^m S^n.

Purpose:

* verify ASPECT--Landlab coupling;
* verify erosion;
* establish a baseline.

20.2 Stage 2: add deposition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Introduce an erosion--deposition formulation.

Purpose:

* verify sediment mass balance;
* measure sediment volume;
* compare erosion and deposition;
* test basin filling.

20.3 Stage 3: explicit sediment thickness
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Introduce

.. math::

   H_s(x,y,t).

Then conceptually,

.. math::

   h = R + H_s.

Purpose:

* distinguish bedrock erosion from sediment deposition;
* quantify basin fill;
* track sediment residence and storage.

20.4 Stage 4: add transport capacity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Introduce

.. math::

   Q_s
   \quad\text{and}\quad
   Q_t.

Then analyze

.. math::

   \frac{Q_s}{Q_t}.

Purpose:

* distinguish detachment-limited and transport-limited regions;
* identify depositional zones;
* investigate sediment starvation versus sediment excess.

20.5 Stage 5: add tectonic subsidence and uplift
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ASPECT to generate spatially and temporally varying:

* uplift;
* subsidence;
* faulting; and
* deformation.

Then investigate:

.. code-block:: text

    tectonic accommodation
             +
    sediment supply
             |
             v
       basin filling

20.6 Stage 6: add sediment-loading feedback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The next level is particularly interesting for geodynamic coupling.

Conceptually::

    deposition
        |
        v
    sediment thickness
        |
        v
    surface load
        |
        v
    geodynamic response
        |
        v
    subsidence / deformation
        |
        v
    accommodation
        |
        v
    deposition

This creates a genuine two-way geodynamic--surface-process feedback.


21. Why the rift setting is scientifically powerful
---------------------------------------------------

A rift provides a natural environment in which the major processes are
strongly coupled.

The conceptual system is::

                      EXTENSION
                          |
              +-----------+-----------+
              |                       |
              v                       v
           uplift                 subsidence
              |                       |
              v                       v
           erosion               accommodation
              |                       |
              +-----------+-----------+
                          |
                          v
                    sediment supply
                          |
                          v
                    fluvial transport
                          |
                          v
                      deposition
                          |
                          v
                    basin filling
                          |
                          v
                   sediment loading
                          |
                          v
                  geodynamic response

This is much richer than a conventional landscape-evolution experiment
because the basin is not merely a passive sink.

The basin geometry itself evolves because of tectonic deformation, while
sedimentation changes the evolving surface and potentially the mechanical
loading.


22. Important variables for the rift experiment
------------------------------------------------

I would track at least the following fields.

Topographic surface:

.. math::

   h(x,y,t)

Bedrock surface:

.. math::

   R(x,y,t)

Sediment thickness:

.. math::

   H_s(x,y,t)

Sediment flux:

.. math::

   Q_s(x,y,t)

Transport capacity:

.. math::

   Q_t(x,y,t)

Sedimentation rate:

.. math::

   D(x,y,t)

Erosion rate:

.. math::

   E(x,y,t)

Tectonic velocity:

.. math::

   \mathbf{u}_{tect}(x,y,z,t)

Accommodation:

.. math::

   A_c(x,y,t)

These variables allow the experiment to move from asking:

   How much erosion occurs?

toward:

   How does tectonic deformation control sediment production, routing,
   storage, and basin architecture?


23. A common comparison framework for every LEM
-----------------------------------------------

For the literature study, I would use the same questions for every model.

.. list-table:: LEM comparison framework
   :header-rows: 1
   :widths: 35 65

   * - Question
     - What to determine

   * - What is the erosion law?
     - Stream power, sediment-dependent erosion, or another formulation.

   * - What is sediment supply?
     - How is :math:`Q_s` generated?

   * - What is transport capacity?
     - How is :math:`Q_t` defined?

   * - Is sediment explicitly conserved?
     - Identify the governing mass-balance equation.

   * - Is deposition explicit?
     - Determine whether :math:`D_s` is calculated directly.

   * - Is deposition a flux divergence?
     - Determine whether deposition emerges from spatial changes in sediment
       flux.

   * - Is sediment thickness tracked?
     - Determine whether an explicit :math:`H_s` exists.

   * - Is bedrock separated from sediment?
     - Determine whether :math:`R` and :math:`H_s` evolve independently.

   * - Is sediment able to modify erosion?
     - Identify tool and cover effects.

   * - How is sediment routed?
     - SFD, MFD, D8, TIN-based routing, or another approach.

   * - Is marine transport included?
     - Important for coastal and basin-scale studies.

   * - Is stratigraphy retained?
     - Determine whether depositional history can be reconstructed.

   * - How is tectonics imposed?
     - Uplift, subsidence, displacement, deformation maps, etc.

   * - How computationally expensive is it?
     - Important for repeated geodynamic coupling.

   * - Is the framework modular?
     - Determine whether alternative process components can be substituted.

   * - Can it couple to a 3-D geodynamic model?
     - Important for ASPECT integration.


24. The evolution of LEM thinking
--------------------------------

The literature can now be organized as a conceptual sequence.

.. code-block:: text

    GASPARINI & BRANDON
    -------------------
    Sediment modifies erosion
             |
             v
    DAVY & LAGUE
    ------------
    Sediment is explicitly transported
    and erosion/deposition are coupled
             |
             v
    SPACE
    -----
    Sediment conservation
    +
    explicit alluvial thickness
    +
    bedrock/alluvial transition
             |
             v
    YUAN ET AL.
    -----------
    Efficient numerical solution
    of the erosion--deposition system
             |
             v
    FASTSCAPE
    ---------
    Efficient landscape evolution
    +
    sediment transport/deposition
    +
    tectonic coupling
             |
             v
    BADLANDS
    --------
    Regional source-to-sink evolution
    +
    tectonics
    +
    marine transport
    +
    stratigraphy
             |
             v
    TERRAINBENTO
    ------------
    Modular multi-model organization
    +
    comparison
    +
    testing
             |
             v
    ASPECT--LANDLAB
    ---------------
    Geodynamics
    +
    modular surface processes
    +
    coupling
    +
    future sediment feedbacks

The order should not be interpreted as a strict historical ranking of
``better`` and ``worse`` models.

Each framework emphasizes a different aspect of the larger sediment-routing
problem.


25. What Terrainbento adds to this evolution
--------------------------------------------

Terrainbento is conceptually different from the other entries in the
sequence.

The process-model evolution asks:

   What physical processes should be represented?

Terrainbento adds another question:

   How should alternative process formulations be organized and compared?

This is an important shift from a purely equation-centered view of LEMs
toward a **model-framework-centered view**.

The progression can therefore be expressed in two dimensions.

Physical development::

    erosion
       |
       v
    sediment transport
       |
       v
    deposition
       |
       v
    sediment storage
       |
       v
    stratigraphy
       |
       v
    geodynamic feedback

Software development::

    individual formulation
       |
       v
    modular process components
       |
       v
    reusable model framework
       |
       v
    multi-model comparison
       |
       v
    coupled geodynamic framework

The ASPECT--Landlab project sits at the intersection of these two developments.


26. Implications for future sediment modeling
---------------------------------------------

The modular philosophy demonstrated by Terrainbento is particularly relevant
to extending ASPECT--Landlab beyond simple erosion and diffusion.

A future sediment module could be represented as an independent process
layer::

    ASPECT
       |
       | tectonic deformation
       v
    topographic surface
       |
       v
    erosion
       |
       v
    sediment transport
       |
       +----> grain-size evolution
       |
       +----> deposition
       |
       +----> sediment thickness
       |
       v
    surface loading
       |
       v
    ASPECT

This allows sediment transport and deposition to become additional components
of the coupled system rather than requiring a complete redesign of the
ASPECT--Landlab interface.

27. Future grain-size evolution
--------------------------------

A natural extension of the sediment model is to introduce grain size as an
additional state variable.

For example,

.. math::

   D_g(x,y,t)

could represent characteristic grain size, or

.. math::

   f(d,x,y,t)

could represent a grain-size distribution.

The conceptual system then becomes::

    tectonics
       |
       v
    erosion
       |
       v
    sediment production
       |
       v
    grain-size sorting
       |
       v
    sediment transport
       |
       v
    deposition
       |
       v
    grain-size evolution
       |
       v
    stratigraphy
       |
       v
    sediment loading
       |
       v
    geodynamic response

This would move the project beyond a conventional LEM coupling toward a
fully coupled tectonic--erosional--sedimentary system.


28. Research opportunity for ASPECT--Landlab
--------------------------------------------

The strongest research opportunity is therefore not simply to reproduce
SPACE, Badlands, or FastScape inside ASPECT.

Instead, the opportunity is to combine their most useful conceptual features
within a two-way geodynamic--surface-process framework.

A possible long-term architecture is::

                         ASPECT
                           |
                 tectonic deformation
                           |
                           v
                    evolving surface
                           |
                           v
                       Landlab
                           |
              +------------+------------+
              |            |            |
              v            v            v
           erosion     transport     deposition
              |            |            |
              +------------+------------+
                           |
                           v
                    sediment thickness
                           |
                           v
                     basin geometry
                           |
                           v
                     sediment load
                           |
                           v
                         ASPECT

The resulting system would allow investigation of questions such as:

* How does fault-controlled uplift alter sediment production?
* How does subsidence alter accommodation?
* How does sediment supply influence basin filling?
* How does transport capacity determine where deposition occurs?
* How long does sediment remain stored in the basin?
* How does sediment thickness evolve through time?
* How does sediment loading modify the geodynamic system?
* How does grain size evolve during transport?
* How does the resulting stratigraphy record tectonic forcing?


29. Final interpretation
------------------------

The common feature among these LEMs is that they all attempt to describe
Earth-surface evolution under combinations of erosion, transport, deposition,
and tectonic forcing.

The major difference is **how explicitly they represent sediment**.

The progression can therefore be summarized as::

    sediment as a consequence
             |
             v
    sediment as a control
             |
             v
    sediment as a transported quantity
             |
             v
    sediment as a conserved quantity
             |
             v
    sediment as an explicit reservoir
             |
             v
    sediment as a stratigraphic archive
             |
             v
    sediment as part of a two-way
    geodynamic feedback

This gives a more useful framework than simply comparing deposition
coefficients or stream-power exponents.

For the Strat/LEM study, the important questions are therefore:

* What sediment does the model know about?
* Where is that sediment stored?
* How is it transported?
* What determines deposition?
* Is sediment mass conserved?
* Does sediment modify erosion?
* Is sediment thickness explicitly tracked?
* Can the model distinguish bedrock from alluvium?
* Can the model preserve stratigraphic history?
* Are terrestrial and marine deposition treated differently?
* How does tectonic deformation alter sediment routing?
* How does sedimentation feed back on the evolving basin?
* How computationally efficient is the implementation?
* Can different process formulations be exchanged and compared?

The resulting conceptual map is:

.. code-block:: text

    PROCESS PHYSICS
         |
         +--> erosion
         +--> transport
         +--> deposition
         +--> sediment storage
         +--> marine redistribution
         |
         v
    MODEL FORMULATION
         |
         +--> Gasparini & Brandon
         +--> Davy & Lague
         +--> SPACE
         +--> Yuan et al.
         +--> FastScape
         +--> Badlands
         |
         v
    MODEL FRAMEWORK
         |
         +--> Landlab
         +--> Terrainbento
         |
         v
    GEODYNAMIC COUPLING
         |
         +--> ASPECT
         |
         v
    TECTONIC--SURFACE--SEDIMENTARY SYSTEM
         |
         v
    RIFT BASIN
         |
         +--> uplift
         +--> subsidence
         +--> erosion
         +--> sediment transport
         +--> deposition
         +--> basin filling
         +--> sediment loading
         +--> stratigraphy


30. Main takeaway for the ASPECT--Landlab project
-------------------------------------------------

The most important lesson from this study is that the question should not be:

   ``Which deposition equation should I implement?``

A better sequence of questions is:

#. What physical sediment process do I want to represent?
#. Is sediment supply explicitly represented?
#. Is transport capacity explicitly represented?
#. Is sediment conserved?
#. Where can sediment be stored?
#. Is bedrock distinguished from alluvium?
#. How does deposition alter sediment thickness?
#. Does the model distinguish terrestrial and marine environments?
#. Do I need stratigraphic memory?
#. How frequently must the surface process model communicate with ASPECT?
#. How computationally expensive can the formulation be?
#. Can the formulation remain modular enough to compare alternative models?

For the current ASPECT--Landlab development, the most promising conceptual
combination is therefore:

.. code-block:: text

    Davy & Lague
         |
         | sediment conservation
         v
       SPACE
         |
         | explicit sediment thickness
         | bedrock/alluvial evolution
         v
      Landlab
         |
         | modular surface processes
         v
      ASPECT
         |
         | tectonic deformation
         | uplift / subsidence / faulting
         v
    rift basin
         |
         v
    sedimentation
         |
         v
    basin architecture

FastScape provides an important computational and coupling comparison.

Badlands provides an important source-to-sink, marine, and stratigraphic
comparison.

Terrainbento provides an important modular-framework and multi-model
comparison precedent.

Together, these models suggest a long-term direction in which the
ASPECT--Landlab project is not merely a coupling of two existing codes, but a
framework in which different surface-process hypotheses can be tested against
different tectonic scenarios.

.. note::

   The central research opportunity is to move from a one-way workflow,

   ``ASPECT -> surface evolution``,

   toward a physically interpretable sedimentary feedback system,

   ``ASPECT -> erosion -> sediment transport -> deposition -> sediment
   loading -> ASPECT``.

   This provides a natural framework for studying rift-basin development,
   sediment routing, basin filling, stratigraphic architecture, and
   eventually grain-size-dependent sediment evolution.


.. seealso::

   Barnhart, K. R., Glade, R. C., Shobe, C. M., and Tucker, G. E. (2019).
   ``Terrainbento 1.0: a Python package for multi-model analysis in
   long-term drainage basin evolution``.
   *Geoscientific Model Development*, 12, 1267--1297.
   DOI: ``10.5194/gmd-12-1267-2019``.

   Davy, P., and Lague, D. (2009).
   ``Fluvial erosion/transport equation of landscape evolution models:
   Linear approach to a non-linear problem``.
   *Journal of Geophysical Research: Earth Surface*.

   Yuan, X. P., Braun, J., Guerit, L., Rouby, D., and Cordonnier, G. (2019).
   ``A new efficient method to solve the stream power law model taking into
   account sediment deposition``.
   *Journal of Geophysical Research: Earth Surface*, 124, 1346--1365.
   DOI: ``10.1029/2018JF004867``.

   Braun, J., and Willett, S. D. (2013).
   ``A very efficient O(n), implicit and parallel method to solve the stream
   power equation governing fluvial incision and landscape evolution``.
   *Geomorphology*, 170--179.
   DOI: ``10.1016/j.geomorph.2012.10.008``.

   `Badlands documentation: Simulated Processes
   <https://badlands.readthedocs.io/en/latest/proc.html>`__.

   `FastScape documentation <https://fastscape.org/>`__.

   `Terrainbento 1.0 paper
   <https://doi.org/10.5194/gmd-12-1267-2019>`__.