August 28, 2026, Testing Daniel's ``ll_mesh_def`` Branch for ASPECT--Landlab Coupling
=====================================================================================

Purpose
-------

This document records the testing of Daniel Douglas's ``ll_mesh_def`` branch
from ASPECT pull request #7213. The purpose of the test was to determine
whether the 2-D and 3-D ASPECT--Landlab coupling can be built and executed,
and to identify changes required to run an existing Landlab model with the
new branch.

The branch was checked out using::

    git checkout -b ll_mesh_def danieldouglas92/ll_mesh_def

The resulting branch was:

::

    ll_mesh_def

with commit::

    f3381ee50 address Rene comments

The testing was performed on macOS before transferring the test procedure to
the cluster.


Initial ASPECT Repository and Branch Setup
-------------------------------------------

Several ASPECT repositories existed under ``~/software``. Their branches and
remotes were checked to identify the appropriate repository for testing.

The relevant repository selected for the PR test was::

    ~/software/aspect_ll_mesh_def/aspect

The branch was confirmed as::

    ll_mesh_def

The branch commit was::

    f3381ee50 address Rene comments

The ASPECT version reported by the executable was::

    version 3.1.0-pre (ll_mesh_def, f3381ee50)


Build Environment
-----------------

A Python environment was created for the ASPECT checkout. The ASPECT build
initially used this environment for Python support.

The deal.II installations on the system were also checked. The available
configuration included deal.II 9.7.0.

The final ASPECT executable was located at::

    /Users/biraj/software/aspect_ll_mesh_def/build/aspect-release

The executable reported::

    ASPECT version: 3.1.0-pre
    branch: ll_mesh_def
    commit: f3381ee50
    deal.II: 9.7.0
    Trilinos: 16.2.0
    p4est: 2.8.7
    Geodynamic World Builder: 1.1.1


Python and NumPy Issue During Initial Verification
--------------------------------------------------

The first executable verification produced::

    ModuleNotFoundError: No module named 'numpy'

ASPECT therefore aborted during::

    ./aspect-release --version

The build configuration was inspected to determine which Python executable
had been used by CMake.

The build cache contained::

    Python3_EXECUTABLE:UNINITIALIZED=/Users/biraj/software/aspect_ll_mesh_def/.venv/bin/python

and the Python include and library paths corresponded to Python 3.12.

The issue was related to the Python environment being used when the executable
was run. Activating the appropriate virtual environment resolved the NumPy
availability problem.

The executable could then successfully report its version.


Initial Parameter File Test
---------------------------

The existing Landlab parameter file was tested with the new executable.

The first parameter-file incompatibility was::

    No entry with name <Script argument> was declared in the current subsection.

The existing parameter file contained::

    subsection Landlab
      set MPI ranks for Landlab = 1
      set Script name = import-template_Liang_deposition_ada_denial_random_noise
      set Script path = .
      set Script argument =
    end

A search of the new source code showed that the ``Landlab`` mesh deformation
implementation declared::

    MPI ranks for Landlab
    Script path
    Script name

There was no ``Script argument`` parameter in the new implementation.

Therefore the obsolete line was removed::

    set Script argument =

The resulting section was::

    subsection Landlab
      set MPI ranks for Landlab = 1
      set Script name = import-template_Liang_deposition_ada_denial_random_noise
      set Script path = .
    end

This allowed ASPECT to proceed farther into parameter parsing.


Boundary Composition Model Parameter Change
--------------------------------------------

The next parameter-file error was::

    No entry with name <Model name> was declared in the current subsection.

The affected section was::

    subsection Boundary composition model
      set Model name = function
    end

The source code of the new branch was inspected.

The new boundary composition model manager uses::

    List of model names

instead of the old::

    Model name

The source implementation obtains the model names using::

    prm.get("List of model names")

Therefore the parameter was changed from::

    set Model name = function

to::

    set List of model names = function

The corrected section became::

    subsection Boundary composition model
      set List of model names = function
      set Fixed composition boundary indicators = top, bottom
      set Allow fixed composition on outflow boundaries = true

      subsection Function
        ...
      end
    end

After this change, ASPECT proceeded farther into initialization.


Initial Composition Model Parameter Change
-------------------------------------------

A second ``Model name`` error then appeared.

This error was different from the boundary composition error. It occurred in
the initial composition model.

The parameter file contained::

    subsection Initial composition model
      set Model name = function
    end

The ASPECT source reported that ``Model name`` was deprecated for this model
manager and that the model should instead be specified using::

    List of model names

Therefore the parameter was changed to::

    subsection Initial composition model
      set List of model names = function
    end

It is important that this change was made only for the initial composition
model.

Other ASPECT model sections still contained their own ``Model name``
parameters, for example the geometry, material, and gravity models. These were
not changed because they belong to different parameter managers.

This distinction was important when updating the parameter file.


Enabling Landlab Support in CMake
---------------------------------

