
"""
====================================================================
ASPECT-Landlab Substep Analysis Framework
====================================================================

Author:
    Biraj Borgohain

Purpose
-------
Analyze numerical effects of varying n_substeps in
ASPECT-Landlab coupled simulations.

This script studies:

    - Numerical stabilization
    - Diffusion smoothing
    - Operator splitting behavior
    - Elevation evolution
    - Deposition/Erosion evolution
    - Diffusion change
    - Uplift change
    - Convergence behavior
    - Loop scaling effects

Expected Directory Structure
--------------------------------------------------------------------

test_template_ADV_GEO_Project_placeholder/
│
├── outputs/
│   ├── n_substeps-1/
│   ├── n_substeps-2/
│   ├── n_substeps-3/
│   └── ...
│
└── analysis_substeps_figures/

Usage
--------------------------------------------------------------------

python analyze_substeps.py

====================================================================
"""

import os
import re
import glob

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


class TraceAnalyzer:

    """
    ================================================================
    MAIN ANALYZER
    ================================================================
    """

    def __init__(self,
                 outputs_dir,
                 save_dir):

        self.outputs_dir = outputs_dir

        self.save_dir = save_dir

        os.makedirs(
            self.save_dir,
            exist_ok=True
        )

        self.all_data = {}

    # ================================================================
    # FIND TRACE FILES
    # ================================================================
    def find_trace_files(self):

        pattern = os.path.join(
            self.outputs_dir,
            "**",
            "execution_trace_rank_0.txt"
        )

        files = glob.glob(
            pattern,
            recursive=True
        )

        print("\n================================================")
        print("FOUND TRACE FILES")
        print("================================================")

        if len(files) == 0:

            print("\nNo trace files found.\n")

        else:

            for f in sorted(files):
                print(f)

        return sorted(files)

    # ================================================================
    # EXTRACT N_SUBSTEPS
    # ================================================================
    def extract_n_substeps(self, filepath):

        patterns = [

            r"n_substeps[-_](\d+)",

            r"subset[-_](\d+)",

            r"nsubsteps[-_](\d+)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                filepath
            )

            if match:

                return int(match.group(1))

        return None

    # ================================================================
    # ADD RECORD
    # ================================================================
    def add_record(self,
                   records,
                   n_substeps_case,
                   timestep,
                   substep,
                   process,
                   value,
                   current_n_substeps,
                   current_sub_dt):

        records.append({

            "case_n_substeps":
            n_substeps_case,

            "timestep":
            timestep,

            "substep":
            substep,

            "process":
            process,

            "value":
            value,

            "n_substeps":
            current_n_substeps,

            "sub_dt":
            current_sub_dt
        })

    # ================================================================
    # PARSE TRACE FILE
    # ================================================================
    def parse_trace_file(self, filepath):

        print("\n================================================")
        print(f"PARSING:\n{filepath}")
        print("================================================")

        n_substeps_case = self.extract_n_substeps(
            filepath
        )

        if n_substeps_case is None:

            print("Could not extract n_substeps.")
            return

        with open(filepath, "r") as f:

            lines = f.readlines()

        records = []

        timestep = None
        substep = None

        current_n_substeps = None
        current_sub_dt = None

        for line in lines:

            # ====================================================
            # TIMESTEP
            # ====================================================
            match = re.search(
                r"Timestep incremented to (\d+)",
                line
            )

            if match:
                timestep = int(match.group(1))

            # ====================================================
            # N_SUBSTEPS
            # ====================================================
            match = re.search(
                r"n_substeps = (\d+)",
                line
            )

            if match:
                current_n_substeps = int(
                    match.group(1)
                )

            # ====================================================
            # SUB_DT
            # ====================================================
            match = re.search(
                r"sub_dt = ([\d.eE+-]+)",
                line
            )

            if match:
                current_sub_dt = float(
                    match.group(1)
                )

            # ====================================================
            # SUBSTEP
            # ====================================================
            match = re.search(
                r"Starting substep (\d+)",
                line
            )

            if match:
                substep = int(match.group(1))

            # ====================================================
            # PROCESS PARSERS
            # ====================================================

            parsers = [

                (
                    r"Finished diffusion \| "
                    r"max elevation = ([\d.eE+-]+)",
                    "diffusion"
                ),

                (
                    r"Finished uplift \| "
                    r"max elevation = ([\d.eE+-]+)",
                    "uplift"
                ),

                (
                    r"Finished erosion/deposition \| "
                    r"max deposition_erosion = ([\d.eE+-]+)",
                    "deposition"
                ),

                (
                    r"diffusion_change = ([\d.eE+-]+)",
                    "diffusion_change"
                ),

                (
                    r"uplift_change = ([\d.eE+-]+)",
                    "uplift_change"
                )
            ]

            for pattern, process_name in parsers:

                match = re.search(
                    pattern,
                    line
                )

                if match:

                    self.add_record(

                        records,

                        n_substeps_case,

                        timestep,

                        substep,

                        process_name,

                        float(match.group(1)),

                        current_n_substeps,

                        current_sub_dt
                    )

        df = pd.DataFrame(records)

        # ========================================================
        # MERGE DATA
        # ========================================================
        if n_substeps_case not in self.all_data:

            self.all_data[n_substeps_case] = df

        else:

            self.all_data[n_substeps_case] = pd.concat(

                [
                    self.all_data[n_substeps_case],
                    df
                ],

                ignore_index=True
            )

        print(df.head())

    # ================================================================
    # LOAD ALL FILES
    # ================================================================
    def load_all_files(self):

        files = self.find_trace_files()

        if len(files) == 0:

            raise RuntimeError(
                "No trace files found."
            )

        for f in files:

            self.parse_trace_file(f)

    # ================================================================
    # SORTED LEGEND
    # ================================================================
    def apply_sorted_legend(self):

        handles, labels = plt.gca().get_legend_handles_labels()

        pairs = sorted(

            zip(labels, handles),

            key=lambda x: int(
                x[0].split("=")[1]
            )
        )

        labels, handles = zip(*pairs)

        plt.legend(
            handles,
            labels,
            title="n_substeps"
        )

    # ================================================================
    # GENERIC PLOTTER
    # ================================================================
    def generic_plot(self,
                     process_name,
                     x_column,
                     title,
                     ylabel,
                     filename):

        plt.figure(figsize=(12, 7))

        for n_substeps in sorted(
            self.all_data.keys()
        ):

            df = self.all_data[n_substeps]

            subset = df[
                df["process"] == process_name
            ]

            grouped = subset.groupby(
                x_column
            )["value"].max()

            plt.plot(

                grouped.index,

                grouped.values,

                marker='o',

                linewidth=2.5,

                label=f"n_substeps={n_substeps}"
            )

        plt.xlabel(
            x_column.capitalize(),
            fontsize=14
        )

        plt.ylabel(
            ylabel,
            fontsize=14
        )

        plt.title(
            title,
            fontsize=16
        )

        plt.grid(True)

        self.apply_sorted_legend()

        save_path = os.path.join(
            self.save_dir,
            filename
        )

        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(f"\nSaved:\n{save_path}")

    # ================================================================
    # PROCESS VS TIMESTEP
    # ================================================================
    def plot_process_vs_timestep(self):

        plots = [

            (
                "uplift",
                "Maximum Elevation vs Timestep",
                "Maximum Elevation",
                "uplift_vs_timestep.png"
            ),

            (
                "diffusion",
                "Maximum Diffusion vs Timestep",
                "Maximum Diffusion",
                "diffusion_vs_timestep.png"
            ),

            (
                "deposition",
                "Maximum Deposition vs Timestep",
                "Maximum Deposition/Erosion",
                "deposition_vs_timestep.png"
            ),

            (
                "diffusion_change",
                "Diffusion Change vs Timestep",
                "Maximum Diffusion Change",
                "diffusion_change_vs_timestep.png"
            ),

            (
                "uplift_change",
                "Uplift Change vs Timestep",
                "Maximum Uplift Change",
                "uplift_change_vs_timestep.png"
            )
        ]

        for process, title, ylabel, filename in plots:

            self.generic_plot(

                process_name=process,

                x_column="timestep",

                title=title,

                ylabel=ylabel,

                filename=filename
            )

    # ================================================================
    # PROCESS VS SUBSTEP
    # ================================================================
    def plot_process_vs_substep(self):

        plots = [

            (
                "uplift",
                "Maximum Elevation vs Substep",
                "Maximum Elevation",
                "max_elevation_vs_substep.png"
            ),

            (
                "deposition",
                "Maximum Deposition vs Substep",
                "Maximum Deposition/Erosion",
                "max_deposition_vs_substep.png"
            )
        ]

        for process, title, ylabel, filename in plots:

            self.generic_plot(

                process_name=process,

                x_column="substep",

                title=title,

                ylabel=ylabel,

                filename=filename
            )

    # ================================================================
    # LOOP SCALING
    # ================================================================
    def plot_loop_scaling(self):

        results = []

        for n_substeps in sorted(
            self.all_data.keys()
        ):

            df = self.all_data[n_substeps]

            timesteps = df[
                "timestep"
            ].nunique()

            total_loops = (
                timesteps * n_substeps
            )

            results.append({

                "n_substeps":
                n_substeps,

                "timesteps":
                timesteps,

                "total_loops":
                total_loops
            })

        loop_df = pd.DataFrame(results)

        plt.figure(figsize=(10, 6))

        plt.plot(

            loop_df["n_substeps"],

            loop_df["total_loops"],

            marker='o',

            linewidth=3
        )

        plt.xlabel(
            "n_substeps",
            fontsize=14
        )

        plt.ylabel(
            "Total Loop Executions",
            fontsize=14
        )

        plt.title(
            "Loop Scaling with n_substeps",
            fontsize=16
        )

        plt.grid(True)

        save_path = os.path.join(

            self.save_dir,

            "loop_scaling_analysis.png"
        )

        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        loop_df.to_csv(

            os.path.join(
                self.save_dir,
                "loop_scaling_analysis.csv"
            ),

            index=False
        )

    # ================================================================
    # CONVERGENCE ANALYSIS
    # ================================================================
    def convergence_analysis(self):

        reference_n = max(
            self.all_data.keys()
        )

        reference_df = self.all_data[
            reference_n
        ]

        reference = reference_df[
            reference_df["process"] == "uplift"
        ]["value"].values

        results = []

        for n_substeps in sorted(
            self.all_data.keys()
        ):

            df = self.all_data[n_substeps]

            target = df[
                df["process"] == "uplift"
            ]["value"].values

            min_len = min(
                len(reference),
                len(target)
            )

            error = np.linalg.norm(

                reference[:min_len]
                -
                target[:min_len]
            )

            results.append({

                "n_substeps":
                n_substeps,

                "L2_error":
                error
            })

        conv_df = pd.DataFrame(results)

        plt.figure(figsize=(10, 6))

        plt.plot(

            conv_df["n_substeps"],

            conv_df["L2_error"],

            marker='o',

            linewidth=3
        )

        plt.xlabel(
            "n_substeps",
            fontsize=14
        )

        plt.ylabel(
            "L2 Error",
            fontsize=14
        )

        plt.title(
            f"Convergence Against "
            f"n_substeps={reference_n}",
            fontsize=16
        )

        plt.grid(True)

        save_path = os.path.join(

            self.save_dir,

            "convergence_analysis.png"
        )

        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        conv_df.to_csv(

            os.path.join(
                self.save_dir,
                "convergence_analysis.csv"
            ),

            index=False
        )

    # ================================================================
    # SUMMARY STATISTICS
    # ================================================================
    def summary_statistics(self):

        summary = []

        for n_substeps in sorted(
            self.all_data.keys()
        ):

            df = self.all_data[n_substeps]

            for process in df["process"].unique():

                subset = df[
                    df["process"] == process
                ]

                summary.append({

                    "n_substeps":
                    n_substeps,

                    "process":
                    process,

                    "max":
                    subset["value"].max(),

                    "mean":
                    subset["value"].mean(),

                    "std":
                    subset["value"].std()
                })

        summary_df = pd.DataFrame(summary)

        save_path = os.path.join(
            self.save_dir,
            "summary_statistics.csv"
        )

        summary_df.to_csv(
            save_path,
            index=False
        )

        print(f"\nSaved:\n{save_path}")

    # ================================================================
    # EXPORT RAW DATA
    # ================================================================
    def export_all_data(self):

        combined = pd.concat(

            list(self.all_data.values()),

            ignore_index=True
        )

        save_path = os.path.join(

            self.save_dir,

            "combined_trace_data.csv"
        )

        combined.to_csv(
            save_path,
            index=False
        )

        print(f"\nSaved:\n{save_path}")


        # ================================================================
    # MAGNITUDE VS TOTAL LOOPS
    # ================================================================
    def plot_magnitude_vs_total_loops(self):

        results = []

        for n_substeps in sorted(self.all_data.keys()):

            df = self.all_data[n_substeps]

            n_timesteps = df["timestep"].nunique()

            total_loops = (
                n_timesteps * n_substeps
            )

            # --------------------------------------------
            # uplift change
            # --------------------------------------------
            uplift_change = df[
                df["process"] == "uplift_change"
            ]["value"]

            max_uplift_change = (
                uplift_change.max()
                if len(uplift_change) > 0
                else np.nan
            )

            # --------------------------------------------
            # diffusion change
            # --------------------------------------------
            diffusion_change = df[
                df["process"] == "diffusion_change"
            ]["value"]

            max_diffusion_change = (
                diffusion_change.max()
                if len(diffusion_change) > 0
                else np.nan
            )

            # --------------------------------------------
            # maximum elevation
            # --------------------------------------------
            uplift = df[
                df["process"] == "uplift"
            ]["value"]

            max_elevation = (
                uplift.max()
                if len(uplift) > 0
                else np.nan
            )

            results.append({

                "n_substeps":
                n_substeps,

                "total_loops":
                total_loops,

                "max_uplift_change":
                max_uplift_change,

                "max_diffusion_change":
                max_diffusion_change,

                "max_elevation":
                max_elevation
            })

        results_df = pd.DataFrame(results)

        # ============================================================
        # PLOT
        # ============================================================

        plt.figure(figsize=(12,7))

        plt.plot(
            results_df["total_loops"],
            results_df["max_uplift_change"],
            marker="o",
            linewidth=3,
            label="Max uplift change"
        )

        plt.plot(
            results_df["total_loops"],
            results_df["max_diffusion_change"],
            marker="s",
            linewidth=3,
            label="Max diffusion change"
        )

        plt.plot(
            results_df["total_loops"],
            results_df["max_elevation"],
            marker="^",
            linewidth=3,
            label="Max elevation"
        )

        plt.xlabel(
            "Total Loop Executions",
            fontsize=14
        )

        plt.ylabel(
            "Magnitude",
            fontsize=14
        )

        plt.title(
            "Magnitude of Terrain Modification vs Total Loops",
            fontsize=16
        )

        plt.grid(True)

        plt.legend()

        save_path = os.path.join(
            self.save_dir,
            "magnitude_vs_total_loops.png"
        )

        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        results_df.to_csv(
            os.path.join(
                self.save_dir,
                "magnitude_vs_total_loops.csv"
            ),
            index=False
        )

        print(f"\nSaved:\n{save_path}")


        # ================================================================
    # CONVERGENCE OF TOPOGRAPHY
    # ================================================================
    def topography_convergence_analysis(self):

        """
        Compare each n_substeps case
        against reference n_substeps = 40.
        """

        reference_n = max(self.all_data.keys())

        reference_df = self.all_data[reference_n]

        reference = reference_df[
            reference_df["process"] == "uplift"
        ]["value"].values

        results = []

        for n_substeps in sorted(self.all_data.keys()):

            target_df = self.all_data[n_substeps]

            target = target_df[
                target_df["process"] == "uplift"
            ]["value"].values

            min_len = min(
                len(reference),
                len(target)
            )

            reference_trim = reference[:min_len]
            target_trim = target[:min_len]

            # L2 norm
            l2_error = np.linalg.norm(
                target_trim - reference_trim
            )

            # RMS error
            rms_error = np.sqrt(
                np.mean(
                    (target_trim - reference_trim)**2
                )
            )

            # Max error
            max_error = np.max(
                np.abs(
                    target_trim - reference_trim
                )
            )

            results.append({

                "n_substeps": n_substeps,

                "L2_error": l2_error,

                "RMS_error": rms_error,

                "Max_error": max_error
            })

        error_df = pd.DataFrame(results)

        print("\nConvergence statistics")
        print(error_df)

        # ------------------------------------------------------------
        # Plot
        # ------------------------------------------------------------

        plt.figure(figsize=(10,6))

        plt.plot(
            error_df["n_substeps"],
            error_df["RMS_error"],
            marker="o",
            linewidth=3,
            label="RMS error"
        )

        plt.plot(
            error_df["n_substeps"],
            error_df["Max_error"],
            marker="s",
            linewidth=3,
            label="Max error"
        )

        plt.xlabel(
            "n_substeps",
            fontsize=14
        )

        plt.ylabel(
            "Error relative to n_substeps=40",
            fontsize=14
        )

        plt.title(
            "Substep Convergence Analysis",
            fontsize=16
        )

        plt.grid(True)

        plt.legend()

        save_path = os.path.join(
            self.save_dir,
            "substep_convergence.png"
        )

        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        error_df.to_csv(

            os.path.join(
                self.save_dir,
                "substep_convergence.csv"
            ),

            index=False
        )

        print(f"\nSaved:\n{save_path}")

    # ================================================================
    # RUN EVERYTHING
    # ================================================================
    def run_all(self):

        self.load_all_files()

        if len(self.all_data) == 0:

            print("\nNo valid data loaded.\n")
            return

        self.plot_process_vs_timestep()

        self.plot_process_vs_substep()

        self.plot_loop_scaling()

        self.plot_magnitude_vs_total_loops()

        self.topography_convergence_analysis()

        self.convergence_analysis()

        self.summary_statistics()

        self.export_all_data()

        print("\n================================================")
        print("ALL ANALYSIS COMPLETE")
        print("================================================")


# ====================================================================
# MAIN
# ====================================================================

if __name__ == "__main__":

    analyzer = TraceAnalyzer(

        # outputs_dir=(
        #     "./test_template_ADV_GEO_Project_placeholder/outputs"
        # ),

        # save_dir=(
        #     "./test_template_ADV_GEO_Project_placeholder/"
        #     "analysis_substeps_figures"
        # )
         outputs_dir=(
            "./diffusion_5e4_s2yr/outputs"
        ),

        save_dir=(
            "./diffusion_5e4_s2yr/"
            "analysis_substeps_figures"
        )
    )

    analyzer.run_all()

