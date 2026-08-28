
#!/bin/bash

# ============================================================
# Interactive ASPECT Installation Script
#
# ASPECT version:
#     3.1.0-pre
#
# Exact commit:
#     28c914f482fe5d9bba409267d534e66ee5602ceb
#
# Short commit:
#     28c914f48
#
# Purpose:
#     Find the required software environment, allow the user
#     to select the desired installations, download the exact
#     ASPECT source, configure, build, and verify ASPECT.
#
# Compatible with macOS Bash 3.2 and newer Bash versions.
#
# ============================================================

set -e


# ============================================================
# Configuration
# ============================================================

ASPECT_VERSION="3.1.0-pre"

ASPECT_COMMIT="28c914f482fe5d9bba409267d534e66ee5602ceb"

ASPECT_SHORT_COMMIT="28c914f48"

REQUIRED_GCC_VERSION="14.2"

REQUIRED_OPENMPI_VERSION="4.1.8"

REQUIRED_DEAL_II_VERSION="9.7.0"

REQUIRED_CMAKE_VERSION="3.26.4"

REQUIRED_PYTHON_VERSION="3.12.13"


# ============================================================
# Determine directory containing this script
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

SOFTWARE_DIR="$SCRIPT_DIR"

ASPECT_DIR="$SOFTWARE_DIR/aspect-3.1.0-pre-lla-checkpointing-28c914f48-exact"

BUILD_DIR="$ASPECT_DIR/build"

ARCHIVE="$SOFTWARE_DIR/28c914f48.tar.gz"

ASPECT_EXECUTABLE="$BUILD_DIR/aspect-release"


# ============================================================
# Helper functions
# ============================================================

pause_step()
{
    echo
    echo "------------------------------------------------------------"
    read -r -p "Proceed with this step? [y/N]: " ANSWER

    case "$ANSWER" in
        y|Y|yes|YES)
            echo
            echo "Proceeding..."
            ;;
        *)
            echo
            echo "Installation stopped by user."
            exit 0
            ;;
    esac
}


error_exit()
{
    echo
    echo "============================================================"
    echo "ERROR"
    echo "============================================================"
    echo
    echo "$1"
    echo
    exit 1
}


confirm_use()
{
    read -r -p "$1 [y/N]: " ANSWER

    case "$ANSWER" in
        y|Y|yes|YES)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}


# ============================================================
# Welcome
# ============================================================

clear

echo "============================================================"
echo "       Historical ASPECT Interactive Installer"
echo "============================================================"

echo
echo "ASPECT version:"
echo "  $ASPECT_VERSION"

echo
echo "Exact commit:"
echo "  $ASPECT_COMMIT"

echo
echo "Short commit:"
echo "  $ASPECT_SHORT_COMMIT"

echo
echo "Installer directory:"
echo "  $SCRIPT_DIR"

echo
echo "Installation directory:"
echo "  $ASPECT_DIR"

echo
echo "The installer will:"
echo
echo "  1. Check the operating system"
echo "  2. Find required commands"
echo "  3. Find and select the compiler"
echo "  4. Find and select MPI"
echo "  5. Find and select CMake"
echo "  6. Find and select Python"
echo "  7. Find and select deal.II"
echo "  8. Show the complete selected environment"
echo "  9. Download the exact ASPECT commit"
echo " 10. Verify the ASPECT source"
echo " 11. Configure ASPECT"
echo " 12. Build ASPECT"
echo " 13. Verify the executable"

echo
echo "No existing ASPECT installation will be deleted automatically."

pause_step


# ============================================================
# STEP 1
# Operating system
# ============================================================

echo
echo "============================================================"
echo "STEP 1: Operating system"
echo "============================================================"

OS_NAME="$(uname -s)"

echo
echo "Detected operating system:"
echo
echo "  $OS_NAME"

case "$OS_NAME" in

    Linux)

        echo
        echo "Linux detected."

        ;;

    Darwin)

        echo
        echo "macOS detected."

        echo
        echo "WARNING:"
        echo "The documented historical ASPECT environment was"
        echo "built on the NMT Linux/HPC environment."

        echo
        echo "The documented environment used:"
        echo
        echo "  GCC       $REQUIRED_GCC_VERSION"
        echo "  OpenMPI   $REQUIRED_OPENMPI_VERSION"
        echo "  deal.II   $REQUIRED_DEAL_II_VERSION"
        echo "  CMake     $REQUIRED_CMAKE_VERSION"
        echo "  Python    $REQUIRED_PYTHON_VERSION"

        if ! confirm_use "Continue on macOS"; then
            echo
            echo "Installation stopped."
            exit 0
        fi

        ;;

    *)

        error_exit "Unsupported operating system: $OS_NAME"

        ;;

