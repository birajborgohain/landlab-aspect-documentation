In NMT HPC ``lla_checkpoint- ASPECT-3.1.10`` Installation: ASPECT 3.1.0-pre with Landlab
============================================================================================

.. important::

   ::

      mkdir -p ~/software && cd ~/software

      curl -L -o 28c914f48.tar.gz \
        https://github.com/landlab-aspect/aspect/archive/28c914f482fe5d9bba409267d534e66ee5602ceb.tar.gz

      tar -xzf 28c914f48.tar.gz

      mv aspect-28c914f482fe5d9bba409267d534e66ee5602ceb \
        aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

      cd ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

      rm -rf landlab

      git clone https://github.com/landlab/landlab.git landlab

      curl -LsSf https://astral.sh/uv/install.sh | sh

      export PATH="$HOME/.local/bin:$PATH"

      uv venv --python 3.12

      uv sync

      source .venv/bin/activate

      srun -p comptest --qos=compile -N1 -n1 \
        --cpus-per-task=8 --time=00:45:00 --pty bash

      module load external/dealii-for-aspect/9.7.0

      export ASPECT_DIR="$HOME/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact"

      export BUILD_TYPE=DebugRelease

      export PYTHON="$ASPECT_DIR/.venv/bin/python"

      mkdir -p "$ASPECT_DIR/build"

      cd "$ASPECT_DIR/build"

      cmake \
        -DDEAL_II_DIR="$DEAL_II_DIR" \
        -DASPECT_USE_FP_EXCEPTIONS=OFF \
        -DASPECT_WITH_PYTHON=ON \
        -DPython3_EXECUTABLE="$PYTHON" \
        -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
        -DCMAKE_CXX_FLAGS="-Wno-deprecated-declarations -std=c++11 -Wno-unused-variable -Wno-maybe-uninitialized" \
        ../

      make -j8

      ./aspect-release --version


ASPECT MPI Version Test
^^^^^^^^^^^^^^^^^^^^^^^

The ASPECT executable can be tested using ``mpirun`` with one MPI process::

   mpirun -np 1 ./aspect-release --version

The successful output is:

.. code-block:: text

   Could not find platform dependent libraries <exec_prefix>

   -----------------------------------------------------------------------------

   --                             This is ASPECT                              --

   -- The Advanced Solver for Planetary Evolution, Convection, and Tectonics. --

   -----------------------------------------------------------------------------

   --     . version 3.1.0-pre
   --     . using deal.II 9.7.0
   --     .       with 32 bit indices
   --     .       with vectorization level 3 (AVX512, 8 doubles, 512 bits)
   --     . using Trilinos 16.2.0
   --     . using p4est 2.8.7
   --     . using Geodynamic World Builder 1.0.0
   --     . running in OPTIMIZED mode
   --     . running with 1 MPI process
   -----------------------------------------------------------------------------


Run ASPECT with SLURM
^^^^^^^^^^^^^^^^^^^^^

The following SLURM script runs the ASPECT ``convection-box.prm`` example
using 8 MPI processes on one NMT HPC compute node.

.. code-block:: bash

   #!/bin/bash
   #SBATCH --job-name=convection_box
   #SBATCH --partition=comptest
   #SBATCH --qos=compile
   #SBATCH --nodes=1
   #SBATCH --ntasks=8
   #SBATCH --cpus-per-task=1
   #SBATCH --time=01:00:00
   #SBATCH --output=convection_box_%j.out
   #SBATCH --error=convection_box_%j.err

   module load external/dealii-for-aspect/9.7.0

   ASPECT_DIR="$HOME/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact"

   source "$ASPECT_DIR/.venv/bin/activate"

   cd /home/900369162/hpc_cookbooks/convection-box

   pwd
   ls -l convection-box.prm

   mpirun -np "$SLURM_NTASKS" \
       "$ASPECT_DIR/build/aspect-release" \
       convection-box.prm


Submit the job
^^^^^^^^^^^^^^

Save the script as ``convection_box.slurm`` and submit it with::

   sbatch convection_box.slurm

Check the job status with::

   squeue -u 900369162

The SLURM output is written to::

   convection_box_<JOBID>.out

and errors are written to::

   convection_box_<JOBID>.err


Transfer output from NMT to Mac Studio
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. important::

   Run the following ``rsync`` command from the **Mac Terminal**, not from
   the NMT HPC terminal::

      rsync -avh --progress \
          900369162@nmthpc.id.nmt.edu:/home/900369162/data/hpc_cookbooks/3d_ada_HPC/ \
          /Users/biraj/cookbook_biraj/HPC_Linux_NMT/


