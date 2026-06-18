Linking Local Simulation Output Folders with Sphinx Documentation
=================================================================

Motivation
----------

In computational geodynamics and Earth-system modeling workflows,
simulation outputs are often generated in external directories outside
the Sphinx documentation project.

Manually copying figures into the documentation directory becomes:

- inefficient
- error-prone
- difficult to maintain
- non-reproducible

A more scalable and professional approach is to connect simulation
output folders directly to the Sphinx documentation system using
symbolic links.

This enables:

- automatic access to simulation figures
- live-updating documentation
- reproducible scientific workflows
- no duplication of data
- seamless integration between simulations and documentation

Scientific Workflow
-------------------

::

    ASPECT / Landlab Simulation Output
                    ↓
             Symbolic Links
                    ↓
           Sphinx Documentation
                    ↓
            HTML / PDF Output

Example Project Structure
-------------------------

::

    project/
    │
    ├── simulations/
    │   ├── benchmark_001/
    │   │   └── output/
    │   │       ├── topography.png
    │   │       └── velocity.png
    │   │
    │   └── plume_test/
    │       └── output/
    │
    ├── docs/
    │   └── source/
    │       └── _static/
    │           └── figures/

Creating a Symbolic Link
------------------------

Suppose the simulation output directory is:

::

    /Users/biraj/aspect_runs/benchmark_001/output

and the Sphinx project root is:

::

    /Users/biraj/NMT_Biraj/readthedoc_biraj/cpp_geodynamics_coupling

Step 1 — Navigate to Project Root
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    cd ~/NMT_Biraj/readthedoc_biraj/cpp_geodynamics_coupling

Step 2 — Create Figures Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    mkdir -p docs/source/_static/figures

Step 3 — Create Symbolic Link
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    ln -s \
    /Users/biraj/aspect_runs/benchmark_001/output \
    docs/source/_static/figures/benchmark_001

Understanding the Symbolic Link
--------------------------------

This creates:

::

    docs/source/_static/figures/benchmark_001

which behaves like a local directory inside the Sphinx project,
but actually points to:

::

    /Users/biraj/aspect_runs/benchmark_001/output

No files are copied.

The documentation now directly accesses the live simulation output.

Verifying the Link
------------------

Run:

.. code-block:: bash

    ls -l docs/source/_static/figures

Expected output:

::

    benchmark_001 -> /Users/biraj/aspect_runs/benchmark_001/output

The arrow (``->``) indicates a symbolic link.

Using Figures in reStructuredText
---------------------------------

.. code-block:: rst

    .. figure:: /_static/figures/benchmark_001/topography.png
       :width: 80%
       :align: center

       ASPECT benchmark topography evolution.

Using Figures in MyST Markdown
------------------------------

.. code-block:: md

    ```{figure} /_static/figures/benchmark_001/topography.png
    :width: 80%
    :align: center

    ASPECT benchmark topography evolution.
    ```

Advantages of This Workflow
----------------------------

1. No Manual Copying
~~~~~~~~~~~~~~~~~~~~

Figures remain in the original simulation directories.

2. Automatic Updates
~~~~~~~~~~~~~~~~~~~~

Whenever simulations regenerate figures, the documentation
automatically reflects the latest outputs after rebuilding Sphinx.

3. Reproducible Scientific Workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simulation results and documentation remain directly connected.

4. Scalable for Large Projects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This workflow is ideal for:

- ASPECT benchmarks
- Landlab coupling experiments
- erosion simulations
- HPC workflows
- machine-learning experiments
- parameter studies

Example Scientific Workflow
---------------------------

::

    Run Simulation
            ↓
    Generate Figures
            ↓
    Symbolic Link Exposes Outputs
            ↓
    Sphinx Rebuild
            ↓
    Updated HTML / PDF Documentation

Important Note About Online Hosting
-----------------------------------

Absolute local paths such as:

::

    /Users/biraj/...

exist only on the local machine.

If the documentation is later hosted online using Read the Docs
or GitHub Pages, external local paths will not exist on the server.

For online deployment, figures should eventually be:

- committed into the repository
OR
- generated automatically during the documentation build process

However, for local scientific workflows and active research
development, symbolic links provide an extremely efficient and
professional solution.