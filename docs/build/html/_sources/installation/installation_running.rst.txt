Setup Installation
=================================================

This guide summarizes the minimal steps required to install, configure,
and run a coupled ASPECT–Landlab simulation using Python (mpi4py).

`Landlab-ASPECT installation link <https://landlab-aspect.github.io/blog/2026/01/29/using-uv-for-python-and-c-mpi-applications/>`_

------------------------------------------------------------
1. Python Environment (uv)
------------------------------------------------------------

Install and manage Python using ``uv``:

.. code-block:: bash

   brew install uv
   mkdir /Users/biraj/software/landlab_aspect
   cd /Users/biraj/software/landlab_aspect
   git clone --recurse-submodules https://github.com/landlab-aspect/aspect
   cd aspect
   uv venv --python 3.12
   source .venv/bin/activate
   uv sync
   uv pip install numpy meshio (optional)

------------------------------------------------------------
2. Install ASPECT with Python Support
------------------------------------------------------------

Compile ASPECT with deal.II and enable Python:

.. code-block:: bash
    
   cd /Users/biraj/software/landlab_aspect/aspect
   mkdir build
   cd build
   cmake \
     -DDEAL_II_DIR=/Users/biraj/software/dealii/dealii-9.7.1/install/deal.II-v9.7.0 \
     -DASPECT_WITH_PYTHON=ON \
     -DPython3_EXECUTABLE=$(which python) \
     ..
    make -j8
    #Done

**Critical flags:**

- ``ASPECT_WITH_PYTHON=ON`` → enables coupling
- ``Python3_EXECUTABLE`` → must point to uv/conda environment

