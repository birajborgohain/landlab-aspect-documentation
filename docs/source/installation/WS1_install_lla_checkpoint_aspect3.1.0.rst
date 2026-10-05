In Linux (WS1 NMT) ``lla_checkpoint`` installation Landlab-ASPECT commit version 1rst sept 2026
=========================================================================================================

.. important::

   If the installation must be performed **only from the terminal without
   using the installation ``.sh`` script**, the following commands are the
   minimum sequence needed on WS1. These commands reproduce the essential
   installation steps: obtain the exact ASPECT source, clone Landlab, create
   the Python environment, load the NMT deal.II environment, configure ``ASPECT 3.1.0-pre (lla-checkpointing, 28c914f48)``
   with Python support, and build it.

   .. code-block:: bash

      mkdir -p ~/software && cd ~/software

      curl -L -o 28c914f48.tar.gz \
        https://github.com/landlab-aspect/aspect/archive/28c914f482fe5d9bba409267d534e66ee5602ceb.tar.gz

      tar -xzf 28c914f48.tar.gz
      mv aspect-28c914f482fe5d9bba409267d534e66ee5602ceb \
        aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

      cd aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact
      rm -rf landlab
      git clone https://github.com/landlab/landlab.git landlab

      curl -LsSf https://astral.sh/uv/install.sh | sh

      export PATH="$HOME/.local/bin:$PATH"
      uv venv --python 3.12
      uv sync

      source /usr/local/software/gcc-14.2.0/openmpi-4.1.8/dealii/9.7.0/configuration/enable.sh

      mkdir build && cd build
      cmake -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
        -DDEAL_II_DIR="$DEAL_II_DIR" \
        -DASPECT_WITH_PYTHON=ON \
        -DPython3_EXECUTABLE="../.venv/bin/python" \
        ..
      make -j8

   The resulting executable is::

      ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/build/aspect-release




Alternatively, Installation Using ``.sh`` Script
------------------------------------------------

The following Bash installer automates the installation of ASPECT
``3.1.0-pre-lla-checkpointing`` with Landlab checkpointing on a **Linux workstation**.

.. important::

   **ASPECT 3.1.0-pre (lla-checkpointing, 28c914f48) installation using
   the Bash script**

   Download the installation script:

   :download:`Download install_lla_check_point_aspect_3.1.0_uv.sh
   <../_script/WS1_install_lla_checkpoint_aspevct_3.1.0.sh>`

   Make the script executable and run it from the terminal::

       chmod +x install_lla_check_point_aspect_3.1.0_uv.sh
       ./install_lla_check_point_aspect_3.1.0_uv.sh

   If all required software and dependencies are available, the installer
   completes the full installation automatically. If a required component
   is missing or an installation step fails, the script stops and reports
   the error and the corresponding installation step where the problem
   occurred.

Successful Installation Verification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After the installation and build complete successfully, running the ASPECT
executable with 

.. code:: bash

    ./build/aspect-release --version

should produce output similar to the following::

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

This confirms that ASPECT ``3.1.0-pre`` was successfully built and is using
the expected ``deal.II 9.7.0`` and supporting libraries.

.. important::

   **Before running ASPECT with MPI**

   Activate the Python virtual environment and set the Landlab source path::

       source ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/.venv/bin/activate

       export PYTHONPATH="$HOME/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/landlab/src:$PYTHONPATH"

   Then run ASPECT with MPI, for example using 8 processes::

       mpirun -np 8 \
           ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/build/aspect-release \
           3d_64c1t1s1ob1c1_copy_1_fastscape.prm

   Make sure ``(.venv)`` appears in the terminal prompt before running
   ASPECT. The ``PYTHONPATH`` setting allows the ASPECT embedded Python
   interpreter to find the Landlab source.

Overview
--------

This document records the complete installation of the ASPECT 3.1.0-pre
version containing the Landlab checkpointing work on the NMT WS1 workstation.

The goal of the installation was to create a clean and reproducible
environment for developing and testing the ASPECT--Landlab coupling through
Python and MPI.

The final installation contains:

* ASPECT 3.1.0-pre at the exact commit
  ``28c914f482fe5d9bba409267d534e66ee5602ceb``;
* Landlab cloned directly from GitHub;
* Python 3.12;
* a ``uv``-managed Python virtual environment;
* NumPy and ``mpi4py``;
* the NMT GCC, OpenMPI, CMake, and deal.II environment;
* ASPECT compiled with Python support;
* an explicitly specified ``DEAL_II_DIR``;
* a selectable Debug or Release build; and
* a successful standard ASPECT cookbook test.

