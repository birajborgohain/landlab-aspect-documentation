August 18, 2026, Thieulot et al. (2014): 3-D Coupled Tectonic–Landscape Evolution, FANTOM-CASCADE coupling
============================================================================================================

Paper
-----

**Thieulot, C., Steer, P., & Huismans, R. S. (2014).** *Three-dimensional numerical simulations of crustal systems undergoing orogeny and subjected to surface processes.* Geochemistry, Geophysics, Geosystems, 15, 4936–4957. DOI: 10.1002/2014GC005490.

Overview
--------

The central objective of Thieulot et al. (2014) is to develop a numerical framework in which **tectonic deformation and surface processes interact bidirectionally**. The authors couple the 3-D thermomechanical code FANTOM with the landscape-evolution model Cascade.

The basic coupled system is::

    tectonic deformation
            |
            v
        topography
            |
            v
    erosion / transport / deposition
            |
            v
      modified surface
            |
            v
    tectonic response

The important scientific idea is therefore not simply to calculate erosion on a tectonically generated landscape. Instead, erosion and sedimentation modify the surface boundary of the geodynamic model, producing a feedback between surface processes and crustal deformation.

The paper is particularly important because it demonstrates this feedback in a fully three-dimensional numerical framework. Earlier tectonic–surface-process studies were often restricted to two dimensions because of the computational expense of coupling a 3-D geodynamic model with a landscape model.

Key contribution
----------------

The principal contribution can be summarized as::

    FANTOM  <------------------------------>  Cascade
    tectonics                                surface processes

FANTOM provides the tectonic state and surface velocities, while Cascade evolves the surface through erosion and sediment transport. The modified surface is then transferred back to FANTOM.

Thus, the coupling is two-way::

    tectonics -> landscape evolution -> tectonic feedback

This makes the paper an important precedent for modern ASPECT–Landlab coupling.

Numerical coupling architecture
-------------------------------

The paper uses two different surfaces: the **F-surface**, representing the upper surface of the finite-element tectonic model, and the **C-surface**, representing the surface used by Cascade.

Because these surfaces have different discretizations, information must be transferred between them. The conceptual workflow is approximately::

    FANTOM
       |
       | velocity field
       v
    interpolate velocity
       |
       v
    C-surface
       |
       v
    advect surface
       |
       v
    refine surface
       |
       v
    run Cascade
       |
       v
    transfer surface
       |
       v
    FANTOM

This is highly relevant to ASPECT–Landlab because the same fundamental problem occurs when the ASPECT finite-element representation and the Landlab grid do not have identical spatial discretizations.

The coupling therefore has at least two fundamental components::

    ASPECT -> Landlab
    Landlab -> ASPECT

The first transfers tectonic information, such as uplift or velocity, to the landscape model. The second transfers the evolved topographic state back to the geodynamic model.

Temporal coupling and substepping
---------------------------------

One of the most important numerical aspects of the paper is the use of different timesteps for the tectonic and surface-process models.

Cascade uses an explicit, conditionally stable time integration scheme and therefore requires a relatively small timestep. The tectonic model can use a larger timestep.

The authors therefore define a tectonic timestep and divide it into many smaller Cascade timesteps::

    dt_C = dt_F / N

where ``dt_F`` is the FANTOM timestep, ``dt_C`` is the Cascade timestep, and ``N`` is the number of surface-process substeps within one tectonic timestep.

For their production calculations they used approximately::

    dt_C = 10 yr
    N    = 500

which corresponds to::

    dt_F = 5000 yr

The important lesson is not that ``N = 500`` is universally appropriate. Rather, the number of substeps is controlled by the timestep requirements of the surface-process solver.

Connection to the ASPECT–Landlab ``n_substeps`` experiment
------------------------------------------------------------

The current ASPECT–Landlab implementation uses the same general idea::

    dt = end_time - current_time
    sub_dt = dt / n_substeps

The total tectonic displacement over the ASPECT timestep remains the same when the uplift rate is constant::

    total uplift
        = n_substeps * U * sub_dt
        = n_substeps * U * (dt / n_substeps)
        = U * dt

