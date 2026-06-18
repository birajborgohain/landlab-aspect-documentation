import inspect
import numpy as np
from mpi4py import MPI
import importlib.util
import os
import sys


np.set_printoptions(suppress=False, precision=12)
import landlab
from landlab.components import LinearDiffuser, AdvectionSolverTVD

# ===================== ADDED =====================
import json
from landlab.io.legacy_vtk import write_legacy_vtk
# ================================================

# Follwing is to check exceution steps and function calls, to help debug the code and understand the flow of execution.



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
REPORT_STEP = 0
TRACE_STEP = 0
TRACE_FILE = None
GLOBAL_LOOP_COUNTER = 0
TRACE_INITIALIZED = False

# from import_template import initialize_trace
# from import_template import TRACE_INITIALIZED

# if not TRACE_INITIALIZED:
#     initialize_trace(selected_output_dir)
#     TRACE_INITIALIZED = True
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
# initialize_trace(
#     os.path.join(
#         os.getcwd(),
#         "outputs"
#     )
# )
        
# =====================================================
# REPORT FUNCTION
# =====================================================
# def report(msg=""):

#     global TRACE_STEP
#     global TRACE_FILE

#     TRACE_STEP += 1

#     frame = inspect.currentframe().f_back
#     line_no = frame.f_lineno

#     report_message = (
#         f"[STEP {TRACE_STEP} | LINE {line_no}]\n"
#         f"{msg}\n"
#     )

#     print(report_message)

#     if TRACE_FILE is not None:
#         with open(TRACE_FILE, "a") as f:
#             f.write(report_message)

def report(msg=""):

    global REPORT_STEP
    global TRACE_FILE

    REPORT_STEP += 1

    frame = inspect.currentframe().f_back

    line_no = frame.f_lineno

    report_message = (
        f"[STEP {REPORT_STEP} | LINE {line_no}]\n"
        f"{msg}\n"
    )

    print(report_message)

    if TRACE_FILE is not None:
        with open(TRACE_FILE, "a") as f:
            f.write(report_message)

# =====================================================
# LOOP HEADER
# =====================================================
def report_header(title):

    global TRACE_FILE

    header = (
        "\n"
        f"================ {title} ================\n"
    )

    print(header)

    if TRACE_FILE is not None:
        with open(TRACE_FILE, "a") as f:
            f.write(header)

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

    # # =================================================
    # # PRINT TO TERMINAL
    # # =================================================
    # print("\n" + trace_message)

    # # =================================================
    # # SAVE TO FILE
    # # =================================================
    # if TRACE_FILE is not None:

    #     with open(TRACE_FILE, "a") as f:
    #         f.write(trace_message + "\n")


# =====================================================
# EXAMPLE: INITIALIZE TRACE SYSTEM
# =====================================================