esac

pause_step


# ============================================================
# STEP 2
# Basic commands
# ============================================================

echo
echo "============================================================"
echo "STEP 2: Checking basic commands"
echo "============================================================"

COMMANDS="curl tar find grep head sed"

for CMD in $COMMANDS; do

    if command -v "$CMD" >/dev/null 2>&1; then

        echo
        echo "FOUND: $CMD"
        echo "  $(command -v "$CMD")"

    else

        error_exit "$CMD was not found.

Please install or load $CMD before continuing."

    fi

done

pause_step


# ============================================================
# STEP 3
# Compiler detection
# ============================================================

echo
echo "============================================================"
echo "STEP 3: Detecting compiler"
echo "============================================================"

echo
echo "Searching for GCC and other C/C++ compilers..."

GCC_CANDIDATES=""

# ------------------------------------------------------------
# Check common GCC locations
# ------------------------------------------------------------

for GCC_PATH in \
    "/opt/homebrew/bin/gcc-14" \
    "/opt/homebrew/bin/gcc" \
    "/usr/local/bin/gcc-14" \
    "/usr/local/bin/gcc" \
    "$HOME/software/gcc-14.2.0/bin/gcc" \
    "$HOME/bin/gcc"
do

    if [ -x "$GCC_PATH" ]; then

        case "
$GCC_CANDIDATES
" in
            *"
$GCC_PATH
"*)
                ;;
            *)
                GCC_CANDIDATES="${GCC_CANDIDATES}
${GCC_PATH}"
                ;;
        esac

    fi

done


# ------------------------------------------------------------
# Check gcc currently in PATH
# ------------------------------------------------------------

if command -v gcc >/dev/null 2>&1; then

    GCC_PATH="$(command -v gcc)"

    case "
$GCC_CANDIDATES
" in
        *"
$GCC_PATH
"*)
            ;;
        *)
            GCC_CANDIDATES="${GCC_CANDIDATES}
${GCC_PATH}"
            ;;
    esac

fi


# ------------------------------------------------------------
# Display compiler candidates
# ------------------------------------------------------------

if [ -z "$GCC_CANDIDATES" ]; then

    error_exit "No GCC compiler was found."

fi


echo
echo "Compiler candidates found:"
echo

INDEX=1

OLD_IFS="$IFS"
IFS='
'

for GCC_PATH in $GCC_CANDIDATES; do

    echo "[$INDEX] $GCC_PATH"

    GCC_FIRST_LINE="$("$GCC_PATH" --version 2>&1 | head -1)"

    echo "    $GCC_FIRST_LINE"

    GCC_DUMP_VERSION="$("$GCC_PATH" -dumpversion 2>/dev/null || true)"

    echo "    Reported compiler version: $GCC_DUMP_VERSION"

    INDEX=$((INDEX + 1))

done

IFS="$OLD_IFS"


echo
echo "IMPORTANT:"
echo "macOS /usr/bin/gcc is normally Apple Clang."
echo "It is NOT GCC 14.2.0."

echo
echo "The documented ASPECT build requires GCC $REQUIRED_GCC_VERSION."

while true; do

    echo
    read -r -p "Which compiler should ASPECT use? Enter 1-$((INDEX - 1)): " CHOICE

    case "$CHOICE" in
        ''|*[!0-9]*)
            echo "Please enter a number."
            continue
            ;;
    esac

    if [ "$CHOICE" -ge 1 ] && [ "$CHOICE" -lt "$INDEX" ]; then
        break
    fi

    echo "Invalid selection."

done


# ------------------------------------------------------------
# Select GCC
# ------------------------------------------------------------

INDEX=1

IFS='
'

for GCC_PATH in $GCC_CANDIDATES; do

    if [ "$INDEX" -eq "$CHOICE" ]; then
        SELECTED_GCC="$GCC_PATH"
        break
    fi

    INDEX=$((INDEX + 1))

done

IFS="$OLD_IFS"


export CC="$SELECTED_GCC"


# ------------------------------------------------------------
# Find matching C++ compiler
# ------------------------------------------------------------

SELECTED_GXX=""

GCC_DIR="$(dirname "$SELECTED_GCC")"

for GXX_PATH in \
    "$GCC_DIR/g++-14" \
    "$GCC_DIR/g++" \
    "/opt/homebrew/bin/g++-14" \
    "/opt/homebrew/bin/g++" \
    "/usr/local/bin/g++-14" \
    "/usr/local/bin/g++"