Therefore, increasing ``n_substeps`` does not necessarily change the total amount of imposed uplift.

However, increasing ``n_substeps`` changes the frequency with which Landlab interacts with the evolving tectonic surface. Thus::

    n_substeps
        |
        v
    coupling frequency
        |
        v
    frequency of uplift/diffusion/erosion interaction
        |
        v
    different numerical trajectory
        |
        v
    potentially different final landscape

This provides an important interpretation of the observed ASPECT–Landlab results for ``n_substeps = 1, 2, 3, 9, 20, 40``.

The difference between solutions is not necessarily caused by a change in the integrated tectonic displacement. It can arise from the **operator splitting and temporal coupling frequency** between tectonic forcing and surface-process evolution.

Coupling-frequency convergence
------------------------------

The ASPECT–Landlab experiment can be formulated as a formal convergence study.

Let ``N`` represent the number of Landlab substeps per ASPECT timestep. Possible values include::

    N = 1, 2, 5, 10, 20, 40, 80, 160

A high-resolution case can be treated as a reference solution. For example::

    E_N = ||h_N - h_ref|| / ||h_ref||

where ``h_N`` is the topographic field obtained using ``N`` substeps and ``h_ref`` is the reference solution.

The objective is to identify a minimum value ``N_crit`` such that::

    E_N < epsilon

for the quantity of interest.

Possible convergence diagnostics include:

* topographic RMSE;
* maximum elevation;
* mean elevation;
* maximum erosion;
* maximum deposition;
* total eroded volume;
* total deposited volume;
* sediment mass balance;
* spatial distribution of erosion and deposition;
* CPU time.

The result can then be presented as an accuracy-versus-cost relationship. If the solution changes very little beyond ``N = 40``, then ``N = 40`` can be justified as a numerically adequate coupling frequency rather than selected arbitrarily.

Spatial coupling
----------------

The paper also demonstrates that temporal coupling is only one part of the problem. The FANTOM and Cascade surfaces have different spatial representations, so information must be interpolated between the two models.

This is directly analogous to the ASPECT–Landlab problem::

    ASPECT finite-element surface
              |
              | interpolation / mapping
              v
        Landlab grid

and::

    Landlab grid
              |
              | interpolation / mapping
              v
        ASPECT surface

This suggests that the coupled ASPECT–Landlab framework has several independent numerical error sources::

    total coupled error
           |
      +----+----+-------------+
      |         |             |
    temporal  spatial      transfer
      |         |             |
    N_substeps resolution  interpolation

Temporal error depends on ``n_substeps`` and the frequency of ASPECT–Landlab interaction. Spatial error depends on ASPECT and Landlab resolution and their mismatch. Transfer error depends on how quantities are interpolated or mapped between the two grids.

Persistent versus regenerated landscape surface
-----------------------------------------------

An important design choice in the Thieulot et al. framework is that the Cascade surface is advected and evolved rather than simply regenerated from scratch at every coupling step.

This preserves the evolving state of the landscape and its drainage organization.

For ASPECT–Landlab, this raises an important architectural question:

    Should Landlab maintain a persistent evolving surface while ASPECT supplies tectonic deformation?

A persistent Landlab state can preserve drainage organization, evolving channel structure, sediment routing, erosion history, and deposition history.

Surface-grid deformation and resolution
---------------------------------------

The Cascade surface is advected, so nodes can become concentrated in some regions and sparse in others. The authors therefore use node addition and removal to maintain useful spatial resolution.

A RasterModelGrid in Landlab is different: the grid has fixed spacing. This simplifies the implementation, but it also introduces a potential limitation for large horizontal tectonic deformation::

    ASPECT surface deformation
              !=
    deformation of the Landlab grid

Instead, the evolving ASPECT surface state is mapped onto a fixed Landlab grid. For small deformation this may be adequate. For large horizontal deformation or strongly migrating drainage networks, the implications should be tested.

Physical experiments in the paper
---------------------------------

The authors investigate how changes in surface-process efficiency affect orogenic development. Important parameters include:

``K_f``
    fluvial erosion efficiency.

