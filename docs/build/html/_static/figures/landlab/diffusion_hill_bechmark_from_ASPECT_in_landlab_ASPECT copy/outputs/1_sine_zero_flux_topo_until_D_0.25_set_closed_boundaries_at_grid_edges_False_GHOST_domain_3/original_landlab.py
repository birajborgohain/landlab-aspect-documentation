from mpi4py import MPI
import importlib.util
import os
import sys

import numpy as np
np.set_printoptions(suppress=False, precision=12)
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
            n_substeps = 10
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

                # Uplift in loop
                # self.model_grid.at_node["topographic__elevation"][self.model_grid.core_nodes] +=  self.uplift_rate * sub_dt

                # # Horizontal advection (REQUIRED for 3D)
                # self.horizontal_surface_advector.run_one_step(sub_dt)

                deposition_erosion += self.elevation - elevation_before

        self.current_time = end_time

        # self.write_output()
        self.save_landlab_output()


        print("Max elevation:", np.max(self.elevation),
            "Min elevation:", np.min(self.elevation))

        # print("max uplift:", np.max(self.uplift_rate))

        dimensional_deposition_erosion = self.dimensional_deposition_erosion(
            ASPECT_dim,
            deposition_erosion
        )

        return dimensional_deposition_erosion
    

    def set_mesh_information(self, grid_dictionary):
        print("grid_dictionary =", grid_dictionary)

        if grid_dictionary is not None:
            print(grid_dictionary.keys())

        if self.model_grid is not None:
            return
        
        if self.model_grid is not None:
            return

        print("* Creating RasterModelGrid ...")

        # =====================================================
        # FIXED DOMAIN (MATCH ASPECT 3D TOP SURFACE)
        # =====================================================
        x_extent = 3
        y_extent = 3
        spacing  = 0.015625

        # nrows = int(y_extent / spacing) + 1
        # ncols = int(x_extent / spacing) + 1

        # self.model_grid = landlab.RasterModelGrid(
        #     (nrows, ncols),
        #     xy_spacing=(spacing, spacing),
        #     # xy_of_lower_left=(0, -y_extent / 2),
        #     # as Landlab domain goes half away from ASPECT domain
        #     xy_of_lower_left=(0, 0),
        # )

        nrows = int(y_extent / spacing) + 3
        ncols = int(x_extent / spacing) + 3

        self.model_grid = landlab.RasterModelGrid(
            (nrows, ncols),
            xy_spacing=(spacing, spacing),
            xy_of_lower_left=(-spacing, -spacing),
        )

        print("* Creating topographic elevation ...")


        # =====================================================
        # CUSTOM UPLIFT FIELD
        # =====================================================

        # self.uplift_rate = (
        #     self.model_grid.node_y[self.model_grid.core_cells]/ 1e5)

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

        # init_elev = 0.0

        # self.elevation = self.model_grid.add_zeros(
        #     "topographic__elevation",
        #     at="node"
        # )

        # z = self.model_grid.add_zeros("topographic__elevation",at="node")

        # z = self.model_grid.zeros(at="node") + init_elev

        # np.random.seed(0)

        # self.model_grid["node"]["topographic__elevation"] = (
        #     z + np.random.rand(len(z)) / 1000.0
        # )

        # z = self.model_grid.add_zeros(
        #     "topographic__elevation",
        #     at="node"
        # )

        # np.random.seed(0)

        # z[:] = init_elev + np.random.rand(len(z)) / 1000.0

        # self.elevation = z

        # =====================================================
        # CUSTOM liniear slope surface
        # =====================================================
        # z = 0.5 * self.model_grid.node_x
        # # z = np.zeros(self.model_grid.number_of_nodes)

        # self.elevation =  self.model_grid.add_field(
        #     "topographic__elevation", z, at="node"
        # )


        # Note: original bechmark in Landlab used mg.node_y[mg.core_cells]

        # =====================================================
        # CUSTOM topography for diffusion benchmark from Standalone ASPECT 
        # =====================================================
        # z = self.model_grid.add_zeros(
        #             "topographic__elevation",
        #             at="node"
        #         )
        # =====================================================
        # INITIAL TOPOGRAPHY FROM ASPECT .prm
        # =====================================================

        A = 0.075
        L = 3.0

        z = A * np.sin(np.pi * self.model_grid.node_x / L)

        self.elevation = self.model_grid.add_field(
            "topographic__elevation",
            z,
            at="node"
        )

        self.elevation = z


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

        # self.model_grid.set_closed_boundaries_at_grid_edges(
        #     right_is_closed=False,
        #     left_is_closed=False,
        #     top_is_closed=True,
        #     bottom_is_closed=True,
        # )

        # self.model_grid.set_fixed_value_boundaries_at_grid_edges(
        #     right_is_fixed_val=False,
        #     left_is_fixed_val=False,
        #     top_is_fixed_val=False,
        #     bottom_is_fixed_val=False,
        # )

        print("\tnumber of nodes:", self.model_grid.number_of_nodes)

        self.initialize_landlab_components()
        print("* Done")

        return self.model_grid

    def initialize_landlab_components(self):
        # D = 0
        D = 0.25 # m2/second
        # D = 0.25 /self.s2yr # 7*1e-9 m2/second

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