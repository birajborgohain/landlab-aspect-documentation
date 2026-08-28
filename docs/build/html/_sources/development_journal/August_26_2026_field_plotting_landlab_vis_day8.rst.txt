August 26, 2026 ``landlab_vis`` (Day 8) Field Profile Plotting
===============================================================

Static Field Profile Plotting
------------------------------

On August 26, development continued from field extraction to actual
visualization.

A new plotting class was created:

.. code-block:: python

   FieldProfilePlotter


The purpose of this class is to plot a one-dimensional profile obtained
from ``FieldData`` through the ``ProfileData`` representation.

The existing ``ProfilePlotter`` was originally associated with the
previous elevation-profile workflow. Rather than changing that class
and mixing two concepts, a separate ``FieldProfilePlotter`` was
introduced for profiles extracted from generic fields.

The plotting workflow is:

.. code-block:: text

   Reader
      ↓
   Frame
      ↓
   FieldData
      ↓
   ProfileData
      ↓
   FieldProfilePlotter
      ↓
   Static profile


Unit handling was explicitly established for the profile plots.

The horizontal distance is displayed in kilometres:

.. code-block:: python

   distance = self.profile.distance / 1000.0


while the field value remains in metres.

Consequently, the standard axis labels are:

.. code-block:: text

   Distance (km)

   Sediment thickness (m)


This distinction is particularly important for the current model,
whose horizontal dimensions are much larger than individual sediment
thickness values.


Static comparison of sediment thickness
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The three available sediment-thickness profiles were then extracted:

.. code-block:: text

   Landlab
       sediment_deposit__thickness

   Landlab-ASPECT
       sediment_thick

   FastScape-ASPECT
       sediment_thick


They were plotted together using:

.. code-block:: python

   FieldProfilePlotter.plot_comparison(
       [
           landlab_profile,
           landlab_aspect_profile,
           fastscape_aspect_profile,
       ],
       labels=[
           "Landlab",
           "Landlab-ASPECT",
           "FastScape-ASPECT",
       ],
       title="Sediment Thickness Profile",
   )


This established the first direct comparison of the sediment-thickness
profiles through the common ``ProfileData`` representation.

Because the Landlab sediment-thickness field has a different numerical
scale from the ASPECT sediment-thickness fields in the tested output,
the Landlab profile was also plotted separately. This prevents the
different ranges from obscuring the individual field behavior.


FieldProfileAnimation
^^^^^^^^^^^^^^^^^^^^^

The static profile workflow was then extended to time-dependent
visualization.

A new class was introduced:

.. code-block:: python

   FieldProfileAnimation


The class operates on a dataset and extracts the requested profile from
each available frame.

The workflow is therefore:

.. code-block:: text

   Dataset
      ↓
   Frame 0 ──→ FieldData ──→ ProfileData
      ↓
   Frame 1 ──→ FieldData ──→ ProfileData
      ↓
   Frame 2 ──→ FieldData ──→ ProfileData
      ↓
      ...
      ↓
   FieldProfileAnimation


The animation determines global profile limits from the complete time
series before creating the animation. This prevents the axes from
changing every time the animation advances to a new frame.

The time annotation is displayed in kyr, while the profile itself uses:

.. code-block:: text

   Distance (km)
   Sediment thickness (m)


The animation was tested first with the Landlab
``sediment_deposit__thickness`` field.

The resulting workflow was:

.. code-block:: python

   landlab_animation = FieldProfileAnimation(
       landlab,
       field="sediment_deposit__thickness",
       scenario="Landlab",
       profile=profile_spec,
       source="landlab",
   )


The animation can then be created with:

.. code-block:: python

   animation = landlab_animation.create(
       interval=250,
       xlabel="Distance (km)",
       ylabel="Sediment thickness (m)",
       title="Landlab sediment thickness evolution",
   )


and displayed inside a Jupyter Notebook using:

.. code-block:: python

   HTML(
       animation.to_jshtml()
   )


Saving animations
^^^^^^^^^^^^^^^^^

The animation class also provides a ``save()`` method.

The correct object-oriented usage is:

.. code-block:: python

   landlab_animation.save(
       output_file,
       fps=4,
       dpi=150,
   )


rather than calling ``save()`` directly on the class.

The resulting GIFs are stored under the documentation image directory:

.. code-block:: text

   docs/source/_static/images/


This makes the generated animations directly usable by the Sphinx
documentation.


Two-ASPECT profile comparison animation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After establishing the single-dataset animation, the workflow was
extended to compare the two ASPECT outputs simultaneously.

A separate class was introduced:

.. code-block:: python

   FieldProfileComparisonAnimation


The first comparison is:

.. code-block:: text

   Landlab-ASPECT
          vs.
   FastScape-ASPECT


using the common ASPECT field:

.. code-block:: text

   sediment_thick


The two datasets are supplied to the comparison animation together:

