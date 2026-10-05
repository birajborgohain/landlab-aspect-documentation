Preparing the ASPECT–Landlab MFD Sediment Routing Development Environment (Oct 4, 2026,  MFD Day 3)
===================================================================================================

.. important:: This document is a summary of the Git/GitHub preparation for the ASPECT–Landlab.

   **Set up ASPECT:** Forked, cloned, and created the project feature branch.

   **Added Landlab:** Integrated Landlab as a Git submodule.

   **Prepared development:** Created the Landlab feature branch for MFD sediment routing and python file `flow_accumulator_mfd_marine_deposition.py`.

Overview
--------

This document records the Git/GitHub preparation for the ASPECT–Landlab
multiple-flow-direction (MFD) sediment-routing project. The purpose of this
day was to create a clean ASPECT development environment, connect Landlab to
the ASPECT project through Git submodules, and create a dedicated Landlab
feature branch for development of the new component.

The proposed Landlab component is::

    flow_accumulator_mfd_marine_deposition.py

and will eventually be developed under::

    landlab/src/landlab/components/flow_accum/

The central repository concept is:

::

    ASPECT repository
        |
        +-- landlab/  <-- separate Landlab Git repository
                         |
                         +-- feature/mfd-sediment-routing

ASPECT and Landlab remain independent Git repositories. The Landlab repository
is included inside the ASPECT working tree as a Git submodule so that ASPECT
can track a specific Landlab commit while Landlab retains its own history,
branches, tests, and review process.

1. Forking ASPECT
-----------------

The project began by forking the ASPECT repository on GitHub.

Upstream repository::

    https://github.com/geodynamics/aspect.git

Why fork ASPECT?
~~~~~~~~~~~~~~~~

A fork provides a personal GitHub repository in which project-specific
development can be performed without directly modifying the upstream ASPECT
repository.

The fork provides a place to:

* create project-specific branches;
* push development commits;
* maintain the project independently;
* share the work with collaborators;
* eventually propose changes through a pull request.

The fork is therefore the GitHub-level home for the ASPECT side of this
project.

2. Creating a Dedicated Project Directory
------------------------------------------

A separate working directory was created:

::

    ~/software/aspect_fork/aspect-landlab-mfd-sediment

This directory is dedicated to the ASPECT–Landlab MFD sediment-routing
development.

Why create a separate directory?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The project will involve changes to both ASPECT and Landlab. A separate
working directory prevents this experimental development from being mixed
with an existing ASPECT working copy, build, or unrelated research branch.

The intended project structure is:

::

    ~/software/aspect_fork/
        |
        +-- aspect/
        |
        +-- aspect-landlab-mfd-sediment/

The second directory is the clean development environment for this project.

3. Cloning ASPECT
-----------------

Inside the project directory, ASPECT was cloned using:

::

    git clone https://github.com/geodynamics/aspect.git

This created the ASPECT source tree.

The repository contains directories such as:

::

    source/
    tests/
    cookbooks/
    benchmarks/
    include/
    contrib/
    doc/

At this stage, Landlab was not yet present.

4. Inspecting the Initial Git State
------------------------------------

Several commands were used to establish the initial repository state.

4.1 ``git status``
~~~~~~~~~~~~~~~~~~

::

    git status

``git status`` reports the current branch and the state of the working tree.

It tells us whether files are modified, staged, or untracked.

Checking this before development establishes a clean baseline. Later, when
new files are created, ``git status`` makes it possible to see exactly what
has changed.

4.2 ``git branch --show-current``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    git branch --show-current

This displays the currently checked-out Git branch.

It is useful for confirming that development is taking place on the intended
branch rather than accidentally modifying ``main`` or another branch.

4.3 ``git remote -v``
~~~~~~~~~~~~~~~~~~~~~

::

    git remote -v

This displays the configured Git remotes and their fetch/push URLs.

Remotes identify other repositories associated with the local repository.
Understanding the remotes is important before pushing a branch because the
developer needs to know where the branch will be published.

4.4 ``ls -la .gitmodules``
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    ls -la .gitmodules

This checks whether the repository already has a Git submodule configuration
file.

