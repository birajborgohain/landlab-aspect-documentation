PR-1 response (Day1) PR #47: Cleanup of Inherited Commit History
=================================================================

Purpose
-------

This document records the Git cleanup performed for PR #47,
``add_aspect_landlab_diffusion_benchmark``.

The purpose of the cleanup was to address the review comment that the PR had
unintentionally inherited commits from the previous ``add-template-python``
PR.

The main goal was to:

* identify which commits belonged to the previous PR,
* preserve only the diffusion-of-hill benchmark work,
* remove the unrelated inherited commits from the PR history,
* verify that the cleaned PR contains only the intended benchmark changes, and
* safely update the remote GitHub branch.

Problem Identified by the Reviewer
-----------------------------------

The reviewer identified two main concerns.

The first concern was related to the shared library:

``libanalytical_topography.so``

which is referenced in the ASPECT parameter file but whose corresponding
``.cc`` source file was not included in the PR.

The second concern was that the PR had inherited a commit from a previous PR.

This document addresses the **second concern only**. The shared-library issue
is a separate item and still needs to be addressed.

Initial Branch State
--------------------

The branch was:

``add_aspect_landlab_diffusion_benchmark``

The initial Git history showed the following commits above the PR #46 base:

.. code-block:: text

    8c97b4dc5  add landlab-ASPECT diffusion of hill benchmark
    41f098d71  add doc strings
    5548508dd  add python template
    f379b92ac  Merge pull request #46 from danieldouglas92/lla-merge-upstream

The important observation was that the two commits

``5548508dd`` and ``41f098d71``

were not part of the diffusion-of-hill benchmark itself.

They originated from the previous ``add-template-python`` work.

Identifying the Inherited Commits
----------------------------------

The command

.. code-block:: bash

    git --no-pager log --oneline origin/main..HEAD

was used to inspect the commits that were present in the branch history.

The relevant part of the history was:

.. code-block:: text

    8c97b4dc5  add landlab-ASPECT diffusion of hill benchmark
    41f098d71  add doc strings
    5548508dd  add python template
    f379b92ac  Merge pull request #46 from danieldouglas92/lla-merge-upstream

The individual commits were then inspected using:

.. code-block:: bash

    git show --stat --oneline 8c97b4dc5

    git show --stat --oneline 41f098d71

    git show --stat --oneline 5548508dd

The results showed that ``5548508dd`` contained:

.. code-block:: text

    contrib/python/scripts/landlab_template.py
    cookbooks/landlab/test-template/TEST-TEMPLATE.prm
    cookbooks/landlab/test-template/import-template.py
    source/mesh_deformation/landlab.cc

The commit ``41f098d71`` contained:

.. code-block:: text

    contrib/python/scripts/landlab_template.py
    tests/mesh_deformation_external_landlab_01.py
    tests/mesh_deformation_external_landlab_02.py

These files were related to the previous ``add-template-python`` work and
were not intended to be part of the diffusion-of-hill benchmark PR.

Confirming the Previous PR Relationship
---------------------------------------

The history of ``landlab_template.py`` was checked with:

.. code-block:: bash

    git --no-pager log --oneline --all \
        -- contrib/python/scripts/landlab_template.py

This showed:

.. code-block:: text

    895b396ed  (danieldouglas92/add-template-python) add doc strings
    41f098d71  add doc strings
    5548508dd  add python template

This confirmed that these commits were associated with the previous
``add-template-python`` branch.

The Actual Benchmark Commit
----------------------------

The benchmark commit was inspected separately:

.. code-block:: bash

    git show --stat --oneline 8c97b4dc5

The result showed that the benchmark commit contained only three files:

.. code-block:: text

    benchmarks/diffusion_of_hill/1_shine_zero_flux_landlab_import-template.py
    benchmarks/diffusion_of_hill/1_sine_zero_flux_landlab.prm
    benchmarks/diffusion_of_hill/plotter_Landlab_ASPECT_benchmark_diffusion_hill.py

The commit contained:

.. code-block:: text

    3 files changed, 592 insertions(+)

This confirmed that the benchmark itself could be separated cleanly from the
two inherited commits.

Protecting the Existing Work
----------------------------

Before modifying the Git history, the existing uncommitted ``uv.lock``
modification was protected using Git stash.

The command used was:

.. code-block:: bash

    git stash push -m "backup before cleaning PR 47"

Git confirmed:

.. code-block:: text

    Saved working directory and index state
    On add_aspect_landlab_diffusion_benchmark:
    backup before cleaning PR 47

The working tree was then checked:

.. code-block:: bash

    git status

The result was:

.. code-block:: text

    nothing to commit, working tree clean

Creating a Backup Branch
------------------------

Before rewriting the branch history, a backup branch was created:

.. code-block:: bash

    git branch backup-pr47-before-cleanup

This provided an additional safety point in case the history cleanup needed
to be reversed.

The backup branch preserved the previous state of the PR branch before the
history was rewritten.

Resetting to the Correct Base
-----------------------------

The correct base for this PR was identified as:

.. code-block:: text

    f379b92ac

This was the merge commit for PR #46:

.. code-block:: text

    f379b92ac  Merge pull request #46 from danieldouglas92/lla-merge-upstream

The branch was reset to this commit using:

.. code-block:: bash

    git reset --hard f379b92ac

Git confirmed:

.. code-block:: text

    HEAD is now at f379b92ac
    Merge pull request #46 from danieldouglas92/lla-merge-upstream

At this point, the inherited commits

.. code-block:: text

    5548508dd
    41f098d71

were no longer part of the active PR branch.

Restoring Only the Benchmark Commit
-----------------------------------

The original benchmark commit was:

.. code-block:: text

    8c97b4dc5

This commit was preserved and then reapplied to the cleaned branch using
``git cherry-pick``:

.. code-block:: bash

    git cherry-pick 8c97b4dc5

Git created a new commit:

.. code-block:: text

    7f48d264d add landlab-ASPECT diffusion of hill benchmark

The commit contained the same benchmark changes but now existed directly on
top of the correct PR #46 base.

The resulting history became:

.. code-block:: text

    7f48d264d  add landlab-ASPECT diffusion of hill benchmark
    f379b92ac  Merge pull request #46 from danieldouglas92/lla-merge-upstream

This is the desired structure for the PR.

Why the Commit Hash Changed
----------------------------

The original benchmark commit was:

.. code-block:: text

    8c97b4dc5

After cherry-picking it onto a different parent commit, Git created a new
commit:

.. code-block:: text

    7f48d264d

This is expected behavior.

The commit hash changed because a Git commit contains information about its
parent commit. Since the benchmark commit was moved from the old history to
the cleaned history, Git generated a new commit ID.

The benchmark content itself was preserved.

Verifying the Working Tree
--------------------------

After the cherry-pick, the working tree was checked:

.. code-block:: bash

    git status

The result was:

.. code-block:: text

    On branch add_aspect_landlab_diffusion_benchmark

    nothing to commit, working tree clean

This confirmed that the cherry-pick completed successfully and did not leave
uncommitted changes.

Verifying the Commit History
----------------------------

The cleaned history was inspected using:

.. code-block:: bash

    git log --oneline -5

The relevant history became:

.. code-block:: text

    7f48d264d  add landlab-ASPECT diffusion of hill benchmark
    f379b92ac  Merge pull request #46 from danieldouglas92/lla-merge-upstream

The previously inherited commits

.. code-block:: text

    5548508dd  add python template
    41f098d71  add doc strings

were no longer between the PR base and the benchmark commit.

Verifying the PR Changes
------------------------

The difference between the PR #46 base and the new branch was checked using:

.. code-block:: bash

    git diff --name-status f379b92ac..HEAD

The resulting files were:

.. code-block:: text

    A    benchmarks/diffusion_of_hill/1_shine_zero_flux_landlab_import-template.py
    A    benchmarks/diffusion_of_hill/1_sine_zero_flux_landlab.prm
    A    benchmarks/diffusion_of_hill/plotter_Landlab_ASPECT_benchmark_diffusion_hill.py

This is an important verification step because it confirms that the cleaned
branch contains only the intended diffusion-of-hill benchmark files relative
to the PR #46 base.

Updating the GitHub Branch
--------------------------

Because the branch history had been rewritten, a normal ``git push`` would
not be sufficient.

The cleaned branch was pushed using:

.. code-block:: bash

    git push --force-with-lease origin add_aspect_landlab_diffusion_benchmark

The push completed successfully:

.. code-block:: text

    + 8c97b4dc5...7f48d264d
      add_aspect_landlab_diffusion_benchmark
      -> add_aspect_landlab_diffusion_benchmark (forced update)

The use of ``--force-with-lease`` was intentional because the branch history
had been rewritten. It also provides protection against unexpectedly
overwriting newer remote work.

Final Result
------------

Before cleanup, the relevant history was:

.. code-block:: text

    f379b92ac  PR #46 base
        |
    5548508dd  add python template
        |
    41f098d71  add doc strings
        |
    8c97b4dc5  add landlab-ASPECT diffusion of hill benchmark

The first two commits were inherited from the previous PR.

After cleanup, the history is:

.. code-block:: text

    f379b92ac  PR #46 base
        |
    7f48d264d  add landlab-ASPECT diffusion of hill benchmark

The PR now contains only the benchmark changes relative to the PR #46 base.

Issue Addressed
---------------

This cleanup addresses the reviewer's concern:

    "You've inherited a commit from a previous PR here. It would be good
    if you can remove this commit and just keep the changes that you've
    made here."

The inherited ``add-template-python`` commits were removed from the PR
history, while the diffusion-of-hill benchmark was preserved.

The final PR branch was also successfully pushed to GitHub.

Remaining Review Issue
----------------------

The shared-library concern is separate from the Git history issue.

The benchmark parameter file currently contains:

.. code-block:: text

    set Additional shared libraries = libanalytical_topography.so

The reviewer also asked whether the hill topography is defined in the
shared library and pointed out that the corresponding ``.cc`` source file
is not included in the PR.

This issue has **not** been resolved by the Git cleanup described above.

The next step is therefore to identify:

* where ``libanalytical_topography.so`` is built,
* which ``.cc`` source produces it,
* whether that source already exists in the repository,
* whether it belongs in this benchmark PR, and
* whether the benchmark can instead use an existing ASPECT mechanism without
  requiring an untracked or externally built shared library.

Current Status
--------------

The commit-history issue is resolved.

The current benchmark branch contains the intended benchmark commit:

.. code-block:: text

    7f48d264d  add landlab-ASPECT diffusion of hill benchmark

and is based directly on:

.. code-block:: text

    f379b92ac  Merge pull request #46 from danieldouglas92/lla-merge-upstream

The remaining task is to address the
``libanalytical_topography.so`` / missing ``.cc`` source issue raised in the
review.


Pull Request Review Response
--------------------------------

Thank you, Daniel, for the detailed review and for pointing out the issues.
I have addressed the commit-history issue you mentioned.

Commit History
--------------

The PR had unintentionally inherited two commits from the previous
``add-template-python`` PR:

* ``5548508dd`` — ``add python template``
* ``41f098d71`` — ``add doc strings``

These commits contained changes to ``landlab_template.py``, the test-template
files, and the external Landlab test scripts, which were not part of this
benchmark PR.

I cleaned up the branch by:

#. Stashing my local ``uv.lock`` modification so it would not be affected.
#. Creating a backup branch, ``backup-pr47-before-cleanup``, before modifying
   the history.
#. Resetting the PR branch to the correct base commit:

   ``f379b92ac`` — the merge commit for PR #46.

#. Cherry-picking only my actual benchmark commit.
#. The benchmark is now represented by the new commit:

   ``7f48d264d`` — ``add landlab-ASPECT diffusion of hill benchmark``

#. Verified that this commit contains only the three benchmark files:

   * ``benchmarks/diffusion_of_hill/1_shine_zero_flux_landlab_import-template.py``
   * ``benchmarks/diffusion_of_hill/1_sine_zero_flux_landlab.prm``
   * ``benchmarks/diffusion_of_hill/plotter_Landlab_ASPECT_benchmark_diffusion_hill.py``

#. Force-pushed the cleaned branch using ``--force-with-lease``.

The resulting history is now essentially::

    f379b92ac  ->  7f48d264d

rather than including the two commits inherited from the previous PR.

I believe this addresses the concern about the inherited commit and keeps
this PR focused only on the diffusion-of-hill benchmark.

Shared Library Issue
--------------------

I have not yet addressed the shared-library issue regarding
``libanalytical_topography.so``. I will handle that separately by checking
the corresponding ``.cc`` source and build setup and updating the PR
accordingly.

Thanks again for the review.