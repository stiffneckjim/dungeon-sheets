===============
 Dungeon Sheets
===============

A tool to create character sheets and session notes for Dungeons and
Dragons 5th edition (D&D 5e).

.. image:: https://github.com/stiffneckjim/dungeon-sheets/actions/workflows/docker.yml/badge.svg
   :target: https://github.com/stiffneckjim/dungeon-sheets/actions/workflows/docker.yml
   :alt: Docker Build Status

.. image:: https://github.com/stiffneckjim/dungeon-sheets/actions/workflows/python-ci.yml/badge.svg
   :target: https://github.com/stiffneckjim/dungeon-sheets/actions/workflows/python-ci.yml
   :alt: Python CI Status

.. image:: https://img.shields.io/badge/linting-ruff-46a758.svg
    :target: https://docs.astral.sh/ruff/

Documentation
=============

Documentation can be found on readthedocs_.

.. _readthedocs: https://dungeon-sheets.readthedocs.io/en/latest/?badge=latest


Docker
======

You can run this repository directly from a container. The container images are automatically
built and published to GitHub Container Registry (GHCR) using GitHub Actions workflows.

Available Tags
--------------

- ``master``: Latest development version from the master branch
- ``latest``: Latest stable release
- Specific version tags (e.g. ``v0.19.0``)

Running the Container
---------------------

Run the following in a directory with valid character files (such as the examples_ directory):

.. code:: bash

    $ docker run -it -v $(pwd):/build ghcr.io/stiffneckjim/dungeon-sheets:master

Building Locally
----------------

To build the container locally:

.. code:: bash

    $ docker build -t dungeon-sheets .

Docker Naming Convention
------------------------

To avoid accumulating ambiguous local images/containers, use this naming scheme:

- **Published images**: ``ghcr.io/stiffneckjim/dungeon-sheets:<tag>``
- **Local runtime image**: ``dungeon-sheets:latest``
- **Local test image**: ``dungeon-sheets-test:latest``
- **One-off run container name**: ``ds-run-<sheet-or-folder>`` (with ``--rm``)

Example (local runtime image):

.. code:: bash

    $ docker build --target dungeon-sheets -t dungeon-sheets:latest .

Example (named one-off container):

.. code:: bash

    $ docker run --rm --name ds-run-rogue1 -v $(pwd):/build dungeon-sheets:latest --fancy --paper-size a4 --output-format pdf --tex-template

If you have older local tags from previous debugging sessions, you can list them with:

.. code:: bash

    $ docker image ls | grep dungeon-sheets

Running Tests with Docker
-------------------------

You can build and run the dedicated test image stage to execute the full test suite
inside the containerized environment.

Build the test stage:

.. code:: bash

    $ docker build --target dungeon-sheets-test -t dungeon-sheets-test .

Run the test stage image:

.. code:: bash

    $ docker run --rm -it dungeon-sheets-test

The test image runs ``.devcontainer/run-tests.sh``, which executes the project's
test checks in the container.

Running CI Builds Locally (Before Push)
---------------------------------------

To validate changes before pushing to GitHub, run the same checks used by
the GitHub Actions workflows.

Python CI workflow equivalent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the fastest way to mirror the Python package workflow:

.. code:: bash

    $ docker build --target dungeon-sheets-test -t dungeon-sheets-test .

.. code:: bash

    $ docker run --rm -it dungeon-sheets-test

This executes linting, sheet generation checks, and pytest via
``.devcontainer/run-tests.sh``.

.. note::

    Coveralls uploads in GitHub Actions come from a single canonical job (Python 3.13)
    using the official Coveralls GitHub Action. The full Python matrix (3.10-3.13)
    is still run for compatibility checks, but coverage reporting is intentionally based
    on that canonical run.