``K_d``
    hillslope diffusivity.

``l_f``
    fluvial transport or erodibility length scale.

Their reference values are approximately::

    K_f = 0.1 m/yr
    K_d = 0.1 m^2/yr
    l_f = 10 km

The model is then used to investigate how changing surface-process efficiency affects topography and tectonic deformation over geological timescales.

The key scientific result is that erosion does not simply reduce mountain height. Instead, erosion modifies the mechanical state of the orogen and can localize deformation.

The feedback can be represented schematically::

    stronger erosion
          |
          v
    removal of topographic load
          |
          v
    modified stress distribution
          |
          v
    stronger deformation localization
          |
          v
    uplift / relief generation
          |
          v
    stronger topography

Therefore, surface processes can actively influence tectonic structure.

Nonlinear response to erosion efficiency
-----------------------------------------

Maximum elevation does not necessarily vary monotonically with erosion efficiency.

For low-to-moderate erosion efficiency, increasing erosion can be associated with increasing maximum elevation. At sufficiently high erosion efficiency, maximum elevation decreases.

This means the relationship cannot simply be written as::

    more erosion -> lower mountains

Instead, the coupled system can contain different regimes. This is important for future ASPECT–Landlab experiments because systematic parameter sweeps may reveal nonlinear or threshold behavior.

Three-dimensional erosion gradients
-----------------------------------

The paper also includes a 3-D experiment in which erosion efficiency varies along strike. One side represents a relatively dry region with lower fluvial erosion efficiency, while the other represents a wetter region with higher erosion efficiency.

The resulting topography and deformation vary strongly along strike. The authors report large variations in maximum elevation, differences in orogen width, enhanced erosion on the wetter side, and increased uplift on that side. Material also develops an along-strike velocity component.

This demonstrates that spatially variable surface processes can generate three-dimensional tectonic responses.

This is particularly relevant to ASPECT–Landlab because Landlab can naturally represent spatially varying surface-process parameters while ASPECT provides the fully 3-D tectonic response.

Limitations of the study
------------------------

The paper identifies several limitations that provide direct opportunities for future ASPECT–Landlab development.

Simplified sediment physics
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Cascade implementation does not fully represent the sediment tool effect. Sediment cover is represented, but the enhanced incision associated with intermediate sediment loads is not fully captured.

Simplified discharge
~~~~~~~~~~~~~~~~~~~~

The model uses an effective discharge rather than fully representing the stochastic distribution of discharge events. This limits the representation of nonlinear river incision associated with variable flood discharge.

Simplified incision law
~~~~~~~~~~~~~~~~~~~~~~~

The surface-process formulation is simplified relative to modern nonlinear stream-power formulations. More general formulations can involve::

    E = K A^m S^n

where ``A`` is drainage area, ``S`` is slope, and ``m`` and ``n`` control the nonlinear dependence.

Limited 3-D computational resolution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The 3-D geodynamic calculations were computationally expensive and therefore limited in spatial resolution and model size. Modern high-performance computing and ASPECT provide an opportunity to perform more detailed experiments.

Relevance to the ASPECT–Landlab project
---------------------------------------

The paper provides a strong conceptual and numerical foundation for the coupled ASPECT–Landlab framework.

The correspondence can be summarized as::

    Thieulot et al.             ASPECT–Landlab

    FANTOM                      ASPECT
    Cascade                     Landlab
    F-surface                   ASPECT surface
    C-surface                   Landlab surface
    velocity transfer           tectonic forcing transfer
    surface evolution           erosion / diffusion / deposition
    surface feedback            updated topography to ASPECT
    multiple Cascade steps      n_substeps
    spatial interpolation       ASPECT–Landlab mapping

The major difference is that the present project has an opportunity to make the coupling architecture more explicit and systematically test its numerical behavior.

Potential numerical experiments
--------------------------------

Stage I: Independent verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verify the individual components before coupling:

* ASPECT free-surface deformation;
* Landlab diffusion;
* Landlab fluvial erosion;
* Landlab deposition;
* analytical or benchmark solutions where available.

The goal is::

    verify ASPECT
    verify Landlab
    verify coupling inputs/outputs

