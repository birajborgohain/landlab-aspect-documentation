"""
ASPECT–Landlab Experiment Runner
================================

This script automates the generation and execution of multiple ASPECT simulations
using parameterized templates and a YAML configuration file.

Key Features:
-------------
1. Reads experiment definitions from a YAML config
2. Renders `.prm` (ASPECT input) and `.py` (Landlab coupling) templates
3. Creates isolated run directories
4. Executes ASPECT using MPI
5. Logs output for each run

"""

import os          # For file system operations
import yaml        # For reading YAML configuration files
import subprocess  # For running external commands (ASPECT via MPI)
import re          # For placeholder substitution using regex


# ===============================
# PATH SETUP
# ===============================

# Absolute path of the current script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to YAML configuration file defining experiments
CONFIG_PATH = os.path.join(BASE_DIR, "config", "experiments.yaml")

# Template files (contain placeholders like {parameter})
TEMPLATE_PRM_PATH = os.path.join(BASE_DIR, "templates", "template.prm")
TEMPLATE_PY_PATH  = os.path.join(BASE_DIR, "templates", "import-template.py")

# Base directory where all simulation outputs will be stored
OUTPUT_BASE = os.path.join(BASE_DIR, "outputs")

# Path to ASPECT Python scripts (needed for coupling / plugins)
ASPECT_PYTHON_SCRIPTS = "/Users/biraj/software/landlab_ASPECT_test_2/aspect/contrib/python/scripts"


# ===============================
# CONFIG LOADER
# ===============================
def load_config(path):
    """
    Load YAML configuration file.

    Parameters
    ----------
    path : str
        Path to YAML file

    Returns
    -------
    dict
        Parsed YAML content

    Raises
    ------
    FileNotFoundError
        If config file does not exist
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path) as f:
        return yaml.safe_load(f)


# ===============================
# STRING SANITIZER (UTILITY)
# ===============================
def sanitize(value):
    """
    Convert a value into a filesystem-safe string.

    Replaces spaces and slashes to avoid invalid paths.

    Example:
        "no Advection / test" -> "no_Advection___test"
    """
    return str(value).replace(" ", "_").replace("/", "_")


# ===============================
# TEMPLATE RENDERER
# ===============================
def safe_render(template_text, context):
    """
    Replace placeholders in template with values from context.

    Placeholders follow this format:
        {parameter_name}

    If a key is missing, it leaves the placeholder unchanged.

    Parameters
    ----------
    template_text : str
        Raw template content

    context : dict
        Dictionary of parameters

    Returns
    -------
    str
        Rendered text
    """

    def replace(match):
        key = match.group(1)  # Extract variable name inside {}
        return str(context.get(key, match.group(0)))  # Replace or keep original

    # Regex finds all {word} patterns
    return re.sub(r"\{(\w+)\}", replace, template_text)


# ===============================
# MAIN EXECUTION FUNCTION
# ===============================
def run_all():
    """
    Main workflow driver.

    Steps:
    ------
    1. Load configuration
    2. Read templates
    3. Loop over each run
    4. Merge parameters
    5. Generate files
    6. Execute ASPECT
    7. Save logs
    """

    print(f"\nBase directory: {BASE_DIR}")

    # Load experiment configuration
    config = load_config(CONFIG_PATH)

    # Read template files into memory
    with open(TEMPLATE_PRM_PATH) as f:
        prm_template = f.read()

    with open(TEMPLATE_PY_PATH) as f:
        py_template = f.read()

    # Extract ASPECT execution settings
    mpi = config["aspect"]["mpi_run"]       # e.g., mpirun or mpiexec
    nproc = str(config["aspect"]["nproc"])  # number of processors
    aspect_exec = config["aspect"]["executable"]  # ASPECT binary path

    # Extract run definitions and constants
    runs = config.get("runs", [])
    constants = config.get("constants", {}) or {}

    if not runs:
        raise ValueError("No 'runs' defined in YAML")

    # Ensure base output directory exists
    os.makedirs(OUTPUT_BASE, exist_ok=True)

    # ===============================
    # LOOP OVER EACH RUN
    # ===============================
    for run in runs:

        # Unique identifier for each simulation
        run_id = run.get("run_id")
        if not run_id:
            raise ValueError("Each run must have a 'run_id'")

        # Create output directory for this run
        output_dir = os.path.join(OUTPUT_BASE, run_id)
        os.makedirs(output_dir, exist_ok=True)

        # ===============================
        # MERGE PARAMETERS
        # ===============================
        # Priority:
        # constants < run-specific values
        context = {}
        context.update(constants)
        context.update(run)

        # Render templates with parameters
        prm_text = safe_render(prm_template, context)
        py_text  = safe_render(py_template, context)

        # Output file paths
        prm_path = os.path.join(output_dir, "case.prm")
        py_path  = os.path.join(output_dir, "import.py")

        # Write generated files
        with open(prm_path, "w") as f:
            f.write(prm_text)

        with open(py_path, "w") as f:
            f.write(py_text)

        print(f"\nRunning: {run_id}")
        print(f"Output directory: {output_dir}")

        # Log file for capturing stdout/stderr
        log_path = os.path.join(output_dir, "log.txt")

        # ===============================
        # ENVIRONMENT SETUP
        # ===============================
        # Ensure ASPECT can find required Python modules
        env = os.environ.copy()
        env["PYTHONPATH"] = (
            ASPECT_PYTHON_SCRIPTS
            + os.pathsep
            + env.get("PYTHONPATH", "")
        )

        # ===============================
        # RUN ASPECT SIMULATION
        # ===============================
        with open(log_path, "w") as log_file:
            try:
                subprocess.run(
                    [
                        mpi,
                        "-np", nproc,
                        aspect_exec,
                        "case.prm"
                    ],
                    cwd=output_dir,   # Run inside the run directory
                    stdout=log_file, # Save stdout to log
                    stderr=log_file, # Save errors to same log
                    check=True,      # Raise error if command fails
                    env=env          # Custom environment
                )

           
            except subprocess.CalledProcessError as e:

                print("\n================================================")
                print(f"FAILED: {run_id}")
                print("================================================")

                print(f"Return code: {e.returncode}")

                print(f"\nCheck log:\n{log_path}\n")

                continue


        

        print(f"Finished: {run_id}")


# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    run_all()