August 13, 2026 – Badlands (Day 3): Deposition Processes and Exploring Fastscape and landlab_vis Documentation (Day 6)
=======================================================================================================================

Study focus
-----------

Today I continued studying Badlands, with particular attention to the
question of **how sediment deposition is implemented** in landscape-evolution
models.

After studying the Badlands documentation on alluvial and marine deposition,
I started comparing the conceptual framework with **Fastscape** and
**Landlab**.

The main focus of today's study was:

   **Understanding how different landscape-evolution models represent
   erosion, sediment transport, alluvial deposition, marine deposition,
   sediment storage, and the transition from terrestrial to marine
   environments.**

A second major focus was understanding the **software architecture of
Fastscape**, particularly where the sediment-deposition code is located and
how Python, Fastscapelib, C++, and the older Fortran implementation are
related.

The main question that emerged is:

   Where exactly is sediment deposition calculated in Fastscape, what
   variables store the deposited sediment, and how does the implementation
   differ between the terrestrial/fluvial and marine environments?

Fastscape software architecture
-------------------------------

I examined the Fastscape documentation and the ``fastscape.models``
implementation.

The first important observation was that Fastscape is not a single
monolithic code written entirely in one programming language.

Instead, it is a collection of modular components built around the
Xarray-simlab framework.

The general architecture can be thought of as:

.. code-block:: text

                    FASTSCAPE
                       |
              Python / xarray-simlab
                       |
        +--------------+--------------+
        |                             |
    model/processes              model setup
        |
        v
    Fastscapelib
        |
        +-- current C++ / Python implementation
        |
        +-- older Fortran / Python implementation

The Fastscape documentation describes Fastscape as a flexible and modular
landscape-evolution modeling framework that is highly connected to the
Python scientific ecosystem through Xarray-simlab.

Fastscape provides many reusable components that can be combined to create
different landscape-evolution models.

The lower-level Fastscapelib libraries provide efficient implementations of
core landscape-evolution algorithms.

This distinction is important because a Python class visible in the Fastscape
model does not necessarily mean that the complete numerical computation is
performed in Python.

A Python process can provide the high-level model interface while delegating
computationally intensive operations to a lower-level library.

Fastscape and Xarray-simlab
---------------------------

I examined:

.. code-block:: python

   from fastscape.models import basic_model

   basic_model

The output showed:

.. code-block:: text

   <xsimlab.Model (16 processes, 12 inputs)>

This helped clarify that ``basic_model`` is an **xsimlab model composed of
multiple processes**.

The model output included processes such as:

.. code-block:: text

   grid
   boundary
   fs_context
   uplift
   tectonics
   init_topography
   surf2erode
   diffusion
   init_erosion
   flow
   drainage
   spl
   erosion
   vmotion
   topography
   terrain

The important realization is that these are not simply Python variables.
They represent individual processes that make up the landscape-evolution
model.

For example:

.. code-block:: text

   spl
       |
       +-- k_coef
       +-- area_exp
       +-- slope_exp
       +-- tol_rel
       +-- tol_abs
       +-- max_iter

The ``spl`` process corresponds to the ``StreamPowerChannel`` component in
the basic model.

The ``[in]`` notation in the xsimlab model description indicates an input
variable required by that process.

For example:

.. code-block:: text

   uplift
       rate [in]

means that the uplift process receives an uplift-rate input.

The model therefore provides a structured way of connecting processes and
their input/output variables.

Fastscape model hierarchy
--------------------------

The source code revealed an especially useful hierarchy of Fastscape models.

The models are constructed progressively:

.. code-block:: text

   bootstrap_model
          |
          v
     basic_model
          |
          v
    sediment_model
          |
          v
     marine_model

These are not three completely independent models.

Instead, each model is constructed by extending the previous model.

``bootstrap_model``
~~~~~~~~~~~~~~~~~~~

The ``bootstrap_model`` is described as the minimal skeleton required for
simulating the evolution of a topographic surface on a two-dimensional
uniform grid.

Its processes include:

.. code-block:: python

   bootstrap_model = xs.Model(
       {
           "grid": RasterGrid2D,
           "fs_context": FastscapelibContext,
           "boundary": BorderBoundary,
           "tectonics": TectonicForcing,
           "surf2erode": SurfaceToErode,
           "erosion": TotalErosion,
           "vmotion": TotalVerticalMotion,
           "topography": SurfaceTopography,
       }
   )

