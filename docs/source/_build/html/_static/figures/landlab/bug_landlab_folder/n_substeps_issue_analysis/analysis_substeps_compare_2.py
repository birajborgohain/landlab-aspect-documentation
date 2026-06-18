import os
import re
import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class TraceAnalyzer:

    def __init__(self, outputs_dir, save_dir):

        self.outputs_dir = outputs_dir
        self.save_dir = save_dir

        os.makedirs(
            self.save_dir,
            exist_ok=True
        )

        self.all_data = {}

    # ==========================================================
    # FIND FILES
    # ==========================================================
    def find_trace_files(self):

        pattern = os.path.join(
            self.outputs_dir,
            "**",
            "execution_trace_rank_0.txt"
        )

        return sorted(
            glob.glob(
                pattern,
                recursive=True
            )
        )

    # ==========================================================
    # EXTRACT N_SUBSTEPS
    # ==========================================================
    def extract_n_substeps(self, filepath):

        match = re.search(
            r"n_substeps[-_](\d+)",
            filepath
        )

        if match:
            return int(match.group(1))

        return None

    def parse_trace_file(self, filepath):

        n_substeps = self.extract_n_substeps(
            filepath
        )

        records = []
        current = None

        with open(filepath) as f:

            for line in f:

                m = re.search(
                    r"elapsed_time_before = ([\d.eE+-]+)",
                    line
                )

                if m:

                    if current is not None:
                        records.append(current)

                    current = {
                        "n_substeps_case": n_substeps,
                        "time": float(m.group(1)),
                        "max_B": np.nan,
                        "max_C": np.nan,
                        "diffusion_change": np.nan,
                        "uplift_change": np.nan
                    }

                    continue

                if current is None:
                    continue

                m = re.search(
                    r"max diffusion_change = ([\d.eE+-]+)",
                    line
                )

                if m:
                    current["diffusion_change"] = float(
                        m.group(1)
                    )
                    continue

                m = re.search(
                    r"max elevation after diffusion = ([\d.eE+-]+)",
                    line
                )

                if m:
                    current["max_B"] = float(
                        m.group(1)
                    )
                    continue

                m = re.search(
                    r"max uplift_change = ([\d.eE+-]+)",
                    line
                )

                if m:
                    current["uplift_change"] = float(
                        m.group(1)
                    )
                    continue

                m = re.search(
                    r"max elevation after uplift = ([\d.eE+-]+)",
                    line
                )

                if m:
                    current["max_C"] = float(
                        m.group(1)
                    )

        if current is not None:
            records.append(current)

        df = pd.DataFrame(records)

        df["max_A"] = (
            df["max_B"]
            + df["diffusion_change"]
        )

        df["total_change"] = (
            df["max_C"]
            - df["max_A"]
        )

        self.all_data[n_substeps] = df

        
    # ==========================================================
    # LOAD ALL
    # ==========================================================
    def load_all_files(self):

        files = self.find_trace_files()

        for f in files:

            self.parse_trace_file(f)

    # ==========================================================
    # GENERIC PLOT
    # ==========================================================
    def plot_process_vs_time(self, process):

        plt.figure(figsize=(10, 6))

        for n_substeps in sorted(
            self.all_data.keys()
        ):

            df = self.all_data[n_substeps]

            subset = df[
                df["process"] == process
            ]

            plt.plot(
                subset["simulation_time"],
                subset["value"],
                marker="o",
                linewidth=2,
                label=f"n_substeps={n_substeps}"
            )

        plt.xlabel(
            "Simulation Time"
        )

        plt.ylabel(
            process
        )

        plt.title(
            f"{process} vs Simulation Time"
        )

        plt.grid(True)

        plt.legend()

        plt.savefig(
            os.path.join(
                self.save_dir,
                f"{process}_vs_time.png"
            ),
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

    # ==========================================================
    # COMPARE TWO CASES
    # ==========================================================
    def compare_cases(
        self,
        case1=1,
        case2=2
        ):

        fig, ax = plt.subplots(
            figsize=(12, 7)
        )

        plt.subplots_adjust(
            right=0.68
        )

        for case in [case1, case2]:

            df = self.all_data[case]

            linestyle = (
                "-"
                if case == case1
                else "--"
            )

            ax.plot(
                df["time"],
                df["diffusion_change"],
                color="tab:blue",
                marker="o",
                linewidth=2.5,
                linestyle=linestyle,
                label=fr"$D_i$ (n={case})"
            )

            ax.plot(
                df["time"],
                df["uplift_change"],
                color="tab:orange",
                marker="s",
                linewidth=2.5,
                linestyle=linestyle,
                label=fr"$U_i$ (n={case})"
            )

            ax.plot(
                df["time"],
                df["total_change"],
                color="tab:green",
                marker="^",
                linewidth=3,
                linestyle=linestyle,
                label=fr"$T_i=C-A$ (n={case})"
            )

        ax.set_xlabel(
            "Simulation Time",
            fontsize=14
        )

        ax.set_ylabel(
            r"Maximum Elevation Change, $\Delta z$ (m)",
            fontsize=14
        )

        ax.set_title(
            f"Tracer Comparison\n\n"
            f"n_substeps={case1} vs {case2}",
            fontsize=20
        )

        ax.grid(True)

        ax.legend(
            fontsize=11,
            bbox_to_anchor=(1.02, 1.0),
            loc="upper left"
        )

        plt.savefig(
            os.path.join(
                self.save_dir,
                f"compare_{case1}_{case2}.png"
            ),
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

    # ==========================================================
    # EXPORT
    # ==========================================================
    def export_data(self):

        combined = pd.concat(
            self.all_data.values(),
            ignore_index=True
        )

        combined.to_csv(

            os.path.join(
                self.save_dir,
                "combined_trace_data.csv"
            ),

            index=False
        )

    # ==========================================================
    # RUN
    # ==========================================================
    def run_all(self):

        self.load_all_files()

        self.compare_cases(
            case1=1,
            case2=2
        )

        self.export_data()

        print(
            "\nAnalysis complete."
        )


if __name__ == "__main__":

    analyzer = TraceAnalyzer(

       outputs_dir=(
    "./test_template_ADV_GEO_Project_placeholder/outputs"
        ),

        save_dir=(
            "./test_template_ADV_GEO_Project_placeholder/"
            "analysis_substeps_figures"
        )
    )

    analyzer.run_all()