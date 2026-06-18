reset

# -----------------------------------------------------------------------------
# Output
# -----------------------------------------------------------------------------
set terminal pngcairo size 1800,1000 enhanced font "Helvetica,20"
set output 'Topography_benchmark_1_topo_until_boundary_false.png'

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

set title 'Benchmark 1: Surface Topography Evolution (Coupled ASPECT-Landlab with D = 0.25) boundary False' font ",26"

# -----------------------------------------------------------------------------
# Legend
# -----------------------------------------------------------------------------
set key top right box opaque spacing 1.3 font ",18"

# -----------------------------------------------------------------------------
# Matching color pairs
# -----------------------------------------------------------------------------

# --- t = 60 ---------------------------------------------------
set style line 1  lt 1 lw 4 pt 7 ps 1.2 lc rgb "#1f77b4"
set style line 11 dt 2 lw 5           lc rgb "#1f77b4"

# --- t = 120 --------------------------------------------------
set style line 2  lt 1 lw 4 pt 9 ps 1.2 lc rgb "#d62728"
set style line 12 dt 2 lw 5           lc rgb "#d62728"

# --- t = 180 --------------------------------------------------
set style line 3  lt 1 lw 4 pt 5 ps 1.2 lc rgb "#2ca02c"
set style line 13 dt 2 lw 5           lc rgb "#2ca02c"

# -----------------------------------------------------------------------------
# Compute Mean Absolute Difference
# column 3 = ASPECT
# column 4 = Analytical
# -----------------------------------------------------------------------------

stats 'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False/topography.00060' \
    using (abs($3-$4)) nooutput
mad60 = STATS_mean

stats 'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False/topography.00120' \
    using (abs($3-$4)) nooutput
mad120 = STATS_mean

stats 'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False/topography.00180' \
    using (abs($3-$4)) nooutput
mad180 = STATS_mean

# -----------------------------------------------------------------------------
# Display MAD values on plot
# -----------------------------------------------------------------------------

set label 1 sprintf("MAD t=60  = %.3e m", mad60)  at graph 0.02,0.92 tc rgb "#1f77b4" font ",18"
set label 2 sprintf("MAD t=120 = %.3e m", mad120) at graph 0.02,0.87 tc rgb "#d62728" font ",18"
set label 3 sprintf("MAD t=180 = %.3e m", mad180) at graph 0.02,0.82 tc rgb "#2ca02c" font ",18"

# -----------------------------------------------------------------------------
# Plot
# -----------------------------------------------------------------------------

plot \
'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False/topography.00060' \
    u 1:3 w lp ls 1  t 'ASPECT t=60', \
\
'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False/topography.00060' \
    u 1:4 w l  ls 11 t 'Analytical t=60', \
\
'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False/topography.00120' \
    u 1:3 w lp ls 2  t 'ASPECT t=120', \
\
'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False/topography.00120' \
    u 1:4 w l  ls 12 t 'Analytical t=120', \
\
'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False/topography.00180' \
    u 1:3 w lp ls 3  t 'ASPECT t=180', \
\
'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False/topography.00180' \
    u 1:4 w l  ls 13 t 'Analytical t=180'