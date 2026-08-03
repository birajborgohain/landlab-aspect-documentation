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

# Follwing is to check exceution steps and function calls, to help debug the code and understand the flow of execution.
import os
import inspect
import numpy as np
from mpi4py import MPI
from datetime import datetime

timestamp = datetime.now().strftime(
    "%H:%M:%S"
)

# =====================================================
# MPI INFORMATION
# =====================================================
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# =====================================================
# TRACE GLOBAL VARIABLES
# =====================================================
TRACE_STEP = 0
TRACE_FILE = None


# =====================================================
# INITIALIZE TRACE SYSTEM
# =====================================================
def initialize_trace(selected_output_dir):

    global TRACE_FILE

    # =================================================
    # CREATE TRACE DIRECTORY
    # =================================================
    TRACE_DIR = os.path.join(
        selected_output_dir,
        "trace_logs"
    )

    os.makedirs(TRACE_DIR, exist_ok=True)

    # =================================================
    # TRACE FILE FOR EACH MPI RANK
    # =================================================
    TRACE_FILE = os.path.join(
        TRACE_DIR,
        f"execution_trace_rank_{rank}.txt"
    )

    # =================================================
    # INITIAL HEADER
    # =================================================
    with open(TRACE_FILE, "w") as f:

        f.write(
            "=====================================\n"
        )

        f.write(
            "ASPECT-Landlab Execution Trace\n"
        )

        f.write(
            f"MPI Rank: {rank}\n"
        )

        f.write(
            f"Trace File: {TRACE_FILE}\n"
        )

        f.write(
            "=====================================\n\n"
        )


# =====================================================
# TRACE FUNCTION
# =====================================================
def trace(msg=""):

    global TRACE_STEP
    global TRACE_FILE

    TRACE_STEP += 1

    frame = inspect.currentframe().f_back

    line_no = frame.f_lineno
    func_name = frame.f_code.co_name

    trace_message = (
        f"[{timestamp}] "
        f"[RANK {rank}] "
        f"[STEP {TRACE_STEP}] "
        f"Function: {func_name} | "
        f"Line: {line_no} | "
        f"{msg}"
    )

    # =================================================
    # PRINT TO TERMINAL
    # =================================================
    print("\n" + trace_message)

    # =================================================
    # SAVE TO FILE
    # =================================================
    if TRACE_FILE is not None:

        with open(TRACE_FILE, "a") as f:
            f.write(trace_message + "\n")


# =====================================================
# EXAMPLE: INITIALIZE TRACE SYSTEM
# =====================================================

# Example ASPECT output directory
selected_output_dir = (
    "outputs/Landlab_defined_uplift_subset_40_trace"
)

initialize_trace(selected_output_dir)

