# ASPECT–Landlab Coupling Script fro standalone ASPECT diffusion test

"""

Features
--------
- RasterModelGrid setup
- Linear diffusion surface process
- Sinusoidal initial topography
- Stable sub-stepping time integration
- Boundary condition management
- ASPECT callback export


"""

from mpi4py import MPI
import numpy as np
import landlab

from landlab.components import LinearDiffuser
from landlab_template import LandLabTemplate

import json
from landlab.io.legacy_vtk import write_legacy_vtk


# -----------------------------------------------------------------------------
# NUMPY CONFIGURATION
# -----------------------------------------------------------------------------
np.set_printoptions(suppress=False, precision=12)


class AspectLandlabModel(LandLabTemplate):
    """
    Coupled ASPECT–Landlab surface evolution model.

    This model evolves surface topography using linear diffusion and
    exchanges information with ASPECT through the LandlabTemplate API.
    """

    # -------------------------------------------------------------------------
    # MAIN TIME-STEPPING FUNCTION
    # -------------------------------------------------------------------------
    def update_until(
        self,
        end_time,
        aspect_dimension,
        aspect_fields_at_landlab_nodes,
    ):
        """
        Advance the Landlab model until the specified simulation time.

        Parameters
        ----------
        end_time : float
            Target simulation time.

        aspect_dimension : int
            Number of spatial dimensions used in ASPECT.

        aspect_fields_at_landlab_nodes : dict
            Dictionary containing ASPECT fields interpolated onto
            Landlab nodes.

        Returns
        -------
        ndarray
            Dimensional deposition/erosion field returned to ASPECT.
        """

        dt = end_time - self.current_time
        self.timestep += 1

        deposition_erosion = np.zeros(self.model_grid.number_of_nodes)

        # ---------------------------------------------------------------------
        # TIME INTEGRATION
        # ---------------------------------------------------------------------
        if dt > 0:

            n_substeps = 10
            sub_dt = dt / n_substeps

            for _ in range(n_substeps):

                elevation_before = self.elevation.copy()

                # -------------------------------------------------------------
                # LINEAR DIFFUSION
                # -------------------------------------------------------------
                self.linear_diffuser.run_one_step(sub_dt)

                deposition_erosion += (
                    self.elevation - elevation_before
                )

        self.current_time = end_time

        # ---------------------------------------------------------------------
        # SAVE OUTPUT
        # ---------------------------------------------------------------------
        self.save_landlab_output()

        print(
            "Max elevation:", np.max(self.elevation),
            "Min elevation:", np.min(self.elevation)
        )

        dimensional_deposition_erosion = (
            self.dimensional_deposition_erosion(
                aspect_dimension,
                deposition_erosion,
            )
        )

        return dimensional_deposition_erosion

    # -------------------------------------------------------------------------
    # GRID AND MODEL INITIALIZATION
    # -------------------------------------------------------------------------
    def set_mesh_information(self, grid_dictionary):
        """
        Create and initialize the Landlab grid.

        Parameters
        ----------
        grid_dictionary : dict
            Dictionary passed from ASPECT containing mesh information.

        Returns
        -------
        RasterModelGrid
            Initialized Landlab grid.
        """

        # ---------------------------------------------------------------------
        # DOMAIN PARAMETERS
        # ---------------------------------------------------------------------
        x_extent = 1.0
        y_extent = 1.0
        spacing = 0.015625

        nrows = int(y_extent / spacing) + 1
        ncols = int(x_extent / spacing) + 1

        # ---------------------------------------------------------------------
        # CREATE GRID
        # ---------------------------------------------------------------------
        self.model_grid = landlab.RasterModelGrid(
            (nrows, ncols),
            xy_spacing=(spacing, spacing),
            xy_of_lower_left=(0.0, 0.0),
        )

        print("* Creating topographic elevation ...")

        # ---------------------------------------------------------------------
        # INITIAL TOPOGRAPHY
        # ---------------------------------------------------------------------
        amplitude = 0.075
        wavelength = 1.0

        initial_topography = (
            amplitude
            * np.sin(
                np.pi * self.model_grid.node_x / wavelength
            )
        )

        self.elevation = self.model_grid.add_field(
            "topographic__elevation",
            initial_topography,
            at="node",
        )

        # ---------------------------------------------------------------------
        # BOUNDARY CONDITIONS
        # ---------------------------------------------------------------------
        self.model_grid.set_closed_boundaries_at_grid_edges(
            right_is_closed=True,
            left_is_closed=True,
            top_is_closed=False,
            bottom_is_closed=False,
        )

        print(
            "\tNumber of nodes:",
            self.model_grid.number_of_nodes,
        )

        # ---------------------------------------------------------------------
        # INITIALIZE LANDLAB COMPONENTS
        # ---------------------------------------------------------------------
        self.initialize_landlab_components()

        print("* Grid initialization complete")

        return self.model_grid

    # -------------------------------------------------------------------------
    # LANDLAB COMPONENTS
    # -------------------------------------------------------------------------
    def initialize_landlab_components(self):
        """
        Initialize Landlab process components.
        """

        # Diffusivity [m^2/s]
        diffusivity = 0.5 / self.s2yr

        self.diffusivity_field = self.model_grid.add_zeros(
            "linear_diffusivity",
            at="node",
        )

        self.diffusivity_field += diffusivity

        self.linear_diffuser = LinearDiffuser(
            self.model_grid,
            linear_diffusivity=self.diffusivity_field,
        )


# -----------------------------------------------------------------------------
# EXPORT MODEL CALLBACKS TO ASPECT
# -----------------------------------------------------------------------------
model = AspectLandlabModel()
model.export_aspect_callbacks(model, globals())