It does not yet contain the complete set of processes needed for a standard
landscape-evolution experiment.

It is therefore useful to think of it as the **model skeleton**.

``basic_model``
~~~~~~~~~~~~~~~

The ``basic_model`` is created by extending the bootstrap model:

.. code-block:: python

   basic_model = bootstrap_model.update_processes(
       {
           "uplift": BlockUplift,
           "surf2erode": SurfaceAfterTectonics,
           "flow": SingleFlowRouter,
           "drainage": DrainageArea,
           "spl": StreamPowerChannel,
           "diffusion": LinearDiffusion,
           "terrain": TerrainDerivatives,
           "init_topography": FlatSurface,
           "init_erosion": NoErosionHistory,
       }
   )

The documentation describes this as a standard landscape-evolution model
containing:

* block uplift;
* bedrock channel erosion using the stream-power law;
* hillslope erosion/deposition using linear diffusion;
* D8 single-flow-direction routing;
* drainage-area calculation; and
* initially flat topography with random perturbations.

Conceptually:

.. code-block:: text

   basic_model
       |
       +-- tectonics
       |      |
       |      +-- block uplift
       |
       +-- flow
       |      |
       |      +-- SingleFlowRouter
       |
       +-- drainage
       |
       +-- spl
       |      |
       |      +-- StreamPowerChannel
       |
       +-- diffusion
       |
       +-- topography
       |
       +-- terrain

The ``spl`` process is therefore the basic bedrock channel-incision
component.

``sediment_model``
~~~~~~~~~~~~~~~~~~

The next level is:

.. code-block:: python

   sediment_model = basic_model.update_processes(
       {
           "bedrock": Bedrock,
           "active_layer": UniformSedimentLayer,
           "init_bedrock": BareRockSurface,
           "flow": MultipleFlowRouter,
           "spl": DifferentialStreamPowerChannelTD,
           "diffusion": DifferentialLinearDiffusion,
       }
   )

This is particularly important for the deposition investigation.

The source description states that ``sediment_model`` tracks the evolution of
both the topographic surface and the bedrock, separated by a uniform active
layer of sediment.

The model therefore introduces an explicit distinction between:

.. code-block:: text

       topographic surface
       -------------------
       active sediment layer
       ===================
       bedrock
       ###################

This is an important conceptual difference from the simpler ``basic_model``.

The sediment model introduces:

* ``Bedrock``;
* ``UniformSedimentLayer``;
* ``DifferentialStreamPowerChannelTD``;
* ``DifferentialLinearDiffusion``; and
* ``MultipleFlowRouter``.

The change from ``SingleFlowRouter`` to ``MultipleFlowRouter`` is also
important.

The model therefore changes from:

.. code-block:: text

   basic_model
       |
       +-- SingleFlowRouter
       +-- StreamPowerChannel

to:

.. code-block:: text

   sediment_model
       |
       +-- MultipleFlowRouter
       +-- DifferentialStreamPowerChannelTD

Fastscape ``spl`` process
-------------------------

In the basic model, the stream-power component is:

.. code-block:: python

   "spl": StreamPowerChannel

In the sediment model, this is replaced by:

.. code-block:: python

   "spl": DifferentialStreamPowerChannelTD

Therefore:

.. code-block:: text

   basic_model
       |
       +-- StreamPowerChannel
       |
       +-- bedrock channel incision


   sediment_model
       |
       +-- DifferentialStreamPowerChannelTD
       |
       +-- bedrock + sediment
       +-- erosion + transport/deposition

The word **Differential** is particularly interesting.

The model description indicates that different erosion and transport
coefficients can be used for:

* bedrock; and
* soil/sediment.

This means that sediment is not simply treated as the same material as the
underlying bedrock.

Conceptually:

.. code-block:: text

   BEDROCK
      |
      +-- bedrock erosion coefficient
      |
      v
   sediment production
      |
      v
   SEDIMENT
      |
      +-- sediment transport/deposition coefficient

This is one of the places I want to investigate in detail because it may
provide the direct connection between the stream-power equation and
sediment deposition.

Fastscape ``UniformSedimentLayer``
----------------------------------

The sediment model also introduces:

.. code-block:: python

   "active_layer": UniformSedimentLayer

This means that Fastscape explicitly represents an active sediment layer.

This raises an important question:

   Where exactly is sediment thickness stored, and how is the active sediment
   layer updated when erosion or deposition occurs?

