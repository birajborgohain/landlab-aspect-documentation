from mpi4py import MPI
import importlib.util
import os
import sys
import numpy as np
import landlab
from landlab.components import LinearDiffuser, AdvectionSolverTVD

# ===================== ADDED =====================
import json
from landlab.io.legacy_vtk import write_legacy_vtk
# ================================================



# aspect_root = os.path.dirname(os.path.abspath(__file__))

# scripts_path = os.path.join(
#     aspect_root,
#     "contrib",
#     "python",
#     "scripts"
# )

# sys.path.append(scripts_path)

from landlab_template import LandLabTemplate


class MyAspectLandlabModel(LandLabTemplate):

    # def __init__(self):
    #     super().__init__()

    #     # Empty "Lanlab_output" created, so now disabled, a mdofication is proposed 
    #     # which is included in landlab_template.py in `def writeout()`
    #     # section.

    #     self.output_dir = "landlab_outputs"
    #     os.makedirs(self.output_dir, exist_ok=True)

    #     self.vtk_files = []

    def update_until(self, end_time, ASPECT_dim, ASPECT_fields_at_Landlab_nodes_dict):

        dt = end_time - self.current_time
        self.timestep += 1

        deposition_erosion = np.zeros(self.model_grid.number_of_nodes)

        # # =====================================================
        # # VELOCITY FROM ASPECT (TEMPLATE FUNCTIONS)
        # # =====================================================
        # vertical_velocity = self.determine_uplift_velocity(
        #     ASPECT_dim,
        #     ASPECT_fields_at_Landlab_nodes_dict
        # )

        # self.horizontal_velocity = self.determine_horizontal_velocity(
        #     ASPECT_dim,
        #     ASPECT_fields_at_Landlab_nodes_dict
        # )

        # self.horizontal_surface_advector = AdvectionSolverTVD(
        #     self.model_grid,
        #     fields_to_advect=self.elevation
        # )

        # =====================================================
        # COMPOSITION BLOCK (KEPT BUT DISABLED)
        # =====================================================
        # slice_weak_composition   = ASPECT_fields_at_Landlab_nodes_dict["weak"]
        # slice_strong_composition = ASPECT_fields_at_Landlab_nodes_dict["strong"]
        #
        # strong_composition = np.zeros(self.model_grid.number_of_nodes)
        # weak_composition   = np.zeros(self.model_grid.number_of_nodes)
        #
        # unique_x_values = np.unique(self.model_grid.x_of_node)
        # for x in unique_x_values:
        #     strong_composition[self.model_grid.x_of_node == x] = slice_strong_composition[unique_x_values == x]
        #     weak_composition[self.model_grid.x_of_node == x]   = slice_weak_composition[unique_x_values == x]
        #
        # self.Diffusivity[strong_composition >= 0.5] = 1e-10 / self.s2yr
        # self.Diffusivity[weak_composition >= 0.5]   = 10 / self.s2yr
        # =====================================================

        # =====================================================
        # TIME STEPPING
        # =====================================================
        if dt > 0:
            n_substeps = 2
            sub_dt = dt / n_substeps

            for _ in range(n_substeps):
                elevation_before = self.elevation.copy()

                # Diffusion (Landlab physics)
                self.linear_diffuser.run_one_step(sub_dt)

                # # Vertical uplift (ASPECT z-velocity)
                # self.elevation += vertical_velocity * sub_dt

                # #REPLACE ASPECT UPLIFT WITH YOUR LANDLAB UPLIFT
                # self.elevation += (self.uplift_rate * sub_dt)

                # self.elevation[self.model_grid.core_nodes] += (
                #     self.uplift_rate[self.model_grid.core_nodes]
                #     * sub_dt
                # )

                # # Horizontal advection (REQUIRED for 3D)
                # self.horizontal_surface_advector.run_one_step(sub_dt)

                deposition_erosion += self.elevation - elevation_before

        self.current_time = end_time

        


