#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

void replace_all(std::string &text,
                 const std::string &old_str,
                 const std::string &new_str)
{
    size_t pos = 0;

    while ((pos = text.find(old_str, pos)) != std::string::npos)
    {
        text.replace(pos, old_str.length(), new_str);
        pos += new_str.length();
    }
}

int main()
{
    const std::string input_file  = "1_sine_zero_flux.prm";
    const std::string output_file = "1_sine_zero_flux_landlab.prm";

    std::ifstream in(input_file);

    if (!in)
    {
        std::cerr << "Cannot open: " << input_file << std::endl;
        return 1;
    }

    std::stringstream buffer;
    buffer << in.rdbuf();

    std::string text = buffer.str();

    // -----------------------------------------------------
    // Replace geometry
    // -----------------------------------------------------

    replace_all(
        text,
R"(  subsection Box
    set X extent = 1
    set Y extent = 1
  end)",

R"(  subsection Box
    set X extent = 3
    set Y extent = 3
  end)"
    );

    // -----------------------------------------------------
    // Replace mesh deformation
    // -----------------------------------------------------

    replace_all(
        text,
R"(subsection Mesh deformation
  set Mesh deformation boundary indicators = top: diffusion
  set Additional tangential mesh velocity boundary indicators = left, right

  subsection Diffusion
    # The diffusivity
    set Hillslope transport coefficient = 0.25
  end
end)",

R"(subsection Mesh deformation
  set Mesh deformation boundary indicators = top: Landlab
  set Additional tangential mesh velocity boundary indicators =

  subsection Landlab
    set MPI ranks for Landlab = 1
    set Script name           = 1_shine_zero_flux_landlab_import-template
    set Script path           = .
    set Script argument       =
  end
end)"
    );

    // -----------------------------------------------------
    // Remove analytical topography
    // -----------------------------------------------------

    replace_all(
        text,

R"(  subsection Initial topography model
    set Model name = function

    subsection Function
      set Function constants = A=0.075, L=1.
      set Function expression = \
                                A * sin(x*pi)
    end
  end)",

        ""
    );

    // // -----------------------------------------------------
    // // Remove analytical topography postprocessor
    // // -----------------------------------------------------

    // replace_all(
    //     text,
    //     "visualization, analytical topography",
    //     "visualization"
    // );

    // -----------------------------------------------------
    // Change output directory
    // -----------------------------------------------------

    replace_all(
        text,
        "output-1_sine_zero_flux/",
        "output-1_sine_zero_flux_landlab/"
    );

    // -----------------------------------------------------
    // Write output
    // -----------------------------------------------------

    std::ofstream out(output_file);

    out << text;

    std::cout << "Created: "
              << output_file
              << std::endl;

    return 0;
}