This confirms that the ASPECT executable was successfully compiled and can
be launched through the NMT OpenMPI environment with one MPI process.

This document describes the installation of ASPECT ``3.1.0-pre`` with the
Landlab checkpointing modifications on the **NMT HPC system**.

The installation uses the exact ASPECT commit
``28c914f482fe5d9bba409267d534e66ee5602ceb`` (short commit
``28c914f48``).

The complete workflow consists of:

#. Downloading the exact ASPECT source code.
#. Cloning Landlab into the ASPECT source directory.
#. Installing ``uv``.
#. Creating the Python 3.12 virtual environment.
#. Installing the Python dependencies with ``uv sync``.
#. Requesting an HPC compute node using SLURM.
#. Loading the NMT ``deal.II`` environment.
#. Setting the ASPECT and Python environment variables.
#. Configuring ASPECT with CMake.
#. Compiling ASPECT.
#. Verifying the installation.

.. important::

   **ASPECT version used in this installation**

   ``ASPECT 3.1.0-pre``

   Exact commit::

      28c914f482fe5d9bba409267d534e66ee5602ceb

   Short commit::

      28c914f48


Download and prepare ASPECT
---------------------------

The first part of the installation is performed from the NMT HPC login
node.

Create the software directory and enter it::

   mkdir -p ~/software && cd ~/software

Download the exact ASPECT source archive::

   curl -L -o 28c914f48.tar.gz \
     https://github.com/landlab-aspect/aspect/archive/28c914f482fe5d9bba409267d534e66ee5602ceb.tar.gz

Extract the archive::

   tar -xzf 28c914f48.tar.gz

Rename the extracted directory::

   mv aspect-28c914f482fe5d9bba409267d534e66ee5602ceb \
     aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

The resulting directory is::

   ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

The directory name records the ASPECT version, the Landlab checkpointing
modification, and the exact source commit.


Clone Landlab
-------------

Enter the ASPECT source directory::

   cd ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

Remove an existing Landlab directory, if present::

   rm -rf landlab

Clone Landlab directly into the ASPECT source tree::

   git clone https://github.com/landlab/landlab.git landlab

After cloning, the directory structure contains::

   aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/
   ├── landlab/
   ├── source/
   ├── include/
   ├── CMakeLists.txt
   └── ...

The Landlab source is therefore available directly inside the ASPECT source
tree.


Install ``uv`` and create the Python environment
-------------------------------------------------

Install ``uv`` using the official installer::

   curl -LsSf https://astral.sh/uv/install.sh | sh

Add the ``uv`` installation directory to the ``PATH``::

   export PATH="$HOME/.local/bin:$PATH"

Create a Python 3.12 virtual environment::

   uv venv --python 3.12

Install the Python dependencies::

   uv sync

The ``uv sync`` command installs the dependencies specified by the project
configuration and creates the Python environment in::

   .venv/

Activate the environment::

   source .venv/bin/activate

Verify Python::

   python --version

Verify Landlab::

   python -c "import landlab; print('Landlab:', landlab.__version__)"

Verify ``mpi4py``::

   python -c "import mpi4py; print('mpi4py:', mpi4py.__version__)"

For the tested NMT HPC installation, the environment reported:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Package
     - Version
   * - Python
     - ``3.12.13``
   * - Landlab
     - ``2.11.1.dev0``
   * - mpi4py
     - ``4.1.1``


Why ``uv`` and ``.venv`` are used
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ASPECT--Landlab coupling requires Python packages such as Landlab and
``mpi4py``.

The Python virtual environment keeps these packages separate from the
system Python installation provided by the HPC system.

This is particularly important when configuring ASPECT with CMake because
the system may contain multiple Python installations. The Python interpreter
used by CMake should be the same interpreter associated with the environment
containing Landlab and ``mpi4py``.


Request an HPC compile node with SLURM
--------------------------------------

After preparing the source code and Python environment, request an HPC
compute node for compilation.

Run the following command from the HPC login node::

   srun -p comptest --qos=compile -N1 -n1 \
     --cpus-per-task=8 --time=00:45:00 --pty bash

This requests an interactive compilation node.