do

    if [ -x "$GXX_PATH" ]; then
        SELECTED_GXX="$GXX_PATH"
        break
    fi

done


if [ -z "$SELECTED_GXX" ]; then

    error_exit "No compatible g++ compiler was found for:

    $SELECTED_GCC"

fi


export CXX="$SELECTED_GXX"


echo
echo "============================================================"
echo "Selected compiler"
echo "============================================================"

echo
echo "C compiler:"
echo "  $CC"

echo
echo "C++ compiler:"
echo "  $CXX"

echo
echo "Compiler:"
"$CC" --version | head -1

echo
echo "C++ compiler:"
"$CXX" --version | head -1


if confirm_use "Use this compiler"; then
    echo "Compiler selection confirmed."
else
    echo "Installation stopped."
    exit 0
fi

pause_step


# ============================================================
# STEP 4
# Detect and select MPI
# ============================================================

echo
echo "============================================================"
echo "STEP 4: Detecting MPI"
echo "============================================================"

echo
echo "Searching for MPI installations..."

MPI_CANDIDATES=""

for MPI_PATH in \
    "/opt/homebrew/bin/mpirun" \
    "/usr/local/bin/mpirun" \
    "$HOME/software/anaconda3/bin/mpirun" \
    "$HOME/anaconda3/bin/mpirun" \
    "/usr/bin/mpirun"
do

    if [ -x "$MPI_PATH" ]; then

        case "
$MPI_CANDIDATES
" in
            *"
$MPI_PATH
"*)
                ;;
            *)
                MPI_CANDIDATES="${MPI_CANDIDATES}
${MPI_PATH}"
                ;;
        esac

    fi

done


# ------------------------------------------------------------
# Current PATH MPI
# ------------------------------------------------------------

if command -v mpirun >/dev/null 2>&1; then

    MPI_PATH="$(command -v mpirun)"

    case "
$MPI_CANDIDATES
" in
        *"
$MPI_PATH
"*)
            ;;
        *)
            MPI_CANDIDATES="${MPI_CANDIDATES}
${MPI_PATH}"
            ;;
    esac

fi


if [ -z "$MPI_CANDIDATES" ]; then

    error_exit "No mpirun executable was found."

fi


echo
echo "MPI candidates found:"
echo

INDEX=1

IFS='
'

for MPI_PATH in $MPI_CANDIDATES; do

    echo "[$INDEX] $MPI_PATH"

    echo
    echo "    Version information:"

    "$MPI_PATH" --version 2>&1 | head -3 | sed 's/^/      /'

    INDEX=$((INDEX + 1))

done

IFS="$OLD_IFS"


while true; do

    echo
    read -r -p "Which MPI should ASPECT use? Enter 1-$((INDEX - 1)): " CHOICE

    case "$CHOICE" in
        ''|*[!0-9]*)
            echo "Please enter a number."
            continue
            ;;
    esac

    if [ "$CHOICE" -ge 1 ] && [ "$CHOICE" -lt "$INDEX" ]; then
        break
    fi

    echo "Invalid selection."

done


INDEX=1

IFS='
'

for MPI_PATH in $MPI_CANDIDATES; do

    if [ "$INDEX" -eq "$CHOICE" ]; then
        SELECTED_MPI="$MPI_PATH"
        break
    fi

    INDEX=$((INDEX + 1))

done

IFS="$OLD_IFS"


MPI_RUN="$SELECTED_MPI"

export MPI_RUN


# ------------------------------------------------------------
# Find mpicc and mpicxx next to selected mpirun
# ------------------------------------------------------------

MPI_BIN_DIR="$(dirname "$MPI_RUN")"

if [ -x "$MPI_BIN_DIR/mpicc" ]; then
    MPI_CC="$MPI_BIN_DIR/mpicc"
else
    MPI_CC=""
fi

if [ -x "$MPI_BIN_DIR/mpicxx" ]; then
    MPI_CXX="$MPI_BIN_DIR/mpicxx"
elif [ -x "$MPI_BIN_DIR/mpic++" ]; then
    MPI_CXX="$MPI_BIN_DIR/mpic++"
else
    MPI_CXX=""
fi


echo
echo "============================================================"
echo "Selected MPI"
echo "============================================================"

echo
echo "mpirun:"
echo "  $MPI_RUN"

if [ -n "$MPI_CC" ]; then
    echo
    echo "mpicc:"
    echo "  $MPI_CC"
fi

if [ -n "$MPI_CXX" ]; then
    echo
    echo "mpicxx:"
    echo "  $MPI_CXX"
fi

echo
echo "Version:"
"$MPI_RUN" --version 2>&1 | head -3

