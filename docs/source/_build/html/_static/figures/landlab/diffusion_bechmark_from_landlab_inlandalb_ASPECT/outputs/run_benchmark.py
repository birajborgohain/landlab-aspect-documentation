#!/usr/bin/env python3

import os
import subprocess

from benchmark_class import (
    BenchmarkFramework,
    CrossSectionPlotter,
    InitialTimeStepAnalysis
)

# ============================================================
# CHANGE ONLY THIS
# ============================================================

CASE_NAME = (
    # "Linear_slope_substep_10_diffu-1_xy-repition_0_"
    # "global_refin-0_only_Landlab_x-900_y-1900_"
    # "z-1000_no_Advection_no_Stokes"

    # "Linear_Time_test_no_Advection_no_Stokes"
    # "Diffusion_Zero_substep_10_xy-repition_5_global_refin-0_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "global_refin-3_Diffusion_5e4_m2-YEAR_substep_10_xy-repition_5_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "global_refin-0_x_27_y_57-repition_Diffusion_0_substep_10_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "global_refin-0_x_9_y_19-repition_Diffusion_5e4_m2_per_Year_substep_10_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "global_refin-0_x_2_y_2-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_substep_10_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "ASPECT_defined_uplift_global_velocity_boundary_refin-0_x_9_y_19-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_substep_10_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "global_refin-0_x_9_y_19-repition_substep_1_Diffusion_5e4_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "ASPECT_defined_uplift_subset_10_global_velocity_boundary_refin-0_x_9_y_19-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_x-900_y-1900_z-1000_single_Advection_single_Stokes"
    # "Landlab_defined_uplift_subset_10_global_refin-0_x_9_y_19-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "ASPECT_defined_uplift_subset_3_gravity_9.8_new_global_velocity_boundary_refin-0_x_9_y_19-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_x-900_y-1900_z-1000_single_Advection_single_Stokes"
    # "Landlab_defined_uplift_subset_10_global_refin-0_x_9_y_19-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_x-900_y-1900_z-1000_no_Advection_no_Stokes "
    # "Landlab_defined_uplift_subset_1_global_refin-0_x_9_y_19-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "Landlab_defined_uplift_subset_1_more_ASPECT_nodes_global_refin-0_x_27_y_57-repition_Diffusion_5e4_Set_Year-false_x-900_y-1900_z-1_no_Advection_no_Stokes"
    # "Landlab_defined_uplift_subset_9_trace"
    # "Landlab_defined_uplift_subset_1__landlab_test_diff_endtime_1_trace"
    # "Landlab_defined_uplift_N_SUBSET_2_ASPECT_end-time-3_Reference_end-time-3_standalone_Landlab_end-time-4_trace"
    "Landlab_defined_uplift_N_SUBSET_1.5_ASPECT_end-time-3_Reference_end-time-3_standalone_Landlab_end-time-3_DT-0.5_trace"
)

# ============================================================
# OUTPUTS DIRECTORY
# ============================================================

OUTPUTS_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# ============================================================
# RUN TEST DIFFUSION
# ============================================================

test_script = os.path.join(
    OUTPUTS_DIR,
    "test_diffusion.py"
)

print("\n================================================")
print("RUNNING LANDLAB TEST")
print("================================================")

# subprocess.run(
#     ["python", test_script],
#     check=True
# )

subprocess.run(
    [
        "python",
        test_script,
        CASE_NAME
    ],
    check=True
)

# ============================================================
# CREATE BENCHMARK OBJECT
# ============================================================

benchmark = BenchmarkFramework(
    OUTPUTS_DIR,
    CASE_NAME
)

# ============================================================
# RUN BENCHMARK
# ============================================================

print("\n================================================")
print("RUNNING BENCHMARK")
print("================================================")

benchmark.generate_benchmark()

# ============================================================
# GENERATE CROSS SECTION PLOT
# ============================================================

print("\n================================================")
print("GENERATING CROSS SECTION")
print("================================================")

cross_section = CrossSectionPlotter(
    benchmark
)

cross_section.plot_cross_section()


# ============================================================
# INITIAL TIME STEP ANALYSIS
# ============================================================

print("\n================================================")
print("Initital CROSS SECTION")
print("================================================")

initial_analysis = InitialTimeStepAnalysis(
    benchmark
)

initial_analysis.plot_initial_cross_section()


# ============================================================
# FINISHED
# ============================================================

print("\n================================================")
print("BENCHMARK COMPLETED SUCCESSFULLY")
print("================================================")