.. code-block:: python

   comparison_animation = (
       FieldProfileComparisonAnimation(
           [
               landlab_aspect,
               fastscape_aspect,
           ],
           field="sediment_thick",
           scenarios=[
               "Landlab-ASPECT",
               "FastScape-ASPECT",
           ],
           profile=profile_spec,
           source="aspect",
       )
   )


The profiles are then animated simultaneously:

.. code-block:: python

   animation = comparison_animation.create(
       interval=250,
       xlabel="Distance (km)",
       ylabel="Sediment thickness (m)",
       title=(
           "ASPECT Sediment Thickness Profile Evolution"
       ),
       labels=[
           "Landlab-ASPECT",
           "FastScape-ASPECT",
       ],
   )


The comparison animation therefore provides a synchronized view of the
two ASPECT surface-process fields as they evolve through the available
simulation frames.


Development architecture established
-------------------------------------

The work on August 25–26 established a layered architecture for field
visualization.

The current organization can be summarized as:

.. code-block:: text

   ┌─────────────────────────────────────────────┐
   │                  READERS                    │
   │                                             │
   │ Landlab │ FastScape │ ASPECT                │
   └──────────────────────┬──────────────────────┘
                          ↓
                    Dataset / Frame
                          ↓
                 Generic Field Extraction
                          ↓
                       FieldData
                          ↓
                   Profile Extraction
                          ↓
                     ProfileData
                          ↓
             ┌────────────┴────────────┐
             ↓                         ↓
      Static Profile              Animation
             ↓                         ↓
   FieldProfilePlotter      FieldProfileAnimation
                                       │
                                       ↓
                         FieldProfileComparisonAnimation


This organization deliberately separates:

* reading model output,
* identifying and loading fields,
* converting fields into a common representation,
* extracting profiles,
* producing static plots, and
* producing animations.

This separation is important for future expansion because a new model
reader or a new field should not require rewriting the plotting system.


Current supported comparison concept
------------------------------------

The current field-based workflow is already capable of treating
different output formats through a common visualization path.

For the sediment-thickness example:

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Simulation
     - Source field
     - Visualization representation
   * - Landlab
     - ``sediment_deposit__thickness``
     - ``FieldData`` → ``ProfileData``
   * - Landlab-ASPECT
     - ``sediment_thick``
     - ``FieldData`` → ``ProfileData``
   * - FastScape-ASPECT
     - ``sediment_thick``
     - ``FieldData`` → ``ProfileData``
   * - FastScape
     - Reader available; field-specific visualization to be added
       as comparable fields are identified
     - Future ``FieldData`` workflow


Future direction
----------------

The architecture developed during these two days is intentionally
broader than sediment thickness.

The current progression is:

.. code-block:: text

   1-D field profile
          ↓
   2-D field map
          ↓
   Profile line shown on map
          ↓
   Time-dependent 2-D maps
          ↓
   3-D fields
          ↓
   2-D surface fields over 3-D ASPECT geometry
          ↓
   Coupled geodynamic + surface-process visualization


Future ASPECT fields may include geodynamic quantities such as velocity
and plastic strain, together with surface-process quantities such as
sediment thickness, drainage or river information, and topography.

The same conceptual framework could eventually be extended to outputs
from additional modeling systems, including Underworld and Badlands,
provided appropriate readers and field-extraction adapters are
implemented.

The important design principle is that these future extensions should
enter through the reader and field-extraction layers rather than
requiring a separate plotting architecture for every model.


Development status at the end of August 26
------------------------------------------

At the end of this development period, the following pieces had been
established:

.. list-table::
   :header-rows: 1
   :widths: 35 45 20

   * - Component
     - Purpose
     - Status
   * - ``AspectReader``
     - Read ASPECT solution output
     - Established
   * - ``field_metadata()``
     - Describe ASPECT fields
     - Established
   * - ``load_field()``
     - Load ASPECT field arrays
     - Established
   * - ``FieldData``
     - Common field representation
     - Established
   * - ``ProfileSpec``
     - Define profile direction and position
     - Established
   * - ``ProfileData``
     - Store extracted one-dimensional field
     - Established
   * - ``extract_profile()``
     - Extract 1-D profiles from ``FieldData``
     - Established
   * - ``FieldProfilePlotter``
     - Static field-profile plotting
     - Established
   * - ``FieldProfileAnimation``
     - Single-dataset profile animation
     - Established
   * - ``FieldProfileComparisonAnimation``
     - Two-dataset profile comparison animation
     - Established
   * - 2-D field map
     - Spatial field visualization
     - Next development stage
   * - Profile line on map
     - Show cross-section location
     - Next development stage
   * - 3-D field visualization
     - ASPECT geodynamic and surface-process fields
     - Future development


The resulting framework is therefore no longer limited to a
single-purpose sediment-thickness plot. It has begun to establish a
general field-comparison and visualization architecture in which
different model outputs can be converted into common ``FieldData`` and
``ProfileData`` objects and then passed to reusable plotting and
animation classes.