echo
echo "Documented historical environment:"
echo "  OpenMPI $REQUIRED_OPENMPI_VERSION"


if confirm_use "Use this MPI"; then
    echo "MPI selection confirmed."
else
    echo "Installation stopped."
    exit 0
fi

pause_step


# ============================================================
# STEP 5
# Detect and select CMake
# ============================================================

echo
echo "============================================================"
echo "STEP 5: Detecting CMake"
echo "============================================================"

CMAKE_CANDIDATES=""

for CMAKE_PATH in \
    "/opt/homebrew/bin/cmake" \
    "/usr/local/bin/cmake" \
    "$HOME/software/cmake/bin/cmake"
do

    if [ -x "$CMAKE_PATH" ]; then

        case "
$CMAKE_CANDIDATES
" in
            *"
$CMAKE_PATH
"*)
                ;;
            *)
                CMAKE_CANDIDATES="${CMAKE_CANDIDATES}
${CMAKE_PATH}"
                ;;
        esac

    fi

done


if command -v cmake >/dev/null 2>&1; then

    CMAKE_PATH="$(command -v cmake)"

    case "
$CMAKE_CANDIDATES
" in
        *"
$CMAKE_PATH
"*)
            ;;
        *)
            CMAKE_CANDIDATES="${CMAKE_CANDIDATES}
${CMAKE_PATH}"
            ;;
    esac

fi


if [ -z "$CMAKE_CANDIDATES" ]; then

    error_exit "CMake was not found."

fi


echo
echo "CMake candidates found:"
echo

INDEX=1

IFS='
'

for CMAKE_PATH in $CMAKE_CANDIDATES; do

    echo "[$INDEX] $CMAKE_PATH"
    "$CMAKE_PATH" --version | head -1
    INDEX=$((INDEX + 1))

done

IFS="$OLD_IFS"


while true; do

    echo
    read -r -p "Which CMake should ASPECT use? Enter 1-$((INDEX - 1)): " CHOICE

    case "$CHOICE" in
        ''|*[!0-9]*)
            echo "Please enter a number."
            continue
            ;;
    esac

    if [ "$CHOICE" -ge 1 ] && [ "$CHOICE" -lt "$INDEX" ]; then
        break
    fi

    echo "Invalid selection."

done


INDEX=1

IFS='
'

for CMAKE_PATH in $CMAKE_CANDIDATES; do

    if [ "$INDEX" -eq "$CHOICE" ]; then
        SELECTED_CMAKE="$CMAKE_PATH"
        break
    fi

    INDEX=$((INDEX + 1))

done

IFS="$OLD_IFS"


export CMAKE="$SELECTED_CMAKE"


echo
echo "Selected CMake:"
echo "  $CMAKE"

echo
"$CMAKE" --version | head -1

echo
echo "Documented CMake:"
echo "  $REQUIRED_CMAKE_VERSION"


if confirm_use "Use this CMake"; then
    echo "CMake selection confirmed."
else
    echo "Installation stopped."
    exit 0
fi

pause_step

# ============================================================
# STEP 6
# Detect and prepare Python
# ============================================================

echo
echo "============================================================"
echo "STEP 6: Detecting Python"
echo "============================================================"

echo
echo "Required documented Python:"
echo "  $REQUIRED_PYTHON_VERSION"

echo
echo "Python must have NumPy installed."
echo


# ============================================================
# ASPECT virtual environment
# ============================================================

ASPECT_VENV="$SCRIPT_DIR/.venv"

ASPECT_VENV_PYTHON="$ASPECT_VENV/bin/python"


echo "Checking ASPECT Python virtual environment:"
echo
echo "  $ASPECT_VENV"


# ============================================================
# Check existing .venv
# ============================================================

if [ -x "$ASPECT_VENV_PYTHON" ]; then

    echo
    echo "Existing ASPECT Python environment found."

else

    echo
    echo "No ASPECT Python environment found."

    echo
    echo "Searching for Python 3.12.13..."


    BASE_PYTHON=""

    # --------------------------------------------------------
    # Look for the exact Python 3.12.13 installation
    # --------------------------------------------------------

    for PYTHON_PATH in \
        "$HOME/.local/share/uv/python/cpython-3.12.13-macos-aarch64-none/bin/python3.12" \
        "$HOME/software/anaconda3/bin/python3" \
        "$HOME/anaconda3/bin/python3" \
        "/opt/homebrew/bin/python3" \
        "/usr/local/bin/python3"
    do

        if [ -x "$PYTHON_PATH" ]; then

            VERSION="$("$PYTHON_PATH" --version 2>&1)"

            if echo "$VERSION" | grep -q "Python 3.12.13"; then

                BASE_PYTHON="$PYTHON_PATH"

                echo
                echo "Found required Python:"
                echo "  $BASE_PYTHON"

                echo
                echo "Version:"
                echo "  $VERSION"

                break

            fi

        fi

    done


    if [ -z "$BASE_PYTHON" ]; then

        error_exit "Python $REQUIRED_PYTHON_VERSION was not found.