The important distinction is therefore between:

.. code-block:: text

   sediment transport
          |
          v
   sediment flux
          |
          v
   sediment deposition
          |
          v
   sediment storage
          |
          v
   active sediment layer

I want to trace this chain directly through the Fastscape source code.

This is more informative than looking only for a function called
``deposition``.

The key question is:

   **What state variable represents the sediment that has actually been
   deposited?**

Fastscape ``marine_model``
--------------------------

The third level is:

.. code-block:: python

   marine_model = sediment_model.update_processes(
       {
           "init_topography": Escarpment,
           "uplift": TwoBlocksUplift,
           "sea": Sea,
           "marine": MarineSedimentTransport,
           "strati": StratigraphicHorizons,
       }
   )

This is particularly important for the question that emerged during the
second day of Badlands reading.

The marine model explicitly adds:

.. code-block:: text

   Sea
   MarineSedimentTransport
   StratigraphicHorizons

Therefore Fastscape does not simply take the terrestrial sediment model and
continue it into the marine domain.

Instead, it explicitly adds a **marine sediment transport process**.

Conceptually:

.. code-block:: text

                    marine_model
                         |
             +-----------+-----------+
             |                       |
       sediment_model          marine processes
             |                       |
       +-----+-----+           +-----+-------+
       |           |           |             |
    bedrock    sediment       sea         marine
                layer        level       transport
                                             |
                                             v
                                        stratigraphy

This strongly supports the idea that Fastscape distinguishes between
terrestrial/fluvial sediment processes and marine sediment processes at the
model-architecture level.

However, the architecture alone does not establish that the governing
equations are fundamentally different. The actual equations and source code
still need to be traced.

Fastscape marine parameters
---------------------------

The Fastscape parameter file I examined also contains:

.. code-block:: text

   set Use marine component = false

and a separate marine-parameter subsection:

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

This provides another indication that the marine system has its own
parameters and its own process.

The terrestrial sediment model also contains separate parameters such as:

.. code-block:: text

   set Bedrock deposition coefficient   = 1
   set Sediment deposition coefficient = 1

   set Bedrock river incision rate      = 1e-5
   set Sediment river incision rate     = 1e-5

   set Bedrock diffusivity              = 1e-2
   set Sediment diffusivity             = 1e-2

This made me interested in determining exactly how the following processes
are connected:

.. code-block:: text

   bedrock erosion
          |
          v
   sediment production
          |
          v
   sediment transport
          |
          v
   terrestrial deposition
          |
          v
   coastal delivery
          |
          v
   marine transport
          |
          v
   marine deposition
          |
          v
   stratigraphic accumulation

Comparison with Landlab
-----------------------

I also compared this Fastscape architecture with the Landlab implementation
I have been studying.

Two relevant Landlab components are:

.. code-block:: text

   ErosionDeposition
          |
          +-- fluvial erosion/deposition


   SimpleSubmarineDiffuser
          |
          +-- marine sediment redistribution

These appear to represent different environments and different numerical
processes.

Landlab ``ErosionDeposition``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``ErosionDeposition`` component uses an erosion/deposition formulation
associated with Davy and Lague (2009).

The implementation involves sediment influx, erosion, and deposition.

The source contains the conceptual relationship:

.. math::

   E = K q^{m_{sp}} S^{n_{sp}} - \omega.

The deposition rate is then calculated from sediment flux and an effective
settling velocity.

The implementation contains:

.. code-block:: python

   self._depo_rate[positive_q] = self._qs[positive_q] * (
       v_s[positive_q] / self._q[positive_q]
   )

and the surface is updated using the difference between deposition and
erosion:

.. code-block:: python

   dzdt = self._depo_rate - self._erosion_term
   self._topographic__elevation[cores] += dzdt[cores] * dt

This makes the erosion/deposition balance explicit.

Landlab ``SimpleSubmarineDiffuser``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The marine component is different.

The ``SimpleSubmarineDiffuser`` class is described as transporting marine
sediment using a **water-depth-dependent diffusion model**.

The diffusion coefficient is:

.. math::

   D(h) = D_0 f_1(h) f_2(h).

The first function describes the reduction in transport efficiency below
the wave base:

.. math::

   f_1(h) =
   \exp\left(-\frac{h-h_w}{h_w}\right)

for water depths greater than the wave-base depth.

The second function describes the transition around sea level:

.. math::

   f_2(h)
   =
   \frac{\tanh(-h/R_t)+1}{2}.

The component calculates water depth from sea level and topographic
elevation:

.. code-block:: python

   self._depth[:] = (
       sea_level
       - self._grid.at_node["topographic__elevation"]
   )

The diffusion coefficient is then calculated as a function of water depth:

.. code-block:: python

   k[:] = self._shallow_water_diffusivity * self.depth_function(self._depth)

The component subsequently uses the inherited diffusion process:

.. code-block:: python

   super().run_one_step(dt)

and records the change in topographic elevation as deposition or erosion:

.. code-block:: python

   depo[:] = (
       self.grid.at_node["topographic__elevation"] - z_before
   )

This gives a useful conceptual distinction:

.. code-block:: text

   LANDLAB FLUVIAL
   ----------------

   ErosionDeposition
        |
        +-- sediment flux
        +-- erosion
        +-- deposition
        +-- surface change


   LANDLAB MARINE
   --------------

   SimpleSubmarineDiffuser
        |
        +-- water depth
        +-- depth-dependent diffusivity
        +-- marine redistribution
        +-- surface change

This is one of the reasons I do not want to treat "deposition" as one
universal process when comparing landscape-evolution models.

Badlands, Fastscape, and Landlab
--------------------------------

The observations from the last several days are beginning to produce a
three-way conceptual comparison.

.. list-table:: Preliminary comparison of sediment and depositional processes
   :header-rows: 1
   :widths: 18 28 27 27

   * - Model
     - Terrestrial / fluvial process
     - Sediment representation
     - Marine process

   * - Badlands
     - Stream-power incision, sediment transport, and alluvial forced
       deposition
     - Sediment flux and depositional processes
     - Marine deposition and sediment diffusion / redistribution

   * - Fastscape
     - ``DifferentialStreamPowerChannelTD``
     - ``UniformSedimentLayer`` and differential bedrock/sediment processes
     - ``MarineSedimentTransport``

   * - Landlab
     - ``ErosionDeposition``
     - Sediment flux, erosion/deposition, and surface change
     - ``SimpleSubmarineDiffuser``

This comparison is preliminary.

I still need to inspect the actual equations and source code before deciding
whether the three models are mathematically equivalent, partially
equivalent, or fundamentally different.

The most important lesson is that the **software architecture already
reveals meaningful differences in how each model organizes the processes**.

Where to find Fastscape sediment-deposition code
------------------------------------------------

The next practical question was:

   **Where exactly is the sediment-deposition code in Fastscape?**

The first place to look is the Python process:

.. code-block:: python

   DifferentialStreamPowerChannelTD

This is the process used by ``sediment_model``:

.. code-block:: python

   "spl": DifferentialStreamPowerChannelTD

Therefore, the first source file to investigate is the Fastscape channel
process implementation.

The installed package can be located using:

.. code-block:: bash

   python -c "import fastscape; print(fastscape.__file__)"

The channel module can then be located using:

.. code-block:: bash

   python -c "import fastscape.processes.channel as c; print(c.__file__)"

The class can then be located with:

.. code-block:: bash

   grep -n "class DifferentialStreamPowerChannelTD" \
       $(python -c "import fastscape.processes.channel as c; print(c.__file__)")

Related terms can also be searched for:

.. code-block:: bash

   grep -n -i "deposit" channel.py
   grep -n -i "sediment" channel.py
   grep -n -i "active_layer" channel.py
   grep -n -i "transport" channel.py
   grep -n -i "erosion" channel.py

The next source-code target is:

.. code-block:: python

   UniformSedimentLayer

This should help determine where sediment thickness and active sediment
storage are represented.

The third major target is:

.. code-block:: python

   MarineSedimentTransport

This should allow the marine transport and deposition formulation to be
traced separately from the terrestrial sediment model.

Python versus Fortran versus C++
--------------------------------

Another important question was whether Fastscape is written completely in
Python, completely in Fortran, or using a combination of languages.

The Fastscape documentation makes it clear that it is a **combination of
different software layers**.

At the high level:

.. code-block:: text

   Python
      |
      +-- Fastscape model processes
      +-- xarray-simlab
      +-- model configuration
      +-- user interface
      +-- Jupyter / Xarray ecosystem

At the lower level:

.. code-block:: text

   Fastscapelib
      |
      +-- efficient numerical algorithms
      |
      +-- current C++ implementation
      |
      +-- Python interface