# =========================
        # WRITE VTK + SERIES (FINAL)
        # =========================
        import os
        import json
        from landlab.io.legacy_vtk import write_legacy_vtk

        # -------------------------------------------------
        # FIND ASPECT OUTPUT DIRECTORY (same as your working code)
        # -------------------------------------------------
        cwd = os.getcwd()
        outputs_root = os.path.join(cwd, "outputs")

        subdirs = [
            os.path.join(outputs_root, d)
            for d in os.listdir(outputs_root)
            if os.path.isdir(os.path.join(outputs_root, d))
            and not d.lower().startswith("landlab")
            and not d.lower().startswith("default")
        ]

        subdirs.sort(key=os.path.getmtime, reverse=True)
        base_output_dir = subdirs[0]

        output_directory = os.path.join(base_output_dir, "landlab")
        os.makedirs(output_directory, exist_ok=True)

        # -------------------------------------------------
        # ATTACH DATA
        # -------------------------------------------------
        self.model_grid.at_node["topographic__elevation"] = self.elevation

        # -------------------------------------------------
        # WRITE VTK
        # -------------------------------------------------
        filename = f"landlab_{self.timestep:04d}.vtk"
        filepath = os.path.join(output_directory, filename)

        print(f"[Landlab] Writing VTK: {filepath}")

        write_legacy_vtk(
            path=filepath,
            grid=self.model_grid,
            clobber=True
        )

        # -------------------------------------------------
        # TRACK FILES (IMPORTANT)
        # -------------------------------------------------
        if not hasattr(self, "_vtk_files"):
            self._vtk_files = []

        self._vtk_files.append((float(self.current_time), filename))

        # -------------------------------------------------
        # WRITE SERIES FILE (THIS IS THE KEY FIX)
        # -------------------------------------------------
        series_path = os.path.join(output_directory, "landlab.vtk.series")

        with open(series_path, "w") as f:
            json.dump({
                "file-series-version": "1.0",
                "files": [
                    {"name": fname, "time": t}
                    for t, fname in self._vtk_files
                ],
            }, f, indent=2)

        print(f"[Landlab] Updated series: {series_path}")