The installer searched for the documented Python version."

    fi


    # ========================================================
    # Create virtual environment
    # ========================================================

    echo
    echo "The installer will create:"
    echo
    echo "  $ASPECT_VENV"

    echo
    echo "This does NOT modify the uv-managed base Python."

    if confirm_use "Create the ASPECT Python virtual environment"; then

        "$BASE_PYTHON" -m venv "$ASPECT_VENV"

        echo
        echo "Virtual environment created."

    else

        echo
        echo "Installation stopped."

        exit 0

    fi

fi


# ============================================================
# Verify virtual environment
# ============================================================

if [ ! -x "$ASPECT_VENV_PYTHON" ]; then

    error_exit "The ASPECT Python virtual environment was not created:

    $ASPECT_VENV_PYTHON"

fi


PYTHON="$ASPECT_VENV_PYTHON"

export PYTHON


# ============================================================
# Check Python version
# ============================================================

PYTHON_VERSION="$("$PYTHON" --version 2>&1)"


echo
echo "============================================================"
echo "ASPECT Python environment"
echo "============================================================"

echo
echo "Python:"
echo "  $PYTHON"

echo
echo "Version:"
echo "  $PYTHON_VERSION"


if echo "$PYTHON_VERSION" | grep -q "Python 3.12.13"; then

    echo
    echo "Python version: MATCH"

else

    error_exit "The ASPECT virtual environment is not using
Python $REQUIRED_PYTHON_VERSION."

fi


# ============================================================
# Check NumPy
# ============================================================

echo
echo "Checking NumPy..."


if "$PYTHON" -c "import numpy" >/dev/null 2>&1; then

    NUMPY_VERSION="$("$PYTHON" -c \
        "import numpy; print(numpy.__version__)" 2>/dev/null)"

    echo
    echo "NumPy:"
    echo "  FOUND"

    echo
    echo "NumPy version:"
    echo "  $NUMPY_VERSION"


else

    echo
    echo "NumPy:"
    echo "  NOT FOUND"


    echo
    echo "NumPy must be installed into:"
    echo
    echo "  $PYTHON"


    if confirm_use "Install NumPy into this Python environment"; then

        "$PYTHON" -m pip install numpy

    else

        error_exit "NumPy is required for ASPECT_WITH_PYTHON=ON."

    fi


    # --------------------------------------------------------
    # Verify NumPy after installation
    # --------------------------------------------------------

    if "$PYTHON" -c "import numpy" >/dev/null 2>&1; then

        NUMPY_VERSION="$("$PYTHON" -c \
            "import numpy; print(numpy.__version__)")"

        echo
        echo "NumPy installation successful."

        echo
        echo "NumPy version:"
        echo "  $NUMPY_VERSION"

    else

        error_exit "NumPy installation failed."

    fi

fi


# ============================================================
# Final Python confirmation
# ============================================================

echo
echo "============================================================"
echo "Selected Python environment"
echo "============================================================"

echo
echo "Python:"
echo "  $PYTHON"

echo
echo "Version:"
echo "  $PYTHON_VERSION"

echo
echo "NumPy:"
echo "  $NUMPY_VERSION"

echo
echo "ASPECT Python support:"
echo "  ON"

echo

if confirm_use "Use this Python environment for ASPECT"; then

    echo
    echo "Python environment confirmed."

else

    echo
    echo "Installation stopped."

    exit 0

fi


pause_step

# ============================================================
# STEP 7
# Detect and select deal.II
# ============================================================

echo
echo "============================================================"
echo "STEP 7: Detecting deal.II"
echo "============================================================"

echo
echo "Checking known deal.II installation locations..."
echo


DEAL_II_CANDIDATES=""


# ------------------------------------------------------------
# Candidate 1
# ------------------------------------------------------------

DEAL_II_PATH="$HOME/dealii-candi/deal.II-v9.7.0"

if [ -f "$DEAL_II_PATH/lib/cmake/deal.II/deal.IIConfig.cmake" ]; then

    DEAL_II_CANDIDATES="${DEAL_II_CANDIDATES}
$DEAL_II_PATH"

fi


# ------------------------------------------------------------
# Candidate 2
# ------------------------------------------------------------