Stage II: Basic coupling verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Build progressively more complicated coupled experiments::

    ASPECT + Landlab diffusion

    ASPECT + Landlab fluvial erosion

    ASPECT + diffusion + fluvial erosion

    ASPECT + erosion + deposition

This isolates errors associated with individual surface-process components.

Stage III: Temporal convergence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Systematically vary::

    n_substeps = 1, 2, 5, 10, 20, 40, 80, 160

and compare topography, erosion, deposition, sediment volume, tectonic response, and runtime.

The goal is to determine ``N_crit`` and quantify the computational cost of stronger coupling.

Stage IV: Spatial convergence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Vary ASPECT mesh resolution, Landlab grid spacing, relative ASPECT/Landlab resolution, and interpolation method. This allows temporal and spatial coupling errors to be separated.

Stage V: Scientific experiments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the numerical behavior is understood, perform geological experiments such as mountain building and erosion, spatially variable precipitation, asymmetric erosion, rifting, tectonic subsidence, sedimentary basin development, coupled erosion and deposition, and grain-size-dependent sediment transport.

Connection to sediment evolution
--------------------------------

The paper is especially relevant to the longer-term goal of introducing more sophisticated sediment dynamics into the ASPECT–Landlab framework.

A simple coupled model may track::

    topography h(x,y,t)

A more advanced sediment-routing model could track::

    h(x,y,t)
    Q_s(x,y,t)
    D_g(x,y,t)
    H_s(x,y,t)

where ``h`` is surface elevation, ``Q_s`` is sediment flux, ``D_g`` is characteristic grain size or grain-size distribution, and ``H_s`` is sediment thickness.

The resulting coupling becomes::

    ASPECT
       |
       | tectonic deformation
       v
    Landlab
       |
       +--> erosion
       |
       +--> sediment production
       |
       +--> transport
       |
       +--> deposition
       |
       +--> grain-size evolution
       |
       v
    sediment load / surface elevation
       |
       v
    ASPECT

This would extend the basic tectonic–landscape feedback of Thieulot et al. toward a more complete tectonic–erosional–sedimentary system.

Potential rift application
---------------------------

The Thieulot et al. study focuses primarily on orogenic systems. The same numerical architecture can be applied to extensional systems.

For a rift, the feedback can be expressed as::

    tectonic extension
           |
           v
    faulting + uplift + subsidence
           |
           +----------------+
           |                |
           v                v
        erosion        accommodation
           |                |
           v                v
    sediment transport -> deposition
                            |
                            v
                      basin filling
                            |
                            v
                     sediment loading
                            |
                            v
                     tectonic response

This is a natural application for ASPECT–Landlab because ASPECT can calculate tectonic uplift, subsidence, faulting, and deformation while Landlab can calculate erosion, transport, and deposition.

Longer-term scientific direction
--------------------------------

The conceptual progression can be expressed as::

    Thieulot et al. (2014)

        Can a 3-D tectonic model be coupled
        with a landscape-evolution model?
                         |
                         v
                    demonstrated

        ASPECT–Landlab

        How should the numerical coupling
        be designed and validated?
                         |
                         v
                convergence studies

        Advanced ASPECT–Landlab

        How do sediment dynamics, grain size,
        deposition, basin loading and tectonics
        interact?
                         |
                         v
             coupled Earth-surface system

The research opportunity is therefore not simply to reproduce an older tectonic–landscape coupling model. It is to use modern ASPECT and Landlab capabilities to investigate the numerical and physical consequences of different coupling strategies.

Most important connection to the current work
---------------------------------------------

The central connection to the current ``n_substeps`` investigation can be stated as follows:

    Thieulot et al. demonstrated that a tectonic timestep can contain many
    smaller surface-process timesteps because the surface model operates on
    a faster numerical timescale.

    The ASPECT–Landlab project can take the next step by asking whether the
    number of those surface substeps changes the coupled solution and by
    determining a quantitatively converged coupling frequency rather than
    simply prescribing one.