#========================
        print("Max elevation:", np.max(self.elevation),
              "Min elevation:", np.min(self.elevation))

        dimensional_deposition_erosion = self.dimensional_deposition_erosion(
            ASPECT_dim,
            deposition_erosion
        )

        # # =====================================================
        # # SIMPLE DIRECT OUTPUT
        # # =====================================================

        # output_directory = "landlab_outputs"

        # os.makedirs(output_directory, exist_ok=True)

        # filename = os.path.join(
        #     output_directory,
        #     f"landlab_{self.timestep:04d}.vtk"
        # )

        # print(f"[Landlab] Writing {filename}")

        # self.model_grid.at_node[
        #     "topographic__elevation"
        # ] = self.elevation

        # write_legacy_vtk(
        #     path=filename,
        #     grid=self.model_grid,
        #     clobber=True
        # )

        return dimensional_deposition_erosion

    # def write_output(self, postprocess_dictionary):
    #     """
    #     Write output for visualizing the landlab mesh. This calls a function in the Landlab Python module to write output vtk files. 
    #     This function is called at the end of each ASPECT timestep after the ASPECT model has been updated and the topography has been evolved.

    #     Parameters:
    #     - postprocess_dictionary: a dictionary containing information about the current ASPECT timestep, time, and output directory.
    #     """
    #     step = postprocess_dictionary["ASPECT timestep"]
    #     time = postprocess_dictionary["ASPECT time"]
    #     output_directory = postprocess_dictionary["ASPECT output directory"]


    #     # #=====================================================
    #     # # FIXED OUTPUT DIRECTORY HANDLING
    #     # # =====================================================
    #     # output_directory = postprocess_dictionary["ASPECT output directory"]

    #     # if not os.path.isabs(output_directory):
    #     #     output_directory = os.path.abspath(output_directory)

    #     # os.makedirs(output_directory, exist_ok=True)
    #     # # =====================================================

    #     output_frequency = 1
    #     if step % output_frequency != 0:
    #         return

    #     filename = f"{output_directory}/landlab_{str(step).zfill(3)}.vtk"
    #     write_legacy_vtk(path=filename, grid=self.model_grid, clobber=True)
    #     self.vtks.append((time, filename))

    #     with open(f"{output_directory}/landlab.vtk.series", "w") as f:
    #         series = {
    #             "file-series-version": "1.0",
    #             "files": [
    #                 {"name": os.path.basename(vtk_name), "time": vtk_time}
    #                 for vtk_time, vtk_name in self.vtks
    #             ],
    #         }
    #         json.dump(series, f, indent=2)

    #     pass
   

    def set_mesh_information(self, grid_dictionary):
        if self.model_grid is not None:
            return

        print("* Creating RasterModelGrid ...")

        # =====================================================
        # FIXED DOMAIN (MATCH ASPECT 3D TOP SURFACE)
        # =====================================================
        x_extent = 900
        y_extent = 1900
        spacing  = 100

        nrows = int(y_extent / spacing) + 1
        ncols = int(x_extent / spacing) + 1

        self.model_grid = landlab.RasterModelGrid(
            (nrows, ncols),
            xy_spacing=(spacing, spacing),
            # xy_of_lower_left=(0, -y_extent / 2),
            # as Landlab domain goes half away from ASPECT domain
            xy_of_lower_left=(0, 0),
        )

        print("* Creating topographic elevation ...")

        # # =====================================================
        # # FLAT SURFACE INITIALIZATION
        # # =====================================================
        # self.elevation = self.model_grid.add_zeros(
        #     "topographic__elevation",
        #     at="node"
        # )

        # self.horizontal_velocity = self.model_grid.add_zeros(
        #     "advection__velocity",
        #     at="link"
        # )

        # =====================================================
        # INITIAL TOPOGRAPHY
        # =====================================================

        init_elev = 0.0

        self.elevation = self.model_grid.add_zeros(
            "topographic__elevation",
            at="node"
        )

        z = self.model_grid.zeros(at="node") + init_elev

        np.random.seed(0)

        self.elevation[:] = (
            z + np.random.rand(len(z)) / 1000.0
        )

        # =====================================================
        # CUSTOM UPLIFT FIELD
        # =====================================================

        # self.uplift_rate = (
        #     self.model_grid.y_of_node
        #     / 1e6
        # )
        # Note: original bechmark in Landlab used mg.node_y[mg.core_cells]


        # =====================================================
        # TRIANGULAR MOUNTAIN (KEPT BUT DISABLED)
        # =====================================================
        # topo_height  = 20e3
        # left_x_arr   = np.array([25e3, 50e3])
        # left_y_arr   = np.array([0.0, topo_height])
        # right_x_arr  = np.array([50e3, 75e3])
        # right_y_arr  = np.array([topo_height, 0.0])
        #
        # left_m,  left_b  = np.polyfit(left_x_arr,  left_y_arr,  deg=1)
        # right_m, right_b = np.polyfit(right_x_arr, right_y_arr, deg=1)
        #
        # self.elevation[self.model_grid.x_of_node <= 50e3] = (
        #     left_m * self.model_grid.x_of_node[self.model_grid.x_of_node <= 50e3] + left_b
        # )
        # self.elevation[self.model_grid.x_of_node > 50e3] = (
        #     right_m * self.model_grid.x_of_node[self.model_grid.x_of_node > 50e3] + right_b
        # )
        # self.elevation[self.model_grid.x_of_node < np.min(left_x_arr)]  = 0.0
        # self.elevation[self.model_grid.x_of_node > np.max(right_x_arr)] = 0.0
        # =====================================================

        self.model_grid.set_closed_boundaries_at_grid_edges(
            right_is_closed=True,
            left_is_closed=True,
            top_is_closed=True,
            bottom_is_closed=True,
        )

        # self.model_grid.set_fixed_value_boundaries_at_grid_edges(
        #     right_is_fixed_val=True,
        #     left_is_fixed_val=True,
        #     top_is_fixed_val=True,
        #     bottom_is_fixed_val=True,
        # )

        print("\tnumber of nodes:", self.model_grid.number_of_nodes)

        self.initialize_landlab_components()
        print("* Done")

        return self.model_grid

    def initialize_landlab_components(self):
        D = 0/self.s2yr

        self.Diffusivity = self.model_grid.add_zeros(
            "linear_diffusivity",
            at="node"
        )

        self.Diffusivity += D

        self.linear_diffuser = LinearDiffuser(
            self.model_grid,
            linear_diffusivity=self.Diffusivity
        )


# =====================================================
# EXPORT TO ASPECT
# =====================================================
model = MyAspectLandlabModel()
model.export_aspect_callbacks(model, globals())