DEAL_II_PATH="$HOME/software/dealii/dealii-9.7.1/install/deal.II-v9.7.0"

if [ -f "$DEAL_II_PATH/lib/cmake/deal.II/deal.IIConfig.cmake" ]; then

    DEAL_II_CANDIDATES="${DEAL_II_CANDIDATES}
$DEAL_II_PATH"

fi


# ------------------------------------------------------------
# Also check existing DEAL_II_DIR
# ------------------------------------------------------------

if [ -n "${DEAL_II_DIR:-}" ] &&
   [ -f "$DEAL_II_DIR/lib/cmake/deal.II/deal.IIConfig.cmake" ]; then

    case "
$DEAL_II_CANDIDATES
" in
        *"
$DEAL_II_DIR
"*)
            ;;
        *)
            DEAL_II_CANDIDATES="${DEAL_II_CANDIDATES}
$DEAL_II_DIR"
            ;;
    esac

fi


# ------------------------------------------------------------
# Check whether anything was found
# ------------------------------------------------------------

if [ -z "$DEAL_II_CANDIDATES" ]; then

    error_exit "No working deal.II 9.7.0 installation was found.

The installer checked:

    $HOME/dealii-candi/deal.II-v9.7.0

    $HOME/software/dealii/dealii-9.7.1/install/deal.II-v9.7.0

Neither contains:

    lib/cmake/deal.II/deal.IIConfig.cmake"

fi


# ============================================================
# Display candidates
# ============================================================

echo
echo "============================================================"
echo "deal.II installations found"
echo "============================================================"
echo

INDEX=1

IFS='
'

for CANDIDATE in $DEAL_II_CANDIDATES; do

    echo "[$INDEX] $CANDIDATE"

    echo
    echo "    Configuration:"
    echo "      $CANDIDATE/lib/cmake/deal.II/deal.IIConfig.cmake"

    if [ -f "$CANDIDATE/include/deal.II/base/config.h" ]; then
        echo
        echo "    Include files:"
        echo "      FOUND"
    else
        echo
        echo "    Include files:"
        echo "      NOT FOUND"
    fi

    echo
    INDEX=$((INDEX + 1))

done

IFS="$OLD_IFS"


# ============================================================
# Select deal.II
# ============================================================

while true; do

    echo
    read -r -p \
        "Which deal.II installation should ASPECT use? Enter 1-$((INDEX - 1)): " \
        CHOICE

    case "$CHOICE" in

        ''|*[!0-9]*)

            echo
            echo "Please enter a number."

            continue

            ;;

    esac


    if [ "$CHOICE" -ge 1 ] &&
       [ "$CHOICE" -lt "$INDEX" ]; then

        break

    fi


    echo
    echo "Invalid selection."

done


# ============================================================
# Get selected installation
# ============================================================

INDEX=1

IFS='
'

for CANDIDATE in $DEAL_II_CANDIDATES; do

    if [ "$INDEX" -eq "$CHOICE" ]; then

        SELECTED_DEAL_II="$CANDIDATE"

        break

    fi

    INDEX=$((INDEX + 1))

done

IFS="$OLD_IFS"


export DEAL_II_DIR="$SELECTED_DEAL_II"


# ============================================================
# Show selected installation
# ============================================================

echo
echo "============================================================"
echo "Selected deal.II"
echo "============================================================"

echo
echo "DEAL_II_DIR:"
echo
echo "  $DEAL_II_DIR"

echo
echo "Configuration:"
echo
echo "  $DEAL_II_DIR/lib/cmake/deal.II/deal.IIConfig.cmake"

echo
echo "Required version:"
echo
echo "  $REQUIRED_DEAL_II_VERSION"


# ============================================================
# Confirm
# ============================================================

echo

if confirm_use "Use this deal.II installation"; then

    echo
    echo "deal.II selection confirmed."

else

    echo
    echo "Installation stopped."

    exit 0

fi


pause_step

# ============================================================
# STEP 8
# Final environment summary
# ============================================================

echo
echo "============================================================"
echo "STEP 8: Final software environment"
echo "============================================================"

echo
echo "This is the environment that will be used to build ASPECT."

echo
echo "------------------------------------------------------------"
echo "Compiler"
echo "------------------------------------------------------------"
echo "C compiler:"
echo "  $CC"
"$CC" --version | head -1

echo
echo "C++ compiler:"
echo "  $CXX"
"$CXX" --version | head -1


echo
echo "------------------------------------------------------------"
echo "MPI"
echo "------------------------------------------------------------"
echo "mpirun:"
echo "  $MPI_RUN"
"$MPI_RUN" --version 2>&1 | head -3