The final installation directory is::

   ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

The installation is automated by::

   install_lla_checkpoint_aspect_3.1.0_ws1.sh


Installation Objective
----------------------

The main objective was to install the specific ASPECT source containing the
Landlab checkpointing implementation and prepare it for Python-based
Landlab coupling.

The installation was intentionally performed as a new, independent
installation rather than modifying an existing ASPECT or Landlab checkout.

The desired source relationship is::

   ASPECT
      |
      +-- exact checkpointing source
      |
      +-- local Landlab Git repository
      |
      +-- local Python 3.12 environment
      |
      +-- mpi4py
      |
      +-- NMT MPI/deal.II environment

This structure makes it easier to determine which source, Python
environment, and external libraries are being used.


Installation Environment
------------------------

The installation was performed on the NMT WS1 workstation.

The important software versions are:

.. list-table::
   :header-rows: 1
   :widths: 25 35 40

   * - Software
     - Version
     - Purpose
   * - ASPECT
     - 3.1.0-pre
     - Geodynamics solver
   * - ASPECT commit
     - ``28c914f482fe5d9bba409267d534e66ee5602ceb``
     - Exact checkpointing source
   * - Landlab
     - GitHub ``master`` at installation
     - Landscape evolution model
   * - Python
     - 3.12
     - Python coupling
   * - uv
     - 0.12.7 during installation
     - Python environment manager
   * - GCC
     - 14.2.0
     - C/C++ compiler
   * - OpenMPI
     - 4.1.8
     - MPI communication
   * - CMake
     - 3.26.4
     - Build system
   * - deal.II
     - 9.7.0
     - Finite-element library
   * - Trilinos
     - 16.2.0
     - Linear algebra and solver infrastructure
   * - p4est
     - 2.8.7
     - Parallel mesh infrastructure
   * - Geodynamic World Builder
     - 1.0.0
     - ASPECT dependency


Final Directory Structure
-------------------------

The final installation has the following general structure::

   ~/software/
   |
   +-- aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/
       |
       +-- CMakeLists.txt
       +-- source/
       +-- cookbooks/
       +-- contrib/
       |
       +-- landlab/
       |   |
       |   +-- pyproject.toml
       |   +-- landlab/
       |   +-- src/
       |   +-- tests/
       |   +-- docs/
       |   +-- ...
       |
       +-- .venv/
       |   |
       |   +-- bin/
       |       +-- python
       |       +-- ...
       |
       +-- build/
           |
           +-- aspect-release
           +-- CMakeCache.txt
           +-- ...

The important point is that ``landlab/`` is an independent Git repository
cloned directly from GitHub. It was not copied from another local Landlab
checkout.


Exact ASPECT Source
-------------------

The required ASPECT commit was::

   28c914f482fe5d9bba409267d534e66ee5602ceb

The short commit identifier used in the installation directory name is::

   28c914f48

The original plan was to clone ASPECT and then check out this commit.


Problem: ASPECT Git Checkout
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The initial approach attempted to use::

   git clone https://github.com/landlab-aspect/aspect.git

followed by::

   git checkout 28c914f482fe5d9bba409267d534e66ee5602ceb

The clone succeeded, but the checkout failed with::

   fatal: reference is not a tree:
   28c914f482fe5d9bba409267d534e66ee5602ceb

The requested commit was not available in the local Git object database.

This was also checked with::

   git cat-file -t 28c914f482fe5d9bba409267d534e66ee5602ceb

Git reported that it could not obtain information about the requested
object.


Correction: Use the GitHub Commit Archive
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because the exact commit was not available through the normal Git checkout,
the exact GitHub source archive was used.

The archive URL is::

   https://github.com/landlab-aspect/aspect/archive/28c914f482fe5d9bba409267d534e66ee5602ceb.tar.gz

It was downloaded with::

   curl -L \
       -o 28c914f48.tar.gz \
       https://github.com/landlab-aspect/aspect/archive/28c914f482fe5d9bba409267d534e66ee5602ceb.tar.gz

The archive was extracted with::

   tar -xzf 28c914f48.tar.gz

The extracted directory was then renamed to::

   aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

This provides the exact requested ASPECT source.

Because this method uses a source archive rather than a Git clone, the
resulting ASPECT directory does not contain a ``.git`` directory. Therefore,
commands such as::

   git status
   git remote -v

