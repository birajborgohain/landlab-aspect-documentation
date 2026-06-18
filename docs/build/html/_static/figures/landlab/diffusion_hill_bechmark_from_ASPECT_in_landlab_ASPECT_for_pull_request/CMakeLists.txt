# Copyright (C) 2011 - 2024 by the authors of the ASPECT code.
#
# This file is part of ASPECT.
#
# ASPECT is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# ASPECT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ASPECT; see the file LICENSE.  If not see
# <http://www.gnu.org/licenses/>.

cmake_minimum_required(VERSION 3.13.4)

find_package(Aspect 2.1.0 QUIET HINTS ${Aspect_DIR} ../ ../../ $ENV{ASPECT_DIR})

if (NOT Aspect_FOUND)
  message(FATAL_ERROR "\n"
    "Could not find a valid ASPECT build/installation directory. "
    "Please specify the directory where you are building ASPECT by passing\n"
    "   -D Aspect_DIR=<path to ASPECT>\n"
    "to cmake or by setting the environment variable ASPECT_DIR in your shell "
    "before calling cmake. See the section 'How to write a plugin' in the "
    "manual for more information.")
endif ()

DEAL_II_INITIALIZE_CACHED_VARIABLES()

set(TARGET "analytical_topography")
project(${TARGET})

add_library(${TARGET} SHARED analytical_topography.cc)
ASPECT_SETUP_PLUGIN(${TARGET})

# --------------------------------------------------------
# Build prm generator
# --------------------------------------------------------

add_executable(make_1_sine_zero_flux_landlab_prm
               make_1_sine_zero_flux_landlab_prm.cc)

# --------------------------------------------------------
# Generate modified benchmark prm automatically
# --------------------------------------------------------

add_custom_command(
  OUTPUT 1_sine_zero_flux_landlab.prm

  COMMAND $<TARGET_FILE:make_1_sine_zero_flux_landlab_prm>

  DEPENDS make_1_sine_zero_flux_landlab_prm.cc
          1_sine_zero_flux.prm

  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}

  COMMENT "Generating Landlab benchmark prm"
)

add_custom_target(generate_landlab_prm ALL
                  DEPENDS 1_sine_zero_flux_landlab.prm)