The documentation also describes:

.. code-block:: text

   Fastscapelib-Fortran
      |
      +-- Fortran implementation
      +-- Python-compatible low-level API
      +-- older backend

Therefore, Fastscape should not be thought of simply as a Python code or
simply as a Fortran code.

It is better understood as a **multi-layer software ecosystem**:

.. code-block:: text

                     Fastscape
                         |
                  Python / xsimlab
                         |
              model/process interface
                         |
                   Fastscapelib
                         |
              +----------+----------+
              |                     |
           C++ backend         older Fortran
              |                     |
              +----------+----------+
                         |
                 efficient algorithms

This is important when tracing a particular equation.

A Python process may define the high-level process and variables, while the
actual computationally intensive operation may be delegated to a compiled
library.

Best approach for studying the code
------------------------------------

Rather than attempting to read the entire Fastscape source tree, the most
effective approach is to trace one physical process from the high-level
model down to the numerical implementation.

For sediment deposition, the recommended sequence is:

.. code-block:: text

   sediment_model
        |
        v
   DifferentialStreamPowerChannelTD
        |
        +-- read class definition
        |
        +-- identify inputs
        |
        +-- identify outputs
        |
        +-- identify erosion calculation
        |
        +-- identify sediment transport
        |
        +-- identify deposition
        |
        +-- identify active-layer interaction
        |
        v
   UniformSedimentLayer
        |
        +-- sediment thickness
        +-- active layer
        +-- bedrock/sediment interface
        |
        v
   Fastscapelib call?
        |
        +-- yes
        |     |
        |     v
        |   inspect lower-level implementation
        |
        +-- no
              |
              v
          Python implementation

A separate trace should then be performed for the marine system:

.. code-block:: text

   marine_model
        |
        v
   MarineSedimentTransport
        |
        +-- sea level
        +-- sediment transport
        +-- deposition
        +-- compaction
        +-- stratigraphy
        |
        v
   Fastscapelib / numerical implementation

Source-code investigation strategy
-----------------------------------

The investigation should proceed in the following order.

**Step 1: Find the installed Fastscape package**

.. code-block:: bash

   python -c "import fastscape; print(fastscape.__file__)"

**Step 2: Find the channel process**

.. code-block:: bash

   python -c "import fastscape.processes.channel as c; print(c.__file__)"

**Step 3: Find ``DifferentialStreamPowerChannelTD``**

.. code-block:: bash

   grep -n "DifferentialStreamPowerChannelTD" channel.py

**Step 4: Inspect the class**

Python can be used to inspect the source:

.. code-block:: python

   import inspect

   from fastscape.processes.channel import DifferentialStreamPowerChannelTD

   print(inspect.getsource(DifferentialStreamPowerChannelTD))

**Step 5: Determine inheritance**

Use:

.. code-block:: python

   print(DifferentialStreamPowerChannelTD.__mro__)

This will show which parent classes provide inherited functionality.

**Step 6: Find ``UniformSedimentLayer``**

.. code-block:: bash

   grep -R -n "class UniformSedimentLayer" fastscape/

**Step 7: Find ``MarineSedimentTransport``**

.. code-block:: bash

   grep -R -n "class MarineSedimentTransport" fastscape/

**Step 8: Follow any Fastscapelib calls**

Only after understanding the Python process should the investigation move into
the lower-level C++ or older Fortran implementation.

This should make it possible to distinguish between:

* model configuration;
* process definition;
* state-variable management;
* numerical algorithm; and
* compiled backend.

Current conceptual understanding
--------------------------------

The main conceptual picture emerging from this study is:

.. code-block:: text

                         LANDSCAPE EVOLUTION
                                 |
                +----------------+----------------+
                |                                 |
          TERRESTRIAL                         MARINE
                |                                 |
        bedrock erosion                    sea level
                |                                 |
        sediment production                coastal delivery
                |                                 |
        sediment transport                 marine transport
                |                                 |
        alluvial deposition                marine deposition
                |                                 |
        sediment storage                   compaction
                |                                 |
                +----------------+----------------+
                                 |
                                 v
                         basin sediment sink

The three models can then be viewed as different implementations of this
general source-to-sink problem.

Badlands
~~~~~~~~

.. code-block:: text

   TIN
    |
   SFD flow routing
    |
   stream-power / sediment processes
    |
   alluvial forced deposition
    |
   marine deposition / diffusion
    |
   basin

