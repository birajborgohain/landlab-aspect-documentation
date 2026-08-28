Installing ASPECT version:``ll_mesh_def`` Branch (ASPECT PR #7213) August 28, 2026
================================================================================================

.. note::

   Before running the Landlab-ASPECT model, activate the Python virtual
   environment containing the required NumPy installation::

       source ~/software/aspect_ll_mesh_def/.venv/bin/activate

   Then move to the directory containing the model input file and run ASPECT
   with 23 MPI processes::

       cd /path/to/your/model_folder_containing_original_lla_28_48.prm

       /opt/homebrew/bin/mpirun -np 23 \
       /Users/biraj/software/aspect_ll_mesh_def/build/aspect-release \
       original_lla_28_48.prm

   This command uses the ``ll_mesh_def`` ASPECT executable built from commit
   ``f3381ee50``.

Purpose
-------

This document records the workflow used to test the ``ll_mesh_def`` branch from
Daniel Douglas's open ASPECT pull request #7213. The goal is to build a clean
ASPECT checkout containing Daniel's branch and then use it to test the Landlab
2-D and 3-D models on the cluster.

The workflow is documented in two forms:

* installation and testing directly from the terminal;
* an interactive Bash ``.sh`` script that automates the same setup.

The existing Landlab-ASPECT working copies should not be modified for this
test. A separate clean ASPECT checkout is used instead.

.. important::

   The ``ll_mesh_def`` test checkout is separate from existing Landlab
   development/test copies such as ``template_Landlab_denial_90296f6_test``,
   ``landlab_ASPECT_test_2``, and ``landlab_aspect``. This prevents local
   modifications from those environments from affecting the PR test.

Starting point
--------------

The clean test repository is created at::

    ~/software/aspect_ll_mesh_def

The repository is checked out to Daniel Douglas's branch::

    ll_mesh_def

The branch was obtained from the remote::

    danieldouglas92

The workflow follows the branch checkout suggested for PR #7213::

    git checkout -b ll_mesh_def danieldouglas92/ll_mesh_def


Part 1: Terminal-only workflow
------------------------------

Step 1: Go to the software directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Move to the directory where the new ASPECT checkout will be kept::

    cd ~/software


Step 2: Clone a clean ASPECT repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clone the official ASPECT repository into a new directory::

    git clone https://github.com/geodynamics/aspect.git aspect_ll_mesh_def

Enter the new repository::

    cd ~/software/aspect_ll_mesh_def


Step 3: Confirm the repository is clean
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Check the Git state::

    git status

Check the current branch::

    git branch --show-current

Check the latest commit::

    git log -1 --oneline

At this stage the checkout should be a clean repository before the PR branch is
selected.


Step 4: Add Daniel's repository as a remote
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add Daniel Douglas's ASPECT repository::

    git remote add danieldouglas92 https://github.com/danieldouglas92/aspect

Check the configured remotes::

    git remote -v

The repository should now have both ``origin`` and ``danieldouglas92``.


Step 5: Fetch Daniel's branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Fetch the branches from Daniel's repository::

    git fetch danieldouglas92

Check that the requested branch is available::

    git branch -r | grep ll_mesh_def

The expected remote branch is::

    danieldouglas92/ll_mesh_def


Step 6: Create the local ``ll_mesh_def`` branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a local branch from Daniel's remote branch::

    git checkout -b ll_mesh_def danieldouglas92/ll_mesh_def

Verify the branch::

    git branch --show-current

The output should be::

    ll_mesh_def

Verify the commit::

    git log -1 --oneline

The test should use the commit shown by this command. For example, during
this workflow the checkout showed::

    f3381ee50 (HEAD -> ll_mesh_def, danieldouglas92/ll_mesh_def) address Rene comments

The exact commit can change if Daniel updates the PR, so the current
``git log`` output should be recorded rather than assuming an old commit.


Step 7: Confirm the build environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before configuring ASPECT, identify the available compiler, MPI, CMake,
Python, and deal.II installations::

    which cmake
    cmake --version

    which mpirun
    mpirun --version

    which mpicxx
    mpicxx --version

    echo $DEAL_II_DIR

Search for installed deal.II CMake configuration files::

    find "$HOME" -type f -name "deal.IIConfig.cmake" 2>/dev/null

The documented environment uses deal.II 9.7.0. In the current installation,
the following installed trees were found::

    ~/dealii-candi/deal.II-v9.7.0

    ~/software/dealii/dealii-9.7.1/install/deal.II-v9.7.0

Temporary build trees should not be selected as the deal.II installation
root. The selected installation should contain::

    lib/cmake/deal.II/deal.IIConfig.cmake

and the corresponding deal.II include files.


Step 8: Prepare Python and NumPy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ASPECT is configured with Python support::

    -DASPECT_WITH_PYTHON=ON

The Python interpreter used by CMake must have NumPy available.

A system or Homebrew Python may be marked as an externally managed
environment. Attempting::

    python3 -m pip install numpy

can therefore produce a PEP 668 error::

    error: externally-managed-environment

Do not use ``--break-system-packages`` for this workflow.

Instead, create a virtual environment inside the ASPECT test checkout::

    cd ~/software/aspect_ll_mesh_def

    python3.12 -m venv .venv

Activate it::

    source .venv/bin/activate

Then install NumPy into the virtual environment::

    python -m pip install numpy

Verify both Python and NumPy::

    python --version

    python -c "import numpy; print(numpy.__version__)"

The resulting interpreter should be::

    ~/software/aspect_ll_mesh_def/.venv/bin/python

When CMake is configured, explicitly point it to this interpreter::

    -DPython3_EXECUTABLE="$PWD/.venv/bin/python"


Step 9: Create the ASPECT build directory
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the ASPECT source directory::

    cd ~/software/aspect_ll_mesh_def

Create and enter the build directory::

    mkdir -p build
    cd build


Step 10: Configure ASPECT
^^^^^^^^^^^^^^^^^^^^^^^^^

Configure ASPECT using the selected compiler, deal.II, and Python
environment::

    cmake \
      -DCMAKE_C_COMPILER=/path/to/gcc \
      -DCMAKE_CXX_COMPILER=/path/to/g++ \
      -DDEAL_II_DIR=/path/to/deal.II-v9.7.0 \
      -DASPECT_WITH_PYTHON=ON \
      -DPython3_EXECUTABLE=../.venv/bin/python \
      ..

The actual compiler and deal.II paths must be replaced with the installations
available on the target cluster.

An equivalent form using shell variables is::

    cmake \
      -DCMAKE_C_COMPILER="$CC" \
      -DCMAKE_CXX_COMPILER="$CXX" \
      -DDEAL_II_DIR="$DEAL_II_DIR" \
      -DASPECT_WITH_PYTHON=ON \
      -DPython3_EXECUTABLE="$PYTHON" \
      "$ASPECT_DIR"


Step 11: Build ASPECT
^^^^^^^^^^^^^^^^^^^^^

Build using all available build threads::

    cmake --build . --parallel

Wait for the build to finish successfully before proceeding to the model
tests.


Step 12: Verify the executable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The release executable is normally::

    ./aspect-release

Before running ASPECT, activate the Python virtual environment::

    cd ~/software/aspect_ll_mesh_def
    source .venv/bin/activate

Then enter the build directory::

    cd ~/software/aspect_ll_mesh_def/build

Check the ASPECT version::

    ./aspect-release --version

The output should identify ASPECT and report the version and dependency
information associated with the selected checkout.


Part 2: Interactive ``.sh`` workflow
------------------------------------

Why use a shell script?
^^^^^^^^^^^^^^^^^^^^^^^

The terminal-only procedure is useful when setting up or debugging the
environment manually. The ``.sh`` script performs the same setup
systematically and reduces repeated typing.

The script used for the ``ll_mesh_def`` test is intentionally different from
the historical installer used for the old fixed ASPECT commit. It does not
download or extract the old ``28c914f48`` source. Instead, it works directly
with the existing clean Git checkout::

    ~/software/aspect_ll_mesh_def

and therefore builds the currently checked-out::

    ll_mesh_def

branch.


Create the script
^^^^^^^^^^^^^^^^^

From the ASPECT checkout::

    cd ~/software/aspect_ll_mesh_def

Create the script::

    nano build_ll_mesh_def.sh

Paste the ``ll_mesh_def`` build script into the file and save it.

Make it executable::

    chmod +x build_ll_mesh_def.sh


Check the script before running
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Run the Bash syntax check::

    bash -n build_ll_mesh_def.sh

If Bash reports no output, there are no syntax errors detected by this check.

Run the installer::

    ./build_ll_mesh_def.sh


What the ``.sh`` script contains
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The script is organized into sequential steps. Each major stage pauses and
asks the user whether to continue. This makes the build interactive and
prevents an incorrect compiler, MPI, Python, or deal.II installation from
being selected without confirmation.

.. list-table::
   :header-rows: 1
   :widths: 20 55 25

   * - Step
     - Function
     - Main result
   * - 1
     - Check the ASPECT source directory
     - Confirms ``aspect_ll_mesh_def`` and the ``ll_mesh_def`` branch.
   * - 2
     - Check basic commands
     - Finds tools such as CMake, MPI, and Python.
   * - 3
     - Detect the compiler
     - Selects ``CC`` and ``CXX``.
   * - 4
     - Detect MPI
     - Selects ``mpirun`` and matching MPI compiler wrappers.
   * - 5
     - Detect CMake
     - Selects the CMake executable.
   * - 6
     - Prepare Python
     - Creates ``.venv`` and checks/install NumPy.
   * - 7
     - Detect deal.II
     - Finds installed deal.II 9.7.0 candidates and lets the user select one.
   * - 8
     - Show environment
     - Prints all selected build components before configuration.
   * - 9
     - Create build directory
     - Creates ``build``.
   * - 10
     - Configure ASPECT
     - Runs CMake with the selected environment.
   * - 11
     - Build ASPECT
     - Runs ``cmake --build . --parallel``.
   * - 12
     - Verify executable
     - Activates ``.venv`` and runs ``aspect-release --version``.


ASPECT source selection in the script
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The script defines the test source and build locations near the beginning::

    ASPECT_DIR="$HOME/software/aspect_ll_mesh_def"
    BUILD_DIR="$ASPECT_DIR/build"

This is important because the script does not operate on the existing
Landlab development repositories.

It also expects the branch to be::

    ll_mesh_def

and checks the Git state before continuing.


Compiler selection
^^^^^^^^^^^^^^^^^^

The compiler section searches common compiler locations and displays the
available candidates.

The selected C compiler is exported as::

    export CC="$SELECTED_CC"

and the selected C++ compiler as::

    export CXX="$SELECTED_CXX"

The CMake configuration then uses::

    -DCMAKE_C_COMPILER="$CC"

    -DCMAKE_CXX_COMPILER="$CXX"

This keeps the compiler used by CMake explicit.


MPI selection
^^^^^^^^^^^^^

The MPI section searches for ``mpirun`` and allows the user to select one of
the detected MPI installations.

After selecting ``mpirun``, the script determines the corresponding
``mpicc`` and ``mpicxx`` from the same MPI installation directory.

This is important because the MPI runtime and compiler wrappers should come
from the same MPI installation.

The selected runtime is stored as::

    MPI_RUN

The script prints the MPI version before continuing.


CMake selection
^^^^^^^^^^^^^^^

The CMake section searches for available CMake executables, displays their
versions, and stores the selected executable in::

    CMAKE

The same executable is used for both configuration and building::

    "$CMAKE" ...

    "$CMAKE" --build . --parallel


Python virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^

The Python section was modified after the initial script encountered the
following error::

    error: externally-managed-environment

The cause was that the script attempted to install NumPy into a
system/Homebrew-managed Python.

The corrected script first checks for::

    $ASPECT_DIR/.venv/bin/python

If the virtual environment does not exist, it searches for the required
Python 3.12.13 interpreter and creates::

    $ASPECT_DIR/.venv

NumPy is then installed using the virtual-environment interpreter::

    "$PYTHON" -m pip install numpy

The script checks NumPy using::

    "$PYTHON" -c "import numpy"

This keeps the base Python installation unchanged.

Before verifying the ASPECT executable, the script should activate the same
virtual environment::

    cd "$ASPECT_DIR"
    source .venv/bin/activate

Then it enters the build directory::

    cd "$BUILD_DIR"

and runs::

    "$ASPECT_EXECUTABLE" --version


deal.II detection
^^^^^^^^^^^^^^^^^

The deal.II section checks known installed locations.

For the current machine, the two installed candidates found during the setup
were::

    $HOME/dealii-candi/deal.II-v9.7.0

and::

    $HOME/software/dealii/dealii-9.7.1/install/deal.II-v9.7.0

The script verifies that a candidate contains::

    lib/cmake/deal.II/deal.IIConfig.cmake

and the expected include files.

The selected installation is exported as::

    DEAL_II_DIR

CMake receives that location with::

    -DDEAL_II_DIR="$DEAL_II_DIR"


Environment summary
^^^^^^^^^^^^^^^^^^^

Before configuring ASPECT, the script prints the complete selected
environment, including:

* ASPECT source directory;
* current Git branch;
* current Git commit;
* C compiler;
* C++ compiler;
* MPI;
* CMake;
* Python;
* NumPy;
* deal.II;
* build directory.

This summary is useful for reproducibility because it records exactly which
software environment was used for the PR test.


CMake configuration in the script
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The core CMake command is::

    "$CMAKE" \
        -DCMAKE_C_COMPILER="$CC" \
        -DCMAKE_CXX_COMPILER="$CXX" \
        -DDEAL_II_DIR="$DEAL_II_DIR" \
        -DASPECT_WITH_PYTHON=ON \
        -DPython3_EXECUTABLE="$PYTHON" \
        "$ASPECT_DIR"

The important point is that the Python interpreter is explicitly specified.
This prevents CMake from selecting a different system Python after NumPy has
been verified in the virtual environment.


Building in the script
^^^^^^^^^^^^^^^^^^^^^^

The build stage runs::

    "$CMAKE" --build . --parallel

Using ``--parallel`` allows CMake to select parallel build jobs appropriate to
the system unless a different job limit is specified.


Executable verification in the script
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

After the build, the script expects::

    $BUILD_DIR/aspect-release

It checks that the executable exists and is executable.

Before running the executable, the script activates the ASPECT virtual
environment::

    cd "$ASPECT_DIR"
    source .venv/bin/activate

Then it enters the build directory::

    cd "$BUILD_DIR"

It then runs::

    "$ASPECT_EXECUTABLE" --version

The version output provides the first confirmation that the selected
``ll_mesh_def`` source successfully compiled with the selected dependency
environment.


Part 3: Testing the 2-D and 3-D models
--------------------------------------

After ASPECT successfully builds and the executable is verified, the next
objective is to test the Landlab-ASPECT models on the cluster.

The test should be performed separately for the 2-D and 3-D cases.

The important reproducibility information to record for each test is:

.. list-table::
   :header-rows: 1
   :widths: 25 50 25

   * - Item
     - Information to record
     - Example
   * - ASPECT branch
     - Git branch used for the test
     - ``ll_mesh_def``
   * - ASPECT commit
     - Output of ``git log -1 --oneline``
     - ``f3381ee50``
   * - Model
     - 2-D or 3-D test case
     - ``2D-T`` or 3-D model
   * - Cluster
     - Cluster/system where the test was run
     - NMT HPC
   * - deal.II
     - Selected deal.II installation/version
     - ``9.7.0``
   * - MPI
     - Selected MPI implementation/version
     - Record actual cluster value
   * - Result
     - Whether the model ran successfully
     - Record success/failure
   * - Landlab output
     - Whether sediment and Landlab fields were produced
     - Record observed fields
   * - Error
     - Full error if the run fails
     - Record exact message


2-D model test
^^^^^^^^^^^^^^

Run the 2-D Landlab model using the same model input and data that are used
for the comparison test.

Record:

* the ASPECT branch and commit;
* the exact ``.prm`` file;
* the command used to launch ASPECT;
* the number of MPI processes;
* whether the model completed;
* whether sediment was generated;
* whether the expected sediment fields were available;
* any World Builder or mesh-related error.


3-D model test
^^^^^^^^^^^^^^

Repeat the same procedure for the 3-D model.

The 3-D test should use the same ``ll_mesh_def`` ASPECT executable so that the
comparison isolates the effect of the PR branch rather than introducing a
different ASPECT build.

Record the same information as for the 2-D test.


Recommended test record
^^^^^^^^^^^^^^^^^^^^^^^

A compact test record can be maintained as follows::

    Model:
    Cluster:
    ASPECT source:
    Branch:
    Commit:
    deal.II:
    MPI:
    Compiler:
    CMake:
    Python:
    NumPy:
    Input .prm:
    MPI processes:
    Result:
    Sediment generated:
    Sediment fields visible:
    Error:


Troubleshooting
---------------

Git shows ``(END)`` after ``git log``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes Git opens its output in the ``less`` pager. For example::

    f3381ee50 (HEAD -> ll_mesh_def, danieldouglas92/ll_mesh_def) address Rene comments
    (END)

This is not an ASPECT error.

Press::

    q

to leave the pager and return to the shell script.

PEP 668 NumPy error
^^^^^^^^^^^^^^^^^^^

If the script reports::

    error: externally-managed-environment

the selected Python is an externally managed system/Homebrew/uv Python.

Do not install NumPy directly into that environment and do not use
``--break-system-packages``.

Instead create the ASPECT virtual environment::

    python3.12 -m venv ~/software/aspect_ll_mesh_def/.venv

Activate it::

    source ~/software/aspect_ll_mesh_def/.venv/bin/activate

Install NumPy::

    python -m pip install numpy

Then verify::

    python -c "import numpy; print(numpy.__version__)"


Wrong ASPECT repository
^^^^^^^^^^^^^^^^^^^^^^^

Before building, always check::

    cd ~/software/aspect_ll_mesh_def

    git branch --show-current

    git log -1 --oneline

The branch should be::

    ll_mesh_def

Do not accidentally run the PR test from a modified ``pr43`` checkout.


Dirty working tree
^^^^^^^^^^^^^^^^^^

Check::

    git status

The ``aspect_ll_mesh_def`` checkout should normally be clean before testing.

If the checkout has local modifications, determine why they exist before
continuing. Do not use ``git restore`` or ``git clean`` unless the local
changes have been intentionally identified as disposable.


Reproducibility
---------------

For every 2-D and 3-D test, preserve the following information:

.. list-table::
   :header-rows: 1
   :widths: 30 50 20

   * - Category
     - Record
     - Required
   * - Source
     - ASPECT repository and branch
     - Yes
   * - Commit
     - ``git log -1 --oneline``
     - Yes
   * - Build
     - Compiler, MPI, CMake, deal.II
     - Yes
   * - Python
     - Python version and NumPy version
     - Yes when Python support is enabled
   * - Model
     - 2-D/3-D input and ``.prm`` file
     - Yes
   * - Runtime
     - MPI process count and launch command
     - Yes
   * - Result
     - Success/failure and output behavior
     - Yes
   * - Error
     - Exact error output for failed runs
     - If applicable


Summary
-------

The recommended workflow for testing Daniel Douglas's ``ll_mesh_def`` branch
is:

#. Keep existing Landlab-ASPECT working copies unchanged.
#. Create a new clean ASPECT checkout at
   ``~/software/aspect_ll_mesh_def``.
#. Add Daniel's repository as the ``danieldouglas92`` remote.
#. Fetch and check out ``danieldouglas92/ll_mesh_def`` as the local
   ``ll_mesh_def`` branch.
#. Record the current commit with ``git log -1 --oneline``.
#. Identify the cluster compiler, MPI, CMake, Python, and deal.II environment.
#. Use a local ``.venv`` for Python and install NumPy there.
#. Configure ASPECT with the selected deal.II and Python interpreter.
#. Build with ``cmake --build . --parallel``.
#. Activate the ``.venv`` before running the ASPECT executable.
#. Verify ``aspect-release --version``.
#. Run the 2-D Landlab model.
#. Run the 3-D Landlab model.
#. Record the branch, commit, build environment, input files, runtime
   settings, output, and errors for both tests.

This procedure keeps the PR test isolated from existing Landlab development
work and makes the 2-D/3-D results reproducible.