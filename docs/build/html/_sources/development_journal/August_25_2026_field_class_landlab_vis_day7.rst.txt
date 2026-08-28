August 25, 2026 ``landlab_vis`` (day 7) Field-Based Cross-Section and Animation Framework
=============================================================================================


On August 25, 2026, the visualization framework was developed
further so that fields from the four simulation scenarios can be handled
through a common field-based workflow.

The main objective was to move away from writing separate plotting logic
for each simulation output and instead establish a reusable sequence:

.. code-block:: text

   Reader
      ↓
   Dataset / Frame
      ↓
   Generic Field extraction
      ↓
   FieldData
      ↓
   Profile extraction
      ↓
   ProfileData
      ↓
   Static profile plot / Profile animation


The four simulation scenarios considered in this development are:

* Landlab
* FastScape
* Landlab-ASPECT
* FastScape-ASPECT

The work specifically focused on making comparable surface-process
fields accessible through the same field/profile visualization framework.
The sediment-thickness field was used as the first test case.


August 25, 2026
----------------

Field Metadata and Sediment-Field Investigation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The development began with an investigation of the ASPECT output fields
and their metadata. The ``AspectFrame.field_metadata()`` method was
examined and was found to require a field name as an argument.

The implemented interface is:

.. code-block:: python

   field_metadata(
       field: str,
   ) -> dict

The method determines whether a requested field exists in
``mesh.point_data`` or ``mesh.cell_data`` and returns information such
as:

* field name,
* field location,
* array shape,
* data type, and
* number of components.

For example, the ASPECT ``sediment_thick`` field was found to have:

.. code-block:: text

   name:       sediment_thick
   location:   point
   shape:      (486000,)
   dtype:      float32
   components: 1


The ``load_field()`` method was also examined. It provides the actual
NumPy array corresponding to a requested ASPECT field.

This established an important separation:

.. code-block:: text

   field_metadata()
          ↓
   describe a field

   load_field()
          ↓
   obtain field values


Comparison of ``sediment`` and ``sediment_thick``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The relationship between the ASPECT ``sediment`` and
``sediment_thick`` fields was investigated.

For the FastScape-ASPECT output, both fields were populated:

.. code-block:: text

   sediment
       min:      -0.025965646
       max:       0.60746586
       mean:      0.0016370164
       nonzero:   14492

   sediment_thick
       min:      -115.66396
       max:      2814.1763
       mean:      7.405662
       nonzero:   14496


The correlation between the two fields was approximately:

.. math::

   r = 0.9664

A linear fit gave approximately:

.. math::

   sediment\_thick
   \approx
   4505.94\,sediment + 0.0294


This demonstrated that the two fields are strongly related, but are not
simply identical fields.

The investigation also found a small number of negative values in the
ASPECT output. These were retained during the diagnostic investigation
rather than being silently removed.

Vertical-position investigation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The sediment fields were also examined against ASPECT vertical
coordinates.

At one representative vertical column, the following values were
observed:

.. code-block:: text

       z (m)          sediment       sediment_thick

       145008.109       0.220233          1187.262
       147510.766       0.339854          1688.609
       150013.422       0.607466          2814.176


A vertical integration test gave:

.. code-block:: text

   Vertical integral of sediment: 1886.26

   Top sediment_thick:
       2814.1763

   Bottom sediment_thick:
       0.0


This investigation was important because it established that
``sediment_thick`` should be treated as the field to visualize for the
surface sediment-thickness comparison rather than assuming that
``sediment`` itself represented the same physical quantity.

The investigation also confirmed that the ASPECT field extraction
machinery was able to recover the surface field needed for subsequent
profile visualization.


Transition toward a generic field workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The next development step was to avoid building plotting routines that
were tied directly to one particular model or one particular field.

The desired architecture became:

.. code-block:: text

   Landlab reader
   FastScape reader
   ASPECT reader
          ↓
       Dataset
          ↓
        Frame
          ↓
   Generic field extraction
          ↓
       FieldData
          ↓
     Profile extraction
          ↓
      ProfileData
          ↓
      Plotting classes


This design makes the field extraction layer independent from the
plotting layer.

The immediate test field was sediment thickness:

.. code-block:: text

   Landlab
       sediment_deposit__thickness

   Landlab-ASPECT
       sediment_thick

   FastScape-ASPECT
       sediment_thick


FieldData
^^^^^^^^^

A generic ``FieldData`` representation was introduced as the common
representation between readers and visualization.

The extracted object contains information such as:

* field name,
* simulation scenario,
* simulation time,
* field values,
* x coordinates,
* y coordinates, and
* z coordinates.

For the ASPECT surface fields, the extraction process produced a
two-dimensional horizontal representation suitable for subsequent
profile extraction.

This was a major architectural step because the plotting code no longer
needs to know how the original ASPECT mesh or Landlab grid was stored.


ProfileSpec and ProfileData
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A ``ProfileSpec`` class was used to describe the requested profile.

For example:

.. code-block:: python

   profile_spec = ProfileSpec(
       direction="x",
       position="middle",
   )


For an ``x``-directed profile, the implementation finds the horizontal
coordinate corresponding to the requested ``y`` position and extracts
the field values along ``x``.

For a ``y``-directed profile, the corresponding ``x`` position is used
and the field is extracted along ``y``.

The extracted result is represented by ``ProfileData``.

This produces another clean separation:

.. code-block:: text

   FieldData
       ↓
   ProfileSpec
       ↓
   extract_profile()
       ↓
   ProfileData


This means that the profile extraction operation is independent of the
eventual plotting method.


