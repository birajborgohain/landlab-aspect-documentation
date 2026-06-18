
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
from matplotlib.ticker import MaxNLocator

plt.gca().xaxis.set_major_locator(
    MaxNLocator(integer=True)
)
from matplotlib.ticker import LinearLocator

plt.gca().yaxis.set_major_locator(
    LinearLocator(3)
)


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
    # DIFFUSION/Uplift Change vs Loop Number
    # ================================================================
    def plot_loopwise_changes(self):

        import re

        trace_files = self.find_trace_files()

        for trace_file in trace_files:

            loops = []
            diffusion_changes = []
            uplift_changes = []

            current_loop = None

            with open(trace_file, "r") as f:

                for line in f:

                    # ----------------------------------------
                    # LOOP NUMBER
                    # ----------------------------------------
                    match = re.search(
                        r"LOOP\s+(\d+)",
                        line
                    )

                    if match:

                        current_loop = int(
                            match.group(1)
                        )

                    # ----------------------------------------
                    # MAX DIFFUSION CHANGE
                    # ----------------------------------------
                    match = re.search(
                        r"max diffusion_change = ([\d.eE+-]+)",
                        line
                    )

                    if match:

                        loops.append(current_loop)

                        diffusion_changes.append(
                            float(match.group(1))
                        )

                    # ----------------------------------------
                    # MAX UPLIFT CHANGE
                    # ----------------------------------------
                    match = re.search(
                        r"max uplift_change = ([\d.eE+-]+)",
                        line
                    )

                    if match:

                        uplift_changes.append(
                            float(match.group(1))
                        )

            # --------------------------------------------
            # Safety
            # --------------------------------------------
            n = min(
                len(loops),
                len(diffusion_changes),
                len(uplift_changes)
            )

            loops = loops[:n]
            diffusion_changes = diffusion_changes[:n]
            uplift_changes = uplift_changes[:n]

            if n == 0:

                print(
                    f"No valid data found in {trace_file}"
                )

                continue

            # --------------------------------------------
            # Plot
            # --------------------------------------------
            plt.figure(figsize=(12,7))

            # plt.plot(
            #     loops,
            #     diffusion_changes,
            #     marker="o",
            #     linewidth=2.5,
            #     label="Max diffusion change"
            # )

            # plt.plot(
            #     loops,
            #     uplift_changes,
            #     marker="s",
            #     linewidth=2.5,
            #     label="Max uplift change"
            # )

            plt.plot(
                loops,
                diffusion_changes,
                marker="o",
                linewidth=2.5,
                label=r"$D_i$ (Diffusion contribution)"
            )

            plt.plot(
                loops,
                uplift_changes,
                marker="s",
                linewidth=2.5,
                label=r"$U_i$ (Uplift contribution)"
            )

            # --------------------------------------------
            # Label diffusion points
            # --------------------------------------------
            # for i, (x, y) in enumerate(
            #     zip(loops, diffusion_changes),
            #     start=1
            # ):

            #     plt.annotate(
            #         f"D{i}",
            #         (x, y),
            #         textcoords="offset points",
            #         xytext=(0, 8),
            #         ha="center",
            #         fontsize=10
            #     )

            for i, (x, y) in enumerate(
                zip(loops, diffusion_changes),
                start=1
            ):

                plt.annotate(
                    f"D{i}",
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, -15),   # below point
                    ha="center",
                    va="top",
                    fontsize=10,
                    fontweight="bold"
                )

            # --------------------------------------------
            # Label uplift points
            # --------------------------------------------
            # for i, (x, y) in enumerate(
            #     zip(loops, uplift_changes),
            #     start=1
            # ):

            #     plt.annotate(
            #         f"U{i}",
            #         (x, y),
            #         textcoords="offset points",
            #         xytext=(0, -12),
            #         ha="center",
            #         fontsize=10
            #     )

            for i, (x, y) in enumerate(
                zip(loops, uplift_changes),
                start=1
            ):

                plt.annotate(
                    f"U{i}",
                    (x, y),
                    textcoords="offset points",
                    xytext=(0, 12),    # above point
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    fontweight="bold"
                )

            plt.xlabel(
                "Coupling Loop Number",
                fontsize=14
            )

            plt.ylabel(
                "Maximum Elevation Change, Δz (meter)",
                fontsize=14
            )

            # folder_name = os.path.basename(
            #     os.path.dirname(trace_file)
            # )

            # plt.title(
            #     f"{n_substeps}\n"
            #     f"Diffusion and Uplift Change vs Loop Number",
            #     fontsize=15
            # )
            n_substeps = self.extract_n_substeps(trace_file)

            plt.title(
                f"n_substeps = {n_substeps}\n"
                f"Results of Tracer Methodology for Isolating Diffusion and Uplift Effects",
                fontsize=15
            )

            plt.grid(True)

            plt.legend(
                fontsize=14,
                title_fontsize=16
            )

            # --------------------------------------------------
            # Equation box
            # --------------------------------------------------
            # plt.text(
            #     0.98,
            #     0.15,
            #     (
            #         r"$Max\ uplift\_change = z_{new\ after\ uplift}"
            #         r" - z_{old\ before\ uplift}$" "\n"
            #         r"$z_{new}=z_{old}+U\,\Delta t_{loop}$" "\n"
            #         r"$Max\ uplift\_change = U\,\Delta t_{loop}$" "\n"
            #         r"$elevation = z$"
            #     ),
            #     transform=plt.gca().transAxes,
            #     fontsize=13,
            #     ha="right",
            #     va="bottom",
            #     bbox=dict(
            #         facecolor="white",
            #         alpha=0.8,
            #         edgecolor="black"
            #     )
            # )

            

            

            # plt.text(
            #     0.50,
            #     0.50,
            #     (
            #         "Code:\n"
            #         "elevation += uplift_rate * sub_dt\n\n"
            #         "where:\n"
            #         "elevation = z\n"
            #         "uplift_rate = U\n"
            #         "sub_dt = Δt_loop"
            #     ),
            #     transform=plt.gca().transAxes,
            #     fontsize=11,
            #     family="monospace",
            #     ha="center",
            #     va="center",
            #     bbox=dict(
            #         facecolor="white",
            #         alpha=0.85,
            #         edgecolor="black"
            #     )
            # )

            # --------------------------------------------------
            # Legend
            # --------------------------------------------------
            plt.legend(
                fontsize=14,
                loc="lower right"
            )

            # plt.text(
            #     0.02,
            #     0.98,
            #     (
            #         r"$uplift\_change = z_{after\ uplift}"
            #         r" - z_{before\ uplift}$" "\n"
            #         r"$z_{new}=z_{old}+U\,\Delta t_{loop}$" "\n"
            #         r"$uplift\_change = U\,\Delta t_{loop}$"
            #     ),
            #     transform=plt.gca().transAxes,
            #     fontsize=12,
            #     verticalalignment="top",
            #     bbox=dict(
            #         facecolor="white",
            #         alpha=0.8,
            #         edgecolor="black"
            #     )
            # )

            # save_path = os.path.join(
            #     os.path.dirname(trace_file),
            #     "diffusion_uplift_vs_loop.png"
            # )
            # folder_name = os.path.basename(
            #     os.path.dirname(trace_file)
            # )

            # save_path = os.path.join(
            #     self.save_dir,
            #     f"loop_vs_max_uplift_diffusion_change_{folder_name}.png"
            # )
            n_substeps = self.extract_n_substeps(trace_file)

            save_path = os.path.join(
                self.save_dir,
                f"loop_vs_max_uplift_diffusion_change_n_substeps_{n_substeps}.png"
            )

            ymin = min(
                min(diffusion_changes),
                min(uplift_changes)
            )

            ymax = max(
                max(diffusion_changes),
                max(uplift_changes)
            )

            padding = 0.15 * (ymax - ymin)

            plt.ylim(
                ymin - padding,
                ymax + padding
            )

            from mpl_toolkits.axes_grid1.inset_locator import inset_axes

            ax = plt.gca()

            axins = inset_axes(
                ax,
                width="35%",
                height="28%",
                loc="lower left",
                borderpad=2
            )

            axins.axis("off")

            axins.text(
                0.5,
                0.78,
                "Diffusion:\nA → LinearDiffuser → B\nΔz = B − A",
                ha="center",
                va="center",
                fontsize=12,          # bigger font
                fontweight="bold",
                color="tab:blue",
                bbox=dict(
                    facecolor="#E8F2FF",   # light blue background
                    edgecolor="tab:blue",
                    boxstyle="round,pad=0.5",
                    alpha=0.95
                )
            )

            axins.text(
                0.5,
                0.25,
                "Uplift:\nB → uplift_rate·Δt → C\nΔz = C − B",
                ha="center",
                va="center",
                fontsize=12,          # bigger font
                fontweight="bold",
                color="tab:orange",
                bbox=dict(
                    facecolor="#FFF1E6",   # light orange background
                    edgecolor="tab:orange",
                    boxstyle="round,pad=0.5",
                    alpha=0.95
                )
            )
            plt.savefig(
                save_path,
                dpi=300,
                bbox_inches="tight"
            )

            plt.close()

            print(
                f"Saved:\n{save_path}"
            )


            # ================================================================
    # MAX DIFFUSION CHANGE VS LOOP NUMBER
    # ALL n_substeps ON ONE FIGURE
    # ================================================================
    def plot_max_diffusion_change_all_cases(self):

        plt.figure(figsize=(12, 7))

        for n_substeps in sorted(self.all_data.keys()):

            df = self.all_data[n_substeps]

            diffusion_df = df[
                df["process"] == "diffusion_change"
            ].copy()

            if diffusion_df.empty:
                continue

            # Loop number = row order
            diffusion_df = diffusion_df.reset_index(drop=True)

            loop_numbers = np.arange(
                1,
                len(diffusion_df) + 1
            )

            plt.plot(
                loop_numbers,
                diffusion_df["value"],
                marker="o",
                linewidth=2.5,
                label=f"n_substeps={n_substeps}"
            )

        plt.xlabel(
            "Loop Number",
            fontsize=14
        )

        max_loop = max(
            len(
                self.all_data[n]["process"][
                    self.all_data[n]["process"] == "diffusion_change"
                ]
            )
            for n in self.all_data.keys()
        )

        plt.xticks(
            np.arange(1, max_loop + 1, 1)
        )

        plt.ylabel(
            "Max Diffusion Change",
            fontsize=14
        )

        # plt.yticks(
        #     [
        #         min(diffusion_changes),
        #         uplift_changes[0] / 2,
        #         uplift_changes[0]
        #     ]
        # )

        ax = plt.gca()

        plt.draw()

        ymin, ymax = ax.get_ylim()

        ticks = [
            ymin,
            (ymin + ymax)/2,
            ymax
        ]

        ax.set_yticks(ticks)

        plt.title(
            "Max Diffusion Change vs Loop Number",
            fontsize=16
        )

        plt.grid(True)

        # --------------------------------------------------
        # Sorted legend
        # --------------------------------------------------
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
            title="n_substeps",
            loc="best"
        )

        save_path = os.path.join(
            self.save_dir,
            "max_diffusion_change_vs_loop_number_all_cases.png"
        )

        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(
            f"Saved:\n{save_path}"
        )

        # ================================================================
    # MAX UPLIFT CHANGE VS LOOP NUMBER
    # ALL n_substeps ON ONE FIGURE
    # ================================================================
    def plot_max_uplift_change_all_cases(self):

        plt.figure(figsize=(12, 7))

        for n_substeps in sorted(self.all_data.keys()):

            df = self.all_data[n_substeps]

            uplift_df = df[
                df["process"] == "uplift_change"
            ].copy()

            if uplift_df.empty:
                continue

            uplift_df = uplift_df.reset_index(drop=True)

            loop_numbers = np.arange(
                1,
                len(uplift_df) + 1
            )

            plt.plot(
                loop_numbers,
                uplift_df["value"],
                marker="o",
                linewidth=2.5,
                label=f"n_substeps={n_substeps}"
            )

        plt.xlabel(
            "Loop Number",
            fontsize=14
        )

        plt.ylabel(
            "Max Uplift Change",
            fontsize=14
        )

        plt.title(
            "Max Uplift Change vs Loop Number",
            fontsize=16
        )

        plt.grid(True)

        # --------------------------------------------------
        # Sort legend numerically
        # --------------------------------------------------
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
            title="n_substeps",
            loc="best"
        )

        save_path = os.path.join(
            self.save_dir,
            "max_uplift_change_vs_loop_number_all_cases.png"
        )

        plt.savefig(
            save_path,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(
            f"Saved:\n{save_path}"
        )


        # ================================================================
    # TOTAL UPLIFT CHANGE VS N_SUBSTEPS
    # ================================================================
    def plot_total_uplift_change_vs_n_substeps(self):

        results = []

        for n_substeps in sorted(self.all_data.keys()):

            df = self.all_data[n_substeps]

            uplift_df = df[
                df["process"] == "uplift_change"
            ]

            if uplift_df.empty:
                continue

            total_uplift_change = uplift_df["value"].sum()

            results.append({

                "n_substeps": n_substeps,

                "total_uplift_change":
                total_uplift_change
            })

        results_df = pd.DataFrame(results)

        plt.figure(figsize=(10, 6))

        # plt.plot(
        #     results_df["n_substeps"],
        #     results_df["total_uplift_change"],
        #     marker="o",
        #     linewidth=3
        # )
        # for _, row in results_df.iterrows():

        #     plt.scatter(
        #         row["n_substeps"],
        #         row["total_uplift_change"],
        #         s=150,
        #         label=f'n_substeps={int(row["n_substeps"])}'
        #     )

        for _, row in results_df.iterrows():

            plt.scatter(
                row["n_substeps"],
                row["total_uplift_change"],
                s=150,
                label=f'n_substeps={int(row["n_substeps"])}'
            )

        plt.legend(title="n_substeps")

        plt.xlabel(
            "n_substeps",
            fontsize=14
        )

        plt.ylabel(
            "Total Uplift Change",
            fontsize=14
        )

        plt.title(
            "Cumulative Uplift Change vs n_substeps",
            fontsize=16
        )

        plt.grid(True)

        save_path = os.path.join(
            self.save_dir,
            "total_uplift_change_vs_n_substeps.png"
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
                "total_uplift_change_vs_n_substeps.csv"
            ),
            index=False
        )

        

        print(
            f"Saved:\n{save_path}"
        )


        # ================================================================
    # TOTAL DIFFUSION CHANGE VS N_SUBSTEPS
    # ================================================================
    def plot_total_diffusion_change_vs_n_substeps(self):

        results = []

        for n_substeps in sorted(self.all_data.keys()):

            df = self.all_data[n_substeps]

            diffusion_df = df[
                df["process"] == "diffusion_change"
            ]

            if diffusion_df.empty:
                continue

            total_diffusion_change = (
                diffusion_df["value"].sum()
            )

            results.append({

                "n_substeps": n_substeps,

                "total_diffusion_change":
                total_diffusion_change
            })

        results_df = pd.DataFrame(results)

        plt.figure(figsize=(10,6))

        for _, row in results_df.iterrows():

            plt.scatter(
                row["n_substeps"],
                row["total_diffusion_change"],
                s=200,
                label=f'n_substeps={int(row["n_substeps"])}'
            )

        plt.xlabel(
            "n_substeps",
            fontsize=14
        )

        plt.ylabel(
            "Total Diffusion Change",
            fontsize=14
        )

        plt.title(
            "Cumulative Diffusion Change vs n_substeps",
            fontsize=16
        )

        plt.grid(True)

        plt.legend(
            title="n_substeps"
        )

        save_path = os.path.join(
            self.save_dir,
            "total_diffusion_change_vs_n_substeps.png"
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
                "total_diffusion_change_vs_n_substeps.csv"
            ),
            index=False
        )

        print(
            f"Saved:\n{save_path}"
        )

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

        self.plot_max_diffusion_change_all_cases()

        self.plot_max_uplift_change_all_cases()

        self.plot_total_uplift_change_vs_n_substeps()

        self.plot_total_diffusion_change_vs_n_substeps()

        for n_substeps in sorted(self.all_data.keys()):

            df = self.all_data[n_substeps]

            print(
                n_substeps,
                df["process"].unique()
            )

        # self.topography_convergence_analysis()

        self.plot_loopwise_changes()

        # self.convergence_analysis()

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

        outputs_dir=(
            "./test_template_ADV_GEO_Project_placeholder/outputs"
        ),

        save_dir=(
            "./test_template_ADV_GEO_Project_placeholder/"
            "analysis_substeps_figures"
        )
        #  outputs_dir=(
        #     "./diffusion_5e4_s2yr/outputs"
        # ),

        # save_dir=(
        #     "./diffusion_5e4_s2yr/"
        #     "analysis_substeps_figures"
        # )

        #  outputs_dir=(
        #     "./n_substeps_diffusion_s2yr/outputs"
        # ),

        # save_dir=(
        #     "./n_substeps_diffusion_s2yr/"
        #     "analysis_substeps_figures"
        # )

        
    )

    analyzer.run_all()

