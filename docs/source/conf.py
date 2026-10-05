#====================================================================================================
#  Copyright (c) 2026,
#  Biraj Borgohain
#
#  Project: Geodynamic and Surface Processes Notes
#====================================================================================================

import pathlib
import os
import sys

# -- Path setup --------------------------------------------------------------

project_root = pathlib.Path(__file__).parents[2].resolve().as_posix()
sys.path.insert(0, project_root)

# -- Project information -----------------------------------------------------

project = 'Landlab-Aspect Development Documentation'
copyright = '2026, Biraj Borgohain'
author = 'Biraj Borgohain'
release = '0.1'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.intersphinx',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinxcontrib.bibtex',
    'sphinx_design',
    'sphinx_revealjs',
    "myst_parser",
]

templates_path = ['_templates']
exclude_patterns = []
revealjs_style_theme = "black"

# Bibliography
bibtex_bibfiles = ['References/refs.bib']
bibtex_default_style = 'apa'
bibtex_reference_style = 'author_year'

# Allow cross-folder inclusion
include_patterns = ['**']

# -- HTML output -------------------------------------------------------------

html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']

html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 4,
    "prev_next_buttons_location": "both",
}

# -----------------------------------------------------------------------------
# Syntax highlighting
# -----------------------------------------------------------------------------

pygments_style = "friendly"
pygments_dark_style = "monokai"

# -- Mock imports (safe for RTD) --------------------------------------------

autodoc_mock_imports = ["pyviztools", "faulttools"]

# -- Custom substitutions ----------------------------------------------------

rst_prolog = """
.. |ASPECT| replace:: *Advanced Solver for Problems in Earth's ConvecTion*
.. |FastScape| replace:: *Landscape evolution model*
"""

# -- Custom CSS --------------------------------------------------------------

html_css_files = ['custom.css']

html_js_files = [
    'slides.js',
]

revealjs_script_plugins = [
]

revealjs_plugins = [
]

revealjs_show_slide_number = True

revealjs_controls = True

revealjs_progress = True

revealjs_history = True

revealjs_center = True

revealjs_touch = True

revealjs_mouse_wheel = True

revealjs_transition = "slide"

revealjs_navigation_mode = "default"

#-----Latex output -------------------------------------------------------------
latex_engine = "xelatex"

# project = "Geodynamic and Surface Processes"
author = "Biraj Borgohain"

# master_doc = "Tools/coupling_ASPECT_Landlab/benchmark_test/uplift_diffusion_n_substeps_to_pdf"
master_doc = "index"
latex_documents = [
    (
        master_doc,
        "uplift_diffusion_n_substeps_to_pdf.tex",
        "",
        "",
        "howto",
    ),
]

latex_toplevel_sectioning = "section"

latex_elements = {
    "tableofcontents": "",
    "sphinxsetup": r"""
verbatimwithframe=false,
VerbatimColor={rgb}{0.96,0.96,0.96},
VerbatimBorderColor={rgb}{1,1,1}
""",
}

numfig = False

html_js_files = [
    'code-blocks.js',
    'slides.js',
]

# latex_elements = {
#     "sphinxsetup": r"""
# verbatimwithframe=false,
# VerbatimColor={rgb}{0.96,0.96,0.96},
# VerbatimBorderColor={rgb}{1,1,1}
# """,
# }



# latex_documents = [
#     (
#         'index',
#         'geodynamicandsurfaceprocesses.tex',
#         'Geodynamic and Surface Processes',
#         'Biraj Borgohain',
#         'manual',
#     ),
# ]

# # master_doc = "uplift_diffusion_n_substeps_to_pdf"
# master_doc = "Tools/coupling_ASPECT_Landlab/benchmark_test/uplift_diffusion_n_substeps_to_pdf"
# # latex_documents = [
# #     (
# #         "Tools/coupling_ASPECT_Landlab/benchmark_test/uplift_diffusion_n_substeps_to_pdf",
# #         "uplift_diffusion_n_substeps_to_pdf.tex",
# #         "Uplift Diffusion with Substeps",
# #         "Biraj Borgohain",
# #         "howto",
# #     ),
# # ]
# latex_toplevel_sectioning = "section"
# latex_elements = {
#     "tableofcontents": "",
# }
# latex_elements = {
#     "maketitle": r"""
# \maketitle
# """
# }

