#!/usr/bin/env bash

# ============================================================================
# ASPECT 3.1.0-pre + Landlab checkpointing
# Exact source commit:
# 28c914f482fe5d9bba409267d534e66ee5602ceb
#
# Linux / HPC installation script
#
# This script:
#   1. Checks the Linux environment
#   2. Downloads the exact ASPECT commit as a GitHub archive
#   3. Verifies the ASPECT version and Landlab checkpointing source
#   4. Detects or installs uv
#      - official curl installer first
#      - pip fallback second
#   5. Creates a Python 3.12 virtual environment
#   6. Runs uv sync for the ASPECT/Landlab Python workspace
#   7. Verifies NumPy, mpi4py, and Landlab
#   8. Detects GCC, G++, OpenMPI, CMake, and deal.II
#   9. Configures ASPECT with Python support
#  10. Builds ASPECT
#  11. Verifies aspect-release
#
# Usage:
#
#   chmod +x install_lla_check_point_aspect_3.1.0_uv.sh
#   ./install_lla_check_point_aspect_3.1.0_uv.sh
#
# If your HPC system requires a deal.II environment script, set it first:
#
#   export DEALII_ENABLE_SCRIPT=/path/to/dealii/configuration/enable.sh
#
# Then run this script.
# ============================================================================

set -Eeuo pipefail

# ============================================================================
# Configuration
# ============================================================================

ASPECT_VERSION="3.1.0-pre"
ASPECT_COMMIT="28c914f482fe5d9bba409267d534e66ee5602ceb"
ASPECT_COMMIT_SHORT="28c914f48"

SOFTWARE_DIR="${SOFTWARE_DIR:-$HOME/software}"

ASPECT_DIR="${ASPECT_DIR:-$SOFTWARE_DIR/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact}"

BUILD_DIR="${BUILD_DIR:-$ASPECT_DIR/build}"

VENV="${VENV:-$ASPECT_DIR/.venv}"

PYTHON_VERSION="${PYTHON_VERSION:-3.12}"

ASPECT_ARCHIVE="${ASPECT_ARCHIVE:-$SOFTWARE_DIR/28c914f48.tar.gz}"

# Optional HPC/deal.II environment setup script.
#
# Example for NMT:
#
# export DEALII_ENABLE_SCRIPT=/usr/local/software/gcc-14.2.0/openmpi-4.1.8/dealii/9.7.0/configuration/enable.sh
#
DEALII_ENABLE_SCRIPT="${DEALII_ENABLE_SCRIPT:-}"

# ============================================================================
# Utility functions
# ============================================================================

error_exit()
{
    echo
    echo "ERROR:"
    echo "$1"
    echo
    exit 1
}

info()
{
    echo
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}

command_exists()
{
    command -v "$1" >/dev/null 2>&1
}

# ============================================================================
# STEP 1: Check Linux environment
# ============================================================================

info "STEP 1: Checking Linux environment"

if [[ "$(uname -s)" != "Linux" ]]; then
    error_exit "This installer is intended for Linux/HPC systems.
Detected operating system: $(uname -s)"
fi

echo "Operating system : $(uname -s)"
echo "Architecture     : $(uname -m)"
echo "Home directory   : $HOME"
echo "Software dir     : $SOFTWARE_DIR"
echo "ASPECT dir       : $ASPECT_DIR"

for cmd in curl tar; do
    if ! command_exists "$cmd"; then
        error_exit "Required command '$cmd' was not found.

Please load or install '$cmd' and run this script again."
    fi
done

mkdir -p "$SOFTWARE_DIR"

# ============================================================================
# STEP 2: Download and extract exact ASPECT commit
# ============================================================================

info "STEP 2: Downloading ASPECT commit $ASPECT_COMMIT_SHORT"

cd "$SOFTWARE_DIR"

# --------------------------------------------------------------------------
# Remove an incomplete previous installation
# --------------------------------------------------------------------------

if [[ -d "$ASPECT_DIR" ]]; then
    echo
    echo "An ASPECT directory already exists:"
    echo "  $ASPECT_DIR"
    echo
    echo "Removing it before installing the exact source archive..."
    rm -rf "$ASPECT_DIR"
fi

# --------------------------------------------------------------------------
# Download exact GitHub commit archive
# --------------------------------------------------------------------------

echo
echo "Downloading exact ASPECT source:"
echo
echo "  https://github.com/landlab-aspect/aspect/archive/${ASPECT_COMMIT}.tar.gz"
echo