The SLURM options mean:

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Option
     - Meaning
   * - ``-p comptest``
     - Use the ``comptest`` partition.
   * - ``--qos=compile``
     - Use the compile quality-of-service configuration.
   * - ``-N1``
     - Request one compute node.
   * - ``-n1``
     - Request one task.
   * - ``--cpus-per-task=8``
     - Allocate eight CPUs to the task.
   * - ``--time=00:45:00``
     - Request up to 45 minutes.
   * - ``--pty bash``
     - Start an interactive Bash shell on the allocated compute node.

Once the allocation starts, the prompt should indicate a compute node such
as::

   [I have no name!@nmthpc-node1 ...]

The compute node can be verified with::

   hostname

For the tested installation, the hostname was::

   nmthpc-node1.id.nmt.edu

The SLURM allocation can also be checked with::

   echo "$SLURM_JOB_ID"
   echo "$SLURM_CPUS_PER_TASK"
   echo "$SLURM_JOB_PARTITION"

For the tested allocation, these reported eight CPUs and used the
``comptest`` partition.


Why SLURM is required
^^^^^^^^^^^^^^^^^^^^^

The login node is primarily intended for interactive work, file management,
and job submission.

Compiling ASPECT is computationally intensive. The SLURM allocation provides
dedicated compute resources for the compilation.

The ``--cpus-per-task=8`` option allocates eight CPUs. Therefore, the
compilation should use eight parallel processes.


Load the NMT deal.II environment
--------------------------------

After entering the SLURM compute node, load the NMT ASPECT-compatible
``deal.II`` environment::

   module load external/dealii-for-aspect/9.7.0

Verify the installed software::

   which cmake
   which gcc
   which g++
   which mpirun
   echo "$DEAL_II_DIR"

Check the versions::

   cmake --version
   gcc --version
   mpirun --version

The tested NMT environment provides:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Software
     - Version
   * - GCC
     - ``14.2.0``
   * - OpenMPI
     - ``4.1.8``
   * - CMake
     - ``3.26.4``
   * - deal.II
     - ``9.7.0``

The ``DEAL_II_DIR`` variable should point to::

   /usr/local/software/gcc-14.2.0/openmpi-4.1.8/dealii/9.7.0/deal.II-v9.7.0


Why the deal.II module is required
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ASPECT is built using the deal.II finite-element library.

The ``DEAL_II_DIR`` variable tells CMake where the NMT installation of
deal.II is located.

Loading the module also provides the compiler, MPI, CMake, and associated
software environment expected by this deal.II installation.


Set the ASPECT build environment
--------------------------------

Enter the ASPECT source directory::

   cd ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

Activate the Python environment::

   source .venv/bin/activate

Set the ASPECT source directory::

   export ASPECT_DIR="$HOME/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact"

Set the build type::

   export BUILD_TYPE=DebugRelease

Set the Python interpreter::

   export PYTHON="$ASPECT_DIR/.venv/bin/python"

Verify the variables::

   echo "$ASPECT_DIR"
   echo "$BUILD_TYPE"
   echo "$PYTHON"
   echo "$DEAL_II_DIR"

The expected values are similar to::

   /home/900369162/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

   DebugRelease

   /home/900369162/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/.venv/bin/python

   /usr/local/software/gcc-14.2.0/openmpi-4.1.8/dealii/9.7.0/deal.II-v9.7.0


Why the Python executable is specified explicitly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The HPC system can contain multiple Python installations.

For this installation, the required Python packages are installed inside
the ASPECT ``.venv`` environment. Therefore, CMake should use::

   $ASPECT_DIR/.venv/bin/python

rather than an unrelated system Python installation.

This is specified with::

   -DPython3_EXECUTABLE="$PYTHON"


Configure ASPECT with CMake
---------------------------

Create the ASPECT build directory::

   cd "$ASPECT_DIR"

   mkdir -p build

Enter the build directory::

   cd build

The ASPECT configuration uses::

   cmake \
     -DDEAL_II_DIR="$DEAL_II_DIR" \
     -DASPECT_USE_FP_EXCEPTIONS=OFF \
     -DASPECT_WITH_PYTHON=ON \
     -DPython3_EXECUTABLE="$PYTHON" \
     -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
     -DCMAKE_CXX_FLAGS="-Wno-deprecated-declarations -std=c++11 -Wno-unused-variable -Wno-maybe-uninitialized" \
     ../