Fastscape
~~~~~~~~~

.. code-block:: text

   Raster grid
       |
   basic_model
       |
   sediment_model
       |
   active sediment layer
       |
   DifferentialStreamPowerChannelTD
       |
   marine_model
       |
   MarineSedimentTransport
       |
   stratigraphic horizons
       |
   basin

Landlab
~~~~~~~

.. code-block:: text

   Landlab grid
       |
   ErosionDeposition
       |
   fluvial sediment transport/deposition
       |
   coastal transition
       |
   SimpleSubmarineDiffuser
       |
   marine sediment redistribution
       |
   basin

What particularly caught my attention today
-------------------------------------------

The most important observation from today's study is that the question of
sediment deposition cannot be separated completely from the **software
architecture of the model**.

The equation itself is only one part of the problem.

To understand deposition, I need to know:

1. what sediment variable is being evolved;
2. where sediment is stored;
3. how sediment flux is calculated;
4. how erosion changes sediment supply;
5. how deposition changes surface elevation;
6. how bedrock and sediment are distinguished;
7. how the active sediment layer is updated;
8. how the terrestrial system connects to the marine system;
9. whether the marine process uses the same equation or a different one;
10. whether the expensive numerical calculation is performed in Python or
   delegated to a compiled library.

This is a more complete way of thinking about the model than simply searching
for a ``deposition`` function.

Important questions for the next stage
--------------------------------------

Fastscape fluvial deposition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* What is the exact equation implemented by
  ``DifferentialStreamPowerChannelTD``?
* Where is the sediment transport capacity calculated?
* How is deposition calculated?
* What determines the transition between erosion and deposition?
* How does the active layer affect the calculation?
* How are bedrock and sediment erosion coefficients used?
* Is the implementation directly related to Yuan et al. (2019)?

Fastscape sediment storage
~~~~~~~~~~~~~~~~~~~~~~~~~~

* What variables are contained in ``UniformSedimentLayer``?
* How is sediment thickness represented?
* Is sediment mass explicitly conserved?
* What happens when the active layer becomes thicker or thinner?
* How does erosion expose bedrock?
* How does deposition increase the sediment layer?

Fastscape marine system
~~~~~~~~~~~~~~~~~~~~~~~

* What equations are implemented by ``MarineSedimentTransport``?
* How does the process determine where marine sediment is deposited?
* How are sand and silt represented?
* What are the e-folding depths?
* How are transport coefficients used?
* How is water depth incorporated?
* How is compaction implemented?
* How are stratigraphic horizons updated?

Badlands comparison
~~~~~~~~~~~~~~~~~~~

* Is Badlands alluvial forced deposition fundamentally different from
  transport-limited deposition?
* How does Badlands store sediment?
* How does its marine diffusion differ from Fastscape's
  ``MarineSedimentTransport``?
* Does Badlands explicitly track an active sediment layer?

Landlab comparison
~~~~~~~~~~~~~~~~~~

* How does ``ErosionDeposition`` compare mathematically with
  ``DifferentialStreamPowerChannelTD``?
* How does ``SimpleSubmarineDiffuser`` compare with
  ``MarineSedimentTransport``?
* Are both marine components essentially diffusion models, or do they solve
  different sediment-transport equations?
* How do the models conserve sediment mass?

ASPECT--Landlab coupling
~~~~~~~~~~~~~~~~~~~~~~~~

* If a coupled ASPECT--Landlab model includes terrestrial and marine
  sediment processes, should these be represented as separate components?
* How should sediment thickness be transferred between Landlab and ASPECT?
* How should sea-level crossing be handled?
* How should the sediment field be mapped between the ASPECT mesh and the
  Landlab grid?
* Could an active-layer formulation be incorporated into the
  ASPECT--Landlab coupling?

Current conclusion
------------------

Today's study moved the investigation from simply reading about Badlands
deposition to examining how **Fastscape organizes the same general
source-to-sink problem**.

The most important realization is that Fastscape is organized hierarchically:

.. code-block:: text

   bootstrap_model
          |
          v
     basic_model
          |
          v
    sediment_model
          |
          v
     marine_model

The sediment model introduces:

.. code-block:: text

   Bedrock
   +
   UniformSedimentLayer
   +
   DifferentialStreamPowerChannelTD
   +
   DifferentialLinearDiffusion
   +
   MultipleFlowRouter

while the marine model adds:

.. code-block:: text

   Sea
   +
   MarineSedimentTransport
   +
   StratigraphicHorizons

This provides a clear path for the next stage of investigation.

The next step is to stop looking at the model only from the outside and begin
following the **actual source-code execution path**:

.. code-block:: text

   model definition
        |
        v
   process class
        |
        v
   equations / state variables
        |
        v
   numerical method
        |
        v
   Fastscapelib
        |
        v
   C++ / Fortran implementation

The immediate target should therefore be
``DifferentialStreamPowerChannelTD`` because this is the component most
directly connected to the question of **terrestrial sediment erosion,
transport, and deposition**.

After that, ``UniformSedimentLayer`` should be examined to understand
sediment storage, followed by ``MarineSedimentTransport`` to understand the
marine component.

This should provide the basis for a rigorous comparison of **Badlands,
Fastscape, and Landlab**, and eventually help determine which aspects of
these approaches could be useful for the development of the coupled
**ASPECT--Landlab** framework.

See also
--------

`Fastscape documentation <https://fastscape.org/>`__

`Fastscape GitHub organization <https://github.com/fastscape-lem>`__

`Fastscape repository <https://github.com/fastscape-lem/fastscape>`__

`Fastscapelib repository <https://github.com/fastscape-lem/fastscapelib>`__

`Fastscapelib-Fortran repository <https://github.com/fastscape-lem/fastscapelib-fortran>`__

`Badlands documentation <https://badlands.readthedocs.io/>`__




landlab_vis Documentation (Day 6)
-----------------------------------

Today we focused on organizing and documenting the ``landlab_vis``
package, particularly the core API and Python Basics documentation.

Main activities
---------------

* Finalized the documentation structure:

  .. code-block:: text

     landlab_vis
     ├── Getting Started
     ├── Installation
     ├── Cookbook
     ├── API Documentation
     ├── Detailed API Guide
     └── Developer Guide

* Organized the API documentation into:

  .. code-block:: text

     docs/source/api/
     ├── api.rst
     ├── core.rst
     ├── io.rst
     ├── analysis.rst
     └── plotting.rst

* Created a separate ``detailed_api`` section for detailed,
  class-by-class explanations.

* Documented ``Dataset`` conceptually and connected the main API page
  to its detailed documentation.

* Developed the ``Dataset`` documentation workflow:

  Concept
      → Simple example
      → Example output
      → Data location
      → Detailed API

* Added a concise HTML link style for detailed documentation:

  .. code-block:: rst

     .. raw:: html

        <p class="detailed-api-link">
           ➜ <a href="../detailed_api/dataset.html">
           Click here for the Detailed Dataset API
           </a>
        </p>

* Reviewed the actual ``Dataset`` source code and identified its:

  * constructor
  * properties
  * methods
  * class method
  * navigation
  * visualization
  * analysis interface
  * Python container methods

* Reviewed the actual ``Frame`` source code and prepared its detailed
  API structure for the next session.

Python Basics
-------------

We also developed a Python Basics section covering concepts directly
used by ``landlab_vis``:

.. code-block:: text

   python_basics/
   ├── index.rst
   ├── paths.rst
   ├── classes_and_objects.rst
   ├── inheritance.rst
   ├── properties_and_methods.rst
   ├── composition.rst
   ├── special_methods.rst
   ├── type_hints.rst
   ├── modules_and_imports.rst
   ├── functions.rst
   └── exceptions.rst

These topics were explained using examples from the actual
``Dataset`` and ``Frame`` implementations.

Important documentation style decisions
---------------------------------------

* Use reStructuredText (``.rst``) for the documentation.
* Use ``.. list-table::`` rather than grid tables.
* Keep the main API documentation concise.
* Put extensive class explanations in ``detailed_api``.
* Use automatically generated Sphinx API documentation where
  appropriate.
* Keep user-facing examples practical and connected to actual
  ``landlab_vis`` workflows.
* Use ``pathlib.Path`` for user-supplied Landlab output locations.
* Continue using the same documentation/link style consistently.

Next session
------------

Resume with the detailed documentation of:

.. code-block:: text

   Detailed API Guide
          |
          └── Frame
               ├── Constructor
               ├── Inheritance
               ├── Attributes
               ├── Geometry
               ├── Mesh
               ├── Fields
               ├── Plotting
               ├── Loading state
               ├── summary()
               ├── __repr__
               └── Complete API