are not expected to work from the ASPECT root. This is normal for this
installation method.


Landlab Installation
--------------------

The ASPECT archive already contained an empty directory named::

   landlab/

This directory is part of the ASPECT source layout, but it was not a complete
Landlab installation.


Problem: Copying an Existing Landlab Checkout
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An existing Landlab checkout was available elsewhere on the workstation.

However, copying that checkout into the new ASPECT installation was avoided.

Copying another checkout would introduce a dependency on another local
directory and could make it difficult to determine which Landlab source
version was being used.


Correction: Clone Landlab Directly from GitHub
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The empty ``landlab/`` directory supplied by the ASPECT archive was removed.

Landlab was then cloned directly from GitHub using the exact command::

   git clone https://github.com/landlab/landlab.git landlab

This command was executed from::

   ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact

The resulting repository is::

   ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/landlab

The clone was verified by checking::

   landlab/pyproject.toml

The repository remote was checked with::

   git -C landlab remote -v

The installed Landlab commit was recorded with::

   git -C landlab log -1 --oneline


Landlab Commit Used
^^^^^^^^^^^^^^^^^^^

The installation reported::

   63ab267a1

with the commit message::

   Merge pull request #2481 from landlab/dependabot/pip/requirements/coverage-7.16.0

This means that Landlab was cloned from the repository's ``master`` branch
at that commit.

The ASPECT source is therefore pinned to a specific exact commit, while
Landlab was initially obtained from the current ``master`` branch.

For complete future reproducibility, a specific Landlab commit can
subsequently be pinned in the installation script.


Python Environment
------------------

The ASPECT--Landlab coupling requires Python support.

A separate Python environment was created inside the ASPECT directory using
Python 3.12.

The environment is::

   ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/.venv

The Python executable is::

   ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/.venv/bin/python


Installing uv
^^^^^^^^^^^^^

The installer first checks whether ``uv`` is already available.

If ``uv`` is not available, the official installation command is used::

   curl -LsSf https://astral.sh/uv/install.sh | sh

The installer adds::

   $HOME/.local/bin

to ``PATH``.

If the official installer does not make ``uv`` available, the installer
attempts the fallback::

   python3 -m pip install --user uv

On WS1, ``uv`` was successfully installed and was available as::

   ~/.local/bin/uv

The version reported during the installation was::

   uv 0.12.7


Creating the Python Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Python environment was created with::

   uv venv --python 3.12 .venv

The resulting environment contains its own Python interpreter and packages.

The environment can later be activated interactively with::

   source .venv/bin/activate


Installing Python Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After creating the environment, the installer runs::

   uv sync

from the ASPECT root.

The ASPECT project contains a Python workspace configuration in which the
local ``landlab/`` directory is used as a workspace member.

This allows the local Landlab source to be used by the Python environment
without copying it into another location.


Python Package Verification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The installer verifies Python, Landlab, NumPy, and ``mpi4py``.

Python is checked with::

   .venv/bin/python --version

Landlab is checked with::

   .venv/bin/python -c "import landlab; print(landlab.__version__)"

NumPy is checked with::

   .venv/bin/python -c "import numpy; print(numpy.__version__)"

MPI support through ``mpi4py`` is checked with::

   .venv/bin/python -c "import mpi4py; print(mpi4py.__version__)"

These checks are performed before compiling ASPECT so that Python problems
can be separated from C++ build problems.


NMT WS1 Build Environment
-------------------------

The WS1 workstation provides the required compiler, MPI, CMake, and deal.II
environment.

The environment setup file is::

   /usr/local/software/gcc-14.2.0/openmpi-4.1.8/dealii/9.7.0/configuration/enable.sh

It is loaded with::

   source /usr/local/software/gcc-14.2.0/openmpi-4.1.8/dealii/9.7.0/configuration/enable.sh

The environment provides the following important components:

.. list-table::
   :header-rows: 1
   :widths: 25 40 35

   * - Component
     - WS1 location / version
     - Purpose
   * - GCC
     - 14.2.0
     - C/C++ compilation
   * - OpenMPI
     - 4.1.8
     - MPI execution
   * - CMake
     - 3.26.4
     - ASPECT configuration
   * - deal.II
     - 9.7.0
     - Finite-element framework


Checking the Compiler
^^^^^^^^^^^^^^^^^^^^^

The installer checks::

   which gcc
   gcc --version