curl -L -o "$ASPECT_ARCHIVE" \
    "https://github.com/landlab-aspect/aspect/archive/${ASPECT_COMMIT}.tar.gz"

if [[ ! -s "$ASPECT_ARCHIVE" ]]; then
    error_exit "ASPECT archive was not downloaded correctly:
$ASPECT_ARCHIVE"
fi

echo
echo "Archive downloaded:"
echo "  $ASPECT_ARCHIVE"

# --------------------------------------------------------------------------
# Extract archive
# --------------------------------------------------------------------------

echo
echo "Extracting archive..."

tar -xzf "$ASPECT_ARCHIVE"

EXTRACTED_DIR="$SOFTWARE_DIR/aspect-$ASPECT_COMMIT"

if [[ ! -d "$EXTRACTED_DIR" ]]; then
    error_exit "Expected extracted ASPECT directory was not found:

$EXTRACTED_DIR"
fi

# --------------------------------------------------------------------------
# Rename extracted directory
# --------------------------------------------------------------------------

mv "$EXTRACTED_DIR" "$ASPECT_DIR"

echo
echo "ASPECT source installed at:"
echo "  $ASPECT_DIR"

# ============================================================================
# STEP 3: Verify ASPECT source
# ============================================================================

info "STEP 3: Verifying ASPECT source"

cd "$ASPECT_DIR"

# --------------------------------------------------------------------------
# Verify VERSION
# --------------------------------------------------------------------------

if [[ ! -f "$ASPECT_DIR/VERSION" ]]; then
    error_exit "ASPECT VERSION file was not found:
$ASPECT_DIR/VERSION"
fi

echo
echo "ASPECT VERSION:"
cat "$ASPECT_DIR/VERSION"

if ! grep -q "$ASPECT_VERSION" "$ASPECT_DIR/VERSION"; then
    error_exit "The VERSION file does not contain the expected version:
$ASPECT_VERSION"
fi

echo
echo "ASPECT version verified: $ASPECT_VERSION"

# --------------------------------------------------------------------------
# Verify Landlab checkpointing source
# --------------------------------------------------------------------------

LANDLAB_SOURCE="$ASPECT_DIR/source/mesh_deformation/landlab.cc"

if [[ ! -f "$LANDLAB_SOURCE" ]]; then
    error_exit "Landlab source file was not found:
$LANDLAB_SOURCE"
fi

if ! grep -q "resume_checkpoint" "$LANDLAB_SOURCE"; then
    error_exit "The expected 'resume_checkpoint' checkpointing code was not
found in:

$LANDLAB_SOURCE

This may indicate that the downloaded source is not the expected commit."
fi

echo
echo "Landlab checkpointing source verified:"
echo "  $LANDLAB_SOURCE"

# ============================================================================
# STEP 4: Detect or install uv
# ============================================================================

info "STEP 4: Checking uv"

# uv installed by the official installer is normally placed here.
export PATH="$HOME/.local/bin:$PATH"

# --------------------------------------------------------------------------
# uv already installed
# --------------------------------------------------------------------------

if command_exists uv; then

    echo
    echo "uv is already installed."
    echo
    echo "uv path:"
    echo "  $(command -v uv)"
    echo
    echo "uv version:"
    uv --version

else

    echo
    echo "uv was not found."
    echo "Trying to install uv..."
    echo

    # ----------------------------------------------------------------------
    # METHOD 1: Official uv installer using curl
    # ----------------------------------------------------------------------

    echo "METHOD 1: Official uv installer"
    echo

    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        echo
        echo "Official uv installer completed."
    else
        echo
        echo "Official uv installer failed."
    fi

    # The official installer normally places uv in ~/.local/bin.
    export PATH="$HOME/.local/bin:$PATH"

    if command_exists uv; then

        echo
        echo "uv successfully installed using the official installer."
        echo
        echo "uv path:"
        echo "  $(command -v uv)"
        echo
        echo "uv version:"
        uv --version

    fi

    # ----------------------------------------------------------------------
    # METHOD 2: pip fallback
    # ----------------------------------------------------------------------

    if ! command_exists uv; then

        echo
        echo "METHOD 2: pip fallback"
        echo

        if command_exists python3; then

            if python3 -m pip --version >/dev/null 2>&1; then

                echo "Installing uv with:"
                echo
                echo "  python3 -m pip install --user uv"
                echo

                python3 -m pip install --user uv

                export PATH="$HOME/.local/bin:$PATH"

            else

                echo "python3 was found, but pip is not available."

            fi

        else

            echo "python3 was not found."

        fi

    fi

    # ----------------------------------------------------------------------
    # Final uv verification
    # ----------------------------------------------------------------------

    if ! command_exists uv; then

        error_exit "uv could not be installed.