Thus, the important research question becomes::

    n_substeps
        |
        v
    coupling frequency
        |
        v
    operator interaction
        |
        v
    landscape response
        |
        v
    tectonic response
        |
        v
    numerical convergence

A useful formal criterion is::

    N >= N_crit
        =>
    |Q_N - Q_ref| < epsilon

where ``Q`` can represent topography, erosion, deposition, sediment flux, or tectonic deformation.

This turns the current ``n_substeps`` investigation from a debugging or implementation exercise into a formal **numerical-methods study of coupled geodynamic–landscape evolution**.

Future scope
------------

The major future directions suggested by the study and its limitations are:

#. Develop a systematic temporal coupling-convergence framework.
#. Quantify spatial interpolation and grid-mismatch errors.
#. Test conservation of mass and sediment during ASPECT–Landlab transfers.
#. Include nonlinear erosion and transport laws.
#. Include explicit sediment production, transport, and deposition.
#. Investigate sediment cover and tool effects.
#. Introduce variable discharge and climate forcing.
#. Track sediment grain-size evolution.
#. Couple sediment loading back into the geodynamic model.
#. Investigate rift and sedimentary-basin systems.
#. Explore spatially heterogeneous tectonic and climatic forcing.
#. Quantify the computational accuracy versus cost of stronger coupling.
#. Use high-performance computing to explore larger and higher-resolution three-dimensional experiments.

Overall assessment
------------------

Thieulot et al. (2014) provides an important foundation for the ASPECT–Landlab project because it demonstrates that tectonic deformation and landscape evolution should be treated as a coupled system rather than as independent models.

Its most important contribution for the present work is the numerical coupling strategy: a large geodynamic timestep can contain many smaller surface-process timesteps, while information is repeatedly exchanged between the two models.

For the current ASPECT–Landlab development, the paper should therefore be viewed as both a **precedent** and a **benchmark**.

The precedent is::

    3-D tectonics <-> surface processes

The benchmark is::

    multiple surface-process substeps
    within one tectonic timestep

The opportunity for the present work is to go further by quantifying::

    temporal convergence
    +
    spatial convergence
    +
    transfer accuracy
    +
    computational cost

and then extending the coupled system toward::

    erosion
    + transport
    + deposition
    + grain-size evolution
    + sediment loading
    + tectonic deformation

This provides a pathway from a basic ASPECT–Landlab coupling test toward a general numerical framework for investigating coupled tectonic, geomorphic, and sedimentary-basin evolution.


Analytical Benchmark and Parametric Analysis Framework
----------------------------------------------------------

Whipple and Meade (2004): Analytical Surface-Process Solution
--------------------------------------------------------------

An important analytical reference for the development and validation of the
coupled tectonic--surface-process framework is the work of Whipple and Meade
(2004):

    Whipple, K. X., & Meade, B. J. (2004), Controls on the strength of
    coupling among climate, erosion, and deformation in two-sided, frictional
    orogenic wedges at steady state, *Journal of Geophysical Research*,
    109, F01011. doi:10.1029/2003JF000019.

This paper is particularly useful because it provides an analytical treatment
of the coupling between tectonic deformation, erosion, and climate in a
two-sided frictional orogenic wedge at steady state. The analytical solution
provides a useful reduced-order description against which numerical
surface-process and tectonic models can be compared.

For the present ASPECT--Landlab framework, the analytical solution can be
treated as a benchmark rather than as a replacement for the numerical model.
The purpose would be to determine whether the numerical model reproduces the
expected first-order relationships between tectonic forcing, erosion
efficiency, topographic relief, orogen width, and rock uplift.

The benchmark analysis should focus on the following questions:

* Does the numerical model approach a flux steady state comparable to the
  analytical solution?
* How does increasing erosion efficiency modify the width and relief of the
  numerical orogen?
* Does the numerical model reproduce the expected relationship between erosion
  rate and rock uplift rate?
* How does the numerical solution depart from the analytical solution when
  transient effects, spatially variable erosion, hillslope diffusion, or
  complex tectonic deformation become important?

A useful first step would therefore be to implement the analytical solution
as a Python reference module. The numerical model output could then be
compared directly against the analytical prediction for a simplified
configuration.

