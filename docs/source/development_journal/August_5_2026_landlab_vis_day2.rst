August 5, 2026 landlab_vis: A Python Visualization and Analysis Framework for Landlab and ASPECT Outputs
==========================================================================================================



Overview
--------

Today's work marked a major milestone in the development of **landlab_vis**. The project evolved from a conceptual design into a functional Python library capable of reading, organizing, and preparing Landlab VTK outputs for visualization.

The primary focus was on completing the core object model, implementing the data ingestion pipeline, establishing a robust testing framework, and beginning the visualization architecture.

An important architectural discussion also emerged after investigating the internal structure of Landlab-generated VTK files. This investigation significantly influenced the future direction of the visualization framework.

--------------------------------------------------------------------------

Investigation of Landlab VTK Mesh Structure
------------------------------------------

The first task was to understand how Landlab stores its computational mesh inside VTK files so that an appropriate visualization backend could be designed.

Initial Assumption
~~~~~~~~~~~~~~~~~~

The original plan was to convert every mesh into a triangular representation and use Matplotlib's triangulation tools for plotting.

The expected workflow was

.. code-block:: text

    VTK
      ↓
    Triangulate
      ↓
    Matplotlib Triangulation
      ↓
    Publication-quality figures

Mesh Investigation
~~~~~~~~~~~~~~~~~~

Using PyVista, a sample Landlab VTK file was examined.

The investigation showed that

* the file is loaded as a ``pyvista.UnstructuredGrid``.
* applying ``mesh.triangulate()`` still returns an ``UnstructuredGrid``.
* the expected ``regular_faces`` attribute is not available.
* the mesh instead exposes

  * ``cells``
  * ``cell_connectivity``
  * ``offset``
  * ``celltypes``

This indicates that Landlab preserves its native mesh representation rather than exposing a simple triangular surface.

Architectural Implications
~~~~~~~~~~~~~~~~~~~~~~~~~~

This discovery prompted a redesign discussion.

Instead of forcing every mesh into triangles during file reading, the preferred long-term architecture became

.. code-block:: text

    Read mesh faithfully
            ↓
       Store geometry
            ↓
    Plot using appropriate backend

This separation keeps readers responsible only for reading data while allowing plotting classes to decide how the mesh should be visualized.

--------------------------------------------------------------------------

Development of ``landlab_vis``
------------------------------

Project Structure
~~~~~~~~~~~~~~~~~

The project directory structure was finalized.

.. code-block:: text

    landlab_vis/

        core/

        io/

        plotting/

        analysis/

        utilities/

A complete Sphinx documentation project was also created and successfully configured using the Read the Docs theme.

--------------------------------------------------------------------------

Core Object Model
-----------------

BaseObject
~~~~~~~~~~

A common base class was implemented for all core objects.

Current functionality includes

* object name
* metadata dictionary
* metadata management
* summary()
* readable object representation

Metadata Design
~~~~~~~~~~~~~~~

A clear distinction was introduced between

* strongly typed core attributes

  * filename
  * timestep
  * simulation time

* optional metadata

  * units
  * spacing
  * solver information
  * user-defined attributes

This design provides a much cleaner and more scalable object model.

--------------------------------------------------------------------------

Geometry
--------

The Geometry class was implemented to manage spatial information.

Current functionality

* store mesh points
* x coordinates
* y coordinates
* z coordinates
* number of mesh points
* empty-state detection
* geometry clearing

Future extensions will likely include mesh connectivity and additional geometric information.

--------------------------------------------------------------------------

Field
-----

A dedicated Field class was implemented.

Current functionality includes

* field name
* numerical values
* units
* location
* statistics

  * minimum
  * maximum
  * mean
  * size

A deep-copy mechanism was also implemented.

--------------------------------------------------------------------------

FieldCollection
---------------

A dedicated FieldCollection class was developed to manage multiple simulation fields.

Implemented functionality

* add fields
* remove fields
* retrieve by name
* iteration
* membership testing
* field names
* number of fields