The installer tried:

  1. Official curl installer
  2. python3 -m pip install --user uv

Please install uv manually and run this script again."

    fi

    echo
    echo "uv is available:"
    echo "  $(command -v uv)"
    uv --version

fi

# ============================================================================
# STEP 5: Create Python virtual environment
# ============================================================================

info "STEP 5: Creating Python $PYTHON_VERSION virtual environment"

cd "$ASPECT_DIR"

if [[ -d "$VENV" ]]; then

    echo "Existing Python environment found:"
    echo "  $VENV"
    echo
    echo "It will be reused."

else

    echo "Creating Python virtual environment:"
    echo "  $VENV"
    echo

    uv venv --python "$PYTHON_VERSION" "$VENV"

fi

PYTHON="$VENV/bin/python"

if [[ ! -x "$PYTHON" ]]; then
    error_exit "Python executable was not created:
$PYTHON"
fi

echo
echo "Python version:"
"$PYTHON" --version

echo
echo "Python executable:"
echo "  $PYTHON"

# ============================================================================
# STEP 6: Verify Landlab workspace and run uv sync
# ============================================================================

info "STEP 6: Installing ASPECT/Landlab Python dependencies"

cd "$ASPECT_DIR"

if [[ ! -f "$ASPECT_DIR/pyproject.toml" ]]; then
    error_exit "ASPECT pyproject.toml was not found:
$ASPECT_DIR/pyproject.toml"
fi

# ASPECT's pyproject.toml declares Landlab as a uv workspace member.
# Therefore this file must exist.
if [[ ! -f "$ASPECT_DIR/landlab/pyproject.toml" ]]; then

    error_exit "The Landlab uv workspace is incomplete.

Expected:
  $ASPECT_DIR/landlab/pyproject.toml

The ASPECT pyproject.toml expects Landlab to be available as a workspace
member.

Make sure the correct Landlab source is present and run the installer again."

fi

echo "ASPECT pyproject.toml found."
echo "Landlab workspace found."
echo

echo "Running:"
echo "  uv sync"
echo

uv sync

# ============================================================================
# STEP 7: Verify Python packages
# ============================================================================

info "STEP 7: Verifying Python packages"

"$PYTHON" - <<'PY'
import sys

print("Python:")
print(sys.version)

print()

try:
    import numpy
    print("NumPy:", numpy.__version__)
except Exception as exc:
    print("ERROR: NumPy import failed:")
    print(exc)
    raise SystemExit(1)

try:
    import mpi4py
    print("mpi4py:", mpi4py.__version__)
except Exception as exc:
    print("ERROR: mpi4py import failed:")
    print(exc)
    raise SystemExit(1)

try:
    import landlab
    print("Landlab:", getattr(landlab, "__version__", "unknown"))
except Exception as exc:
    print("ERROR: Landlab import failed:")
    print(exc)
    raise SystemExit(1)
PY

# ============================================================================
# STEP 8: Detect compiler, MPI, CMake, and deal.II
# ============================================================================

info "STEP 8: Detecting build dependencies"

# --------------------------------------------------------------------------
# Optional HPC environment setup
# --------------------------------------------------------------------------

if [[ -n "$DEALII_ENABLE_SCRIPT" ]]; then

    if [[ ! -f "$DEALII_ENABLE_SCRIPT" ]]; then
        error_exit "DEALII_ENABLE_SCRIPT was specified but does not exist:

$DEALII_ENABLE_SCRIPT"
    fi

    echo "Loading deal.II environment:"
    echo "  $DEALII_ENABLE_SCRIPT"
    echo

    # shellcheck disable=SC1090
    source "$DEALII_ENABLE_SCRIPT"

fi

# --------------------------------------------------------------------------
# GCC
# --------------------------------------------------------------------------

if ! command_exists gcc; then
    error_exit "gcc was not found.

Load your GCC environment/module and run this script again."
fi

if ! command_exists g++; then
    error_exit "g++ was not found.

Load your GCC environment/module and run this script again."
fi

# --------------------------------------------------------------------------
# MPI
# --------------------------------------------------------------------------

if ! command_exists mpirun; then
    error_exit "mpirun was not found.

Load your OpenMPI environment/module and run this script again."
fi