if [ -n "$MPI_CC" ]; then
    echo
    echo "mpicc:"
    echo "  $MPI_CC"
fi

if [ -n "$MPI_CXX" ]; then
    echo
    echo "mpicxx:"
    echo "  $MPI_CXX"
fi


echo
echo "------------------------------------------------------------"
echo "CMake"
echo "------------------------------------------------------------"
echo "  $CMAKE"
"$CMAKE" --version | head -1


echo
echo "------------------------------------------------------------"
echo "Python"
echo "------------------------------------------------------------"
echo "  $PYTHON"
"$PYTHON" --version 2>&1


echo
echo "------------------------------------------------------------"
echo "deal.II"
echo "------------------------------------------------------------"
echo "  $DEAL_II_DIR"


echo
echo "------------------------------------------------------------"
echo "Required historical versions"
echo "------------------------------------------------------------"
echo
echo "GCC:       $REQUIRED_GCC_VERSION"
echo "OpenMPI:   $REQUIRED_OPENMPI_VERSION"
echo "deal.II:   $REQUIRED_DEAL_II_VERSION"
echo "CMake:     $REQUIRED_CMAKE_VERSION"
echo "Python:    $REQUIRED_PYTHON_VERSION"


echo
echo "============================================================"

pause_step


# ============================================================
# STEP 9
# Installation directory
# ============================================================

echo
echo "============================================================"
echo "STEP 9: Installation directory"
echo "============================================================"

echo
echo "Script directory:"
echo "  $SCRIPT_DIR"

echo
echo "ASPECT source directory:"
echo "  $ASPECT_DIR"

echo
echo "ASPECT build directory:"
echo "  $BUILD_DIR"

echo
echo "ASPECT archive:"
echo "  $ARCHIVE"


if [ -d "$ASPECT_DIR" ]; then

    echo
    echo "WARNING:"
    echo "The ASPECT source directory already exists:"
    echo
    echo "  $ASPECT_DIR"

    if confirm_use "Use the existing ASPECT source"; then
        echo
        echo "Using existing source."
    else
        echo
        echo "Installation stopped."
        exit 0
    fi

else

    echo
    echo "The ASPECT source directory does not exist."
    echo "It will be created during extraction."

fi

pause_step


# ============================================================
# STEP 10
# Download exact ASPECT commit
# ============================================================

echo
echo "============================================================"
echo "STEP 10: Download exact ASPECT source"
echo "============================================================"

echo
echo "ASPECT version:"
echo "  $ASPECT_VERSION"

echo
echo "Exact commit:"
echo "  $ASPECT_COMMIT"

echo
echo "Archive:"
echo "  $ARCHIVE"

echo
echo "Source URL:"
echo "  https://github.com/landlab-aspect/aspect/archive/$ASPECT_COMMIT.tar.gz"

pause_step


mkdir -p "$SOFTWARE_DIR"


if [ ! -f "$ARCHIVE" ]; then

    echo
    echo "Downloading exact ASPECT commit..."

    curl -L -o "$ARCHIVE" \
        "https://github.com/landlab-aspect/aspect/archive/$ASPECT_COMMIT.tar.gz"

else

    echo
    echo "Archive already exists:"
    echo "  $ARCHIVE"

    if confirm_use "Use the existing archive"; then
        echo
        echo "Using existing archive."
    else
        echo
        echo "Installation stopped."
        exit 0
    fi

fi


echo
echo "Download completed."

pause_step


# ============================================================
# STEP 11
# Extract source
# ============================================================

echo
echo "============================================================"
echo "STEP 11: Extract ASPECT source"
echo "============================================================"

echo
echo "Archive:"
echo "  $ARCHIVE"

echo
echo "Destination:"
echo "  $SOFTWARE_DIR"

pause_step


if [ ! -d "$ASPECT_DIR" ]; then

    tar -xzf "$ARCHIVE" -C "$SOFTWARE_DIR"

    EXTRACTED_DIR="$SOFTWARE_DIR/aspect-$ASPECT_COMMIT"

    if [ -d "$EXTRACTED_DIR" ]; then

        mv "$EXTRACTED_DIR" "$ASPECT_DIR"

    else

        error_exit "The expected extracted directory was not found:

    $EXTRACTED_DIR"

    fi

else

    echo
    echo "Source directory already exists."
    echo "Skipping extraction."

fi


echo
echo "Source extraction completed."

pause_step


# ============================================================
# STEP 12
# Verify ASPECT source
# ============================================================

echo
echo "============================================================"
echo "STEP 12: Verify ASPECT source"
echo "============================================================"