This replaces the earlier dictionary-based implementation.

--------------------------------------------------------------------------

Frame
-----

Frame became the central data container of the library.

Current responsibilities include

* filename
* timestep
* simulation time
* geometry
* field collection
* metadata
* loading state

Convenience properties include

* x
* y
* z
* points
* field names
* number of fields
* number of points

Several design improvements were introduced, including

* internal loading state management
* cleaner summaries
* improved object representation

--------------------------------------------------------------------------

Dataset
-------

Dataset was implemented as a collection of Frame objects.

Implemented functionality

* append
* indexing
* iteration
* length
* representation

This forms the basis for managing complete simulation time series.

--------------------------------------------------------------------------

Input / Output Layer
--------------------

FolderReader
~~~~~~~~~~~~

FolderReader was implemented to automatically discover Landlab VTK outputs.

Current functionality

* directory scanning
* filename sorting
* automatic Frame creation
* Dataset construction

VTKReader
~~~~~~~~~

VTKReader was implemented using PyVista.

Current functionality

* read VTK files
* populate Geometry
* populate FieldCollection
* preserve all Landlab point-data arrays
* update Frame loading state

The reader currently supports all scalar fields written by Landlab without requiring any hard-coded field names.

--------------------------------------------------------------------------

Testing
-------

A comprehensive testing framework was developed.

Implemented tests include

* BaseObject
* Geometry
* Field
* FieldCollection
* Frame
* Dataset
* FolderReader
* VTKReader
* FramePlotter initialization

All implemented components successfully passed their respective unit tests.

--------------------------------------------------------------------------

Visualization Framework
-----------------------

The plotting architecture was initiated.

FramePlotter
~~~~~~~~~~~~

A dedicated plotting package was created.

Current progress

* plotting package established
* FramePlotter class created
* plotting API designed

The intended public interface is

.. code-block:: python

    frame.plot("topographic__elevation")

Circular import issues between Frame and FramePlotter were identified and successfully resolved using deferred imports together with ``TYPE_CHECKING``.

--------------------------------------------------------------------------

Notebook-Based Development Workflow
-----------------------------------

A new development workflow was adopted.

Instead of repeatedly writing standalone scripts, an interactive notebook will now serve as the primary development environment.

The notebook will be used for

* loading datasets
* inspecting geometry
* inspecting fields
* testing visualization methods
* experimenting with plotting styles
* validating API design

Once functionality becomes stable, it will be transferred into the official documentation.

--------------------------------------------------------------------------

Current Status
--------------

Completed components

.. code-block:: text

    ✓ BaseObject

    ✓ Geometry

    ✓ Field

    ✓ FieldCollection

    ✓ Frame

    ✓ Dataset

    ✓ FolderReader

    ✓ VTKReader

    ✓ Testing framework

    ✓ Plotting architecture

Current capabilities include

* automatic discovery of Landlab outputs
* management of simulation timesteps
* reading VTK files
* storage of mesh geometry
* storage of scalar fields
* clean object-oriented API

--------------------------------------------------------------------------

Plans for the Next Development Session
--------------------------------------

The next session will focus on implementing the first complete visualization workflow.

Objectives
~~~~~~~~~~

1. Preserve the original PyVista mesh inside the Frame object.

2. Modify VTKReader to store the native mesh without unnecessary triangulation.

3. Complete the first implementation of FramePlotter using PyVista as the visualization backend.

4. Achieve the first end-to-end visualization

.. code-block:: python

    frame = Frame(filename)

    VTKReader().read(frame)

    frame.plot("topographic__elevation")

5. Verify that interactive visualization correctly displays Landlab simulation outputs.

Expected Milestone
~~~~~~~~~~~~~~~~~~

By the end of the next development session, **landlab_vis** should be capable of loading a Landlab VTK file and displaying an interactive visualization using a single command.

This will represent the first complete visualization workflow implemented entirely within the new Python framework and will replace a substantial portion of the existing ParaView-based visualization process.