#!/usr/bin/env python3

# ============================================================
# FILE: run_class_artifect_detection.py
# ============================================================

import os

from class_artifact_detection import (
    ArtifactDetection
)

# ============================================================
# CHANGE ONLY THIS
# ============================================================

# CASE_NAME = (
    # "global_refin-3_Diffusion_5e4_m2-YEAR_substep_10_xy-repition_5_x-900_y-1900_z-1000_no_Advection_no_Stokes"
# )
CASE_NAME = (
    # "global_refin-2_Diffusion_5e4_m2-YEAR_substep_10_xy-repition_5_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "global_refin-0_x_9_y_19-repition_Diffusion_5e4_m2_per_Year_substep_10_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "global_refin-2_Diffusion_5e4_m2-YEAR_substep_10_xy-repition_5_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "global_refin-0_x_27_y_57-repition_Diffusion_0_substep_10_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "global_refin-3_Diffusion_5e4_m2-YEAR_substep_10_xy-repition_5_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "Rank_0_global_refin-2_x_4_y_4-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_substep_10_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    "global_refin-0_x_2_y_2-repition_Diffusion_5e4_m2_per_Year_Set_Year-false_substep_10_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    # "global_refin-0_x_18_y_38-repition_Diffusion_0_substep_10_x-900_y-1900_z-1000_no_Advection_no_Stokes"
    )

# ============================================================
# OUTPUTS DIRECTORY
# ============================================================

OUTPUTS_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# ============================================================
# RUN
# ============================================================

print("\n================================================")
print("RUNNING ARTIFACT DETECTION")
print("================================================")

detector = ArtifactDetection(
    base_output_dir=OUTPUTS_DIR,
    case_name=CASE_NAME
)

detector.run_analysis()

print("\n================================================")
print("ARTIFACT DETECTION COMPLETED")
print("================================================")