#-----------------------------------------------------------------------------

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

    # def update_until(self, end_time, ASPECT_dim, ASPECT_fields_at_Landlab_nodes_dict):

    #     dt = end_time - self.current_time
    #     self.timestep += 1

    #     deposition_erosion = np.zeros(self.model_grid.number_of_nodes)

    #     # # =====================================================
    #     # # VELOCITY FROM ASPECT (TEMPLATE FUNCTIONS)
    #     # # =====================================================
    #     # vertical_velocity = self.determine_uplift_velocity(
    #     #     ASPECT_dim,
    #     #     ASPECT_fields_at_Landlab_nodes_dict
    #     # )

    #     # self.horizontal_velocity = self.determine_horizontal_velocity(
    #     #     ASPECT_dim,
    #     #     ASPECT_fields_at_Landlab_nodes_dict
    #     # )

    #     # self.horizontal_surface_advector = AdvectionSolverTVD(
    #     #     self.model_grid,
    #     #     fields_to_advect=self.elevation
    #     # )

    #     # =====================================================
    #     # COMPOSITION BLOCK (KEPT BUT DISABLED)
    #     # =====================================================
    #     # slice_weak_composition   = ASPECT_fields_at_Landlab_nodes_dict["weak"]
    #     # slice_strong_composition = ASPECT_fields_at_Landlab_nodes_dict["strong"]
    #     #
    #     # strong_composition = np.zeros(self.model_grid.number_of_nodes)
    #     # weak_composition   = np.zeros(self.model_grid.number_of_nodes)
    #     #
    #     # unique_x_values = np.unique(self.model_grid.x_of_node)
    #     # for x in unique_x_values:
    #     #     strong_composition[self.model_grid.x_of_node == x] = slice_strong_composition[unique_x_values == x]
    #     #     weak_composition[self.model_grid.x_of_node == x]   = slice_weak_composition[unique_x_values == x]
    #     #
    #     # self.Diffusivity[strong_composition >= 0.5] = 1e-10 / self.s2yr
    #     # self.Diffusivity[weak_composition >= 0.5]   = 10 / self.s2yr
    #     # =====================================================

    #     # =====================================================
    #     # TIME STEPPING
    #     # =====================================================
    #     if dt > 0:
    #         n_substeps = 10
    #         sub_dt = dt / n_substeps

    #         for _ in range(n_substeps):
    #             elevation_before = self.elevation.copy()

    #             # Diffusion (Landlab physics)
    #             self.linear_diffuser.run_one_step(sub_dt)

    #             # # Vertical uplift (ASPECT z-velocity)
    #             # self.elevation += vertical_velocity * sub_dt

    #             # #REPLACE ASPECT UPLIFT WITH YOUR LANDLAB UPLIFT
    #             # self.elevation += (self.uplift_rate * sub_dt)

    #             # self.elevation[self.model_grid.core_nodes] += (
    #             #     self.uplift_rate[self.model_grid.core_nodes]
    #             #     * sub_dt
    #             # )

    #             # Uplift in loop
    #             self.model_grid.at_node["topographic__elevation"][self.model_grid.core_nodes] +=  self.uplift_rate * sub_dt

    #             # # Horizontal advection (REQUIRED for 3D)
    #             # self.horizontal_surface_advector.run_one_step(sub_dt)

    #             deposition_erosion += self.elevation - elevation_before

    #     self.current_time = end_time

    #     # self.write_output()
    #     self.save_landlab_output()


    #     print("Max elevation:", np.max(self.elevation),
    #         "Min elevation:", np.min(self.elevation))

    #     print("max uplift:", np.max(self.uplift_rate))

    #     dimensional_deposition_erosion = self.dimensional_deposition_erosion(
    #         ASPECT_dim,
    #         deposition_erosion
    #     )

    #     return dimensional_deposition_erosion

    def update_until(self,end_time,ASPECT_dim,ASPECT_fields_at_Landlab_nodes_dict):
        trace("Entered update_until")    

        dt = end_time - self.current_time
        trace(f"Computed dt = {dt}")
        self.timestep += 1
        trace(f"Timestep incremented to {self.timestep}")

        deposition_erosion = np.zeros(self.model_grid.number_of_nodes)
        trace("Initialized deposition_erosion array")
        if dt > 0:
            trace("dt > 0 condition TRUE")
            n_substeps = 40
            trace(f"n_substeps = {n_substeps}")
            sub_dt = dt / n_substeps
            trace(f"sub_dt = {sub_dt}")

            for i in range(n_substeps):
                trace(f"Starting substep {i}")

                elevation_before = self.elevation.copy()

                trace(
                    f"Copied elevation_before | "
                    f"max = {np.max(elevation_before)}"
                )

         
                
                # =================================================
                # DIFFUSION
                # =================================================

                trace("Starting diffusion")

                elevation_before_diffusion = (
                    self.elevation.copy()
                )

                self.linear_diffuser.run_one_step(sub_dt)

                elevation_after_diffusion = (
                    self.elevation.copy()
                )

                # =================================================
                # DIFFUSION CHANGE
                # =================================================
                diffusion_change = (
                    elevation_after_diffusion
                    -
                    elevation_before_diffusion
                )

                trace(
                    f"Finished diffusion | "
                    f"max elevation = {np.max(self.elevation)}"
                )

                trace(
                    f"diffusion_change = "
                    f"{np.max(np.abs(diffusion_change))}"
                )


                            



                if np.any(np.isnan(self.elevation)):
                    raise ValueError("NaN detected in elevation")

                if np.any(np.isinf(self.elevation)):
                    raise ValueError("INF detected in elevation")
                                

                # =================================================
                # UPLIFT
                # =================================================
                # trace("Starting uplift")
                # self.model_grid.at_node[
                #     "topographic__elevation"
                # ][self.model_grid.core_nodes] += (
                #     self.uplift_rate * sub_dt
                # )
                # trace(
                #     f"Finished uplift | "
                #     f"max elevation = {np.max(self.elevation)}"
                # )

              
                # =================================================
                # UPLIFT
                # =================================================

                trace("Starting uplift")

                elevation_before_uplift = (
                    self.elevation.copy()
                )

                self.model_grid.at_node[
                    "topographic__elevation"
                ][self.model_grid.core_nodes] += (
                    self.uplift_rate * sub_dt
                )

                elevation_after_uplift = (
                    self.elevation.copy()
                )

                # =================================================
                # UPLIFT CHANGE
                # =================================================
                uplift_change = (
                    elevation_after_uplift
                    -
                    elevation_before_uplift
                )

                trace(
                    f"Finished uplift | "
                    f"max elevation = {np.max(self.elevation)}"
                )

                trace(
                    f"uplift_change = "
                    f"{np.max(np.abs(uplift_change))}"
                )



                # =================================================
                # EROSION / DEPOSITION
                # =================================================
                
                trace("Starting erosion/deposition")
                deposition_erosion += (
                    self.elevation - elevation_before
                )
                trace(
                    f"Finished erosion/deposition | "
                    f"max deposition_erosion = {np.max(deposition_erosion)}"
                )

        # =====================================================
        # UPDATE MODEL TIME
        # =====================================================
        trace(f"Updating current_time to {end_time}")
        self.current_time = end_time

        trace("Saving landlab output")
        self.save_landlab_output()
        trace("Finished saving landlab output")

        


        # =====================================================
        # RETURN TO ASPECT
        # =====================================================
        trace("Computing dimensional deposition/erosion")
        dimensional_deposition_erosion = (
            self.dimensional_deposition_erosion(
                ASPECT_dim,
                deposition_erosion
            )
        )

        

        trace(
            f"Final elevation stats | "
            f"min={np.min(self.elevation)}, "
            f"max={np.max(self.elevation)}"
        )

        trace(
            f"Final deposition_erosion stats | "
            f"min={np.min(deposition_erosion)}, "
            f"max={np.max(deposition_erosion)}"
        )

        trace("Returning dimensional_deposition_erosion")
        return dimensional_deposition_erosion
        

    def set_mesh_information(self, grid_dictionary):

        trace("Setting mesh information")
        if self.model_grid is not None:
            trace("model_grid already exists -> returning existing grid")
            return
        trace("Creating RasterModelGrid")

        

        print("* Creating RasterModelGrid ...")

        # =====================================================
        # FIXED DOMAIN (MATCH ASPECT 3D TOP SURFACE)
        # =====================================================
        x_extent = 900
        y_extent = 1900
        spacing  = 100

        trace(
            f"Domain parameters | "
            f"x_extent={x_extent}, "
            f"y_extent={y_extent}, "
            f"spacing={spacing}"
        )

        nrows = int(y_extent / spacing) + 1
        ncols = int(x_extent / spacing) + 1

        trace(
            f"Computed grid size | "
            f"nrows={nrows}, ncols={ncols}"
        )

        self.model_grid = landlab.RasterModelGrid(
            (nrows, ncols),
            xy_spacing=(spacing, spacing),
            # xy_of_lower_left=(0, -y_extent / 2),
            # as Landlab domain goes half away from ASPECT domain
            xy_of_lower_left=(0, 0),
        )

        trace(
            f"RasterModelGrid created | "
            f"nodes={self.model_grid.number_of_nodes}"
        )

        print("* Creating topographic elevation ...")


        # =====================================================
        # CUSTOM UPLIFT FIELD
        # =====================================================

        self.uplift_rate = (
            self.model_grid.node_y[self.model_grid.core_cells]/ 1e5)
        
        trace(
            f"Initialized uplift_rate | "
            f"min={np.min(self.uplift_rate)}, "
            f"max={np.max(self.uplift_rate)}"
        )

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

        z = self.model_grid.add_zeros(
            "topographic__elevation",
            at="node"
        )

        trace("Creating initial topography field")

        np.random.seed(0)
        trace("Random seed set to 0")

        # z[:] = init_elev + np.random.rand(len(z)) / 1000.0

        z[:] = 0.0

        trace(
            f"Initialized elevation field | "
            f"min={np.min(z)}, "
            f"max={np.max(z)}"
        )

        self.elevation = z

        trace("Setting fixed-value boundary conditions")

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

        # self.model_grid.set_closed_boundaries_at_grid_edges(
        #     right_is_closed=True,
        #     left_is_closed=True,
        #     top_is_closed=True,
        #     bottom_is_closed=True,
        # )

        # self.model_grid.set_closed_boundaries_at_grid_edges(
        #     right_is_closed=False,
        #     left_is_closed=False,
        #     top_is_closed=True,
        #     bottom_is_closed=True,
        # )
        trace("Setting fixed-value boundary conditions")

        self.model_grid.set_fixed_value_boundaries_at_grid_edges(
            right_is_fixed_val=True,
            left_is_fixed_val=True,
            top_is_fixed_val=True,
            bottom_is_fixed_val=True,
        )
        

        # print("\tnumber of nodes:", self.model_grid.number_of_nodes)
        trace(
            f"Grid summary | "
            f"number_of_nodes={self.model_grid.number_of_nodes}"
        )
        trace("Initializing Landlab components")
        self.initialize_landlab_components()

        
        print("* Done")

        trace("Returning model_grid")
        return self.model_grid
        

    def initialize_landlab_components(self):
        trace("Entered initialize_landlab_components")
        # D = 0
        # D = 50000.0 # m2/second
        D = 50000.0 /self.s2yr # m2/second
        trace(f"Diffusivity D = {D}")
        

        self.Diffusivity = self.model_grid.add_zeros(
            "linear_diffusivity",
            at="node"
        )
        trace("Created linear_diffusivity field")

        self.Diffusivity += D
        trace(
            f"Assigned diffusivity values | "
            f"min={np.min(self.Diffusivity)}, "
            f"max={np.max(self.Diffusivity)}"
        )

        self.linear_diffuser = LinearDiffuser(
            self.model_grid,
            linear_diffusivity=self.Diffusivity
        )

        trace("LinearDiffuser initialized")


# =====================================================
# EXPORT TO ASPECT
# =====================================================
model = MyAspectLandlabModel()
model.export_aspect_callbacks(model, globals())