After the parameter-file issues were corrected, ASPECT reached the Landlab
mesh deformation implementation but reported::

    To use the 'Landlab' mesh deformation plugin, ASPECT needs to be
    configured using ASPECT_WITH_LANDLAB=ON.

The CMake cache was checked using::

    grep -i "ASPECT_WITH_LANDLAB" CMakeCache.txt

The result was::

    ASPECT_WITH_LANDLAB:BOOL=OFF

Therefore the executable had been built without Landlab support.

The existing build was reconfigured using::

    cmake .. -DASPECT_WITH_LANDLAB=ON

The CMake cache was then checked again and confirmed::

    ASPECT_WITH_LANDLAB:BOOL=ON

The ASPECT executable was rebuilt.

This was a build-configuration issue rather than a parameter-file issue.


Landlab Script Path Issue
-------------------------

After enabling Landlab support, ASPECT successfully entered the Landlab
initialization code but reported that the specified Python script did not
exist.

The parameter file initially used::

    set Script path = .

The Landlab implementation constructs the Python module filename by combining
the script path and script name. With the path specified as ``.``, the
constructed name resulted in a filename beginning with::

    .

instead of the intended relative path::

    ./

The parameter was therefore changed to::

    set Script path = ./

with::

    set Script name = import-template_Liang_deposition_ada_denial_random_noise

This allowed ASPECT to find and start importing the Python script.


Landlab Python Environment in the New Branch
--------------------------------------------

After the executable was configured with Landlab support, the Python
environment provided by the new branch was inspected.

The new branch contains::

    contrib/landlab/

with::

    contrib/landlab/.python-version
    contrib/landlab/README.md
    contrib/landlab/pyproject.toml
    contrib/landlab/uv.lock

The README specifies that the Landlab environment should be installed using::

    uv sync --project contrib/landlab/
    source ./contrib/landlab/.venv/bin/activate

The ``pyproject.toml`` declares ``landlab`` as a dependency.

The environment was therefore created using::

    cd ~/software/aspect_ll_mesh_def
    uv sync --project contrib/landlab/

and activated using::

    source ./contrib/landlab/.venv/bin/activate

The installed Landlab version was checked using::

    python -c "import landlab; print(landlab.__version__)"

The result was::

    2.11.0

Thus the new branch provides its own Landlab Python environment under
``contrib/landlab/.venv``.


Missing ``landlab_template.py``
-------------------------------

The custom Liang Landlab script contains::

    from landlab_template import LandLabTemplate

However, the new ``ll_mesh_def`` branch does not contain::

    contrib/python/scripts/landlab_template.py

A search of the new checkout confirmed that no ``LandLabTemplate`` class was
present::

    grep -R "class LandLabTemplate" -n ~/software/aspect_ll_mesh_def

and::

    grep -R "LandLabTemplate" -n ~/software/aspect_ll_mesh_def

returned no results.

Older Landlab-ASPECT checkouts did contain the file. For example::

    ~/software/template_Landlab_denial_90296f6_test/aspect/
    contrib/python/scripts/landlab_template.py

and::

    ~/software/landlab_ASPECT_test_2/aspect/
    contrib/python/scripts/landlab_template.py

However, the file was not copied into the new PR checkout because doing so
would mix the older interface with the new implementation.

The absence of ``landlab_template.py`` is therefore an important observation:
the new branch uses a different Python coupling interface.


Landlab Files in the New Branch
--------------------------------

A search of the Git tree for Landlab-related files showed that the new branch
contains::

    contrib/landlab/.python-version
    contrib/landlab/README.md
    contrib/landlab/pyproject.toml
    contrib/landlab/uv.lock

    include/aspect/mesh_deformation/landlab.h
    source/mesh_deformation/landlab.cc

    tests/landlab_01.cc
    tests/landlab_01.prm
    tests/landlab_01.py
    tests/landlab_01.sh

    tests/mesh_deformation_landlab_01.prm
    tests/mesh_deformation_landlab_02.prm
    tests/mesh_deformation_landlab_03.prm
    tests/mesh_deformation_landlab_cartesian.py
    tests/mesh_deformation_landlab_spherical.py

Notably, there was no ``cookbooks/landlab`` directory in the new branch.

This differs from the older Landlab-ASPECT repository organization, where
Landlab-related cookbook files existed under ``cookbooks/landlab``.

Therefore the new branch should not be assumed to use the same cookbook
structure as the previous Landlab-ASPECT implementation.


Native Landlab Test in Daniel's Branch
--------------------------------------

Before modifying the existing Liang model, the native Landlab test supplied
with Daniel's branch was executed.

The simple Landlab installation test was::

    tests/landlab_01.py

This test creates a small RasterModelGrid and verifies that Landlab can be
imported.

The more important coupling tests are::

    tests/mesh_deformation_landlab_cartesian.py
    tests/mesh_deformation_landlab_spherical.py

The spherical script was selected for the 3-D coupling test.

The test was run with the Landlab environment supplied by the branch.

