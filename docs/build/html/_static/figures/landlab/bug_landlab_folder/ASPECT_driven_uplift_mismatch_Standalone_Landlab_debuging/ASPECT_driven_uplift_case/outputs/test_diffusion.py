
# ============================================================
# BENCHMARK OUTPUT
# ============================================================

import os
import sys

from benchmark_class import BenchmarkFramework

CASE_NAME = sys.argv[1]

# CASE_NAME = (
#     # "Linear_slope_substep_10_diffu-1_xy-repition_0_"
#     # "global_refin-0_only_Landlab_x-900_y-1900_"
#     # "z-1000_no_Advection_no_Stokes"

#     # "Linear_Time_test_no_Advection_no_Stokes"
#     # "Diffusion_Zero_substep_10_xy-repition_5_global_refin-0_x-900_y-1900_z-1000_no_Advection_no_Stokes"
#     "global_refin-1_Diffusion_5e4_m2-YEAR_substep_10_xy-repition_5_x-900_y-1900_z-1000_no_Advection_no_Stokes"
# )

OUTPUTS_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

benchmark = BenchmarkFramework(
    OUTPUTS_DIR,
    CASE_NAME
)

import numpy as np
# import pytest
from numpy.testing import assert_array_almost_equal
# from numpy.testing import assert_equal

from landlab import HexModelGrid
from landlab import RasterModelGrid
from landlab.components.diffusion import LinearDiffuser

# pip install pytest


def test_diffusion():
    dt = 1
    time_to_run = 3.0
    init_elev = 0.0

    mg = RasterModelGrid((20, 10), xy_spacing=(100.0, 100.0))
    uplift_rate = mg.node_y[mg.core_cells] / 100000.0

    # create the fields in the grid
    mg.add_zeros("topographic__elevation", at="node")
    z = mg.zeros(at="node") + init_elev
    np.random.seed(0)
    mg["node"]["topographic__elevation"] = z + np.random.rand(len(z)) / 1000.0

        # ------------------------------------------------------------
    # SAVE INITIAL TOPOGRAPHY
    # ------------------------------------------------------------

    benchmark_dir = os.path.join(
        OUTPUTS_DIR,
        CASE_NAME,
        "results_benchmark"
    )

    os.makedirs(benchmark_dir, exist_ok=True)

    initial_output_file = os.path.join(
        benchmark_dir,
        "z_initial_reference.txt"
    )

    with open(initial_output_file, "w") as f:

        f.write("# x y z_initial\n")

        for node in range(mg.number_of_nodes):

            f.write(
                f"{mg.node_x[node]:.6f} "
                f"{mg.node_y[node]:.6f} "
                f"{mg.at_node['topographic__elevation'][node]:.15f}\n"
            )

    print("\nInitial reference topography saved.")
    mg.set_fixed_value_boundaries_at_grid_edges(True, True, True, True)

    # instantiate:
    dfn = LinearDiffuser(mg, linear_diffusivity=50000.0)

    # perform the loop:
    # elapsed_time = 0.0  # total time in simulation
    # while elapsed_time < time_to_run:
        # if elapsed_time + dt > time_to_run:
        #     dt = time_to_run - elapsed_time
        # dfn.run_one_step(dt)
        # mg.at_node["topographic__elevation"][mg.core_nodes] += uplift_rate * dt
        # elapsed_time += dt

    elapsed_time = 0.0
    step = 0

    while elapsed_time < time_to_run:

        if elapsed_time + dt > time_to_run:
            dt = time_to_run - elapsed_time

        step += 1

#------------Special case Uplift first than Diffusion second---------
        # # -----------------------------
        # # Before Uplift
        # # -----------------------------
        # z_before = mg.at_node["topographic__elevation"].copy()
        
        # mg.at_node["topographic__elevation"][mg.core_nodes] += (
        #     uplift_rate * dt
        # )
        # # -----------------------------
        # # AFTER UPLIFT
        # # -----------------------------
        # z_after_diffusion = mg.at_node["topographic__elevation"].copy()

        # # -----------------------------
        # # BEFORE DIFFUSION
        # # -----------------------------

        # dfn.run_one_step(dt)
        # # -----------------------------
        # # AFTER Diffusion
        # # -----------------------------

        # z_after_uplift = mg.at_node["topographic__elevation"].copy()
