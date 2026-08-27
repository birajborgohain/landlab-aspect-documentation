August 23, 2026 — Landlab-Vis Development ``landlab_vis`` (day 6)
==================================================================

August 23 focused on developing the ``landlab_vis`` framework for
Landlab--FastScape comparison and visualization. A dedicated
``FastScapeReader`` was implemented to read FastScape topography, basement,
and sea-level VTK files and assemble them into ``Dataset`` and ``Frame``
objects. The ``DatasetReader`` was improved to obtain Landlab output times
from VTK series metadata rather than assuming a fixed timestep, allowing
different simulations to use different timestep sizes.

The Landlab and FastScape datasets were then matched using physical
simulation time. Their horizontal coordinates were verified to be identical,
allowing direct point-by-point comparison of elevation. RMSE and maximum
topographic differences were calculated through time, providing a basis for
quantitative model comparison.

A reusable ``ProfileComparison`` class was developed to automate profile
extraction, map visualization, time matching, and animation. Users can
select the Landlab and FastScape folders, fields, profile direction and
position, axis limits, and Crameri scientific colour maps. The resulting
animation combines the evolving Landlab--FastScape profiles with maps showing
the cross-section location. GIF output with optional reflected playback was
also implemented.

Testing was added for ``ProfileComparison``, and a cookbook example was
created to document the workflow and show how it can be applied to new
Landlab--FastScape datasets. Overall, the work moved the comparison workflow
from notebook-based analysis toward a reusable and testable
``landlab_vis`` library.