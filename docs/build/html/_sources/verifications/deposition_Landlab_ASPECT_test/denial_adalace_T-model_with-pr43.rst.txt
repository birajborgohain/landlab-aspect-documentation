Error-2: Segmentation Fault During World Builder Initialization
=================================================================

Description
-----------

After resolving the previous Python callback interface error, ASPECT was
rebuilt from the ``pr43`` branch and executed again. Unlike the previous
failure, the simulation does **not** reach the initialization of the
Landlab interface or the first timestep.

Instead, ASPECT terminates immediately with a segmentation fault during
construction of the Geodynamic World Builder object.

Command
-------

.. code-block:: bash

   /opt/homebrew/bin/mpirun -np 23 \
     /Users/biraj/software/landlab_ASPECT_test_2/aspect/build/aspect-release \
     original_ll.prm

Software Environment
--------------------

================ ===============================
Component        Version
================ ===============================
ASPECT           3.1.0-pre (pr43, commit 41f098d71)
deal.II          9.7.0
Trilinos         16.2.0
p4est            2.8.7
MPI              OpenMPI (Homebrew)
MPI Processes    23
================ ===============================

Simulation Progress
-------------------

ASPECT starts normally and prints its version information.

.. code-block:: text

   -----------------------------------------------------------------------------
   --                             This is ASPECT                              --
   -----------------------------------------------------------------------------

Immediately afterwards, every MPI process terminates with

.. code-block:: text

   Signal: Segmentation fault: 11
   Signal code: Invalid permissions (2)
   Failing at address: 0x440000f8

No Python module is imported, and no Landlab initialization messages are
printed.

Failure
-------

Each MPI rank reports

.. code-block:: text

   Signal: Segmentation fault: 11

followed by

.. code-block:: text

   Signal code: Invalid permissions (2)

and finally

.. code-block:: text

   Failing at address: 0x440000f8

The MPI launcher subsequently reports

.. code-block:: text

   prterun noticed that process rank 7 exited on
   signal 11 (Segmentation fault)

Stack Trace
-----------

The first frames of the stack trace are

.. code-block:: text

   WorldBuilder::World::World(...)
   std::allocator<WorldBuilder::World>::construct(...)
   aspect::Simulator<2>::Simulator(...)
   main()

The crash therefore occurs while constructing the
``WorldBuilder::World`` object inside the ASPECT simulator constructor.

Root Cause
----------

Unlike the previous error, this failure does **not** originate from the
Landlab Python interface.

The simulation terminates before

* importing the Python module,
* constructing the RasterModelGrid,
* initializing Landlab components, or
* entering the timestep loop.

The stack trace indicates that the failure occurs during initialization of
the Geodynamic World Builder.

Possible causes include

* an invalid or incompatible World Builder configuration,
* an ABI mismatch between ASPECT and the linked World Builder library,
* memory corruption introduced during recent code modifications,
* inconsistent rebuild after switching branches, or
* incompatible compiler or library versions.

Execution Flow
--------------

The execution sequence is

.. code-block:: text

   MPI starts
       │
       ▼
   ASPECT executable begins
       │
       ▼
   Simulator constructor
       │
       ▼
   Construct WorldBuilder::World
       │
       ▼
   Segmentation fault (SIGSEGV)
       │
       ▼
   MPI terminates all ranks

Unlike the previous Python callback error, execution never reaches the
Landlab interface.

Comparison with Previous Failure
--------------------------------

============================== ================================= ==============================
Stage                          Previous Failure                  Current Failure
============================== ================================= ==============================
ASPECT starts                  Yes                               Yes
Python imported                Yes                               No
RasterModelGrid created        Yes                               No
Landlab initialized            Yes                               No
First timestep reached         Yes                               No
Failure type                   Python ``TypeError``              Segmentation fault
Origin                         Python callback                   World Builder initialization
MPI termination                Consequence                       Consequence
============================== ================================= ==============================

Resolution
----------

Recommended debugging steps are

1. Rebuild ASPECT, World Builder, and all dependencies from a clean build
   directory.

2. Verify that the World Builder library linked against ASPECT matches the
   version used during compilation.

3. Run the executable without the World Builder plugin (if possible) to
   isolate the source of the crash.

4. Execute the program under a debugger (e.g., ``lldb`` or ``gdb``) to
   obtain a complete backtrace.

5. Compare the ``pr43`` branch against the previous working
   ``landlab-aspect`` branch to identify changes affecting simulator
   initialization.

Summary
-------

==================== ====================================================
Item                 Status
==================== ====================================================
Simulation startup   Partial
Python import        Not reached
Landlab setup        Not reached
First timestep       Not reached
Failure type         Segmentation fault (SIGSEGV)
Origin               ``WorldBuilder::World`` constructor
Root cause           Initialization failure before Landlab interface
MPI                  Secondary; terminates after SIGSEGV
==================== ====================================================