# Example ASPECT output directory
# selected_output_dir = (
#     "outputs/tracer_data"
# )
# selected_output_dir = os.getcwd()
# aspect_output_dir = os.path.dirname(os.path.abspath(__file__))
# selected_output_dir = aspect_output_dir
# print("cwd =", os.getcwd())
# print("__file__ =", os.path.abspath(__file__))
# initialize_trace(selected_output_dir)

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

    

    def update_until(self,end_time,ASPECT_dim,ASPECT_fields_at_Landlab_nodes_dict):
        global GLOBAL_LOOP_COUNTER
       
        dt = end_time - self.current_time
        
        self.timestep += 1
        

        deposition_erosion = np.zeros(self.model_grid.number_of_nodes)

        vertical_velocity = self.determine_uplift_velocity(
            ASPECT_dim,
            ASPECT_fields_at_Landlab_nodes_dict
        )

        # Map vertical_velocity to core nodes if necessary and optionally
        # convert from m/yr to m/s if a flag is set on the model.
        vertical_velocity = np.asarray(vertical_velocity)
        # map to core nodes if needed
        if vertical_velocity.size == len(self.model_grid.core_nodes):
            vertical_velocity_core = vertical_velocity
        elif vertical_velocity.size == self.model_grid.number_of_nodes:
            vertical_velocity_core = vertical_velocity[self.model_grid.core_nodes]
        else:
            raise ValueError(
                f"vertical_velocity length {vertical_velocity.size} doesn't match core nodes {len(self.model_grid.core_nodes)} or total nodes {self.model_grid.number_of_nodes}"
            )

        # optional unit conversion: if velocities provided in m/yr convert to m/s
        s_per_year = getattr(self, "s2yr", 31557600.0)
        if getattr(self, "vertical_velocity_in_m_per_year", False):
            vertical_velocity_core = vertical_velocity_core / s_per_year

        # runtime debug checks (toggle with self.debug_uplift = True/False)
        if getattr(self, "debug_uplift", False):
            print("[debug] dt:", dt)
            print("[debug] vertical_velocity size:", vertical_velocity.size)
            print("[debug] vertical_velocity_core size:", vertical_velocity_core.size)
            print(
                "[debug] vertical_velocity_core min,max,mean:",
                np.nanmin(vertical_velocity_core),
                np.nanmax(vertical_velocity_core),
                np.nanmean(vertical_velocity_core),
            )
            print(
                "[debug] vertical_velocity_core all_zero:",
                np.allclose(vertical_velocity_core, 0.0),
            )
            if getattr(self, "vertical_velocity_in_m_per_year", False):
                print(f"[debug] converted from m/yr to m/s using s_per_year={s_per_year}")
            else:
                print("[debug] no year-to-second conversion applied; assuming vertical velocity units match ASPECT time units")

        
        if dt > 0:
            
            n_substeps = 1
            
            sub_dt = dt / n_substeps
            

            for i in range(n_substeps):
                
                elapsed_time_before = (
                    self.current_time
                    + i * sub_dt
                )

                
                GLOBAL_LOOP_COUNTER += 1

                

                elevation_before = self.elevation.copy()


                

         
                
                # =================================================
                # DIFFUSION
                # =================================================

                
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


                            



                

                

                elevation_before_uplift = (
                    self.elevation.copy()
                )

                # self.model_grid.at_node[
                #     "topographic__elevation"
                # ][self.model_grid.core_nodes] += (
                #     self.uplift_rate * sub_dt
                # )

                # Vertical uplift (ASPECT z-velocity)
                # `vertical_velocity_core` contains the vertical velocity on core nodes
                # (units must be m/s for ASPECT). Store it as `uplift_rate` and apply to
                # the topographic elevation. Do NOT modify node coordinates (node_y).
                self.uplift_rate = vertical_velocity_core

                # Apply uplift to elevation on core nodes
                self.model_grid.at_node["topographic__elevation"][self.model_grid.core_nodes] += (
                    self.uplift_rate * sub_dt
                )
                if getattr(self, "debug_uplift", False):
                    print(
                        "[debug] applied uplift (m/s) max,mean:",
                        np.nanmax(self.uplift_rate),
                        np.nanmean(self.uplift_rate),
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

                # =================================================
                # TOTAL CHANGE (A → C)
                # =================================================

                total_change = (
                    elevation_after_uplift
                    -
                    elevation_before
                )

                
        



                # =================================================
                # EROSION / DEPOSITION
                # =================================================
                
                

                elapsed_time_after = (
                    elapsed_time_before
                    + sub_dt
                )

                # write_tracer(
                #     aspect_step=self.timestep,
                #     loop_number=GLOBAL_LOOP_COUNTER,
                #     elapsed_time=elapsed_time_after,
                #     dt=sub_dt,
                #     n_substeps=n_substeps,
                #     diffusion_change=diffusion_change,
                #     uplift_change=uplift_change,
                #     total_change=total_change,
                #     elevation=elevation_after_uplift
                # )

                

        # =====================================================
        # UPDATE MODEL TIME
        # =====================================================
        
        self.current_time = end_time

        
        self.save_landlab_output()

        # Code to Create elevation change tracing folder
        global TRACE_INITIALIZED

        if not TRACE_INITIALIZED:

            initialize_trace(
                self.aspect_output_directory
            )
            TRACE_INITIALIZED = True
        #End of code to Create elevation change tracing folder
        

        


        # =====================================================
        # RETURN TO ASPECT
        # =====================================================
        
        dimensional_deposition_erosion = (
            self.dimensional_deposition_erosion(
                ASPECT_dim,
                deposition_erosion
            )
        )

        self.save_landlab_output()

        
        return dimensional_deposition_erosion
        

    def set_mesh_information(self, grid_dictionary):

        
        if self.model_grid is not None:
            
            return
        

        

       
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

        

        # =====================================================
        # CUSTOM UPLIFT FIELD
        # =====================================================

        # self.uplift_rate = (
        #     self.model_grid.node_y[self.model_grid.core_cells]/ 1e5)
        
        

        

        init_elev = 0.0

        

        z = self.model_grid.add_zeros(
            "topographic__elevation",
            at="node"
        )

       

        np.random.seed(0)
        

        z[:] = init_elev + np.random.rand(len(z)) / 1000.0

     

        

        self.elevation = z

        self.uplift_rate = np.zeros(len(self.model_grid.core_nodes))
        self.debug_uplift = True
        self.vertical_velocity_in_m_per_year = False

        

        self.model_grid.set_fixed_value_boundaries_at_grid_edges(
            right_is_fixed_val=True,
            left_is_fixed_val=True,
            top_is_fixed_val=True,
            bottom_is_fixed_val=True,
        )
        

       
        self.initialize_landlab_components()

        
        
        return self.model_grid
        

    def initialize_landlab_components(self):
        
        # D = 0
        D = 50000.0 # m2/year
        
        # D = 50000.0 /self.s2yr # m2/second

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