and::

   which g++
   g++ --version

This confirms that the expected compiler environment is available.


Checking MPI
^^^^^^^^^^^^

The MPI environment is checked with::

   which mpirun
   mpirun --version

This verifies that OpenMPI is available before ASPECT is compiled.


Checking CMake
^^^^^^^^^^^^^^^

CMake is checked with::

   which cmake
   cmake --version

CMake is then used to configure the ASPECT source.


Checking deal.II
^^^^^^^^^^^^^^^^^^

The installer checks::

   echo "$DEAL_II_DIR"

The final procedure requires ``DEAL_II_DIR`` to be set after loading the NMT
environment.

The installer also verifies that the directory exists.


Explicit deal.II Configuration
------------------------------

An important correction was made to the final installer.

The earlier CMake configuration relied on the NMT environment to allow CMake
to discover deal.II.

Although that worked, it was not explicit in the CMake command.

The final installer explicitly passes::

   -DDEAL_II_DIR="$DEAL_II_DIR"

This makes the CMake configuration clearer and more reproducible.

The resulting CMake command is::

   cmake \
       -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
       -DDEAL_II_DIR="$DEAL_II_DIR" \
       -DASPECT_WITH_PYTHON=ON \
       -DPython3_EXECUTABLE="$PYTHON" \
       "$ASPECT_DIR"


Enabling Python in ASPECT
-------------------------

Python support is required for the ASPECT--Landlab coupling.

The following CMake option is therefore required::

   -DASPECT_WITH_PYTHON=ON

This enables ASPECT's Python interface.

The Python interpreter is also explicitly specified::

   -DPython3_EXECUTABLE="$PYTHON"

where::

   PYTHON="$ASPECT_DIR/.venv/bin/python"

This ensures that ASPECT uses the Python environment containing the installed
Landlab and ``mpi4py`` packages.


Debug and Release Builds
------------------------

The final installer supports both Debug and Release builds.

The default build type is::

   BUILD_TYPE=Debug

Debug mode is the preferred mode while developing and testing the
ASPECT--Landlab coupling.

It is particularly useful for investigating:

* C++/Python communication;
* ``landlab.cc``;
* Python function calls;
* MPI communicator handling;
* surface-node exchange;
* topographic evolution;
* elevation changes;
* mesh deformation;
* checkpointing; and
* runtime errors.

A Release build can be selected with::

   BUILD_TYPE=Release ./install_lla_checkpoint_aspect_3.1.0_ws1.sh

Release mode is appropriate for production calculations after the coupling
has been verified.

The first successful build during this installation used Release mode and
reported::

   running in OPTIMIZED mode


CMake Configuration
-------------------

A clean build directory is created::

   ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/build

CMake is run from this directory.

The final configuration is::

   cmake \
       -DCMAKE_BUILD_TYPE="$BUILD_TYPE" \
       -DDEAL_II_DIR="$DEAL_II_DIR" \
       -DASPECT_WITH_PYTHON=ON \
       -DPython3_EXECUTABLE="$PYTHON" \
       "$ASPECT_DIR"

The four important configuration options are:

.. list-table::
   :header-rows: 1
   :widths: 38 62

   * - Option
     - Meaning
   * - ``CMAKE_BUILD_TYPE``
     - Selects Debug or Release compilation.
   * - ``DEAL_II_DIR``
     - Explicitly identifies the NMT deal.II installation.
   * - ``ASPECT_WITH_PYTHON=ON``
     - Enables ASPECT Python support.
   * - ``Python3_EXECUTABLE``
     - Selects the Python 3.12 interpreter from the local ``.venv``.


Building ASPECT
---------------

After successful CMake configuration, ASPECT is compiled using::

   cmake --build . --parallel

The build completed successfully on WS1.

The executable produced by the ASPECT build is::

   build/aspect-release


Why the Executable Is Called ``aspect-release``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ASPECT executable is named::

   aspect-release

even when the CMake build type is Debug.

Therefore the installer checks for::

   build/aspect-release

The build type controls compilation settings, while the executable name
remains ``aspect-release``.


Verifying ASPECT
----------------

The installer checks that the executable exists and is executable.

It then runs::

   ./aspect-release --version

The successful WS1 installation reported:

::

   This is ASPECT
   . version 3.1.0-pre
   . using deal.II 9.7.0
   . using Trilinos 16.2.0
   . using p4est 2.8.7
   . using Geodynamic World Builder 1.0.0