The analytical benchmark can be organized conceptually as

.. math::

    \text{tectonic forcing}
    \rightarrow
    \text{material flux}
    \rightarrow
    \text{erosion}
    \rightarrow
    \text{topographic response}.

At steady state, the balance between tectonic rock uplift and erosion provides
an especially important diagnostic. For the orogen as a whole, the numerical
model should approach a condition in which the incoming and outgoing material
fluxes are approximately balanced. For the orogen itself, the corresponding
erosion/uplift balance can be examined through

.. math::

    \frac{E}{U} \rightarrow 1.

The analytical solution can therefore be incorporated into the Python
framework as a ``benchmark`` component. Each numerical experiment can be
associated with a set of analytical predictions, allowing the analysis
software to report both the numerical measurement and its deviation from the
analytical expectation.

A useful development strategy is to begin with a simplified one-dimensional
or symmetric configuration before attempting comparisons with the full
two-dimensional ASPECT--Landlab model.


Section 5.2: Parametric Investigation and Characteristic Features
-------------------------------------------------------------------

The parametric investigation described in Section 5.2 provides a useful
template for developing a systematic Python analysis framework for the
ASPECT--Landlab experiments.

The main objective should not initially be to reproduce a particular figure.
Instead, the goal should be to develop a reusable framework that converts
each numerical experiment into a standardized set of quantitative
measurements.

The surface-process parameters that can be investigated include

* ``Kd`` -- hillslope diffusivity,
* ``Kf`` -- fluvial erosion efficiency, and
* ``lf`` -- fluvial transport length scale.

Following the strategy described in Section 5.2, an initial investigation
could vary ``Kf`` while keeping ``Kd`` and ``lf`` fixed. This provides a
controlled experiment in which the influence of fluvial erosion efficiency
on landscape morphology and tectonic deformation can be isolated.

The Python framework should nevertheless be designed so that ``Kd``, ``Kf``,
and ``lf`` are all treated as experiment parameters. This will make it
possible to extend the study later to multidimensional parameter sweeps.

Objective Measurements
~~~~~~~~~~~~~~~~~~~~~~

For every model output, the analysis framework should calculate a standard
set of objective measurements describing the morphology, structure, and
material fluxes of the orogen.

The primary quantities should include:

.. math::

    Z_{\mathrm{mean}}

mean elevation of the orogen,

.. math::

    Z_{\mathrm{max}}

maximum or summit elevation,

.. math::

    W

total orogen width,

.. math::

    W_L,\quad W_R

left and right half-widths,

.. math::

    R

topographic relief,

.. math::

    I_{\mathrm{asym}}
    =
    \left|
    \frac{W_L-W_R}{W_L+W_R}
    \right|

topographic asymmetry,

.. math::

    \alpha

dip angle of the principal shear zone,

and the material-flux quantities

.. math::

    F_{\mathrm{in}},\qquad
    F_{\mathrm{out}},\qquad
    E,\qquad
    U.

Two particularly important nondimensional diagnostics are

.. math::

    \frac{F_{\mathrm{out}}}{F_{\mathrm{in}}}

and

.. math::

    \frac{E}{U}.

These ratios provide a direct measure of the relative importance of tectonic
transport and surface processes. Values approaching unity indicate a
flux-steady configuration.

Python Analysis Framework
~~~~~~~~~~~~~~~~~~~~~~~~~

The analysis should be developed as a separate Python package rather than as
individual plotting scripts. A possible structure is:

.. code-block:: text

    analysis/
    ├── io.py
    ├── metrics.py
    ├── morphology.py
    ├── fluxes.py
    ├── shear_zone.py
    ├── steady_state.py
    ├── benchmark.py
    ├── experiments.py
    └── plotting/
        ├── morphology.py
        ├── flux.py
        ├── convergence.py
        └── parameter_sweep.py

The central idea is that every model run should be converted into a common
``ExperimentResult`` object containing the model parameters, time, and
objective measurements.

For example:

.. code-block:: python

    result = {
        "Kd": Kd,
        "Kf": Kf,
        "lf": lf,
        "time": time,
        "Zmean": Zmean,
        "Zmax": Zmax,
        "W": W,
        "WL": WL,
        "WR": WR,
        "R": relief,
        "Iasym": asymmetry,
        "alpha": alpha,
        "Fin": Fin,
        "Fout": Fout,
        "E": erosion,
        "U": uplift,
    }

This approach separates the numerical simulation from the scientific
interpretation of the results.

Time-Series Analysis
~~~~~~~~~~~~~~~~~~~~

For each experiment, the first level of analysis should be the temporal
evolution of the objective measurements.

For example:

.. math::

    Z_{\mathrm{max}}(t),\qquad
    Z_{\mathrm{mean}}(t),\qquad
    W(t),\qquad
    R(t),\qquad
    I_{\mathrm{asym}}(t).

The corresponding flux quantities should also be tracked:

.. math::

    F_{\mathrm{in}}(t),\qquad
    F_{\mathrm{out}}(t),\qquad
    E(t),\qquad
    U(t).

This will make it possible to distinguish transient evolution from the
eventual steady or quasi-steady state.

A particularly useful diagnostic is therefore

.. math::

    \epsilon_{\mathrm{flux}}
    =
    \frac{E-U}{U}.

When ``epsilon_flux`` approaches zero, the model is approaching the
erosion--uplift balance.

Similarly,

.. math::

    \epsilon_{\mathrm{flux,out}}
    =
    \frac{F_{\mathrm{out}}-F_{\mathrm{in}}}{F_{\mathrm{in}}}

can be used to quantify the approach toward whole-orogen flux steady state.

Parameter-Sweep Analysis
~~~~~~~~~~~~~~~~~~~~~~~~

The next stage should automatically execute and analyze a suite of experiments
in which ``Kf`` is varied relative to a reference value.

For example:

.. code-block:: python

    Kf_values = [
        0.25 * Kf_reference,
        0.50 * Kf_reference,
        1.00 * Kf_reference,
        2.00 * Kf_reference,
        4.00 * Kf_reference,
    ]

For each experiment, the framework should automatically:

#. identify the experiment parameters,
#. read the model output,
#. calculate the objective measurements,
#. determine whether the model has reached a quasi-steady state,
#. calculate the steady-state averages,
#. store the results in a common table, and
#. generate the corresponding figures.

The resulting dataset could have a structure such as:

.. list-table:: Parametric experiment summary
   :header-rows: 1

   * - ``Kf / Kf_ref``
     - ``Zmax``
     - ``Zmean``
     - ``W``
     - ``R``
     - ``Iasym``
     - ``E/U``
     - ``Fout/Fin``
   * - 0.25
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
   * - 0.50
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
   * - 1.00
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
   * - 2.00
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
   * - 4.00
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...
     - ...

This table would become the central data product from which the figures are
generated.

Suggested Figures
~~~~~~~~~~~~~~~~~

The framework should initially generate a small number of diagnostic figures
rather than attempting to reproduce every figure from the reference paper.

The most useful first plots are:

**1. Morphological evolution**

.. math::

    Z_{\mathrm{max}}, Z_{\mathrm{mean}}, W, R
    \quad \mathrm{vs.}\quad t.

**2. Flux evolution**

.. math::

    E,\ U,\ F_{\mathrm{in}},\ F_{\mathrm{out}}
    \quad \mathrm{vs.}\quad t.

**3. Steady-state morphology versus erosion efficiency**

.. math::

    Z_{\mathrm{max}},\quad
    W,\quad
    R
    \quad \mathrm{vs.}\quad
    K_f/K_{f,\mathrm{ref}}.

**4. Flux balance**

.. math::

    E/U
    \quad \mathrm{vs.}\quad
    K_f/K_{f,\mathrm{ref}}.

**5. Asymmetry**

.. math::

    I_{\mathrm{asym}}
    \quad \mathrm{vs.}\quad
    K_f/K_{f,\mathrm{ref}}.

**6. Analytical versus numerical solution**

.. math::

    Q_{\mathrm{numerical}}
    \quad \mathrm{vs.}\quad
    Q_{\mathrm{analytical}}