# --------------------------------------------------------------------------
# CMake
# --------------------------------------------------------------------------

if ! command_exists cmake; then
    error_exit "cmake was not found.

Load/install CMake and run this script again."
fi

# --------------------------------------------------------------------------
# Set compiler/tool paths
# --------------------------------------------------------------------------

CC="${CC:-$(command -v gcc)}"
CXX="${CXX:-$(command -v g++)}"
MPIEXEC="${MPIEXEC:-$(command -v mpirun)}"
CMAKE_COMMAND="${CMAKE_COMMAND:-$(command -v cmake)}"

# --------------------------------------------------------------------------
# deal.II
# --------------------------------------------------------------------------

if [[ -z "${DEAL_II_DIR:-}" ]]; then

    error_exit "DEAL_II_DIR is not set.

Please load your deal.II environment or set:

  export DEAL_II_DIR=/path/to/deal.II

For NMT, you can first source the appropriate deal.II enable.sh file."

fi

if [[ ! -d "$DEAL_II_DIR" ]]; then

    error_exit "DEAL_II_DIR does not point to an existing directory:

$DEAL_II_DIR"

fi

echo "Compiler:"
echo "  CC  = $CC"
echo "  CXX = $CXX"

echo
echo "MPI:"
echo "  MPIEXEC = $MPIEXEC"

echo
echo "CMake:"
echo "  CMAKE_COMMAND = $CMAKE_COMMAND"

echo
echo "deal.II:"
echo "  DEAL_II_DIR = $DEAL_II_DIR"

echo
echo "Compiler version:"
"$CC" --version | head -n 1

echo
echo "CMake version:"
"$CMAKE_COMMAND" --version | head -n 1

echo
echo "MPI version:"
"$MPIEXEC" --version | head -n 1 || true

# ============================================================================
# STEP 9: Configure ASPECT
# ============================================================================

info "STEP 9: Configuring ASPECT with CMake"

cd "$ASPECT_DIR"

if [[ -d "$BUILD_DIR" ]]; then
    echo "Removing previous build directory:"
    echo "  $BUILD_DIR"
    rm -rf "$BUILD_DIR"
fi

mkdir -p "$BUILD_DIR"

cd "$BUILD_DIR"

echo
echo "CMake configuration:"
echo
echo "  C compiler      = $CC"
echo "  C++ compiler    = $CXX"
echo "  deal.II         = $DEAL_II_DIR"
echo "  Python          = $PYTHON"
echo "  ASPECT source   = $ASPECT_DIR"
echo

"$CMAKE_COMMAND" \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DDEAL_II_DIR="$DEAL_II_DIR" \
    -DASPECT_WITH_PYTHON=ON \
    -DPython3_EXECUTABLE="$PYTHON" \
    "$ASPECT_DIR"

# ============================================================================
# STEP 10: Build ASPECT
# ============================================================================

info "STEP 10: Building ASPECT"

cd "$BUILD_DIR"

echo "Building ASPECT..."
echo

"$CMAKE_COMMAND" --build . --parallel

# ============================================================================
# STEP 11: Verify ASPECT executable
# ============================================================================

info "STEP 11: Verifying aspect-release"

ASPECT_EXECUTABLE="$BUILD_DIR/aspect-release"

if [[ ! -x "$ASPECT_EXECUTABLE" ]]; then

    error_exit "The ASPECT executable was not created:

$ASPECT_EXECUTABLE"

fi

echo
echo "ASPECT executable:"
echo "  $ASPECT_EXECUTABLE"

echo
echo "ASPECT version:"
"$ASPECT_EXECUTABLE" --version

# ============================================================================
# STEP 12: Final summary
# ============================================================================

info "INSTALLATION COMPLETE"

echo
echo "ASPECT source:"
echo "  $ASPECT_DIR"

echo
echo "Exact ASPECT commit:"
echo "  $ASPECT_COMMIT"

echo
echo "Python environment:"
echo "  $VENV"

echo
echo "Build directory:"
echo "  $BUILD_DIR"

echo
echo "ASPECT executable:"
echo "  $ASPECT_EXECUTABLE"

echo
echo "To activate the Python environment:"
echo
echo "  source \"$VENV/bin/activate\""

echo
echo "To run ASPECT:"
echo
echo "  \"$ASPECT_EXECUTABLE\" your_file.prm"

echo
echo "To run ASPECT with MPI:"
echo
echo "  mpirun -np 8 \"$ASPECT_EXECUTABLE\" your_file.prm"

echo
echo "Installation finished successfully."