This confirms that the compiled ASPECT executable can identify its expected
version and major dependencies.


Standard ASPECT Runtime Test
----------------------------

After compiling ASPECT, a standard cookbook example was used to verify that
the executable could actually run an ASPECT model.

The test directory was::

   ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/cookbooks/convection-box

The directory contains::

   convection-box.prm
   doc/
   tutorial-onset-of-convection/

The standard parameter file was run from that directory using::

   ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/build/aspect-release \
       convection-box.prm

The test completed successfully.

This is an important verification step because a successful compilation alone
does not guarantee that the executable can initialize and run a simulation.


MPI Runtime Test
----------------

For parallel execution, ASPECT can be launched with ``mpirun``.

For example::

   mpirun -np 4 \
       ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/build/aspect-release \
       convection-box.prm

For initial debugging, a single MPI process is useful because it reduces the
complexity of the runtime environment.

After the serial test succeeds, MPI execution can be tested.


ASPECT--Landlab Coupling
------------------------

The standard convection-box test verifies the ASPECT installation itself.

The next stage is the actual ASPECT--Landlab coupling.

The coupling uses ASPECT's Python interface together with Landlab and
``mpi4py``.

The general execution sequence is:

#. ASPECT starts the simulation.
#. ASPECT initializes the Python interface.
#. The Landlab Python module is imported.
#. The Landlab grid is initialized.
#. ASPECT and Landlab exchange the required surface information.
#. ASPECT provides the surface state to the Python side.
#. Landlab evolves the topography.
#. Landlab returns an elevation change ``dz``.
#. ASPECT converts the surface change into mesh deformation.
#. The simulation continues to the next timestep.


Important Coupling Requirement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Landlab Python side must implement the interface expected by the ASPECT
Landlab mesh-deformation implementation.

One important distinction is that the Python side returns an elevation
change::

   dz

rather than an absolute elevation field.

Therefore:

``elevation``
   Represents the current absolute topography.

``dz``
   Represents the change in elevation that should be applied to the ASPECT
   surface.


Python Environment for Coupled Runs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before working interactively with Landlab, the environment can be activated
with::

   cd ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact
   source .venv/bin/activate

Then verify Landlab::

   python -c "import landlab; print(landlab.__version__)"

and MPI support::

   python -c "from mpi4py import MPI; print(MPI.Get_version())"


Important Installation Lessons
------------------------------

Several lessons were learned during the installation.


Exact ASPECT Commit
^^^^^^^^^^^^^^^^^^^

Do not assume that::

   git clone

followed by::

   git checkout <commit>

will always work for a historical or development commit.

For this installation, the requested ASPECT commit was not available in the
local Git object database.

The reliable solution was to download the GitHub archive for the exact
commit.


Landlab Should Be Cloned
^^^^^^^^^^^^^^^^^^^^^^^^

The Landlab source should not be copied from another local checkout when a
clean independent installation is desired.

The final procedure uses::

   git clone https://github.com/landlab/landlab.git landlab

This makes the Landlab repository directly visible inside the ASPECT
workspace.


Do Not Use Mac-Specific Paths on WS1
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The original installation documentation contained paths such as::

   /Users/biraj/software/...

Those paths belong to a macOS environment and cannot be used on WS1.

The WS1 installation instead uses the NMT software environment and paths such
as::

   /usr/local/software/gcc-14.2.0/openmpi-4.1.8/dealii/9.7.0/

The Python environment is also created locally under the ASPECT directory.


Make the deal.II Path Explicit
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Although CMake was previously able to discover deal.II through the loaded
environment, the final procedure explicitly passes::

   -DDEAL_II_DIR="$DEAL_II_DIR"

This makes it clear which deal.II installation is being used.


Use the Correct Python
^^^^^^^^^^^^^^^^^^^^^^

Do not rely on whichever ``python`` happens to appear first in ``PATH``.

The final installer creates::

   .venv/bin/python

and passes it directly to CMake::

   -DPython3_EXECUTABLE="$PYTHON"

This ensures that ASPECT uses the Python environment containing Landlab and
``mpi4py``.


Use Debug During Development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The coupling is still under development, so Debug mode is the preferred
default.

The installer therefore uses::

   BUILD_TYPE="${BUILD_TYPE:-Debug}"

Release mode can be selected when production performance is required.


Reproducibility of Landlab
^^^^^^^^^^^^^^^^^^^^^^^^^^

