ASPECT PR #7325 — macOS Installation September 2, 2026
=========================================================

This document records the terminal commands used to obtain, configure, build,
and verify ASPECT PR #7325 with Landlab on macOS.

Installation commands
---------------------

.. important::

   Run the following commands in order.

   .. code-block:: bash

      cd ~/software/sep_2_2026_biraj_fork_aspect_landlab_7325/aspect
      git fetch upstream pull/7325/head:pr-7325
      git checkout -b aspect-7325 pr-7325
      git clone https://github.com/landlab/landlab.git landlab
      source ../.venv/bin/activate
      python -m ensurepip --upgrade
      python -m pip install --upgrade pip
      python -m pip install numpy
      export DEAL_II_DIR="$HOME/software/dealii/dealii-9.7.1/install/deal.II-v9.7.0"
      mkdir -p build
      cd build
      cmake -DCMAKE_BUILD_TYPE=Release \
        -DDEAL_II_DIR="$DEAL_II_DIR" \
        -DASPECT_WITH_PYTHON=ON \
        -DPython3_EXECUTABLE="$(which python)" \
        -DPython3_NumPy_INCLUDE_DIRS="$(python -c 'import numpy; print(numpy.get_include())')" \
        ..
      make -j8
      ./aspect-release --version

Installation locations
----------------------

ASPECT PR #7325 source:

.. code-block:: text

   ~/software/sep_2_2026_biraj_fork_aspect_landlab_7325/aspect

Python virtual environment:

.. code-block:: text

   ~/software/sep_2_2026_biraj_fork_aspect_landlab_7325/.venv

deal.II 9.7.0:

.. code-block:: text

   ~/software/dealii/dealii-9.7.1/install/deal.II-v9.7.0

Landlab source:

.. code-block:: text

   ~/software/sep_2_2026_biraj_fork_aspect_landlab_7325/aspect/landlab

ASPECT build directory:

.. code-block:: text

   ~/software/sep_2_2026_biraj_fork_aspect_landlab_7325/aspect/build

Build configuration
-------------------

The build uses:

* ASPECT PR #7325.
* Landlab from the Landlab GitHub repository.
* Python from the active virtual environment.
* NumPy installed in that environment.
* deal.II 9.7.0.
* A Release build configuration.

Verification
------------

After the build completes, verify the executable with:

.. code-block:: bash

   ./aspect-release --version

Runtime Landlab coupling tests can then be performed separately.
