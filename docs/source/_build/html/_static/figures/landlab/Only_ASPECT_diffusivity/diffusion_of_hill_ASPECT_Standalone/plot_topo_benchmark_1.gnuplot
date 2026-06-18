reset

# -----------------------------------------------------------------------------
# Terminal / Output
# -----------------------------------------------------------------------------
set terminal pngcairo enhanced size 1800,1000 font "Helvetica,20"
set output 'Topography_benchmark_1_stadalone.png'

# -----------------------------------------------------------------------------
# General appearance
# -----------------------------------------------------------------------------
set border lw 2
set tics out nomirror
set grid lw 1 lc rgb "#d9d9d9"

set xrange [0:1]
set yrange [0:0.1]

set xlabel 'X [-]' font ",22"
set ylabel 'Topography [m]' font ",22"

# -----------------------------------------------------------------------------
# Title
# -----------------------------------------------------------------------------
set title 'Benchmark 1: Surface Topography Evolution (Standalone ASPECT Diffusion Model)' font ",24"

# -----------------------------------------------------------------------------
# Legend
# -----------------------------------------------------------------------------
set key top right box opaque spacing 1.3 font ",18"

# -----------------------------------------------------------------------------
# ASPECT styles (original strong appearance)
# -----------------------------------------------------------------------------
set style line 1  lt 1 lw 8 pt 7 ps 1.2 lc rgb "black"
set style line 2  lt 1 lw 9 pt 9 ps 1.2 lc rgb "black"
set style line 3  lt 1 lw 10 pt 5 ps 1.2 lc rgb "black"

# -----------------------------------------------------------------------------
# Analytical styles
# Different colors + dashed
# -----------------------------------------------------------------------------

set style line 4  dt 2 lw 7 lc rgb "#1f77b4"   # blue
set style line 5  dt 2 lw 8 lc rgb "#d62728"   # red
set style line 6  dt 2 lw 9 lc rgb "#2ca02c"   # green

# -----------------------------------------------------------------------------
# Compute Mean Absolute Difference
# column 3 = ASPECT
# column 4 = Analytical
# -----------------------------------------------------------------------------

stats '1_sine_zero_flux/topography.00060' \
    using (abs($3-$4)) nooutput
mad60 = STATS_mean

stats '1_sine_zero_flux/topography.00120' \
    using (abs($3-$4)) nooutput
mad120 = STATS_mean

stats '1_sine_zero_flux/topography.00180' \
    using (abs($3-$4)) nooutput
mad180 = STATS_mean

# -----------------------------------------------------------------------------
# Display MAD values
# -----------------------------------------------------------------------------

set label 1 sprintf("MAD t=60  = %.3e m", mad60) \
    at graph 0.02,0.92 tc rgb "#1f77b4" font ",18"

set label 2 sprintf("MAD t=120 = %.3e m", mad120) \
    at graph 0.02,0.87 tc rgb "#d62728" font ",18"

set label 3 sprintf("MAD t=180 = %.3e m", mad180) \
    at graph 0.02,0.82 tc rgb "#2ca02c" font ",18"

# -----------------------------------------------------------------------------
# Plot
# -----------------------------------------------------------------------------

plot \
'1_sine_zero_flux/topography.00060' \
    u 1:3 w lp ls 1 t 'ASPECT t=60', \
\
'1_sine_zero_flux/topography.00120' \
    u 1:3 w lp ls 2 t 'ASPECT t=120', \
\
'1_sine_zero_flux/topography.00180' \
    u 1:3 w lp ls 3 t 'ASPECT t=180', \
\
'1_sine_zero_flux/topography.00060' \
    u 1:4 w l ls 4 t 'Analytical t=60', \
\
'1_sine_zero_flux/topography.00120' \
    u 1:4 w l ls 5 t 'Analytical t=120', \
\
'1_sine_zero_flux/topography.00180' \
    u 1:4 w l ls 6 t 'Analytical t=180'