The initial ASPECT ``.gitmodules`` contained:

::

    [submodule "contrib/WorldBuilder"]
            path = contrib/WorldBuilder
            url = https://github.com/GeodynamicWorldBuilder/WorldBuilder.git

This showed that ASPECT already used a Git submodule for WorldBuilder.

Importantly, there was initially no Landlab entry.

5. The Initial ``.gitmodules`` Situation
----------------------------------------

The initial configuration was:

::

    [submodule "contrib/WorldBuilder"]
            path = contrib/WorldBuilder
            url = https://github.com/GeodynamicWorldBuilder/WorldBuilder.git

The absence of:

::

    [submodule "landlab"]

meant that Landlab was not configured as a submodule in this clone.

This distinction matters because Landlab is an independent Git repository.
Simply using Landlab in the project does not automatically place its source
tree inside ASPECT. It has to be explicitly added.

6. Creating the ASPECT Project Branch
-------------------------------------

A dedicated ASPECT feature branch was created for the project.

The branch name is:

::

    feature/landlab-mfd-sediment-routing

This branch belongs to the ASPECT repository.

Why use a feature branch?
~~~~~~~~~~~~~~~~~~~~~~~~~

The feature branch isolates project development from the main development
line.

Conceptually:

::

    ASPECT main
        |
        +---- feature/landlab-mfd-sediment-routing
                         |
                         +-- ASPECT–Landlab project

A feature branch provides:

* an isolated development history;
* a clean basis for testing;
* easier code review;
* the ability to make experimental changes without affecting ``main``;
* a clear branch that can later be shared through GitHub.

7. Adding Landlab as a Git Submodule
------------------------------------

From:

::

    ~/software/aspect_fork/aspect-landlab-mfd-sediment

the Landlab repository was added with:

::

    git submodule add https://github.com/landlab-aspect/landlab.git landlab

The command cloned Landlab into:

::

    ~/software/aspect_fork/aspect-landlab-mfd-sediment/landlab

and changed the ASPECT ``.gitmodules`` configuration.

The resulting configuration became:

::

    [submodule "contrib/WorldBuilder"]
            path = contrib/WorldBuilder
            url = https://github.com/GeodynamicWorldBuilder/WorldBuilder.git

    [submodule "landlab"]
            path = landlab
            url = https://github.com/landlab-aspect/landlab.git

8. What ``git submodule add`` Actually Does
-------------------------------------------

The command:

::

    git submodule add https://github.com/landlab-aspect/landlab.git landlab

does several related things.

First, it clones the Landlab repository into the requested directory:

::

    landlab/

Second, it creates or updates ``.gitmodules`` in the parent ASPECT
repository.

Third, the parent ASPECT repository records the Landlab repository as a
submodule at a particular commit.

The important point is that the parent repository does not simply copy all
Landlab files into ASPECT's Git history.

Instead:

::

    ASPECT
      |
      +-- landlab/
             |
             +-- separate Git repository

This preserves the identity of Landlab as an independent project.

9. Why Submoduling Is Important Here
-------------------------------------

A Git submodule is particularly appropriate for this project because ASPECT
and Landlab are separate software projects.

They have independent:

* repositories;
* Git histories;
* branches;
* development workflows;
* maintainers;
* tests;
* releases.

The submodule creates a controlled relationship between the two.

The parent ASPECT repository can record a particular Landlab commit. This
means that the coupled development environment can be associated with an
exact Landlab source state.

The relationship can be represented as:

::

    ASPECT repository
          |
          | records a specific Landlab commit
          v
    Landlab repository

This is preferable to copying Landlab source code into ASPECT because the
new component is intended to be genuine Landlab development.

10. The Two Git Levels
----------------------

After adding the submodule, there are now two Git repositories involved.

10.1 Parent repository: ASPECT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The parent repository contains the ASPECT project branch:

::

    feature/landlab-mfd-sediment-routing

This branch controls ASPECT-side changes and the state of the Landlab
submodule used by the project.

10.2 Nested repository: Landlab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inside:

::

    aspect-landlab-mfd-sediment/landlab