The native 3-D parameter file was::

    tests/mesh_deformation_landlab_03.prm

The test was run using one MPI process initially::

    /opt/homebrew/bin/mpirun -np 1 \
    ~/software/aspect_ll_mesh_def/build/aspect-release \
    tests/mesh_deformation_landlab_03.prm

The test successfully imported::

    mesh_deformation_landlab_spherical

and created an ``IcosphereGlobalGrid``.

The output reported::

    The number of Landlab grid nodes is: 162

Landlab successfully created the topographic elevation field and initialized
the ``LinearDiffuser``.

ASPECT then successfully called the Landlab update function multiple times,
including::

    Landlab running update_until: end_time = 0.0
    Landlab running update_until: end_time = 0.0005
    Landlab running update_until: end_time = 0.001

The simulation reached its specified end time and terminated normally.

Therefore Daniel's native 3-D ASPECT--Landlab coupling test passed.


New Python Coupling Interface
-----------------------------

Inspection of the native Landlab test showed that the new branch does not use
the old ``LandLabTemplate`` class.

Instead, the Python module provides functions such as::

    initialize(comm_handle)
    finalize()
    set_mesh_information(dict_grid_information)
    get_grid_x(...)
    get_grid_y(...)
    get_grid_z(...)
    get_initial_topography(...)
    update_until(aspect_solution_dict, aspect_auxiliary_dict)
    write_output()

The exact interface is demonstrated by the native tests in the PR.

This explains why the older custom Liang script cannot be used unchanged.

The older script uses::

    from landlab_template import LandLabTemplate

and defines a class derived from::

    LandLabTemplate

The new branch does not provide that class.

The existing Liang model will therefore need to be adapted to the new
function-based interface before it can be used with ``ll_mesh_def``.


Current Status of the Testing
-----------------------------

The testing has established the following:

ASPECT branch::

    ll_mesh_def

Commit::

    f3381ee50

ASPECT version::

    3.1.0-pre

deal.II::

    9.7.0

Landlab::

    2.11.0

Landlab CMake option::

    ASPECT_WITH_LANDLAB=ON

ASPECT executable::

    /Users/biraj/software/aspect_ll_mesh_def/build/aspect-release

The following issues were identified and resolved:

* ``Script argument`` was removed because it is not declared by the new
  Landlab mesh deformation interface.
* ``Boundary composition model / Model name`` was changed to
  ``List of model names``.
* ``Initial composition model / Model name`` was changed to
  ``List of model names``.
* ``ASPECT_WITH_LANDLAB`` was changed from ``OFF`` to ``ON`` and ASPECT was
  rebuilt.
* ``Script path`` was changed from ``.`` to ``./`` so the Python module could
  be located.
* The new ``contrib/landlab`` Python environment was installed and verified.
* Landlab 2.11.0 was successfully imported.
* Daniel's native 3-D Landlab coupling test was successfully executed.


Remaining Issue
---------------

The remaining incompatibility is with the existing custom Liang Landlab
Python model.

The custom script depends on::

    landlab_template.py

and::

    LandLabTemplate

Neither is present in the ``ll_mesh_def`` branch.

The new branch instead uses a function-based Python interface.

Therefore the custom Liang model has not yet been converted to the new
interface.

This conversion is a separate task from validating Daniel's PR itself.


Summary
-------

The test demonstrates that Daniel's ``ll_mesh_def`` branch can successfully
build and execute ASPECT--Landlab coupling when the new branch configuration
and Python interface are used correctly.

The major observations were:

* The PR branch is ``ll_mesh_def`` at commit ``f3381ee50``.
* The ASPECT executable builds successfully with deal.II 9.7.0.
* Landlab support must explicitly be enabled using
  ``ASPECT_WITH_LANDLAB=ON``.
* The new branch uses ``List of model names`` for the boundary and initial
  composition model managers where the older parameter files used
  ``Model name``.
* The old ``Script argument`` parameter is not part of the new Landlab mesh
  deformation interface.
* The Landlab script path needs to be specified as ``./`` for the tested
  local script configuration.
* The new branch provides a dedicated Landlab Python environment under
  ``contrib/landlab`` and uses ``uv`` to install it.
* Landlab 2.11.0 was successfully installed and imported.
* The new branch does not contain the older ``landlab_template.py`` or
  ``LandLabTemplate`` class.
* The new branch does not contain the older ``cookbooks/landlab`` directory.
* Daniel's supplied 3-D spherical Landlab coupling test passed successfully.
* Therefore, the fundamental ASPECT--Landlab coupling implemented by the PR
  is functional.
* The remaining work is to adapt the existing Liang
  ``import-template_Liang_deposition_ada_denial_random_noise.py`` model from
  the old ``LandLabTemplate`` interface to Daniel's new function-based
  interface.

The native 3-D test is therefore a successful validation of the new
``ll_mesh_def`` Landlab coupling. The custom Liang model should be treated as
a separate compatibility/conversion task rather than evidence that the PR
coupling itself is failing.