# latex_documents = [
#     (
#         "Tools/coupling_ASPECT_Landlab/benchmark_test/uplift_diffusion_n_substeps_to_pdf",
#         "uplift_diffusion_n_substeps_to_pdf.tex",
#         "",
#         "",
#         "howto",
#     ),
# ]

# latex_engine = "xelatex"

# # latex_elements = {
# #     "preamble": r"""
# # \usepackage{minted}
# # """
# # }
# highlight_language = "python"
# pygments_style = "friendly"

# latex_elements = {
#     "sphinxsetup": r"""
# verbatimwithframe=false,
# VerbatimColor={rgb}{0.96,0.96,0.96},
# VerbatimBorderColor={rgb}{1,1,1}
# """
# }

# project = "Math 335 Homework 1"
author = "Biraj Borgohain"

extensions = [
    "sphinx.ext.mathjax",
]

# root_doc = "Language/Science_language/ODE_calculus/course_MATH_3035/homework_assignments/index_pdf"

numfig = True

latex_engine = "pdflatex"

latex_documents = [
    (
        "Language/Science_language/ODE_calculus/course_MATH_3035/homework_assignments/index_pdf",
        "Math335_HW1.tex",
        "Math 335 Homework 1 Solutions",
        "Biraj Borgohain",
        "manual",
    ),
]

# project = "Math 335 Homework 1"

extensions = [
    "sphinx.ext.mathjax",
]

# root_doc = "index"
# root_doc = "Language/Science_language/ODE_calculus/course_MATH_3035/homework_assignments/index_html"


html_theme = "sphinx_rtd_theme"


import os
import shutil

figure_sources = {
    "0007": "/Users/biraj/cookbook_biraj/0007_20260910_asp310_landlab_pr43_3d_Xue3Dfastmodel-smaller_with_self_template_with_topography_with_field_sea0/outputs/0007_20260910_asp310_landlab_pr43_3d_Xue3Dfastmodel_smaller_with_self_template_with_topography_with_field_sea0/figure_landlab_vis",

    "0006": "/Users/biraj/cookbook_biraj/0006_20260908_asp310_landlab_pr43_3D_Xue_3Dfastmodel-smaller_with_self_template_with_topography_with_field/outputs/lla_check_landlab_xue_self_template_with_topography_with_field/figure_landlab_vis",

    "0005": "/Users/biraj/cookbook_biraj/0005_20260905_asp310_land_lla_check_3D_Ada_Tmodel_noWB_z_corrected/outputs/no_wb_z_corrected_3D_Ada_MAC_SA-INS/figure_landlab_vis",

    "0004": "/Users/biraj/cookbook_biraj/0004_20260905_asp310_landlab_pr43_3D_Xue_3Dfastmodel-smaller_with_self_template_with_topography/outputs/lla_check_landlab_xue_self_template_with_topography/figure_landlab_vis",

    "0001": "/Users/biraj/cookbook_biraj/0001_20260904_asp310_landlab_lla_check_2D_Ada_Tmodel_noWB_but_fault_in_prm_with_topography/figure_landlab_vis",

    "0003": "/Users/biraj/cookbook_biraj/0003_20260904_asp310_fastsca_lla_check_3D_Xue_3Dfastmodel_smaller_with_topography/figure_landlab_vis",
    
    "0010": "/Users/biraj/cookbook_biraj/0010_20260913_asp310_fastscape_pr43_3D_Xue_3Dfastsmaller_with_topography_field_sea0/0010_20260913_field_sea0/figure_landlab_vis"
}


# Documentation directory
docs_dir = os.path.dirname(__file__)

destination_root = os.path.join(
    docs_dir,
    "figure_landlab_vis",
)


for run_name, source in figure_sources.items():

    destination = os.path.join(
        destination_root,
        run_name,
    )

    if os.path.exists(source):
        shutil.rmtree(destination, ignore_errors=True)
        shutil.copytree(source, destination)