there is a complete Landlab Git repository.

Its initial remote was:

::

    origin  https://github.com/landlab-aspect/landlab.git

The initial commit observed was:

::

    4ca9f8086
    Merge pull request #2358 from mcflugen/mcflugen/fix-dataset-update-for-new-xarray

These are independent Git histories.

11. Creating the Landlab Feature Branch
---------------------------------------

After adding the Landlab submodule, the Landlab repository was entered:

::

    cd landlab

The initially checked-out branch was:

::

    landlab-aspect

Rather than modifying this base branch directly, a new feature branch was
created:

::

    git checkout -b feature/mfd-sediment-routing

The branch was verified with:

::

    git branch --show-current

which returned:

::

    feature/mfd-sediment-routing

The working tree was then checked:

::

    git status

and was clean:

::

    On branch feature/mfd-sediment-routing
    nothing to commit, working tree clean

12. Why the Landlab Checkout Is Necessary
------------------------------------------

The new Python component belongs to Landlab:

::

    flow_accumulator_mfd_marine_deposition.py

Therefore, its source code should have a Landlab Git history.

Creating:

::

    feature/mfd-sediment-routing

provides an isolated development branch for the new component.

The structure is now:

::

    Landlab base branch
          |
          +---- feature/mfd-sediment-routing
                       |
                       +-- new component
                           flow_accumulator_mfd_marine_deposition.py

This keeps experimental development separate from the base Landlab branch.

13. Difference Between the Two Feature Branches
-----------------------------------------------

There are now two related but distinct feature branches.

ASPECT:

::

    feature/landlab-mfd-sediment-routing

Landlab:

::

    feature/mfd-sediment-routing

They have different responsibilities.

The ASPECT branch represents the coupled project environment and ASPECT-side
work.

The Landlab branch contains the actual Landlab component development.

Their relationship is:

::

    ASPECT
    feature/landlab-mfd-sediment-routing
            |
            | submodule pointer
            v
    Landlab
    feature/mfd-sediment-routing
            |
            +-- flow_accumulator_mfd_marine_deposition.py

14. Why Not Just Copy Landlab Into ASPECT?
------------------------------------------

Copying the Landlab source tree into ASPECT would obscure the distinction
between the two projects.

A submodule instead preserves the repository boundary.

This is especially important because the intended development will eventually
be shared with the Landlab group.

The new component should therefore be developed and tested as Landlab code,
rather than as an ASPECT-local copy of Landlab.

15. What Will Be Developed in Landlab
--------------------------------------

The proposed file is:

::

    flow_accumulator_mfd_marine_deposition.py

and its target location is:

::

    landlab/src/landlab/components/flow_accum/

The component will eventually build on existing Landlab infrastructure.

The development should proceed incrementally rather than implementing the
complete terrestrial–marine model in one step.

A useful progression is:

::

    Minimal Landlab component
            |
            v
    MFD receiver/proportion handling
            |
            v
    Sediment-routing mass conservation
            |
            v
    Connection to erosion
            |
            v
    Deposition
            |
            v
    Terrestrial-to-marine transfer
            |
            v
    Marine sediment routing
            |
            v
    FastScape verification
            |
            v
    ASPECT–Landlab coupling

16. What the Git History Will Represent
---------------------------------------

Changes made to the Landlab Python component should be committed in the
Landlab repository.

For example, after the component is implemented:

::

    git add src/landlab/components/flow_accum/flow_accumulator_mfd_marine_deposition.py
    git commit -m "Add MFD sediment routing component"

That commit belongs to Landlab.

The ASPECT repository, meanwhile, tracks the Landlab submodule at a
particular Landlab commit.

Therefore the Git history has two levels:

::

    Landlab commit
        |
        +-- actual Python source-code change

    ASPECT commit
        |
        +-- records the Landlab submodule commit used by ASPECT

This distinction is one of the most important concepts in the project.

17. Preparing for Collaboration With the Landlab Group
-------------------------------------------------------

The Landlab feature branch provides a natural location for sharing progress
with the Landlab development group.

The intended workflow is:

::

    Develop Landlab component
            |
            v
    Test locally
            |
            v
    Commit changes
            |
            v
    Push Landlab feature branch
            |
            v
    Share branch / create draft PR
            |
            v
    Obtain Landlab developer feedback
            |
            v
    Refine implementation

This allows feedback to be obtained while the component is still being
developed rather than waiting until the entire coupled ASPECT–Landlab system
is complete.

18. Why Start With a Clean Branch
---------------------------------

The Landlab feature branch currently reports:

::

    On branch feature/mfd-sediment-routing
    nothing to commit, working tree clean

This is an important checkpoint.

There are no component modifications yet. Therefore the first future commit
can clearly represent the beginning of the new development.

A clean baseline also makes debugging and code review easier because every
subsequent modification has a known starting point.

19. Final Repository Architecture After Day 3 Preparation
----------------------------------------------------------

The project now has the following architecture:

::

    ~/software/aspect_fork/
    |
    +-- aspect/
    |     |
    |     +-- existing ASPECT development
    |
    +-- aspect-landlab-mfd-sediment/
          |
          +-- ASPECT repository
          |     |
          |     +-- source/
          |     +-- tests/
          |     +-- contrib/
          |     +-- .gitmodules
          |     |
          |     +-- landlab/  <-- Git submodule
          |           |
          |           +-- Landlab repository
          |                 |
          |                 +-- src/
          |                 +-- tests/
          |                 +-- docs/
          |                 +-- ...
          |
          +-- ASPECT branch:
          |     feature/landlab-mfd-sediment-routing
          |
          +-- Landlab branch:
                feature/mfd-sediment-routing

20. Final ``.gitmodules`` Configuration
----------------------------------------

The final ``.gitmodules`` configuration after adding Landlab is:

::

    [submodule "contrib/WorldBuilder"]
            path = contrib/WorldBuilder
            url = https://github.com/GeodynamicWorldBuilder/WorldBuilder.git

    [submodule "landlab"]
            path = landlab
            url = https://github.com/landlab-aspect/landlab.git

The first entry was already part of ASPECT.

The second entry was added specifically for this ASPECT–Landlab project.

21. Day 3 Checkpoint
--------------------

At the end of this preparation, the following conditions were established.

ASPECT project directory:

::

    ~/software/aspect_fork/aspect-landlab-mfd-sediment

ASPECT feature branch:

::

    feature/landlab-mfd-sediment-routing

Landlab submodule:

::

    landlab/

Landlab remote:

::

    https://github.com/landlab-aspect/landlab.git

Landlab development branch:

::

    feature/mfd-sediment-routing

Landlab working tree:

::

    clean

The project is therefore ready for the first source-code development step.

22. Next Step: Begin Component Development
-------------------------------------------

The next task is not yet to implement the complete MFD marine sediment
model.

First, the current Landlab implementation should be inspected, especially
the existing ``FlowAccumulator`` and MFD flow-routing infrastructure.

The proposed new file will be:

::

    src/landlab/components/flow_accum/flow_accumulator_mfd_marine_deposition.py

The first implementation should follow the current Landlab component
architecture and conventions.

Development will then proceed through small, testable steps.

Conclusion
----------

Day 3 established the GitHub and repository foundation for the
ASPECT–Landlab MFD sediment-routing project.

The most important outcome is the separation of responsibilities:

::

    ASPECT
       |
       +-- coupled geodynamic framework
       |
       +-- Landlab submodule
               |
               +-- surface-process development

The Landlab source is not copied into ASPECT as ordinary source files.
Instead, it remains an independent Git repository and is linked to ASPECT
through a Git submodule.

The final development relationship is:

::

    ASPECT fork
        |
        +-- feature/landlab-mfd-sediment-routing
        |
        +-- landlab/  (Git submodule)
              |
              +-- feature/mfd-sediment-routing
                    |
                    +-- future
                        flow_accumulator_mfd_marine_deposition.py

This provides a clean, reproducible, and collaborative foundation for the
next stage of development: implementing and testing the new Landlab MFD
sediment-routing component and subsequently integrating it into the
ASPECT–Landlab workflow.
