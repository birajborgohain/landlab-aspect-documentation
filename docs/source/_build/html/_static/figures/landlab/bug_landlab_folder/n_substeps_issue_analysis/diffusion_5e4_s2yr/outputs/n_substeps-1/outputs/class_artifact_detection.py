# ============================================================
# FILE: class_artifact_detection.py
# ============================================================

import os
import glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.spatial import cKDTree


class ArtifactDetection:

    def __init__(self, base_output_dir, case_name):

        self.base_output_dir = base_output_dir

        self.case_name = case_name

        # =====================================================
        # CASE DIRECTORIES
        # =====================================================

        self.case_dir = os.path.join(
            self.base_output_dir,
            self.case_name
        )

        self.landlab_dir = os.path.join(
            self.case_dir,
            "landlab"
        )

        self.aspect_dir = os.path.join(
            self.case_dir,
            "topography"
        )

        self.results_dir = os.path.join(
            self.case_dir,
            "results_artifact"
        )

        os.makedirs(
            self.results_dir,
            exist_ok=True
        )

        # =====================================================
        # AUTO DETECT FILES
        # =====================================================

        self.landlab_file = self.find_first_landlab_file()

        self.aspect_file = self.find_first_aspect_file()

        # =====================================================
        # SETTINGS
        # =====================================================

        self.SEAM_THRESHOLD = 0.003

        self.SEARCH_RADIUS = 150

        self.TARGET_Y = 1000

        self.Y_TOL = 60

    # =========================================================
    # FIND FIRST LANDLAB FILE
    # =========================================================

    def find_first_landlab_file(self):

        files = sorted(
            glob.glob(
                os.path.join(
                    self.landlab_dir,
                    "landlab_*.vtk"
                )
            )
        )

        if len(files)  < 2:

            raise FileNotFoundError(
                f"\nNo Landlab vtk file found in:\n{self.landlab_dir}"
            )

        return files[1]

    # =========================================================
    # FIND FIRST ASPECT FILE
    # =========================================================

    def find_first_aspect_file(self):

        files = sorted(
            glob.glob(
                os.path.join(
                    self.aspect_dir,
                    "topography.*"
                )
            )
        )

        if len(files)  < 2:

            raise FileNotFoundError(
                f"\nNo ASPECT topography file found in:\n{self.aspect_dir}"
            )

        return files[1]

    # =========================================================
    # READ LANDLAB VTK
    # =========================================================

    def read_landlab_vtk(self):

        with open(self.landlab_file, "r") as f:

            lines = f.readlines()

        # =====================================================
        # READ POINTS
        # =====================================================

        point_start = None

        n_points = None

        for i, line in enumerate(lines):

            if line.startswith("POINTS"):

                point_start = i + 1

                n_points = int(
                    line.split()[1]
                )

                break

        if point_start is None:

            raise RuntimeError(
                "POINTS section not found"
            )

        points = []

        for line in lines[point_start:]:

            if line.startswith("CELLS"):

                break

            vals = line.strip().split()

            if len(vals) == 3:

                x, y, z = map(float, vals)

                points.append([x, y])

        points = np.array(points)

        # =====================================================
        # READ TOPOGRAPHIC ELEVATION
        # =====================================================

        topo_start = None

        for i, line in enumerate(lines):

            if (
                "SCALARS topographic__elevation"
                in line
            ):

                topo_start = i + 2

                break

        if topo_start is None:

            raise RuntimeError(
                "topographic__elevation not found"
            )

        topo = []

        for line in lines[topo_start:]:

            line = line.strip()

            if len(line) == 0:

                continue

            if line.startswith("SCALARS"):

                break

            topo.append(float(line))

            if len(topo) == n_points:

                break

        topo = np.array(topo)

        # =====================================================
        # DATAFRAME
        # =====================================================

        df = pd.DataFrame({
            "x": points[:, 0],
            "y": points[:, 1],
            "topo": topo
        })

        return df

    # =========================================================
    # READ ASPECT TOPOGRAPHY FILE
    # =========================================================

    def read_aspect_data(self):

        data = []

        with open(self.aspect_file, "r") as f:

            for line in f:

                line = line.strip()

                if (
                    len(line) == 0
                    or line.startswith("#")
                ):
                    continue

                vals = line.split()

                # =============================================
                # FORMAT:
                #
                # x y z topo
                #
                # topo is column 4
                # =============================================

                if len(vals) >= 4:

                    x = float(vals[0])

                    y = float(vals[1])

                    topo = float(vals[3])

                    data.append([
                        x,
                        y,
                        topo
                    ])

        df = pd.DataFrame(
            data,
            columns=[
                "x",
                "y",
                "topo"
            ]
        )

        return df

    # =========================================================
    # RUN ANALYSIS
    # =========================================================

    def run_analysis(self):

        print("\n================================================")
        print("LOADING DATA")
        print("================================================")

        landlab = self.read_landlab_vtk()

        aspect = self.read_aspect_data()

        print(
            "Landlab nodes :",
            len(landlab)
        )

        print(
            "ASPECT nodes  :",
            len(aspect)
        )

        # =====================================================
        # KD TREE
        # =====================================================

        landlab_points = np.column_stack(
            [
                landlab["x"],
                landlab["y"]
            ]
        )

        kdtree = cKDTree(
            landlab_points
        )

        aspect_points = np.column_stack(
            [
                aspect["x"],
                aspect["y"]
            ]
        )

        distances, indices = kdtree.query(
            aspect_points
        )

        aspect["nearest_distance"] = distances

        aspect["donor_x"] = (
            landlab.iloc[indices]["x"].values
        )

        aspect["donor_y"] = (
            landlab.iloc[indices]["y"].values
        )

        aspect["donor_topo"] = (
            landlab.iloc[indices]["topo"].values
        )

        # =====================================================
        # DIFFERENCE
        # =====================================================

        aspect["difference"] = (
            aspect["topo"]
            -
            aspect["donor_topo"]
        )

        # =====================================================
        # ZERO COLLAPSE NODES
        # =====================================================

        problem_nodes = aspect[
            (
                np.abs(aspect["topo"]) < 1e-12
            )
            &
            (
                np.abs(aspect["donor_topo"]) > 1e-6
            )
        ]

        # =====================================================
        # CROSS SECTION
        # =====================================================

        landlab_cross = landlab[
            np.abs(
                landlab["y"]
                -
                self.TARGET_Y
            ) < self.Y_TOL
        ].sort_values("x")

        aspect_cross = aspect[
            np.abs(
                aspect["y"]
                -
                self.TARGET_Y
            ) < self.Y_TOL
        ].sort_values("x")

        # =====================================================
        # SEAM DETECTION
        # =====================================================

        aspect_cross = aspect_cross.copy()

        aspect_cross["dz"] = np.abs(
            np.diff(
                aspect_cross["topo"],
                prepend=aspect_cross[
                    "topo"
                ].iloc[0]
            )
        )

        seams = aspect_cross[
            aspect_cross["dz"]
            >
            self.SEAM_THRESHOLD
        ]
        # =====================================================
        # REPEATED SEAM X POSITIONS
        # =====================================================

        rounded_x = np.round(
            seams["x"],
            6
        )

        counts = rounded_x.value_counts()

        # =====================================================
        # LARGE DISTANCE NODES
        # =====================================================

        large_distance = aspect[
            aspect["nearest_distance"]
            >
            self.SEARCH_RADIUS
        ]

        # =====================================================
        # INTERPRETATION TEXT
        # =====================================================

        interpretation = []

        interpretation.append(
            "FINAL INTERPRETATION"
        )

        interpretation.append("=" * 60)

        interpretation.append("")

        interpretation.append(
            f"CASE : {self.case_name}"
        )

        interpretation.append("")

        interpretation.append(
            f"Landlab file : "
            f"{os.path.basename(self.landlab_file)}"
        )

        interpretation.append(
            f"ASPECT file  : "
            f"{os.path.basename(self.aspect_file)}"
        )

        interpretation.append("")

        interpretation.append(
            f"Detected seams : {len(seams)}"
        )

        interpretation.append(
            f"Zero collapse nodes : "
            f"{len(problem_nodes)}"
        )

        interpretation.append(
            f"Large distance nodes : "
            f"{len(large_distance)}"
        )

        interpretation.append("")

        if len(problem_nodes) > 0:

            interpretation.append(
                "Detected nodes where ASPECT"
            )

            interpretation.append(
                "topography became zero while"
            )

            interpretation.append(
                "Landlab donor remained non-zero."
            )

            interpretation.append("")

            interpretation.append(
                "This strongly suggests"
            )

            interpretation.append(
                "interpolation or transfer failure."
            )

            interpretation.append("")

        if len(seams) > 0:

            interpretation.append(
                "Large topographic jumps detected."
            )

            interpretation.append("")

            interpretation.append(
                "Possible causes:"
            )

            interpretation.append(
                "- MPI partition seams"
            )

            interpretation.append(
                "- non-nested interpolation"
            )

            interpretation.append(
                "- transfer strip mismatch"
            )

            interpretation.append(
                "- donor ownership discontinuity"
            )

            interpretation.append("")

        if len(large_distance) > 0:

            interpretation.append(
                "Some ASPECT nodes are far from"
            )

            interpretation.append(
                "their nearest Landlab donor."
            )

            interpretation.append("")

            interpretation.append(
                "This may produce unstable"
            )

            interpretation.append(
                "interpolation behavior."
            )

            interpretation.append("")

        interpretation.append(
            "If seams repeat spatially,"
        )

        interpretation.append(
            "the artifact is likely numerical"
        )

        interpretation.append(
            "rather than physical."
        )

        interpretation_text = "\n".join(
            interpretation
        )

                # =====================================================
        # COMBINED FIGURE
        # =====================================================

        fig = plt.figure(
            figsize=(16, 26)
        )

        gs = fig.add_gridspec(
            4,
            1,
            height_ratios=[1.5, 1, 1, 0.9]
        )

        # =====================================================
        # FIGURE 1
        # NODE STRUCTURE
        # =====================================================

        ax1 = fig.add_subplot(gs[0])

        ax1.scatter(
            landlab["x"],
            landlab["y"],
            s=220,
            marker='s',
            label='Landlab nodes'
        )

        ax1.scatter(
            aspect["x"],
            aspect["y"],
            s=30,
            marker='o',
            label='ASPECT nodes'
        )

        for _, row in problem_nodes.iterrows():

            ax1.plot(
                [row["x"], row["donor_x"]],
                [row["y"], row["donor_y"]],
                color='gray',
                alpha=0.3
            )

        ax1.scatter(
            problem_nodes["x"],
            problem_nodes["y"],
            s=180,
            color='red',
            marker='x',
            label='seam/zero nodes'
        )
        
        # =====================================================
        # CROSS-SECTION LOCATION
        # =====================================================

        ax1.axhline(
            self.TARGET_Y,
            color='red',
            linestyle='--',
            linewidth=4,
            label=f'cross section y = {self.TARGET_Y}'
        )

        # ax1.fill_between(
        #     [
        #         landlab["x"].min(),
        #         landlab["x"].max()
        #     ],
        #     self.TARGET_Y - self.Y_TOL,
        #     self.TARGET_Y + self.Y_TOL,
        #     color='red',
        #     alpha=0.12
        # )

        # ax1.set_title(
        #     "Landlab ↔ ASPECT Node Structure",
        #     fontsize=16
        # )

        ax1.set_xlabel(
            "x",
            fontsize=28
        )

        ax1.set_ylabel(
            "y",
            fontsize=28
        )

        ax1.tick_params(
            axis='both',
            labelsize=26
        )

        legend = ax1.legend(
            fontsize=24,
            frameon=True
        )

        legend.get_frame().set_facecolor(
            'white'
        )

        legend.get_frame().set_alpha(
            1.0
        )

        legend.get_frame().set_edgecolor(
            'black'
        )

       

        ax1.grid(alpha=0.3)

        # # =====================================================
        # # FIGURE 2
        # # CROSS SECTION
        # # =====================================================

        # ax2 = fig.add_subplot(gs[1])

        # ax2.plot(
        #     landlab_cross["x"],
        #     landlab_cross["topo"],
        #     '-s',
        #     linewidth=3,
        #     label='Landlab'
        # )

        # ax2.plot(
        #     aspect_cross["x"],
        #     aspect_cross["topo"],
        #     '-o',
        #     linewidth=2,
        #     label='ASPECT transfer'
        # )

        # for _, row in seams.iterrows():

        #     ax2.axvline(
        #         row["x"],
        #         color='red',
        #         linestyle='--',
        #         alpha=0.5
        #     )

        # ax2.set_title(
        #     f"Cross section near y = {self.TARGET_Y}",
        #     fontsize=16
        # )

        # ax2.set_xlabel("x")

        # ax2.set_ylabel("topography")

        # ax2.legend()

        # ax2.grid(alpha=0.3)

                # =====================================================
        # FIGURE 2
        # CROSS SECTION
        # =====================================================

        ax2 = fig.add_subplot(gs[1])

        ax2.plot(
            landlab_cross["x"].values,
            landlab_cross["topo"].values,
            '-s',
            linewidth=3,
            markersize=8,
            label='Landlab'
        )

        ax2.plot(
            aspect_cross["x"].values,
            aspect_cross["topo"].values,
            '-o',
            linewidth=2,
            markersize=5,
            label='ASPECT transfer'
        )

        for _, row in seams.iterrows():

            ax2.axvline(
                row["x"],
                color='red',
                linestyle='--',
                linewidth=1.5,
                alpha=0.5
            )

        ax2.set_title(
            f"Cross section near y = {self.TARGET_Y}",
            fontsize=26
        )

        ax2.set_xlabel(
            "x",
            fontsize=26,
            fontweight='bold'
        )

        ax2.set_ylabel(
            "y",
            fontsize=26,
            fontweight='bold'
        )

        ax2.tick_params(
            axis='both',
            labelsize=22
        )

        legend2 = ax2.legend(
            fontsize=22,
            frameon=True
        )

        legend2.get_frame().set_facecolor(
            'white'
        )

        legend2.get_frame().set_alpha(
            1.0
        )

        legend2.get_frame().set_edgecolor(
            'black'
        )

        ax2.grid(
            alpha=0.3
        )

        # # =====================================================
        # # FIGURE 3
        # # TOPOGRAPHY DIFFERENCE
        # # =====================================================

        # ax3 = fig.add_subplot(gs[2])

        # scatter = ax3.scatter(
        #     aspect["x"],
        #     aspect["difference"],
        #     c=aspect["nearest_distance"],
        #     s=25
        # )

        # cbar = plt.colorbar(
        #     scatter,
        #     ax=ax3
        # )

        # cbar.set_label(
        #     'distance to nearest Landlab donor'
        # )

        # ax3.axhline(
        #     0,
        #     color='black',
        #     linestyle='--'
        # )

        # ax3.set_title(
        #     "ASPECT - Landlab donor difference",
        #     fontsize=16
        # )

        # ax3.set_xlabel("x")

        # ax3.set_ylabel("difference")

        # ax3.grid(alpha=0.3)

        # # =====================================================
        # # FIGURE 3
        # # TOPOGRAPHY DIFFERENCE
        # # =====================================================

        # ax3 = fig.add_subplot(gs[2])

        # sc = ax3.scatter(
        #     aspect["x"].values,
        #     aspect["difference"].values,
        #     s=80,
        #     c=aspect["nearest_distance"].values,
        #     cmap='turbo',
        #     edgecolors='black',
        #     linewidths=0.3,
        #     alpha=0.95
        # )

        # ax3.axhline(
        #     0,
        #     color='black',
        #     linestyle='--',
        #     linewidth=1.5
        # )

        # ax3.set_title(
        #     "ASPECT - Landlab donor difference",
        #     fontsize=20
        # )

        # ax3.set_xlabel(
        #     "x",
        #     fontsize=18
        # )

        # ax3.set_ylabel(
        #     "difference",
        #     fontsize=18
        # )

        # ax3.tick_params(
        #     axis='both',
        #     labelsize=16
        # )

        # ax3.grid(
        #     alpha=0.3
        # )

        #         # =====================================================
        # # HORIZONTAL COLORBAR INSIDE AXIS
        # # =====================================================

        # cax = ax3.inset_axes(
        #     [0.60, 0.82, 0.30, 0.05]
        # )

        # cbar = plt.colorbar(
        #     sc,
        #     cax=cax,
        #     orientation='horizontal'
        # )

        # cbar.set_label(
        #     'distance',
        #     fontsize=14
        # )

        # cbar.ax.tick_params(
        #     labelsize=11
        # )

        
        # =====================================================
        # FIGURE 4
        # INTERPRETATION
        # =====================================================

        ax4 = fig.add_subplot(gs[3])

        ax4.axis("off")

        landlab_name = os.path.basename(
            self.landlab_file
        )

        aspect_name = os.path.basename(
            self.aspect_file
        )

        interpretation_lines = []

        interpretation_lines.append(
            f"Folder name : {self.case_name}"
        )

        interpretation_lines.append("")

        interpretation_lines.append(
            f"Landlab file name : {landlab_name}"
        )

        interpretation_lines.append(
            f"ASPECT file name : {aspect_name}"
        )

        interpretation_lines.append("")

        interpretation_lines.append(
            "=" * 60
        )

        interpretation_lines.append("")

        interpretation_lines.append(
            "FINAL INTERPRETATION"
        )

        interpretation_lines.append(
            "=" * 60
        )

        interpretation_lines.append("")

                # =====================================================
        # INTERPRETATION
        # =====================================================

        artifact_detected = False

        # -----------------------------------------------------
        # ZERO COLLAPSE
        # -----------------------------------------------------

        if len(problem_nodes) > 0:

            artifact_detected = True

            interpretation_lines.append(
                "Detected nodes where ASPECT "
                "topography became zero"
            )

            interpretation_lines.append(
                "while nearby Landlab donor "
                "values remain non-zero."
            )

            interpretation_lines.append("")

            interpretation_lines.append(
                "This strongly indicates "
                "transfer/interpolation failure."
            )

            interpretation_lines.append("")

        # -----------------------------------------------------
        # REPEATED SEAMS
        # -----------------------------------------------------

        if len(counts[counts > 3]) > 0:

            artifact_detected = True

            interpretation_lines.append(
                "Repeated seam positions detected."
            )

            interpretation_lines.append("")

            interpretation_lines.append(
                "This is characteristic of "
                "partition/interface seams"
            )

            interpretation_lines.append(
                "such as MPI boundaries or "
                "transfer-strip boundaries."
            )

            interpretation_lines.append("")

        # -----------------------------------------------------
        # LARGE DISTANCE
        # -----------------------------------------------------

        if len(large_distance) > 0:

            artifact_detected = True

            interpretation_lines.append(
                "Large interpolation distances detected."
            )

            interpretation_lines.append("")

            interpretation_lines.append(
                "Some ASPECT nodes are too far "
                "from valid Landlab donors."
            )

            interpretation_lines.append("")

            interpretation_lines.append(
                "This can create unstable "
                "interpolation or undefined values."
            )

            interpretation_lines.append("")

                # -----------------------------------------------------
        # NO ARTIFACT
        # -----------------------------------------------------

        if artifact_detected is False:

            interpretation_lines.append(
                "No numerical artifact detected."
            )

            interpretation_lines.append("")

            interpretation_lines.append(
                "No strong seam, interpolation failure,"
            )

            interpretation_lines.append(
                "or donor discontinuity was identified."
            )

            interpretation_lines.append("")

            interpretation_lines.append(
                "Landlab ↔ ASPECT transfer appears stable"
            )

            interpretation_lines.append(
                "for this timestep."
            )

         # NODE CORRESPONDENCE
        # =====================================================

        interpretation_lines.append(
            "Landlab ↔ ASPECT x-node correspondence"
        )

        interpretation_lines.append(
            "-" * 80
        )

        interpretation_lines.append("")

        sample_landlab_x = [
            0,
            100,
            200,
            300,
            400,
            500,
            600,
            700,
            800
        ]

        landlab_row = []

        aspect_row = []

        all_aspect_row = []

        for target_x in sample_landlab_x:

            nearest_landlab = landlab.iloc[
                (
                    landlab["x"] - target_x
                ).abs().argsort()[:1]
            ]

            ll_x = nearest_landlab["x"].values[0]

            ll_y = nearest_landlab["y"].values[0]

            aspect_distance = np.sqrt(
                (aspect["x"] - ll_x)**2
                +
                (aspect["y"] - ll_y)**2
            )

            nearest_aspect = aspect.iloc[
                aspect_distance.argsort()[:1]
            ]

            asp_x = nearest_aspect["x"].values[0]

            landlab_row.append(
                f"{ll_x:.0f}"
            )

            aspect_row.append(
                f"{asp_x:.1f}"
            )

        all_aspect_x = np.sort(
            aspect["x"].unique()
        )

        for val in all_aspect_x:

            all_aspect_row.append(
                f"{val:.1f}"
            )

        interpretation_lines.append(
            "Landlab x : "
            + "   ".join(landlab_row)
        )

        interpretation_lines.append("")

        interpretation_lines.append(
            "Mapped ASPECT x : "
            + "   ".join(aspect_row)
        )

        interpretation_lines.append("")

        # =====================================================
        # WRAP ALL ASPECT X VALUES
        # =====================================================

        chunk_size = 15

        interpretation_lines.append(
            "All ASPECT x : "
        )

        interpretation_lines.append("")

        for i in range(
            0,
            len(all_aspect_row),
            chunk_size
        ):

            chunk = all_aspect_row[
                i:i + chunk_size
            ]

            interpretation_lines.append(
                "   ".join(chunk)
            )

        interpretation_lines.append("")

        interpretation_lines.append("")

        interpretation_lines.append(
            "=" * 80
        )

 
        # =====================================================
        # CONVERT TO TEXT
        # =====================================================

        interpretation_text = "\n".join(
            interpretation_lines
        )

        # =====================================================
        # DRAW INTERPRETATION
        # =====================================================

        ax4.text(
            0.01,
            0.98,
            interpretation_text,
            va="top",
            ha="left",
            fontsize=11,
            family="monospace"
        )

        
        # =====================================================
        # FINAL LAYOUT
        # =====================================================

                # =====================================================
        # MAIN TITLE
        # =====================================================

        fig.suptitle(
            "Artifact Detection Report",
            fontsize=22,
            y=1
        )

        

        plt.tight_layout()

        # =====================================================
        # SAVE
        # =====================================================

        output_file = os.path.join(
            self.results_dir,
            "artifact_grid_points_cross_section_difference.png"
        )

        plt.savefig(
            output_file,
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print("\n================================================")
        print("ARTIFACT REPORT SAVED")
        print("================================================")

        print(output_file)

        print("================================================")