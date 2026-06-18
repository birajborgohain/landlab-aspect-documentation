
#!/usr/bin/env python3

"""
============================================================
benchmark_class.py
============================================================

Reusable benchmark framework for:

1. Reference solution
2. Standalone Landlab
3. Coupled Landlab
4. ASPECT topography

============================================================
"""

import os
import re
import glob

import numpy as np
import matplotlib.pyplot as plt

from scipy.interpolate import griddata


class BenchmarkFramework:

    # ========================================================
    # WRITE REPORT SECTION
    # ========================================================

    def write_report_section(
        self,
        f,
        comparison_name,
        equation,
        where_lines,
        description,
        metrics
    ):

        f.write(
            "================================================\n"
        )

        f.write(
            f"COMPARISON: {comparison_name}\n"
        )

        f.write(
            "================================================\n\n"
        )

        f.write(
            "You compare:\n\n"
        )

        f.write(
            f"{equation}\n\n"
        )

        f.write(
            "where:\n\n"
        )

        for line in where_lines:

            f.write(
                f"{line}\n"
            )

        f.write("\n")

        f.write(
            f"{description}\n\n"
        )

        status = (
            "PASS"
            if metrics["passed"]
            else "FAIL"
        )

        f.write(
            f"STATUS: {status}\n\n"
        )

        # =================================================
        # PASS / FAIL CRITERION
        # =================================================

        f.write(
            "PASS/FAIL criterion:\n\n"
        )

        f.write(
            "max(|z_test - z_reference|) "
            "< absolute_tolerance\n\n"
        )

        f.write(
            f"absolute_tolerance = "
            f"{self.absolute_tolerance:.1e}\n\n"
        )

        if status == "PASS":

            f.write(
                "Result: PASS because the maximum "
                "absolute error is smaller than "
                "the prescribed absolute "
                "tolerance.\n\n"
            )

        else:

            f.write(
                "Result: FAIL because the maximum "
                "absolute error exceeds the "
                "prescribed absolute "
                "tolerance.\n\n"
            )

        f.write(
            f"Maximum absolute error : "
            f"{metrics['max_abs_error']:.1e}\n\n"
        )

        f.write(
            f"Mean absolute error    : "
            f"{metrics['mean_abs_error']:.1e}\n\n"
        )

        f.write(
            f"RMSE                   : "
            f"{metrics['rmse']:.1e}\n\n"
        )

        f.write(
            f"L2 norm                : "
            f"{metrics['l2_norm']:.1e}\n\n"
        )

        f.write(
            f"Mass difference        : "
            f"{metrics['mass_difference']:.1e}\n\n"
        )


    # ========================================================
    # INITIALIZE
    # ========================================================

    def __init__(
        self,
        outputs_dir,
        case_name
    ):

        self.outputs_dir = os.path.abspath(
            outputs_dir
        )

        self.case_name = case_name

        self.case_folder = os.path.join(
            self.outputs_dir,
            self.case_name
        )

        self.landlab_folder = os.path.join(
            self.case_folder,
            "landlab"
        )

        self.topography_folder = os.path.join(
            self.case_folder,
            "topography"
        )

        self.results_folder = os.path.join(
            self.case_folder,
            "results_benchmark"
        )

        os.makedirs(
            self.results_folder,
            exist_ok=True
        )

        self.absolute_tolerance = 1e-10

    # ========================================================
    # FIND LAST FILE
    # ========================================================

    def find_last_file(
        self,
        folder,
        pattern,
        regex_pattern
    ):

        files = glob.glob(
            os.path.join(folder, pattern)
        )

        numbered_files = []

        for file in files:

            basename = os.path.basename(
                file
            )

            match = re.search(
                regex_pattern,
                basename
            )

            if match:

                timestep = int(
                    match.group(1)
                )

                numbered_files.append(
                    (
                        timestep,
                        file
                    )
                )

        if len(numbered_files) == 0:

            raise RuntimeError(
                f"No files found in:\n{folder}"
            )

        numbered_files.sort()

        return numbered_files[-1]

    # ========================================================
    # WRITE REFERENCE TOPOGRAPHY
    # ========================================================

    def write_reference_topography(
        self,
        mg,
        z_target
    ):

        reference_file = os.path.join(
            self.results_folder,
            "z_target_reference.txt"
        )

        with open(reference_file, "w") as f:

            f.write(
                "# x y z_target\n"
            )

            for y in range(mg.shape[0]):

                for x in range(mg.shape[1]):

                    node_id = (
                        y * mg.shape[1] + x
                    )

                    xcoord = mg.node_x[
                        node_id
                    ]

                    ycoord = mg.node_y[
                        node_id
                    ]

                    zvalue = z_target[
                        node_id
                    ]

                    f.write(
                        f"{xcoord:.0f} "
                        f"{ycoord:.0f} "
                        f"{zvalue:.15f}\n"
                    )

        print(
            f"\nReference topography file written:\n"
            f"{reference_file}"
        )

    # ========================================================
    # WRITE FINAL TOPOGRAPHY
    # ========================================================

    def write_final_topography(
        self,
        mg,
        z_final
    ):

        final_file = os.path.join(
            self.results_folder,
            "z_final_reference.txt"
        )

        with open(final_file, "w") as f:

            f.write(
                "# x y z_final\n"
            )

            for y in range(mg.shape[0]):

                for x in range(mg.shape[1]):

                    node_id = (
                        y * mg.shape[1] + x
                    )

                    xcoord = mg.node_x[
                        node_id
                    ]

                    ycoord = mg.node_y[
                        node_id
                    ]

                    zvalue = z_final[
                        node_id
                    ]

                    f.write(
                        f"{xcoord:.0f} "
                        f"{ycoord:.0f} "
                        f"{zvalue:.15f}\n"
                    )

        print(
            f"\nFinal topography file written:\n"
            f"{final_file}"
        )

    # ========================================================
    # EXTRACT ASPECT TOPOGRAPHY
    # ========================================================

    def extract_aspect_topography(self):

        timestep, topo_file = (
            self.find_last_file(
                self.topography_folder,
                "topography.*",
                r"topography\.(\d+)"
            )
        )

        output_file = os.path.join(
            self.results_folder,
            f"topography_{timestep:04d}_last_time_step.txt"
        )

        unique_points = set()

        cleaned_data = []

        with open(topo_file, "r") as f:

            for line in f:

                if line.startswith("#"):
                    continue

                parts = line.split()

                if len(parts) < 4:
                    continue

                x = float(parts[0])

                y = float(parts[1])

                topography = float(
                    parts[3]
                )

                key = (
                    round(x, 8),
                    round(y, 8)
                )

                if key not in unique_points:

                    unique_points.add(key)

                    cleaned_data.append(
                        (
                            x,
                            y,
                            topography
                        )
                    )

        cleaned_data.sort(
            key=lambda p: (
                p[1],
                p[0]
            )
        )

        with open(output_file, "w") as f:

            f.write(
                "# x y topography\n"
            )

            for x, y, topo in cleaned_data:

                f.write(
                    f"{x:.6f} "
                    f"{y:.6f} "
                    f"{topo:.15f}\n"
                )

        print(
            f"\nASPECT topography extracted:\n"
            f"{output_file}"
        )

        return output_file


    # ========================================================
    # EXTRACT LANDLAB TOPOGRAPHY
    # ========================================================

    def extract_landlab_topography(self):

        timestep, vtk_file = (
            self.find_last_file(
                self.landlab_folder,
                "landlab_*.vtk",
                r"landlab_(\d+)\.vtk"
            )
        )

        output_file = os.path.join(
            self.results_folder,
            f"landlab_{timestep:04d}_last_time_step.txt"
        )

        x = []
        y = []
        z = []

        with open(vtk_file, "r") as f:

            lines = f.readlines()

        points_start = None
        n_points = 0

        for i, line in enumerate(lines):

            if line.startswith("POINTS"):

                parts = line.split()

                n_points = int(parts[1])

                points_start = i + 1

                break

        if points_start is None:

            raise RuntimeError(
                f"POINTS section not found:\n{vtk_file}"
            )

        for line in lines[
            points_start :
            points_start + n_points
        ]:

            parts = line.split()

            if len(parts) != 3:
                continue

            xcoord = float(parts[0])

            ycoord = float(parts[1])

            zcoord = float(parts[2])

            x.append(xcoord)

            y.append(ycoord)

            z.append(zcoord)

        cleaned_data = list(
            zip(x, y, z)
        )

        cleaned_data.sort(
            key=lambda p: (
                p[1],
                p[0]
            )
        )

        with open(output_file, "w") as f:

            f.write(
                "# x y topography\n"
            )

            for xcoord, ycoord, zcoord in cleaned_data:

                f.write(
                    f"{xcoord:.6f} "
                    f"{ycoord:.6f} "
                    f"{zcoord:.15f}\n"
                )

        print(
            f"\nLandlab topography extracted:\n"
            f"{output_file}"
        )

        return output_file
    
    # ========================================================
    # EXTRACT ASPECT TOPOGRAPHY AT TIMESTEP
    # ========================================================

    def extract_aspect_topography_at_timestep(
        self,
        timestep
    ):

        topo_file = os.path.join(
            self.topography_folder,
            f"topography.{timestep:05d}"
        )

        if not os.path.exists(topo_file):

            raise RuntimeError(
                f"File not found:\n{topo_file}"
            )

        output_file = os.path.join(
            self.results_folder,
            f"topography_{timestep:05d}.txt"
        )

        unique_points = set()
        cleaned_data = []

        with open(topo_file, "r") as f:

            for line in f:

                if line.startswith("#"):
                    continue

                parts = line.split()

                if len(parts) < 4:
                    continue

                x = float(parts[0])
                y = float(parts[1])
                z = float(parts[3])

                key = (
                    round(x, 8),
                    round(y, 8)
                )

                if key not in unique_points:

                    unique_points.add(key)

                    cleaned_data.append(
                        (x, y, z)
                    )

        cleaned_data.sort(
            key=lambda p: (
                p[1],
                p[0]
            )
        )

        with open(output_file, "w") as f:

            f.write("# x y z\n")

            for x, y, z in cleaned_data:

                f.write(
                    f"{x:.6f} "
                    f"{y:.6f} "
                    f"{z:.15f}\n"
                )

        return output_file


    # ========================================================
    # EXTRACT LANDLAB TOPOGRAPHY AT TIMESTEP
    # ========================================================

    def extract_landlab_topography_at_timestep(
        self,
        timestep
    ):

        vtk_file = os.path.join(
            self.landlab_folder,
            f"landlab_{timestep:04d}.vtk"
        )

        if not os.path.exists(vtk_file):

            raise RuntimeError(
                f"File not found:\n{vtk_file}"
            )

        output_file = os.path.join(
            self.results_folder,
            f"landlab_{timestep:04d}.txt"
        )

        x = []
        y = []
        z = []

        with open(vtk_file, "r") as f:
            lines = f.readlines()

        points_start = None
        n_points = 0

        for i, line in enumerate(lines):

            if line.startswith("POINTS"):

                parts = line.split()

                n_points = int(parts[1])

                points_start = i + 1

                break

        for line in lines[
            points_start :
            points_start + n_points
        ]:

            parts = line.split()

            if len(parts) != 3:
                continue

            x.append(float(parts[0]))
            y.append(float(parts[1]))
            z.append(float(parts[2]))

        cleaned_data = list(
            zip(x, y, z)
        )

        cleaned_data.sort(
            key=lambda p: (
                p[1],
                p[0]
            )
        )

        with open(output_file, "w") as f:

            f.write("# x y z\n")

            for xcoord, ycoord, zcoord in cleaned_data:

                f.write(
                    f"{xcoord:.6f} "
                    f"{ycoord:.6f} "
                    f"{zcoord:.15f}\n"
                )

        return output_file
    
    def load_standalone_timestep(
    self,
    timestep,
    column="z_after_uplift"
    ):

        file_name = os.path.join(
            self.results_folder,
            f"z_timestep_{timestep}.txt"
        )

        data = np.loadtxt(
            file_name,
            comments="#"
        )

        x = data[:, 0]
        y = data[:, 1]

        columns = {
            "z_before": 2,
            "z_after_diffusion": 3,
            "z_after_uplift": 4
        }

        z = data[:, columns[column]]

        return x, y, z
    
    def load_initial_standalone(self):

        file_name = os.path.join(
            self.results_folder,
            "z_initial_reference.txt"
        )

        return self.load_xyz(file_name)
        
    # # ========================================================
    # # LOAD VTK XYZ
    # # ========================================================

    # def load_vtk_xyz(self,vtk_file):

    #     x = []
    #     y = []
    #     z = []

    #     with open(vtk_file, "r") as f:

    #         lines = f.readlines()

    #     points_start = None
    #     n_points = 0

    #     for i, line in enumerate(lines):

    #         if line.startswith("POINTS"):

    #             parts = line.split()

    #             n_points = int(parts[1])

    #             points_start = i + 1

    #             break

    #     if points_start is None:

    #         raise RuntimeError(
    #             f"POINTS section not found:\n{vtk_file}"
    #         )

    #     for line in lines[
    #         points_start :
    #         points_start + n_points
    #     ]:

    #         parts = line.split()

    #         if len(parts) != 3:
    #             continue

    #         x.append(float(parts[0]))

    #         y.append(float(parts[1]))

    #         z.append(float(parts[2]))

    #     return (
    #         np.array(x),
    #         np.array(y),
    #         np.array(z)
    #     )

    # ========================================================
    # LOAD XYZ
    # ========================================================

    def load_xyz(
        self,
        file_name
    ):

        data = np.loadtxt(
            file_name,
            comments="#"
        )

        x = data[:, 0]

        y = data[:, 1]

        z = data[:, 2]

        return x, y, z

    # ========================================================
    # COMPUTE METRICS
    # ========================================================

    def compute_metrics(
        self,
        reference,
        test
    ):

        difference = test - reference

        max_abs_error = np.max(
            np.abs(difference)
        )

        mean_abs_error = np.mean(
            np.abs(difference)
        )

        rmse = np.sqrt(
            np.mean(difference**2)
        )

        l2_norm = np.linalg.norm(
            difference
        )

        mass_difference = (
            np.sum(test)
            - np.sum(reference)
        )

        passed = (
            max_abs_error
            < self.absolute_tolerance
        )

        return {

            "difference":
                difference,

            "max_abs_error":
                max_abs_error,

            "mean_abs_error":
                mean_abs_error,

            "rmse":
                rmse,

            "l2_norm":
                l2_norm,

            "mass_difference":
                mass_difference,

            "passed":
                passed
        }

    # ========================================================
    # PRINT METRICS
    # ========================================================

    def print_metrics(
        self,
        label,
        metrics
    ):

        status = (
            "PASS"
            if metrics["passed"]
            else "FAIL"
        )

        print("\n================================================")
        print(f"COMPARISON: {label}")
        print("================================================")

        print(f"\nSTATUS: {status}")

        print(
            f"\nMaximum absolute error : "
            f"{metrics['max_abs_error']:.15e}"
        )

        print(
            f"\nMean absolute error    : "
            f"{metrics['mean_abs_error']:.15e}"
        )

        print(
            f"\nRMSE                   : "
            f"{metrics['rmse']:.15e}"
        )

        print(
            f"\nL2 norm                : "
            f"{metrics['l2_norm']:.15e}"
        )

        print(
            f"\nMass difference        : "
            f"{metrics['mass_difference']:.15e}"
        )

    # ========================================================
    # PLOT MAP
    # ========================================================

    def plot_map(
        self,
        ax,
        data,
        title,
        global_min,
        global_max
    ):

        im = ax.imshow(
            data,
            origin="lower",
            cmap="viridis",
            vmin=global_min,
            vmax=global_max,
            aspect="auto"
        )

        ax.set_title(
            title,
            fontsize=12,
            fontweight="bold"
        )

        ax.set_xlabel("X")

        ax.set_ylabel("Y")

        return im

      # ========================================================
    # FORMAT LONG TITLE
    # ========================================================

    def format_long_title(
        self,
        text,
        max_line_length=60
    ):

        """
        Break long titles into multiple lines.

        Parameters
        ----------
        text : str
            Input long string.

        max_line_length : int
            Maximum characters per line.

        Returns
        -------
        formatted_text : str
            Multi-line formatted string.
        """

        words = text.split("_")

        lines = []

        current_line = ""

        for word in words:

            # +1 for underscore spacing
            proposed = (
                current_line + "_" + word
                if current_line
                else word
            )

            if len(proposed) <= max_line_length:

                current_line = proposed

            else:

                lines.append(current_line)

                current_line = word

        if current_line:

            lines.append(current_line)

        return "\n".join(lines)

    # ========================================================
    # GENERATE BENCHMARK
    # ========================================================

    def generate_benchmark(self):

        # ----------------------------------------------------
        # FILES
        # ----------------------------------------------------

        reference_file = os.path.join(
            self.results_folder,
            "z_target_reference.txt"
        )

        standalone_file = os.path.join(
            self.results_folder,
            "z_final_reference.txt"
        )

        aspect_file = (
            self.extract_aspect_topography()
        )

        # ----------------------------------------------------
        # LOAD REFERENCE
        # ----------------------------------------------------

        x_ref, y_ref, z_ref = (
            self.load_xyz(
                reference_file
            )
        )

        nx = len(
            np.unique(x_ref)
        )

        ny = len(
            np.unique(y_ref)
        )

        reference_2d = z_ref.reshape(
            ny,
            nx
        )

        # ----------------------------------------------------
        # STANDALONE LANDLAB
        # ----------------------------------------------------

        x_s, y_s, z_s = (
            self.load_xyz(
                standalone_file
            )
        )

        standalone_2d = z_s.reshape(
            ny,
            nx
        )

        metrics_standalone = (
            self.compute_metrics(
                z_ref,
                z_s
            )
        )

        self.print_metrics(
            "Standalone Landlab",
            metrics_standalone
        )

    

        # ----------------------------------------------------
        # ASPECT TOPOGRAPHY
        # ----------------------------------------------------

        x_a, y_a, z_a = (
            self.load_xyz(
                aspect_file
            )
        )

        aspect_points = np.column_stack(
            (
                x_a,
                y_a
            )
        )

        reference_points = (
            np.column_stack(
                (
                    x_ref,
                    y_ref
                )
            )
        )

        interpolated_aspect = griddata(
            aspect_points,
            z_a,
            reference_points,
            method="linear"
        )

        nan_mask = np.isnan(
            interpolated_aspect
        )

        if np.any(nan_mask):

            interpolated_aspect[
                nan_mask
            ] = griddata(
                aspect_points,
                z_a,
                reference_points[
                    nan_mask
                ],
                method="nearest"
            )

        aspect_2d = (
            interpolated_aspect.reshape(
                ny,
                nx
            )
        )

        metrics_aspect = (
            self.compute_metrics(
                z_ref,
                interpolated_aspect
            )
        )

        self.print_metrics(
            "ASPECT Topography",
            metrics_aspect
        )

    
        # ----------------------------------------------------
        # COUPLED LANDLAB
        # ----------------------------------------------------

        try:

            # latest_landlab = (
            #     self.find_last_file(
            #         self.landlab_folder,
            #         "landlab_*.vtk",
            #         r"landlab_(\d+)\.vtk"
            #     )
            # )

            coupled_file = (self.extract_landlab_topography())

            x_c, y_c, z_c = (
                self.load_xyz(
                    coupled_file
                )
            )

            coupled_2d = z_c.reshape(
                ny,
                nx
            )

            metrics_coupled = (
                self.compute_metrics(
                    z_ref,
                    z_c
                )
            )

            self.print_metrics(
                "Coupled Landlab",
                metrics_coupled
            )

            coupled_exists = True

        except RuntimeError:

            print(
                "\nNo coupled Landlab files found."
            )

            coupled_exists = False

            coupled_2d = np.zeros_like(
                reference_2d
            )

            metrics_coupled = {

                "mean_abs_error": 0.0,
                "max_abs_error": 0.0,
                "rmse": 0.0,
                "l2_norm": 0.0,
                "mass_difference": 0.0,
                "passed": False
            }




        # ----------------------------------------------------
        # MEAN ABSOLUTE ERRORS
        # ----------------------------------------------------

        standalone_mean_error = (
            metrics_standalone[
                "mean_abs_error"
            ]
        )

        
        if coupled_exists:

            coupled_mean_error = (
                metrics_coupled[
                    "mean_abs_error"
                ]
            )

        else:

            coupled_mean_error = 0.0



        aspect_mean_error = (
            metrics_aspect[
                "mean_abs_error"
            ]
        )




        # ----------------------------------------------------
        # REPORT
        # ----------------------------------------------------

        report_file = os.path.join(
            self.results_folder,
            "benchmark_report.txt"
        )

        with open(report_file, "w") as f:

            f.write(
                "================================================\n"
            )

            f.write(
                "BENCHMARK REPORT\n"
            )

            f.write(
                "================================================\n\n"
            )

            self.write_report_section(
                f=f,
                comparison_name="standalone_landlab",
                equation="z_standalone - z_reference",
                where_lines=[
                    "z_reference   = analytical or target reference topography",
                    "z_standalone  = Landlab-only simulation result"
                ],
                description=(
                    "This comparison evaluates how accurately "
                    "the standalone Landlab simulation "
                    "reproduces the reference topography."
                ),
                metrics=metrics_standalone
            )

            self.write_report_section(
                f=f,
                comparison_name="coupled_landlab",
                equation="z_coupled - z_reference",
                where_lines=[
                    "z_reference = analytical or target reference topography",
                    "z_coupled   = coupled ASPECT-Landlab simulation result"
                ],
                description=(
                    "This comparison evaluates how closely "
                    "the coupled ASPECT-Landlab simulation "
                    "matches the reference topography."
                ),
                metrics=metrics_coupled
            )

            self.write_report_section(
                f=f,
                comparison_name="aspect_topography",
                equation="z_ASPECT - z_reference",
                where_lines=[
                    "z_reference = analytical or target reference topography",
                    "z_ASPECT    = ASPECT free-surface topography"
                ],
                description=(
                    "This comparison evaluates the difference "
                    "between the ASPECT free-surface topography "
                    "and the reference topography."
                ),
                metrics=metrics_aspect
            )

            metrics_coupled_aspect = (
                self.compute_metrics(
                    interpolated_aspect,
                    z_c
                )
            )

            self.write_report_section(
                f=f,
                comparison_name=(
                    "coupled_landlab_vs_aspect_topography"
                ),
                equation="z_coupled - z_ASPECT",
                where_lines=[
                    "z_coupled = coupled ASPECT-Landlab simulation result",
                    "z_ASPECT  = ASPECT free-surface topography"
                ],
                description=(
                    "This comparison evaluates the difference "
                    "between the coupled Landlab topography "
                    "and the ASPECT free-surface topography."
                ),
                metrics=metrics_coupled_aspect
            )

            metrics_aspect_coupled = (
                self.compute_metrics(
                    z_c,
                    interpolated_aspect
                )
            )

            self.write_report_section(
                f=f,
                comparison_name=(
                    "aspect_topography_vs_coupled_landlab"
                ),
                equation="z_ASPECT - z_coupled",
                where_lines=[
                    "z_ASPECT  = ASPECT free-surface topography",
                    "z_coupled = coupled ASPECT-Landlab simulation result"
                ],
                description=(
                    "This comparison evaluates the difference "
                    "between the ASPECT free-surface topography "
                    "and the coupled Landlab topography."
                ),
                metrics=metrics_aspect_coupled
            )

            f.write(
                "================================================\n"
            )

            print(
                f"\nBenchmark report written:\n"
                f"{report_file}"
            )





        
        # ----------------------------------------------------
        # FIGURE
        # ----------------------------------------------------

        fig, axes = plt.subplots(
            4,
            3,
            figsize=(18, 21),
            constrained_layout=True
        )

        global_min = z_ref.min()

        global_max = z_ref.max()

        # ============================================================
        # ROW 1
        # REFERENCE + STANDALONE
        # ============================================================

        im = self.plot_map(
            axes[0, 0],
            reference_2d,
            "Reference Solution",
            global_min,
            global_max
        )

        self.plot_map(
            axes[0, 1],
            standalone_2d,
            "Standalone Landlab",
            global_min,
            global_max
        )

        bars1 = axes[0, 2].bar(
            [
                "Standalone Landlab",
                "Coupled Landlab"
            ],
            [
                standalone_mean_error,
                coupled_mean_error
            ]
        )

        axes[0, 2].set_title(
            "Standalone Landlab vs Coupled Landlab",
            fontsize=12,
            fontweight="bold"
        )

        axes[0, 2].set_ylabel(
            "Mean Absolute Difference"
        )

        axes[0, 2].ticklabel_format(
            axis="y",
            style="sci",
            scilimits=(0, 0)
        )

        for bar in bars1:

            height = bar.get_height()

            axes[0, 2].text(
                bar.get_x() + bar.get_width()/2,
                height,
                f"{height:.2e}",
                ha="center",
                va="bottom",
                fontsize=9
            )

        # ============================================================
        # ROW 2
        # REFERENCE + COUPLED
        # ============================================================

        self.plot_map(
            axes[1, 0],
            reference_2d,
            "Reference Solution",
            global_min,
            global_max
        )

        # self.plot_map(
        #     axes[1, 1],
        #     coupled_2d,
        #     "Coupled Landlab",
        #     global_min,
        #     global_max
        # )
            
        if coupled_exists:

            self.plot_map(
                axes[1, 1],
                coupled_2d,
                "Coupled Landlab",
                global_min,
                global_max
            )

        else:

            axes[1, 1].text(
                0.5,
                0.5,
                "No Coupled\nLandlab File",
                ha="center",
                va="center",
                fontsize=14
            )

            axes[1, 1].set_axis_off()



        bars2 = axes[1, 2].bar(
            [
                "Coupled Landlab",
                "ASPECT"
            ],
            [
                coupled_mean_error,
                aspect_mean_error
            ]
        )

        axes[1, 2].set_title(
            "Coupled Landlab vs ASPECT",
            fontsize=12,
            fontweight="bold"
        )

        axes[1, 2].set_ylabel(
            "Mean Absolute Difference"
        )

        axes[1, 2].ticklabel_format(
            axis="y",
            style="sci",
            scilimits=(0, 0)
        )

        for bar in bars2:

            height = bar.get_height()

            axes[1, 2].text(
                bar.get_x() + bar.get_width()/2,
                height,
                f"{height:.2e}",
                ha="center",
                va="bottom",
                fontsize=9
            )

        # ============================================================
        # ROW 3
        # REFERENCE + ASPECT
        # ============================================================

        self.plot_map(
            axes[2, 0],
            reference_2d,
            "Reference Solution",
            global_min,
            global_max
        )

        self.plot_map(
            axes[2, 1],
            aspect_2d,
            "ASPECT Topography",
            global_min,
            global_max
        )

        bars3 = axes[2, 2].bar(
            [
                "Standalone",
                "Coupled L",
                "ASPECT"
            ],
            [
                standalone_mean_error,
                coupled_mean_error,
                aspect_mean_error
            ]
        )

        axes[2, 2].set_title(
            "All Benchmark Comparisons",
            fontsize=12,
            fontweight="bold"
        )

        axes[2, 2].set_ylabel(
            "Mean Absolute Difference"
        )

        axes[2, 2].ticklabel_format(
            axis="y",
            style="sci",
            scilimits=(0, 0)
        )

        for bar in bars3:

            height = bar.get_height()

            axes[2, 2].text(
                bar.get_x() + bar.get_width()/2,
                height,
                f"{height:.2e}",
                ha="center",
                va="bottom",
                fontsize=9
            )

            # ============================================================
        # ROW 4
        # COUPLED + ASPECT
        # ============================================================

        if coupled_exists:

            self.plot_map(
                axes[3, 0],
                coupled_2d,
                "Coupled Landlab",
                global_min,
                global_max
            )

        else:

            axes[3, 0].text(
                0.5,
                0.5,
                "No Coupled\nLandlab File",
                ha="center",
                va="center",
                fontsize=14
            )

            axes[3, 0].set_axis_off()

        self.plot_map(
            axes[3, 1],
            aspect_2d,
            "ASPECT Topography",
            global_min,
            global_max
        )

        bars4 = axes[3, 2].bar(
            [
                "Standalone",
                "Coupled L vs ASPECT"
            ],
            [
                standalone_mean_error,
                np.mean(np.abs(z_c - interpolated_aspect)
                ) if coupled_exists else 0.0
            ]
        )

        axes[3, 2].set_title(
            "Standalone vs Coupled-ASPECT",
            fontsize=12,
            fontweight="bold"
        )

        axes[3, 2].set_ylabel(
            "Mean Absolute Difference"
        )

        axes[3, 2].ticklabel_format(
            axis="y",
            style="sci",
            scilimits=(0, 0)
        )

        for bar in bars4:

            height = bar.get_height()

            axes[3, 2].text(
                bar.get_x() + bar.get_width()/2,
                height,
                f"{height:.2e}",
                ha="center",
                va="bottom",
                fontsize=9
            )

        # ============================================================
        # COLORBAR
        # ============================================================

        cbar = fig.colorbar(
            im,
            ax=axes[:, 0:2],
            location="right",
            shrink=0.85,
            pad=0.02
        )

        cbar.set_label(
            "Elevation",
            fontsize=12,
            fontweight="bold"
        )

        # ============================================================
        # TITLE
        # ============================================================

        # fig.suptitle(
        #     "ASPECT–Landlab Benchmark Comparison",
        #     fontsize=18,
        #     fontweight="bold"
        # )
        # fig.suptitle(
        #     f"{self.case_name}\nASPECT–Landlab Benchmark Comparison",
        #     fontsize=18,
        #     fontweight="bold"
        # )

        formatted_case_name = self.format_long_title(
            self.case_name,
            max_line_length=60
        )

        fig.suptitle(
            f"{formatted_case_name}\nASPECT–Landlab Benchmark Comparison",
            fontsize=18,
            fontweight="bold"
        )

        # ============================================================
        # SAVE FIGURE
        # ============================================================

        figure_file = os.path.join(
            self.results_folder,
            "benchmark_comparison_figure.png"
        )

        plt.savefig(
            figure_file,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(
            f"\nBenchmark figure written:\n"
            f"{figure_file}"
        )
        

# ============================================================
# CROSS SECTION ANALYSIS
# ============================================================

class CrossSectionPlotter:

    def __init__(self, benchmark):

        self.benchmark = benchmark

    # ========================================================
    # EXTRACT CROSS SECTION
    # ========================================================

    def extract_cross_section(
        self,
        x,
        y,
        z,
        x_section
    ):

        # --------------------------------------------
        # Find nearest x location
        # --------------------------------------------

        unique_x = np.unique(x)

        nearest_x = unique_x[
            np.argmin(
                np.abs(unique_x - x_section)
            )
        ]

        # --------------------------------------------
        # Extract nodes along this x
        # --------------------------------------------

        mask = np.isclose(x, nearest_x)

        y_section = y[mask]

        z_section = z[mask]

        # --------------------------------------------
        # Sort along y direction
        # --------------------------------------------

        sort_index = np.argsort(y_section)

        y_section = y_section[sort_index]

        z_section = z_section[sort_index]

        return (
            nearest_x,
            y_section,
            z_section
        )

    def plot_early_time_steps(self):

        self.plot_cross_section_timestep(
            timestep=1,
            output_name=
            "cross_section_comparison_1rst_time_step.png"
        )

        self.plot_cross_section_timestep(
            timestep=2,
            output_name=
            "cross_section_comparison_2nd_time_step.png"
        )


   
    # def plot_cross_section(self):
    def plot_cross_section_timestep(
    self,
    timestep,
    output_name):

        benchmark = self.benchmark

        # ----------------------------------------------------
        # FILES
        # ----------------------------------------------------

        # reference_file = os.path.join(
        #     benchmark.results_folder,
        #     "z_target_reference.txt"
        # )

        # standalone_file = os.path.join(
        #     benchmark.results_folder,
        #     "z_final_reference.txt"
        # )

        # aspect_file = benchmark.extract_aspect_topography()

        # coupled_file = benchmark.extract_landlab_topography()
        reference_file = os.path.join(
            benchmark.results_folder,
            "z_target_reference.txt"
        )

        # final_file = os.path.join(
        #     benchmark.results_folder,
        #     "z_final_reference.txt"
        # )

        aspect_file = (
            benchmark.extract_aspect_topography_at_timestep(
                timestep
            )
        )

        coupled_file = (
            benchmark.extract_landlab_topography_at_timestep(
                timestep
            )
        )

        # ----------------------------------------------------
        # LOAD DATA
        # ----------------------------------------------------

        x_ref, y_ref, z_ref = benchmark.load_xyz(
            reference_file
        )

        # x_s, y_s, z_s = benchmark.load_xyz(
        #     standalone_file
        # )
        # x_f, y_f, z_f = benchmark.load_xyz(
        #     final_file
        # )
        x_f, y_f, z_f = (
            benchmark.load_standalone_timestep(
                timestep,
                column="z_after_uplift"
            )
        )

        x_a, y_a, z_a = benchmark.load_xyz(
            aspect_file
        )

        x_c, y_c, z_c = benchmark.load_xyz(
            coupled_file
        )

        # ----------------------------------------------------
        # GRID SIZE
        # ----------------------------------------------------

        nx = len(np.unique(x_ref))

        ny = len(np.unique(y_ref))

        reference_2d = z_ref.reshape(ny, nx)

        # ----------------------------------------------------
        # MIDDLE X LOCATION
        # ----------------------------------------------------

        xmin = np.min(x_ref)

        xmax = np.max(x_ref)

        ymin = np.min(y_ref)

        ymax = np.max(y_ref)

        # x_middle = 0.5 * (xmin + xmax)
        x_middle = 700

        # ----------------------------------------------------
        # EXTRACT CROSS SECTIONS
        # ----------------------------------------------------

        xline, y_ref_sec, z_ref_sec = (
            self.extract_cross_section(
                x_ref,
                y_ref,
                z_ref,
                x_middle
            )
        )

        # _, y_s_sec, z_s_sec = (
        #     self.extract_cross_section(
        #         x_s,
        #         y_s,
        #         z_s,
        #         x_middle
        #     )
        # )
        _, y_f_sec, z_f_sec = (
            self.extract_cross_section(
                x_f,
                y_f,
                z_f,
                x_middle
            )
        )

        _, y_a_sec, z_a_sec = (
            self.extract_cross_section(
                x_a,
                y_a,
                z_a,
                x_middle
            )
        )

        _, y_c_sec, z_c_sec = (
            self.extract_cross_section(
                x_c,
                y_c,
                z_c,
                x_middle
            )
        )

        # ====================================================
        # FIGURE
        # ====================================================

        fig, axes = plt.subplots(
            1,
            2,
            figsize=(16, 7),
            constrained_layout=True
        )

        # fig.suptitle(
        #     f"{benchmark.case_name}\nCross Section Analysis",
        #     fontsize=18,
        #     fontweight="bold"
        # )

        formatted_case_name = benchmark.format_long_title(
            benchmark.case_name,
            max_line_length=60
        )

        fig.suptitle(
            f"{formatted_case_name}\nCross Section Analysis",
            fontsize=18,
            fontweight="bold"
        )

        # ====================================================
        # LEFT PANEL
        # MAP WITH CROSS SECTION LINE
        # ====================================================

        ax0 = axes[0]

        im = ax0.imshow(
            reference_2d,
            origin="lower",
            extent=[
                xmin,
                xmax,
                ymin,
                ymax
            ],
            cmap="terrain",
            aspect="auto"
        )

        # --------------------------------------------
        # Cross-section line
        # --------------------------------------------

        ax0.plot(
            [xline, xline],
            [ymin, ymax],
            color="red",
            linewidth=3,
            linestyle="--",
            label="Cross Section"
        )

        ax0.set_title(
            "Reference Topography\nwith Cross Section Line",
            fontsize=15,
            fontweight="bold"
        )

        ax0.set_xlabel(
            "X Coordinate",
            fontsize=13
        )

        ax0.set_ylabel(
            "Y Coordinate",
            fontsize=13
        )

        ax0.legend()

        cbar = fig.colorbar(
            im,
            ax=ax0,
            shrink=0.85
        )

        cbar.set_label(
            "Elevation",
            fontsize=12
        )

        # ====================================================
        # RIGHT PANEL
        # CROSS SECTION
        # ====================================================

        ax1 = axes[1]

        # --------------------------------------------
        # Reference
        # --------------------------------------------

        # ax1.plot(
        #     y_ref_sec,
        #     z_ref_sec,
        #     color="black",
        #     linewidth=4,
        #     linestyle="-",
        #     marker="o",
        #     markersize=5,
        #     markevery=5,
        #     label="Reference"
        # )

        ax1.plot(
            y_f_sec,
            z_f_sec,
            color="blue",
            linewidth=3,
            linestyle="--",
            marker="s",
            markevery=5,
            label="Final Topography"
        )

        # --------------------------------------------
        # Standalone
        # --------------------------------------------

        ax1.plot(
            y_f_sec,
            z_f_sec,
            color="blue",
            linewidth=2.5,
            linestyle="--",
            marker="s",
            markersize=12,
            markevery=5,
            # label="Standalone Landlab"
            label=f"Standalone Landlab Time Step {timestep}"
        )

        # --------------------------------------------
        # Coupled
        # --------------------------------------------

        ax1.plot(
            y_c_sec,
            z_c_sec,
            color="red",
            linewidth=2.5,
            linestyle="-.",
            marker="^",
            markersize=4,
            markevery=5,
            # label="Coupled Landlab"
            label=f"Coupled Landlab Time Step {timestep}"
        )

        # --------------------------------------------
        # ASPECT
        # --------------------------------------------

        ax1.plot(
            y_a_sec,
            z_a_sec,
            color="green",
            linewidth=2.5,
            linestyle=":",
            marker="d",
            markersize=4,
            markevery=5,
            # label="ASPECT"
            label=f"ASPECT Time Step {timestep}"
        )

        # ----------------------------------------------------
        # LABELS
        # ----------------------------------------------------

        ax1.set_title(
            f"Cross Section at x = {xline:.2f}",
            fontsize=16,
            fontweight="bold"
        )

        ax1.set_xlabel(
            "Y Coordinate",
            fontsize=13
        )

        ax1.set_ylabel(
            "Elevation",
            fontsize=13
        )

        ax1.grid(
            True,
            linestyle="--",
            alpha=0.4
        )

        ax1.legend(
            fontsize=11
        )

        # ====================================================
        # SAVE
        # ====================================================

        # figure_file = os.path.join(
        #     benchmark.results_folder,
        #     "cross_section_comparison.png"
        # )
        figure_file = os.path.join(
            benchmark.results_folder,
            output_name
        )

        plt.savefig(
            figure_file,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(
            f"\nCross-section figure written:\n"
            f"{figure_file}"
        )

    # def load_time_zero_data(self):

    #     benchmark = self.benchmark

    #     x_s, y_s, z_s = (
    #         benchmark.load_initial_standalone()
    #     )

    #     aspect_file = (
    #         benchmark.extract_aspect_topography_at_timestep(
    #             0
    #         )
    #     )

    #     coupled_file = (
    #         benchmark.extract_landlab_topography_at_timestep(
    #             0
    #         )
    #     )

    #     x_a, y_a, z_a = benchmark.load_xyz(
    #         aspect_file
    #     )

    #     x_c, y_c, z_c = benchmark.load_xyz(
    #         coupled_file
    #     )

    #     return (
    #         x_s, y_s, z_s,
    #         x_c, y_c, z_c,
    #         x_a, y_a, z_a
    #     )

    def load_time_zero_data(self):

        benchmark = self.benchmark

        reference_file = os.path.join(
            benchmark.results_folder,
            "z_initial_reference.txt"
        )

        # x_s, y_s, z_s = benchmark.load_xyz(
        #     reference_file
        # )
        x_r, y_r, z_r = benchmark.load_xyz(
            reference_file
        )

        # For timestep 0 the standalone solution
        # is identical to the initial reference
        x_s, y_s, z_s = (
            x_r,
            y_r,
            z_r
        )

        aspect_file = (
            benchmark.extract_aspect_topography_at_timestep(
                0
            )
        )

        coupled_file = (
            benchmark.extract_landlab_topography_at_timestep(
                1
            )
        )

        x_a, y_a, z_a = benchmark.load_xyz(
            aspect_file
        )

        x_c, y_c, z_c = benchmark.load_xyz(
            coupled_file
        )

        # return (
        #     x_s, y_s, z_s,
        #     x_c, y_c, z_c,
        #     x_a, y_a, z_a
        # )
        return (
            x_r, y_r, z_r,   # reference

            x_s, y_s, z_s,   # standalone

            x_c, y_c, z_c,   # coupled

            x_a, y_a, z_a    # aspect
        )

    def load_time_step_data(
    self,
    timestep
    ):

        benchmark = self.benchmark

        x_s, y_s, z_s = (
            benchmark.load_standalone_timestep(
                timestep,
                column="z_after_uplift"
            )
        )

        aspect_file = (
            benchmark.extract_aspect_topography_at_timestep(
                timestep
            )
        )

        coupled_file = (
            benchmark.extract_landlab_topography_at_timestep(
                timestep + 1
            )
        )

        x_a, y_a, z_a = benchmark.load_xyz(
            aspect_file
        )

        x_c, y_c, z_c = benchmark.load_xyz(
            coupled_file
        )

        reference_file = os.path.join(
            benchmark.results_folder,
            "z_target_reference.txt"
        )

        x_r, y_r, z_r = benchmark.load_xyz(
            reference_file
        )

        # return (
        #     x_s, y_s, z_s,
        #     x_c, y_c, z_c,
        #     x_a, y_a, z_a
        # )
        return (
            x_r, y_r, z_r,

            x_s, y_s, z_s,

            x_c, y_c, z_c,

            x_a, y_a, z_a
        )

        print(
            f"\nComparison mapping:\n"
            f"Standalone : timestep {timestep}\n"
            f"ASPECT     : topography.{timestep:05d}\n"
            f"Coupled    : landlab_{timestep+1:04d}.vtk"
        )

    def plot_panel(
        self,
        ax,
        timestep,
        x_r, y_r, z_r,
        x_s, y_s, z_s,
        x_c, y_c, z_c,
        x_a, y_a, z_a,
        x_section=700
    ):

        _, y_r_sec, z_r_sec = (
        self.extract_cross_section(
            x_r,
            y_r,
            z_r,
            x_section
        )
        )
        _, y_s_sec, z_s_sec = (
        self.extract_cross_section(
            x_s, y_s, z_s,
            x_section
        )
        )

        _, y_c_sec, z_c_sec = (
            self.extract_cross_section(
                x_c, y_c, z_c,
                x_section
            )
        )

        _, y_a_sec, z_a_sec = (
            self.extract_cross_section(
                x_a, y_a, z_a,
                x_section
            )
        )

        # ax.plot(
        #     y_s_sec,
        #     z_s_sec,
        #     linewidth=3,
        #     label="Standalone"
        # )

        # ax.plot(
        #     y_c_sec,
        #     z_c_sec,
        #     linewidth=2,
        #     label="Coupled"
        # )

        # ax.plot(
        #     y_a_sec,
        #     z_a_sec,
        #     linewidth=2,
        #     label="ASPECT"
        # )
        ax.plot(
            y_r_sec,
            z_r_sec,
            color="black",
            linewidth=5,
            linestyle="-",
            marker='s',
            markersize= 12,
            markeredgecolor='black',
            label="Reference"
        )

        ax.plot(
        y_s_sec,
        z_s_sec,
        color="blue",
        linewidth=4,
        label="Standalone"
        )

        ax.plot(
            y_c_sec,
            z_c_sec,
            color="red",
            linewidth=3,
            linestyle="--",
            marker="o",
            markersize=5,
            label="Coupled"
        )

        ax.plot(
            y_a_sec,
            z_a_sec,
            color="green",
            linewidth=3,
            linestyle=":",
            marker="^",
            markersize=5,
            label="ASPECT"
        )

        # ax.set_title(
        #     f"Time Step {timestep}"
        # )

        # ax.set_xlabel("Y")

        # ax.set_ylabel("Elevation")

        # ax.grid(True)

        # ax.legend()

        ax.set_title(
            f"Time Step {timestep}",
            fontsize=18,
            fontweight="bold"
        )

        ax.set_xlabel(
            "Y Coordinate",
            fontsize=16,
            fontweight="bold"
        )

        ax.set_ylabel(
            "Elevation",
            fontsize=16,
            fontweight="bold"
        )

        ax.tick_params(
            axis="both",
            labelsize=14
        )

        ax.legend(
            fontsize=14,
            loc="best"
        )

    def plot_all_cross_sections(self):

        benchmark = self.benchmark

        fig, axes = plt.subplots(
            2,
            2,
            figsize=(18, 12),
            constrained_layout=True
        )

        self.plot_panel(
            axes[0,0],
            0,
            *self.load_time_zero_data()
        )

        self.plot_panel(
            axes[0,1],
            1,
            *self.load_time_step_data(1)
        )

        self.plot_panel(
            axes[1,0],
            2,
            *self.load_time_step_data(2)
        )

        self.plot_panel(
            axes[1,1],
            3,
            *self.load_time_step_data(3)
        )

        formatted_case_name = (
            benchmark.format_long_title(
                benchmark.case_name,
                max_line_length=60
            )
        )

        fig.suptitle(
            f"{formatted_case_name}\n"
            f"Cross Section Evolution",
            fontsize=18,
            fontweight="bold"
        )

        figure_file = os.path.join(
            benchmark.results_folder,
            "cross_section_all_times.png"
        )

        plt.savefig(
            figure_file,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print(
            f"\nCross-section figure written:\n"
            f"{figure_file}"
        )
  
# ============================================================
# INITIAL TIME STEP ANALYSIS
# ============================================================

# class InitialTimeStepAnalysis:

#     def __init__(self, benchmark):

#         self.benchmark = benchmark

#     # ========================================================
#     # FIND FIRST FILE
#     # ========================================================

#     def find_first_file(
#         self,
#         folder,
#         pattern,
#         regex_pattern
#     ):

#         files = glob.glob(
#             os.path.join(folder, pattern)
#         )

#         numbered_files = []

#         for file in files:

#             basename = os.path.basename(file)

#             match = re.search(
#                 regex_pattern,
#                 basename
#             )

#             if match:

#                 timestep = int(match.group(1))

#                 numbered_files.append(
#                     (
#                         timestep,
#                         file
#                     )
#                 )

#         if len(numbered_files) == 0:

#             raise RuntimeError(
#                 f"No files found in:\n{folder}"
#             )

#         numbered_files.sort()

#         return numbered_files[0]

#     # ========================================================
#     # EXTRACT INITIAL ASPECT TOPOGRAPHY
#     # ========================================================

#     def extract_initial_aspect_topography(self):

#         benchmark = self.benchmark

#         timestep, topo_file = (
#             self.find_first_file(
#                 benchmark.topography_folder,
#                 "topography.*",
#                 r"topography\.(\d+)"
#             )
#         )

#         output_file = os.path.join(
#             benchmark.results_folder,
#             f"topography_{timestep:04d}_initial_time_step.txt"
#         )

#         unique_points = set()

#         cleaned_data = []

#         with open(topo_file, "r") as f:

#             for line in f:

#                 if line.startswith("#"):
#                     continue

#                 parts = line.split()

#                 if len(parts) < 4:
#                     continue

#                 x = float(parts[0])

#                 y = float(parts[1])

#                 z = float(parts[3])

#                 key = (
#                     round(x, 8),
#                     round(y, 8)
#                 )

#                 if key not in unique_points:

#                     unique_points.add(key)

#                     cleaned_data.append(
#                         (
#                             x,
#                             y,
#                             z
#                         )
#                     )

#         cleaned_data.sort(
#             key=lambda p: (
#                 p[1],
#                 p[0]
#             )
#         )

#         with open(output_file, "w") as f:

#             f.write("# x y z\n")

#             for x, y, z in cleaned_data:

#                 f.write(
#                     f"{x:.6f} "
#                     f"{y:.6f} "
#                     f"{z:.15f}\n"
#                 )

#         print(
#             f"\nInitial ASPECT topography extracted:\n"
#             f"{output_file}"
#         )

#         return output_file

#     # ========================================================
#     # EXTRACT INITIAL LANDLAB TOPOGRAPHY
#     # ========================================================

#     def extract_initial_landlab_topography(self):

#         benchmark = self.benchmark

#         timestep, vtk_file = (
#             self.find_first_file(
#                 benchmark.landlab_folder,
#                 "landlab_*.vtk",
#                 r"landlab_(\d+)\.vtk"
#             )
#         )

#         output_file = os.path.join(
#             benchmark.results_folder,
#             f"landlab_{timestep:04d}_initial_time_step.txt"
#         )

#         x = []
#         y = []
#         z = []

#         with open(vtk_file, "r") as f:

#             lines = f.readlines()

#         points_start = None
#         n_points = 0

#         for i, line in enumerate(lines):

#             if line.startswith("POINTS"):

#                 parts = line.split()

#                 n_points = int(parts[1])

#                 points_start = i + 1

#                 break

#         if points_start is None:

#             raise RuntimeError(
#                 f"POINTS section not found:\n{vtk_file}"
#             )

#         for line in lines[
#             points_start :
#             points_start + n_points
#         ]:

#             parts = line.split()

#             if len(parts) != 3:
#                 continue

#             xcoord = float(parts[0])

#             ycoord = float(parts[1])

#             zcoord = float(parts[2])

#             x.append(xcoord)

#             y.append(ycoord)

#             z.append(zcoord)

#         cleaned_data = list(
#             zip(x, y, z)
#         )

#         cleaned_data.sort(
#             key=lambda p: (
#                 p[1],
#                 p[0]
#             )
#         )

#         with open(output_file, "w") as f:

#             f.write("# x y z\n")

#             for xcoord, ycoord, zcoord in cleaned_data:

#                 f.write(
#                     f"{xcoord:.6f} "
#                     f"{ycoord:.6f} "
#                     f"{zcoord:.15f}\n"
#                 )

#         print(
#             f"\nInitial Landlab topography extracted:\n"
#             f"{output_file}"
#         )

#         return output_file

#     # ========================================================
#     # EXTRACT CROSS SECTION
#     # ========================================================

#     def extract_cross_section(
#         self,
#         x,
#         y,
#         z,
#         x_section
#     ):

#         unique_x = np.unique(x)

#         nearest_x = unique_x[
#             np.argmin(
#                 np.abs(unique_x - x_section)
#             )
#         ]

#         mask = np.isclose(
#             x,
#             nearest_x
#         )

#         y_section = y[mask]

#         z_section = z[mask]

#         sort_index = np.argsort(y_section)

#         return (
#             nearest_x,
#             y_section[sort_index],
#             z_section[sort_index]
#         )

#     # ========================================================
#     # PLOT INITIAL CROSS SECTION
#     # ========================================================

#     def plot_initial_cross_section(self):

#         benchmark = self.benchmark

#         # ----------------------------------------------------
#         # FILES
#         # ----------------------------------------------------

#         reference_file = os.path.join(
#             benchmark.results_folder,
#             "z_initial_reference.txt"
#         )

#         landlab_file = (
#             self.extract_initial_landlab_topography()
#         )

#         aspect_file = (
#             self.extract_initial_aspect_topography()
#         )

#         # ----------------------------------------------------
#         # LOAD DATA
#         # ----------------------------------------------------

#         x_ref, y_ref, z_ref = (
#             benchmark.load_xyz(reference_file)
#         )

#         x_l, y_l, z_l = (
#             benchmark.load_xyz(landlab_file)
#         )

#         x_a, y_a, z_a = (
#             benchmark.load_xyz(aspect_file)
#         )

#         # ----------------------------------------------------
#         # GRID
#         # ----------------------------------------------------

#         nx = len(np.unique(x_ref))

#         ny = len(np.unique(y_ref))

#         reference_2d = z_ref.reshape(
#             ny,
#             nx
#         )

#         # ----------------------------------------------------
#         # CROSS SECTION LOCATION
#         # ----------------------------------------------------

#         xmin = np.min(x_ref)

#         xmax = np.max(x_ref)

#         ymin = np.min(y_ref)

#         ymax = np.max(y_ref)

#         # x_middle = 0.5 * (xmin + xmax)
#         x_middle = 700

#         # ----------------------------------------------------
#         # EXTRACT CROSS SECTIONS
#         # ----------------------------------------------------

#         xline, y_ref_sec, z_ref_sec = (
#             self.extract_cross_section(
#                 x_ref,
#                 y_ref,
#                 z_ref,
#                 x_middle
#             )
#         )

#         _, y_l_sec, z_l_sec = (
#             self.extract_cross_section(
#                 x_l,
#                 y_l,
#                 z_l,
#                 x_middle
#             )
#         )

#         _, y_a_sec, z_a_sec = (
#             self.extract_cross_section(
#                 x_a,
#                 y_a,
#                 z_a,
#                 x_middle
#             )
#         )

#         # ====================================================
#         # FIGURE
#         # ====================================================

#         fig, axes = plt.subplots(
#             1,
#             2,
#             figsize=(16, 7),
#             constrained_layout=True
#         )

#         # fig.suptitle(
#         #     f"{benchmark.case_name}\nInitial Cross Section Analysis",
#         #     fontsize=18,
#         #     fontweight="bold"
#         # )

#         formatted_case_name = benchmark.format_long_title(
#             benchmark.case_name,
#             max_line_length=60
#         )

#         fig.suptitle(
#             f"{formatted_case_name}\nInitial Cross Section Analysis",
#             fontsize=18,
#             fontweight="bold"
#         )

#         # ====================================================
#         # LEFT PANEL
#         # ====================================================

#         ax0 = axes[0]

#         im = ax0.imshow(
#             reference_2d,
#             origin="lower",
#             extent=[
#                 xmin,
#                 xmax,
#                 ymin,
#                 ymax
#             ],
#             cmap="terrain",
#             aspect="auto"
#         )

#         ax0.plot(
#             [xline, xline],
#             [ymin, ymax],
#             color="red",
#             linewidth=3,
#             linestyle="--",
#             label="Cross Section"
#         )

#         ax0.set_title(
#             "Initial Reference Topography\nwith Cross Section Line",
#             fontsize=15,
#             fontweight="bold"
#         )

#         ax0.set_xlabel("X Coordinate")

#         ax0.set_ylabel("Y Coordinate")

#         ax0.legend()

#         cbar = fig.colorbar(
#             im,
#             ax=ax0,
#             shrink=0.85
#         )

#         cbar.set_label("Elevation")

#         # ====================================================
#         # RIGHT PANEL
#         # ====================================================

#         ax1 = axes[1]

#         ax1.plot(
#             y_ref_sec,
#             z_ref_sec,
#             color="red",
#             linewidth=4,
            
#             label="Initial Standalone Landlab"
#         )

#         ax1.plot(
#             y_l_sec,
#             z_l_sec,
#             color="blue",
#             linestyle="--",
#             marker="o",
#             markersize=10,
#             linewidth=2.5,
#             label="Initial Coupled Landlab"
#         )

#         ax1.plot(
#             y_a_sec,
#             z_a_sec,
#             color="green",
#             linestyle=":",
#             marker="^",
#             markersize=10,
#             linewidth=2.5,
#             label="Initial ASPECT Topo"
#         )

#         ax1.set_title(
#             f"Initial Cross Section at x = {xline:.2f}",
#             fontsize=15,
#             fontweight="bold"
#         )

#         ax1.set_xlabel("Y Coordinate")

#         ax1.set_ylabel("Elevation")

#         ax1.grid(
#             True,
#             linestyle="--",
#             alpha=0.4
#         )

#         ax1.legend()

#         # ====================================================
#         # SAVE
#         # ====================================================

#         figure_file = os.path.join(
#             benchmark.results_folder,
#             "initial_cross_section_comparison.png"
#         )

#         plt.savefig(
#             figure_file,
#             dpi=300,
#             bbox_inches="tight"
#         )

#         plt.close()

#         print(
#             f"\nInitial cross-section figure written:\n"
#             f"{figure_file}"
#         )

  