Direct host run (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you prefer running directly on your host instead of Docker:

.. code:: bash

    $ uv sync --extra dev

.. code:: bash

    $ bash .devcontainer/run-tests.sh

Docker workflow equivalent
~~~~~~~~~~~~~~~~~~~~~~~~~~

To verify the Docker image build locally:

.. code:: bash

    $ docker build -t dungeon-sheets-local .

To mirror the multi-architecture build used in GitHub Actions:

.. code:: bash

    $ docker buildx create --use --name ds-builder

.. code:: bash

    $ docker buildx build --platform linux/amd64,linux/arm64 --load -t dungeon-sheets-local .

Container Details
-----------------

The container:

- Is based on Ubuntu with required dependencies (pdftk, texlive) pre-installed
- Mounts the current directory as ``/build`` to access character files
- Includes the latest version of dungeon-sheets from the specified branch/tag

Windows Usage
-------------

**Prerequisites:**

- Docker Desktop for Windows installed and running (https://www.docker.com/products/docker-desktop/)
- Character files ready (Python ``.py`` files or JSON exports from VTTs)

**Quick Start:**

1. Build the image (one-time setup):

   .. code:: powershell

       cd C:\path\to\dungeon-sheets
       docker build -t dungeon-sheets .

2. Or use the pre-built image (faster, no build needed):

   .. code:: powershell

       docker pull ghcr.io/stiffneckjim/dungeon-sheets:main

**Generate Character Sheets:**

Using PowerShell:

.. code:: powershell

    # Navigate to your character files directory
    cd C:\DnD\Characters

    # Generate fancy sheets with decorations
    docker run -it -v ${PWD}:/build ghcr.io/stiffneckjim/dungeon-sheets:main --fancy

    # Generate all sheets recursively
    docker run -it -v ${PWD}:/build ghcr.io/stiffneckjim/dungeon-sheets:main --fancy --recursive

    # Generate editable PDF forms
    docker run -it -v ${PWD}:/build ghcr.io/stiffneckjim/dungeon-sheets:main --editable

Using Command Prompt (CMD):

.. code:: cmd

    cd C:\DnD\Characters
    docker run -it -v %cd%:/build ghcr.io/stiffneckjim/dungeon-sheets:main --fancy

**Common Options:**

- ``--fancy``: Generate sheets with D&D styling and decorations (recommended!)
- ``--editable``: Create fillable PDF forms
- ``--recursive``: Process all character files in subdirectories
- ``--output-format=epub``: Generate ePub format for tablets/e-readers

**Example Workflow:**

.. code:: powershell

    # One-time: Create folder and pull image
    mkdir C:\DnD\MyGroup
    docker pull ghcr.io/stiffneckjim/dungeon-sheets:main

    # Add your character .py or .json files to C:\DnD\MyGroup

    # Generate sheets before each session
    cd C:\DnD\MyGroup
    docker run -it -v ${PWD}:/build ghcr.io/stiffneckjim/dungeon-sheets:main --fancy --recursive

The PDFs will be created in the same folder, ready to print or share!

**Troubleshooting:**

- Make sure Docker Desktop is running (check system tray for whale icon)
- Enable file sharing in Docker Desktop → Settings → Resources → File Sharing
- Use ``--debug`` flag for detailed error messages


Installation
============

.. code:: bash

    $ pip install dungeonsheets

For Development
---------------

If you want to contribute or use the fancy D&D 5e LaTeX styling, clone with submodules:

.. code:: bash

    $ git clone https://github.com/canismarko/dungeon-sheets.git
    $ cd dungeon-sheets
    $ git submodule update --init --recursive
    $ pip install -e ".[dev]"

The submodule includes the `D&D 5e LaTeX template`_ for beautiful character sheets.

.. _D&D 5e LaTeX template: https://github.com/rpgtex/DND-5e-LaTeX-Template

.. note::

    Dungeon sheets supports **Python 3.10 through 3.13**.
    If you need to work with older Python versions, pin to an older
    release of dungeon-sheets that still supports your interpreter.

Optional External dependencies
==============================

* You may use **pdftk** to generate the sheets in PDF format.
* You will need **lualatex**, and a few latex packages, installed to
  generate the PDF spell pages (optional).

If **pdftk** is available, it will be used for pdf generation. If not,
a fallback python library (pypdf) will be used. This has the
limitation that it is not able to flatten PDF forms.

Different linux distributions have different names for packages. While
pdftk is available in Debian and derivatives as **pdftk**, the package
is not available in some RPM distributions, such as Fedora and CentOS.
One alternative would be to build your PC sheets using docker.

If the ``lualatex`` command is available on your system, spellcasters
will include a spellbook with descriptions of each spell known. If
not, then this feature will be skipped.

In order to properly format descriptions for spells/features/etc.,
some additional latex packages are needed. On Ubuntu these can be
install with:

.. code:: bash

    $ sudo apt-get -y install pdftk texlive-latex-base texlive-latex-extra texlive-fonts-recommended

Usage
=====

Each character or set of GM notes is described by a python (or a VTTES
JSON) file, which gives many attributes associated with the
character. See examples_ for more information about the character
descriptions.

.. _examples: https://github.com/stiffneckjim/dungeon-sheets/tree/master/examples

The PDF's can then be generated using the ``makesheets`` command. If
no filename is given, the current directory will be parsed and any
valid files found will be processed. If the ``--recursive`` option is
used, sub-folders will also be parsed.

.. code:: bash

    $ cd examples
    $ makesheets

Command Line Reference
----------------------

Usage syntax:

.. code:: bash

        $ makesheets [OPTIONS] [filename_or_directory ...]

Positional arguments
~~~~~~~~~~~~~~~~~~~~

- ``filename_or_directory`` (zero or more)
    - One or more character files (``.py`` or supported VTT JSON exports), or directories containing them.
    - If omitted, ``makesheets`` scans the current directory.
    - Directories are always scanned at the top level; use ``--recursive`` to include nested subdirectories.

Options
~~~~~~~

- ``-e``, ``--editable``
    - Keep PDF form fields editable.
    - Default behavior (without this flag) is to flatten standard fillable PDFs.
    - Note: if ``pdftk`` is unavailable and fallback ``pypdf`` is used, true flattening is limited by the fallback backend.

- ``-r``, ``--recursive``
    - Recursively search subdirectories for valid character files.
    - Useful when pointing to a campaign folder instead of individual files.

- ``-S``, ``--spells-by-level``
    - Sort spell listings by spell level instead of alphabetical order.
    - Affects spellbook/features rendering.

- ``-F``, ``--fancy``, ``--fancy-decorations``
    - Enable D&D-themed decorative LaTeX styling on additional rendered pages.
    - Requires LaTeX dependencies and the D&D 5e template assets.
    - This mode is more visually rich, but can run slower due to extra LaTeX rendering work.

- ``-T``, ``--tex-template``
    - Experimental mode: render the main character sheet from the LaTeX template instead of using fillable PDF forms.
    - Intended for advanced users; output and compatibility can differ from the default PDF-template pipeline.

- ``-o``, ``--output-format {pdf,epub}``
    - Choose output format.
    - ``pdf`` (default): generates merged character sheets as PDF.
    - ``epub``: generates an EPUB file instead of a PDF.

- ``-p``, ``--paper-size {letter,a4}``
    - Set paper size for rendered output pages.
    - Default is ``letter``.

- ``-d``, ``--debug``
    - Enable verbose logging.
    - Also forces single-process execution (instead of multiprocessing), which is useful for diagnosing failures but typically slower for bulk generation.
    - Depending on generation path and failures, intermediate artifacts may be easier to inspect when debugging.

Defaults and behavior summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Default output format is ``pdf``.
- Default paper size is ``letter``.
- Without ``--editable``, standard PDF-form pages are flattened when backend support is available.
- Without ``--debug``, files are processed with multiprocessing for speed.
- Spell pages are only generated for spellcasters.
- Additional features/notes pages are rendered through LaTeX when content is available.

Practical examples
~~~~~~~~~~~~~~~~~~

Generate all valid sheets in the current folder:

.. code:: bash

        $ makesheets

Generate one specific character file:

.. code:: bash

        $ makesheets examples/wizard1.py

Process a directory tree recursively:

.. code:: bash

        $ makesheets examples --recursive

Generate fancy decorated output with A4 pages:

.. code:: bash

        $ makesheets examples/wizard1.py --fancy --paper-size a4

Keep editable form fields:

.. code:: bash

        $ makesheets examples/cleric1.py --editable

Generate EPUB instead of PDF:

.. code:: bash

        $ makesheets examples/bard1.py --output-format epub

Debug a failing character file with verbose logs:

.. code:: bash

        $ makesheets examples/suspect_character.py --debug

dungeon-sheets contains definitions for standard weapons and spells,
so attack bonuses and damage can be calculated automatically.

Consider using the ``-F`` option to include the excellent D&D 5e
template for rendering spellbooks, druid wild forms and features
pages (https://github.com/rpgtex/DND-5e-LaTeX-Template).

By default, your character's spells are ordered alphabetically. If you
would like your spellbook to be ordered by level, you can use the ``-S``
option to do so.

If you'd like a **step-by-step walkthrough** for creating a new
character, just run ``create-character`` from a command line and a
helpful menu system will take care of the basics for you.


Content Descriptions
====================

The descriptions of content elements (e.g. classes, spells, etc.) are
included in docstrings. The descriptions should ideally conform to
reStructured text. This allows certain formatting elements to be
properly parsed and rendered into LaTeX or HTML::

  class Scrying(Spell):
    """You can see and hear a particular creature you choose that is on
    the same plane of existence as you. The target must make a Wisdom
    saving throw, which is modified by how well you know the target
    and the sort of physical connection you have to it. If a target
    knows you're casting this spell, it can fail the saving throw
    voluntarily if it wants to be observed.

    Knowledge - Save Modifier
    -------------------------
    - Secondhand (you have heard of the target) - +5
    - Firsthand (you have met the target) - +0
    - Familiar (you know the target well) - -5

    Connection - Save Modifier
    --------------------------
    - Likeness or picture - -2
    - Possession or garment - -4
    - Body part, lock of hair, bit of nail, or the like - -10

    """
    name = "Scrying"
    level = 5
    ...

For content that is not part of the SRD, consider using other
sources. As an example, parse5e_ can be used to retrieve spells.


.. _parse5e: https://github.com/user18130814200115-2/parse5e
