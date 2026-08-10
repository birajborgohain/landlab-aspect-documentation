August 9, 2026, ``landlab_vis`` (day 3) 2D Profile Analysis and Comparison
===========================================================================

Today we focused mainly on building the **2D profile-analysis and comparison system** for ``landlab_vis``.

Profile Extraction
------------------

* Built and tested profile extraction from a ``Dataset``.
* Added profile location selection, including vertical cross-sections such as
  ``x = 450 m``.
* Added multiple-profile extraction across different frames/timesteps.
* Added cross-section visualization for checking the selected profile location.

Profile Comparison Across Timesteps
------------------------------------

Implemented comparison of profiles extracted from multiple frames of the same
dataset.

For example, the same cross-section can be extracted from:

* ``landlab_0001.vtk``
* ``landlab_0002.vtk``
* ``landlab_0003.vtk``
* ``landlab_0004.vtk``

The resulting profiles can be plotted together using ``ProfileCollection``.

Flexible Profile Labels
-----------------------

Added flexible legend-label strategies:

* ``filename`` -- use the source VTK filename.
* ``frame`` -- use the frame index.
* ``timestep`` -- use the simulation timestep.
* ``time`` -- use the simulation time.

This allows the labeling strategy to be changed without changing the
underlying profile data.

Unit Conversion
---------------

Implemented a general unit-conversion system.

Supported units include:

* ``m``
* ``km``
* ``s``
* ``yr``
* ``ka``
* ``Ma``
* ``m/yr``
* ``m/s``
* ``m2/yr``
* ``m2/s``
* ``m3/s``

The conversion system keeps the full numerical precision internally.
Formatting and rounding are treated as a display issue rather than changing
the scientific values.

For example, a conversion result such as::

    3.168808781402895e-08

can be displayed as::

    3.2e-08

without modifying the underlying value.

Field Metadata
--------------

Created ``field_metadata.py`` to centralize information about dataset fields.

Each registered field can contain:

* field name
* physical quantity
* default/source unit
* allowed display units
* human-readable label

For example::

    topographic__elevation
        quantity = elevation
        unit = m
        allowed_units = ("m", "km")
        label = Topographic elevation

The field metadata therefore acts as the source of truth for field units.

Metadata-Aware Profiles
-----------------------

Connected ``Profile`` to the field metadata system.

A profile now obtains its field information from ``field_metadata.py`` rather
than requiring the unit to be manually specified.

For example, ``topographic__elevation`` automatically receives::

    value_unit = "m"
    quantity = "elevation"
    allowed_units = ("m", "km")

The profile can then request a different display unit when appropriate.

Unit Validation
---------------

Added validation for requested display units.

For example, an elevation profile can be plotted in::

    m
    km

but an invalid request such as::

    y_value_unit = "yr"

is rejected because ``yr`` is not an allowed unit for
``topographic__elevation``.

This prevents scientifically meaningless unit conversions.

Human-Readable Field Labels
----------------------------

Separated the internal Landlab field name from the visualization label.

For example::

    topographic__elevation

is retained internally as the actual field name, while plots can display::

    Topographic elevation (m)

This allows the software to maintain compatibility with Landlab field names
while producing clearer scientific figures.

Two-Folder Dataset Comparison
-----------------------------

Implemented comparison of profiles from two different simulation folders.

For example::

    landlab_diffusion_standalone
    landlab_diffudion_standalone_case_2

The comparison uses the same:

* field
* frame
* profile start coordinate
* profile end coordinate
* sampling spacing
* distance unit
* Y-axis value unit

The two profiles are displayed as side-by-side subplots.

This provides a direct visual comparison between two simulations while
maintaining the same cross-section and plotting scale.

Current Development Status
--------------------------

The main **2D profile-analysis and comparison foundation** is now working.

The current workflow can be summarized as::

    Dataset
        |
        v
    Frame
        |
        v
    Profile extraction
        |
        v
    ProfileCollection
        |
        +----------------------+
        |                      |
        v                      v
    Field metadata        Unit conversion
        |                      |
        +----------+-----------+
                   |
                   v
            Profile plotting
                   |
          +--------+--------+
          |                 |
          v                 v
    Timestep comparison   Two-folder comparison

Features intentionally postponed for later development include:

* 3D visualization
* profile-difference analysis
* RMSE and other profile-comparison statistics
* normalized profile comparison
* profile animation
* more advanced visualization features

Next Step
---------

The next phase is to begin **detailed software documentation**.

The documentation will include not only what was implemented, but also:

* the purpose of each class and method
* why each ``def`` is located where it is
* how the different modules interact
* unit-handling decisions
* field-metadata design
* testing procedures
* errors encountered during development
* how those errors were diagnosed and fixed
* important questions and design decisions raised during development
* examples showing how users should interact with the software