The main CMake options are:

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Option
     - Purpose
   * - ``DEAL_II_DIR``
     - Specifies the NMT deal.II installation.
   * - ``ASPECT_USE_FP_EXCEPTIONS=OFF``
     - Disables ASPECT floating-point exception handling.
   * - ``ASPECT_WITH_PYTHON=ON``
     - Enables ASPECT Python functionality.
   * - ``Python3_EXECUTABLE``
     - Specifies the Python interpreter in ``.venv``.
   * - ``CMAKE_BUILD_TYPE``
     - Specifies the selected ASPECT build configuration.
   * - ``CMAKE_CXX_FLAGS``
     - Provides the additional C++ compiler flags used in this build.
   * - ``../``
     - Specifies the ASPECT source directory relative to ``build/``.

During configuration, CMake checks the compiler, MPI, deal.II, Python, and
other dependencies required by ASPECT.


Compile ASPECT
--------------

After CMake completes successfully, compile ASPECT using the eight CPUs
allocated through SLURM::

   make -j8

Alternatively::

   cmake --build . --parallel 8


Why ``make -j8`` is used
^^^^^^^^^^^^^^^^^^^^^^^^

The SLURM allocation requested eight CPUs with::

   --cpus-per-task=8

Therefore, ``make -j8`` uses the eight CPUs allocated to the compilation.

Using ``make -j64`` would request 64 parallel compilation processes even
though only eight CPUs were allocated to this SLURM job.


Verify the installation
-----------------------

After the compilation finishes, check the ASPECT executable::

   ls -lh aspect-release

Then run::

   ./aspect-release --version

A successful installation should report information similar to::

   -----------------------------------------------------------------------------
   --                             This is ASPECT                              --
   -- The Advanced Solver for Planetary Evolution, Convection, and Tectonics. --
   -----------------------------------------------------------------------------
   --     . version 3.1.0-pre
   --     . using deal.II 9.7.0
   --     .       with 32 bit indices
   --     .       with vectorization level 3 (AVX512, 8 doubles, 512 bits)
   --     . using Trilinos 16.2.0
   --     . using p4est 2.8.7
   --     . using Geodynamic World Builder 1.0.0
   --     . running in OPTIMIZED mode
   --     . running with 1 MPI process
   -----------------------------------------------------------------------------


Complete NMT HPC installation sequence
---------------------------------------

The following sequence summarizes the complete installation procedure.


Prepare ASPECT and Landlab
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run these commands on the HPC login node::

   mkdir -p ~/software && cd ~/software

   curl -L -o 28c914f48.tar.gz \
     https://github.com/landlab-aspect/aspect/archive/28c914f482fe5d9bba409267d534e66ee5602ceb.tar.gz

   tar -xzf 28c914f48.tar.gz

   mv aspect-28c914f482fe5d9bba409267d534e66ee5602ceb \
     aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

   cd aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

   rm -rf landlab

   git clone https://github.com/landlab/landlab.git landlab


Create the Python environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

   curl -LsSf https://astral.sh/uv/install.sh | sh

   export PATH="$HOME/.local/bin:$PATH"

   uv venv --python 3.12

   uv sync


Request the HPC compile node
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

   srun -p comptest --qos=compile -N1 -n1 \
     --cpus-per-task=8 --time=00:45:00 --pty bash


Load deal.II and prepare the environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run these commands inside the allocated compute node::

   module load external/dealii-for-aspect/9.7.0

   cd ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

   source .venv/bin/activate

   export ASPECT_DIR="$HOME/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact"

   export BUILD_TYPE=DebugRelease

   export PYTHON="$ASPECT_DIR/.venv/bin/python"


Configure and compile ASPECT
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

   mkdir -p "$ASPECT_DIR/build"

   cd "$ASPECT_DIR/build"

   cmake \
     -DDEAL_II_DIR="$DEAL_II_DIR" \
     -DASPECT_USE_FP_EXCEPTIONS=OFF \
     -DASPECT_WITH_PYTHON=ON \
     -DPython3_EXECUTABLE="$PYTHON" \
     -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
     -DCMAKE_CXX_FLAGS="-Wno-deprecated-declarations -std=c++11 -Wno-unused-variable -Wno-maybe-uninitialized" \
     ../

   make -j8


Verify the executable
^^^^^^^^^^^^^^^^^^^^^

::

   ls -lh aspect-release

   ./aspect-release --version

The successful completion of these steps provides an NMT HPC installation of
ASPECT ``3.1.0-pre`` with the Landlab checkpointing modifications at commit
``28c914f48``.