cd "$ASPECT_DIR"


if [ ! -f "VERSION" ]; then

    error_exit "VERSION file was not found."

fi


FOUND_VERSION="$(tr -d '[:space:]' < VERSION)"


echo
echo "Expected ASPECT version:"
echo "  $ASPECT_VERSION"

echo
echo "Found ASPECT version:"
echo "  $FOUND_VERSION"


if [ "$FOUND_VERSION" != "$ASPECT_VERSION" ]; then

    error_exit "ASPECT version does not match."

fi


echo
echo "Checking for Landlab checkpointing implementation..."


if grep -q "resume_checkpoint" \
    source/mesh_deformation/landlab.cc 2>/dev/null; then

    echo
    echo "FOUND:"
    echo "  resume_checkpoint"

else

    error_exit "The expected Landlab checkpointing implementation
was not found in:

    source/mesh_deformation/landlab.cc"

fi


echo
echo "ASPECT source verification successful."

pause_step


# ============================================================
# STEP 13
# Create build directory
# ============================================================

echo
echo "============================================================"
echo "STEP 13: Create build directory"
echo "============================================================"

echo
echo "Build directory:"
echo "  $BUILD_DIR"

pause_step


mkdir -p "$BUILD_DIR"

cd "$BUILD_DIR"


# ============================================================
# STEP 14
# Configure ASPECT
# ============================================================

echo
echo "============================================================"
echo "STEP 14: Configure ASPECT with CMake"
echo "============================================================"

echo
echo "CMake:"
echo "  $CMAKE"

echo
echo "C compiler:"
echo "  $CC"

echo
echo "C++ compiler:"
echo "  $CXX"

echo
echo "MPI:"
echo "  $MPI_RUN"

echo
echo "deal.II:"
echo "  $DEAL_II_DIR"

echo
echo "Python:"
echo "  $PYTHON"

echo
echo "ASPECT Python support:"
echo "  ON"

echo
echo "Source:"
echo "  $ASPECT_DIR"

echo
echo "Build:"
echo "  $BUILD_DIR"

pause_step


# ------------------------------------------------------------
# Configure
# ------------------------------------------------------------

"$CMAKE" \
    -DCMAKE_C_COMPILER="$CC" \
    -DCMAKE_CXX_COMPILER="$CXX" \
    -DDEAL_II_DIR="$DEAL_II_DIR" \
    -DASPECT_WITH_PYTHON=ON \
    -DPython3_EXECUTABLE="$PYTHON" \
    "$ASPECT_DIR"


echo
echo "CMake configuration completed."

pause_step


# ============================================================
# STEP 15
# Build ASPECT
# ============================================================

echo
echo "============================================================"
echo "STEP 15: Build ASPECT"
echo "============================================================"

echo
echo "Build command:"
echo
echo "  $CMAKE --build . --parallel"

echo
echo "The ASPECT build may take a significant amount of time."

pause_step


"$CMAKE" --build . --parallel


echo
echo "ASPECT build completed."

pause_step


# ============================================================
# STEP 16
# Verify executable
# ============================================================

echo
echo "============================================================"
echo "STEP 16: Verify ASPECT executable"
echo "============================================================"


if [ -x "$ASPECT_EXECUTABLE" ]; then

    echo
    echo "ASPECT executable FOUND:"
    echo
    echo "  $ASPECT_EXECUTABLE"

else

    error_exit "The ASPECT release executable was not created.

Expected:

    $ASPECT_EXECUTABLE"

fi


echo
echo "Running ASPECT version check..."

"$ASPECT_EXECUTABLE" --version


# ============================================================
# STEP 17
# Final installation record
# ============================================================

echo
echo "============================================================"
echo "STEP 17: Installation complete"
echo "============================================================"

echo
echo "ASPECT version:"
echo "  $ASPECT_VERSION"

echo
echo "Exact source commit:"
echo "  $ASPECT_COMMIT"

echo
echo "Source directory:"
echo "  $ASPECT_DIR"

echo
echo "Build directory:"
echo "  $BUILD_DIR"

echo
echo "Executable:"
echo "  $ASPECT_EXECUTABLE"

echo
echo "Compiler:"
echo "  $CC"

echo
echo "C++ compiler:"
echo "  $CXX"

echo
echo "MPI:"
echo "  $MPI_RUN"

echo
echo "CMake:"
echo "  $CMAKE"

echo
echo "Python:"
echo "  $PYTHON"

echo
echo "deal.II:"
echo "  $DEAL_II_DIR"

echo
echo "============================================================"
echo "Historical ASPECT installation finished successfully."
echo "============================================================"
```
