August 12, 2026 – Badlands Study (Day 2) and landlab_vis Documentation Development (Day 5)
===========================================================================================

Main Activities
----------------

1. **Badlands – Day 2: Website, Documentation, and Algorithm Review**

   Continued studying Badlands as part of the second day of the Badlands
   review. The focus was mainly on the Badlands website and documentation,
   with additional attention to understanding the underlying algorithms and
   overall model workflow.

   The goal was to develop a clearer understanding of how the Badlands model
   is structured, how its major components work together, and how the
   algorithms are implemented. Relevant information was summarized for
   future reference and comparison with other landscape-evolution models.

2. **landlab_vis – Day 5: Source Code and Documentation**

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