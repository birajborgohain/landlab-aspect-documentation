from pathlib import Path


# ---------------------------------------------------------
# Locate files relative to this script
# ---------------------------------------------------------

script_dir = Path(__file__).resolve().parent

input_file = script_dir / "1_sine_zero_flux.prm"

output_file = script_dir / "1_sine_zero_flux_landlab.prm"


# ---------------------------------------------------------
# Read original benchmark
# ---------------------------------------------------------

text = input_file.read_text()


# ---------------------------------------------------------
# Replace geometry
# ---------------------------------------------------------

old_geometry = """
  subsection Box
    set X extent = 1
    set Y extent = 1
  end
"""

new_geometry = """
  subsection Box
    set X extent = 3
    set Y extent = 3
  end
"""

text = text.replace(old_geometry, new_geometry)


# ---------------------------------------------------------
# Replace mesh deformation model
# ---------------------------------------------------------

old_mesh_deformation = """
subsection Mesh deformation
  set Mesh deformation boundary indicators = top: diffusion
  set Additional tangential mesh velocity boundary indicators = left, right

  subsection Diffusion
    # The diffusivity
    set Hillslope transport coefficient = 0.25
  end
end
"""

new_mesh_deformation = """
subsection Mesh deformation
  set Mesh deformation boundary indicators = top: Landlab
  set Additional tangential mesh velocity boundary indicators =

  subsection Landlab
    set MPI ranks for Landlab = 1
    set Script name           = 1_shine_zero_flux_landlab_import-template
    set Script path           = .
    set Script argument       =
  end
end
"""

text = text.replace(old_mesh_deformation, new_mesh_deformation)


# ---------------------------------------------------------
# Remove analytical topography subsection
# ---------------------------------------------------------

old_topography = """
  subsection Initial topography model
    set Model name = function

    subsection Function
      set Function constants = A=0.075, L=1.
      set Function expression = \\
                                A * sin(x*pi)
    end
  end
"""

text = text.replace(old_topography, "")


# ---------------------------------------------------------
# Remove analytical topography postprocessor
# ---------------------------------------------------------

text = text.replace(
    "visualization, analytical topography",
    "visualization, analytical topography"
)


# ---------------------------------------------------------
# Change output directory
# ---------------------------------------------------------

text = text.replace(
    "output-1_sine_zero_flux/",
    "output-1_sine_zero_flux_landlab/"
)


# ---------------------------------------------------------
# Write modified prm
# ---------------------------------------------------------

output_file.write_text(text)

print(f"Created: {output_file}")