for quantities such as width, relief, uplift, or erosion rate where an
analytical prediction is available.

A one-to-one comparison plot is especially useful because it immediately
shows whether the numerical model reproduces the analytical scaling.

Dimensionless Analysis
~~~~~~~~~~~~~~~~~~~~~~

A longer-term goal should be to move beyond plots against dimensional model
parameters and investigate dimensionless controls.

For example, quantities such as

.. math::

    \frac{K_f}{K_{f,\mathrm{ref}}},
    \qquad
    \frac{K_d}{K_{d,\mathrm{ref}}},
    \qquad
    \frac{l_f}{l_{f,\mathrm{ref}}},
    \qquad
    \frac{E}{U},
    \qquad
    \frac{F_{\mathrm{out}}}{F_{\mathrm{in}}}

can provide a more general description of the model behavior.

This would make it easier to determine whether apparently different
experiments are actually dynamically equivalent.

Steady-State Detection
~~~~~~~~~~~~~~~~~~~~~~

The Python framework should avoid defining the final timestep automatically
as the ``steady state``. Instead, a quantitative steady-state criterion
should be developed.

For example, the model could be considered quasi-steady when

.. math::

    \left|
    \frac{1}{Q}\frac{dQ}{dt}
    \right|
    < \epsilon

for a specified averaging interval, where ``Q`` could represent ``Zmax``,
``W``, or another diagnostic.

A more robust approach would be to require several quantities to stabilize
simultaneously:

.. math::

    \frac{dZ_{\mathrm{max}}}{dt} \approx 0,
    \qquad
    \frac{dW}{dt} \approx 0,
    \qquad
    \frac{dR}{dt} \approx 0,
    \qquad
    \frac{E}{U} \approx 1.

This distinction between *instantaneous steady state* and *quasi-steady
state* will be important for long ASPECT--Landlab simulations.

Connection to ASPECT--Landlab Coupling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The framework should also distinguish physical parameter sensitivity from
numerical sensitivity.

For example, if ``Kf`` is varied while the ASPECT--Landlab coupling timestep
or ``n_substeps`` is also changed, the resulting differences cannot
necessarily be attributed entirely to erosion efficiency.

Therefore, the parameter-study framework should record numerical parameters
alongside physical parameters:

.. code-block:: text

    Physical parameters:
        Kd
        Kf
        lf
        uplift rate
        tectonic convergence

    Numerical parameters:
        dt
        n_substeps
        mesh resolution
        Landlab grid spacing
        ASPECT refinement level

This is particularly important for the coupled model because increasing
``n_substeps`` changes the frequency with which the tectonic and surface
process operators interact during a timestep. Consequently, the final
topographic response may contain both a physical parameter dependence and an
operator-splitting dependence.

A useful future experiment would therefore be a two-dimensional parameter
study:

.. math::

    Q = f(K_f, n_{\mathrm{substeps}}).

This would allow the framework to identify regions where the solution is
insensitive to ``n_substeps`` and regions where numerical coupling effects
remain significant.

Recommended Development Sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Python framework can be developed incrementally:

#. Implement extraction of topography and model fields from one experiment.
#. Implement ``Zmean``, ``Zmax``, ``W``, ``WL``, ``WR``, ``R``, and
   ``Iasym``.
#. Implement erosion, uplift, and material-flux calculations.
#. Store all measurements in a standardized tabular format.
#. Implement automatic steady-state detection.
#. Reproduce the basic time-series diagnostics from Section 5.2.
#. Implement automated ``Kf`` parameter sweeps.
#. Add analytical predictions from Whipple and Meade (2004).
#. Generate numerical-versus-analytical comparison plots.
#. Extend the framework to ``Kd`` and ``lf``.
#. Finally, investigate interactions between physical parameters and
   numerical parameters such as ``n_substeps`` and mesh resolution.

The main objective is to create a reusable analysis framework in which adding
a new ASPECT--Landlab experiment automatically produces the same set of
scientific diagnostics. This would turn the parametric investigation from a
collection of manually generated plots into a reproducible quantitative
workflow.