#------------ end of Special case Uplift first than Diffusion second---------

#------------start of Usual case Diffusion first than Uplift second---------
        # -----------------------------
        # BEFORE DIFFUSION
        # -----------------------------
        z_before = mg.at_node["topographic__elevation"].copy()
        
        # The diffusion
        dfn.run_one_step(dt)
        # -----------------------------
        # AFTER DIFFUSION
        # -----------------------------
        z_after_diffusion = mg.at_node["topographic__elevation"].copy()

        # the uplift
        mg.at_node["topographic__elevation"][mg.core_nodes] += (
            uplift_rate * dt
        )
        # -----------------------------
        # AFTER UPLIFT
        # -----------------------------
        z_after_uplift = mg.at_node["topographic__elevation"].copy()

        elapsed_time += dt
#------------End of Usual case Diffusion first than Uplift second---------
        # -----------------------------
        # SAVE THIS TIMESTEP
        # -----------------------------
        output_file = os.path.join(
            benchmark_dir,
            f"z_timestep_{step}.txt"
        )

        with open(output_file, "w") as f:

            f.write(
                "# x y z_before z_after_diffusion z_after_uplift\n"
            )

            for node in range(mg.number_of_nodes):

                f.write(
                    f"{mg.node_x[node]:.6f} "
                    f"{mg.node_y[node]:.6f} "
                    f"{z_before[node]:.15f} "
                    f"{z_after_diffusion[node]:.15f} "
                    f"{z_after_uplift[node]:.15f}\n"
                )

        print(f"Saved timestep {step}")

    z_target = np.array(
        [
            5.48813504e-04,
            7.15189366e-04,
            6.02763376e-04,
            5.44883183e-04,
            4.23654799e-04,
            6.45894113e-04,
            4.37587211e-04,
            8.91773001e-04,
            9.63662761e-04,
            3.83441519e-04,
            7.91725038e-04,
            9.18166135e-04,
            1.02015039e-03,
            1.10666198e-03,
            1.14866514e-03,
            1.20224288e-03,
            1.12953135e-03,
            1.12966219e-03,
            1.00745155e-03,
            8.70012148e-04,
            9.78618342e-04,
            1.12628772e-03,
            1.41663596e-03,
            2.66338249e-03,
            2.80420703e-03,
            2.82445061e-03,
            2.69263914e-03,
            2.44620140e-03,
            2.04237613e-03,
            4.14661940e-04,
            2.64555612e-04,
            2.15073330e-03,
            2.77965579e-03,
            3.22134736e-03,
            3.45859244e-03,
            4.47224671e-03,
            4.25371135e-03,
            3.82941648e-03,
            3.25127747e-03,
            6.81820299e-04,
            3.59507901e-04,
            3.36577718e-03,
            4.20490812e-03,
            4.81467159e-03,
            5.14099588e-03,
            5.15029835e-03,
            4.83533539e-03,
            5.22312276e-03,
            4.37284689e-03,
            3.63710771e-04,
            5.70196770e-04,
            4.65122535e-03,
            5.67854747e-03,
            6.44757828e-03,
            6.85985389e-03,
            6.86464781e-03,
            6.45159799e-03,
            5.65255723e-03,
            4.54258827e-03,
            2.44425592e-04,
            1.58969584e-04,
            5.85971567e-03,
            7.16648352e-03,
            8.10954246e-03,
            8.61082386e-03,
            8.61350727e-03,
            8.10597021e-03,
            7.12594182e-03,
            5.75483957e-03,
            9.60984079e-05,
            9.76459465e-04,
            6.29476234e-03,
            7.70594852e-03,
            9.79504842e-03,
            1.03829367e-02,
            1.03869062e-02,
            9.79374998e-03,
            8.65447904e-03,
            7.07179252e-03,
            1.18727719e-04,
            3.17983179e-04,
            7.43078552e-03,
            9.18353155e-03,
            1.04682910e-02,
            1.11542648e-02,
            1.21643980e-02,
            1.14930584e-02,
            1.02184219e-02,
            8.53727126e-03,
            9.29296198e-04,
            3.18568952e-04,
            8.68034110e-03,
            1.06702554e-02,
            1.21275181e-02,
            1.29049224e-02,
            1.29184938e-02,
            1.21616788e-02,
            1.17059081e-02,
            9.66728348e-03,
            4.69547619e-06,
            6.77816537e-04,
            1.00128306e-02,
            1.21521279e-02,
            1.37494046e-02,
            1.46053573e-02,
            1.46205669e-02,
            1.37908840e-02,
            1.22146332e-02,
            1.01165765e-02,
            9.52749012e-04,
            4.47125379e-04,
            1.12069867e-02,
            1.35547122e-02,
            1.52840440e-02,
            1.62069802e-02,
            1.62196380e-02,
            1.53169489e-02,
            1.35997836e-02,
            1.12818577e-02,
            6.92531590e-04,
            7.25254280e-04,
            1.14310516e-02,
            1.38647655e-02,
            1.66771925e-02,
            1.76447108e-02,
            1.76515649e-02,
            1.66885162e-02,
            1.48507549e-02,
            1.23206170e-02,
            2.90077607e-04,
            6.18015429e-04,
            1.24952067e-02,
            1.49924260e-02,
            1.68435913e-02,
            1.78291009e-02,
            1.88311310e-02,
            1.78422046e-02,
            1.59665841e-02,
            1.34122052e-02,
            4.31418435e-04,
            8.96546596e-04,
            1.34612553e-02,
            1.58763600e-02,
            1.76887976e-02,
            1.86526609e-02,
            1.86492669e-02,
            1.76752679e-02,
            1.68480793e-02,
            1.44368883e-02,
            9.98847007e-04,
            1.49448305e-04,
            1.40672989e-02,
            1.64140227e-02,
            1.81162514e-02,
            1.90091351e-02,
            1.89959971e-02,
            1.80757625e-02,
            1.63425116e-02,
            1.39643530e-02,
            6.91669955e-05,
            6.97428773e-04,
            1.47340964e-02,
            1.66453353e-02,
            1.80835612e-02,
            1.88335770e-02,
            1.88048458e-02,
            1.80022362e-02,
            1.65110248e-02,
            1.44854151e-02,
            1.71629677e-04,
            5.21036606e-04,
            1.40633664e-02,
            1.54867652e-02,
            1.75865008e-02,
            1.81309867e-02,
            1.80760242e-02,
            1.74501109e-02,
            1.63343931e-02,
            1.48208186e-02,
            3.18389295e-05,
            1.64694156e-04,
            1.41550038e-02,
            1.49870334e-02,
            1.57563641e-02,
            1.60213295e-02,
            1.69074625e-02,
            1.64888825e-02,
            1.58787450e-02,
            1.50671910e-02,
            3.11944995e-04,
            3.98221062e-04,
            2.09843749e-04,
            1.86193006e-04,
            9.44372390e-04,
            7.39550795e-04,
            4.90458809e-04,
            2.27414628e-04,
            2.54356482e-04,
            5.80291603e-05,
            4.34416626e-04,
        ]
    )

    # assert_array_almost_equal(mg.at_node["topographic__elevation"], z_target)


    # ------------------------------------------------------------
    # SAVE REFERENCE
    # ------------------------------------------------------------

    benchmark.write_reference_topography(
        mg,
        z_target
    )

    # ------------------------------------------------------------
    # SAVE FINAL
    # ------------------------------------------------------------

    benchmark.write_final_topography(
        mg,
        mg.at_node["topographic__elevation"]
    )

    print("\nBenchmark reference files saved.")

if __name__ == "__main__":

    test_diffusion()