The ASPECT source is fully pinned to the exact commit::

   28c914f482fe5d9bba409267d534e66ee5602ceb

Landlab was cloned from ``master`` and the resulting commit was recorded::

   63ab267a1

If complete reproducibility is required in the future, the Landlab commit
should also be explicitly pinned.


Final Installation Checklist
----------------------------

Before beginning a coupled simulation, verify the following:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Item
     - Expected result
   * - ASPECT version
     - ``3.1.0-pre``
   * - ASPECT commit
     - ``28c914f482fe5d9bba409267d534e66ee5602ceb``
   * - ASPECT directory
     - ``~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact``
   * - Landlab
     - Fresh Git clone under ``ASPECT_DIR/landlab``
   * - Landlab commit
     - Recorded with ``git log -1 --oneline``
   * - Python
     - Python 3.12
   * - Python environment
     - ``ASPECT_DIR/.venv``
   * - uv
     - Available in ``PATH``
   * - NumPy
     - Imports successfully
   * - mpi4py
     - Imports successfully
   * - GCC
     - 14.2.0
   * - OpenMPI
     - 4.1.8
   * - deal.II
     - 9.7.0
   * - ``DEAL_II_DIR``
     - Set and passed explicitly to CMake
   * - Python support
     - ``ASPECT_WITH_PYTHON=ON``
   * - Python executable
     - ``.venv/bin/python``
   * - Build mode
     - Debug for development or Release for production
   * - ASPECT executable
     - ``build/aspect-release``
   * - ASPECT runtime
     - ``aspect-release --version`` succeeds
   * - Standard test
     - ``convection-box.prm`` runs successfully
   * - Coupled test
     - Landlab initializes and exchanges data with ASPECT correctly


Complete Installation Procedure
-------------------------------

For a new WS workstation, the final procedure is:

#. Obtain the installation script.
#. Make the script executable::

      chmod +x install_lla_checkpoint_aspect_3.1.0_ws1.sh

#. Run the Debug installation::

      BUILD_TYPE=Debug ./install_lla_checkpoint_aspect_3.1.0_ws1.sh

#. Activate the Python environment::

      cd ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact
      source .venv/bin/activate

#. Verify Python::

      python --version

#. Verify Landlab::

      python -c "import landlab; print(landlab.__version__)"

#. Verify mpi4py::

      python -c "import mpi4py; print(mpi4py.__version__)"

#. Move to the standard convection-box test::

      cd cookbooks/convection-box

#. Run the standard test::

      ~/software/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact/build/aspect-release \
          convection-box.prm

#. After the standard test succeeds, proceed to the Landlab-coupled
   parameter file.


Final Result
------------

The final WS1 installation successfully established the following software
chain::

   ASPECT 3.1.0-pre
       |
       +-- exact checkpointing source
       |   28c914f482fe5d9bba409267d534e66ee5602ceb
       |
       +-- local Landlab Git repository
       |   63ab267a1
       |
       +-- Python 3.12
       |   |
       |   +-- uv
       |   +-- NumPy
       |   +-- mpi4py
       |
       +-- GCC 14.2.0
       |
       +-- OpenMPI 4.1.8
       |
       +-- deal.II 9.7.0
       |
       +-- Python support
       |
       +-- Debug/Release build
       |
       +-- standard ASPECT runtime test

The standard ``convection-box.prm`` test was successfully executed.

Therefore, the ASPECT installation itself is working on WS1 and the
environment is ready for the next stage of testing the ASPECT--Landlab
surface evolution and mesh-deformation coupling.


Installation Script
-------------------

The corresponding installation script is::

   install_lla_checkpoint_aspect_3.1.0_ws1.sh

The script performs the complete sequence automatically:

#. checks basic commands;
#. downloads the exact ASPECT commit archive;
#. extracts and verifies ASPECT;
#. removes the empty archive ``landlab/`` directory;
#. clones Landlab directly from GitHub;
#. installs or detects ``uv``;
#. creates Python 3.12 ``.venv``;
#. runs ``uv sync``;
#. verifies Landlab, NumPy, and ``mpi4py``;
#. loads the NMT deal.II/OpenMPI environment;
#. checks GCC, G++, MPI, CMake, and deal.II;
#. configures CMake with explicit deal.II and Python paths;
#. builds ASPECT;
#. verifies ``aspect-release``; and
#. prints the final installation information.

The script defaults to Debug mode and can be switched to Release mode with
``BUILD_TYPE=Release``.
