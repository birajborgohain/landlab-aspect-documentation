August 4, 2026, FastScape Benchmark Investigation and Transition from ParaView to `landlab_vis` (Day 1) a Reusable Landlab (.vtk files) Visualization Framework
==================================================================================================================================================================


Overview
--------

Today's work focused on two major objectives:

1. Investigating the FastScape implementation to understand parameter units and identify the source of discrepancies observed in the ASPECT–Landlab coupling.
2. Transitioning from a ParaView-based visualization workflow toward developing a dedicated Python visualization framework, **landlab_vis**, together with its supporting documentation infrastructure.

--------------------------------------------------------------------------

Investigation of FastScape Unit Handling
----------------------------------------

The first task of the day was to investigate the FastScape implementation with the goal of reproducing the published FastScape benchmark within the ASPECT–Landlab framework.

The primary focus was understanding how FastScape handles physical units for:

- Bedrock river incision coefficient (**K**)
- Hillslope diffusivity (**D**)
- Marine (submarine) diffusivity
- Internal time stepping
- Unit conversions

During the investigation it became increasingly evident that the current handling of the **seconds-to-years conversion (``s2yr``)** inside the Landlab coupling is likely introducing inconsistencies.

Previous diffusion benchmark experiments had already indicated suspicious behavior, and today's code inspection further strengthened the hypothesis that automatic conversion between SI units (seconds) and geological units (years) is not being handled consistently across ASPECT, Landlab, and FastScape.

Several questions remain to be answered before reproducing the FastScape benchmark:

- What are the native units expected by FastScape for **K**?
- What units are expected for hillslope diffusivity (**D**)?
- How is submarine diffusivity parameterized?
- Does FastScape internally assume years or SI units?
- Where are unit conversions performed inside the FastScape code?

Answering these questions is essential before reproducing published benchmark experiments within the coupled ASPECT–Landlab framework.

--------------------------------------------------------------------------

Evaluation of ParaView-Based Visualization
------------------------------------------

The second objective was to investigate whether ParaView could serve as the primary visualization platform for Landlab VTK outputs.

Several workflows were explored, including:

- Trace generation
- Automatic Python script generation
- Cross-section extraction
- Profile plotting
- General visualization workflows

The ParaView **Trace** functionality proved useful for learning the processing pipeline because it automatically generates equivalent Python code.

However, several limitations became apparent:

- Generated Python scripts are lengthy and difficult to interpret.
- The workflow depends heavily on ParaView-specific filters.
- Generated scripts become difficult to maintain.
- Scaling the workflow to many simulations or hundreds of timesteps would become increasingly cumbersome.
- Building reusable analysis tools on top of ParaView-generated scripts would require substantial effort.

Although ParaView remains an excellent interactive visualization environment, it became clear that it is not an ideal foundation for a reusable scientific visualization framework.

This realization motivated a shift toward developing a dedicated Python package specifically tailored for Landlab and ASPECT visualization.

--------------------------------------------------------------------------

Development of ``landlab_vis``
------------------------------

A strategic decision was made to begin developing **``landlab_vis``**, a reusable Python visualization and analysis framework for Landlab and ASPECT outputs.

The long-term goals of the project include:

- Native reading of Landlab VTK files
- Time-series management
- Cross-section extraction
- Profile visualization
- Statistical analysis
- Interactive visualization
- Animation generation
- Comparison between multiple simulation runs
- Integration with modern scientific Python visualization tools

Rather than relying on ParaView-generated scripts, the framework will provide a scalable, maintainable, and extensible platform dedicated to geomorphic and geodynamic visualization.

--------------------------------------------------------------------------

Documentation Infrastructure
----------------------------

A complete documentation infrastructure was established using **Sphinx**.

Major accomplishments include:

- Repository bootstrap
- Modular project structure
- Automated documentation generation scripts
- Markdown support through MyST
- Successful Sphinx documentation build
- Editable package installation using ``pyproject.toml``
- Documentation hierarchy for:

  - Getting Started
  - Theory
  - Tutorials
  - API Reference
  - Interactive Components
  - Gallery
  - Developer Guide
  - Project Documentation

This documentation system will evolve alongside software development to ensure implementation and documentation remain synchronized.

--------------------------------------------------------------------------

Development of the Core Software Architecture
---------------------------------------------

Development then shifted from documentation to implementing the core software architecture of ``landlab_vis``.

Instead of beginning with plotting routines, emphasis was placed on designing a clean object-oriented data model.

The current architecture is:

.. code-block:: text

    BaseObject
          │
          ▼
    Frame
    ├── Geometry
    ├── Metadata
    └── Fields (temporary dictionary)

Implemented Components
^^^^^^^^^^^^^^^^^^^^^^

**BaseObject**

Provides common functionality shared across future classes, including:

- Metadata management
- Summary generation
- Object representation
- Shared utility methods

**Geometry**

A dedicated container for mesh geometry including:

- Point coordinates
- ``x``, ``y`` and ``z`` coordinate accessors
- Geometry management

Separating geometry from field data mirrors the internal organization of VTK datasets and provides a clean software architecture.

**Frame**

Represents a single Landlab VTK timestep.

Current functionality includes:

- Lazy loading architecture
- Filename management
- Simulation timestep storage
- Physical time storage
- Geometry ownership
- Field storage
- Metadata inheritance
- Summary reporting
- Loading state management
- Comprehensive unit tests

The design intentionally keeps ``Frame`` lightweight. It represents a single timestep and deliberately avoids responsibilities such as plotting, interpolation, or file parsing.

--------------------------------------------------------------------------

Software Engineering Infrastructure
-----------------------------------

The project was converted into a fully installable Python package.

Major milestones include:

- Creation of ``pyproject.toml``
- Editable installation using:

  .. code-block:: bash

      pip install -e .

- Successful package import
- Unit testing using ``pytest``
- Successful execution of all current tests

This establishes a solid software engineering foundation for future development.

--------------------------------------------------------------------------

Current Status
--------------

At the conclusion of today's work:

- The documentation infrastructure is fully operational.
- The Python package can be installed and imported successfully.
- The object-oriented architecture has been established.
- ``BaseObject``, ``Geometry``, and ``Frame`` have been implemented and tested.
- Investigation into FastScape unit handling has identified the ``s2yr`` conversion as a likely source of discrepancies that must be resolved before benchmark reproduction.
- A strategic transition has been made from ParaView-based scripting toward the development of a dedicated visualization framework (``landlab_vis``) designed specifically for Landlab and ASPECT outputs.

--------------------------------------------------------------------------

Next Steps
----------

The immediate development priorities are:

1. Implement ``Field``.
2. Implement ``FieldCollection``.
3. Replace the temporary field dictionary within ``Frame`` by ``FieldCollection``.
4. Implement ``Dataset`` as a collection of ``Frame`` objects.
5. Develop ``FolderReader`` for automatic discovery of Landlab VTK timesteps.
6. Implement ``VTKReader`` to populate ``Frame`` objects from VTK files.
7. Continue investigating FastScape parameter units, particularly **K**, **D**, and submarine diffusivity, to ensure consistent unit handling in the ASPECT–Landlab benchmark implementation.