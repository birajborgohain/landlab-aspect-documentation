
reset

set terminal pngcairo size 1800,1000 enhanced font "Helvetica,20"

set output 'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False_GHOST/result_benchmark_ASPECT/surface_topo_error_benchmark_ASPECT_1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False_GHOST.png'

set border lw 2
set tics out nomirror
set grid lw 1 lc rgb "#d9d9d9"

set xrange [0:1]
set yrange [0:2]

set xlabel 'X [-]' font ",22"
set ylabel 'Error topography [%]' font ",22"

set title 'Surface Topography Error Benchmark ASPECT +\n1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False_GHOST' font ",26"

set key top center box opaque font ",18"

set style line 1 lw 2 pt 7 ps 1.0 lc rgb "#1f77b4"
set style line 2 lw 3 pt 9 ps 1.0 lc rgb "#d62728"
set style line 3 lw 4 pt 5 ps 1.0 lc rgb "#2ca02c"

plot \
'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False_GHOST/topography.00060' u ($1):(abs((($4)-$3)/($4)*100.)) ls 1 with linespoints t 't=60', \
\
'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False_GHOST/topography.00120' u ($1):(abs((($4)-$3)/($4)*100.)) ls 2 with linespoints t 't=120', \
\
'outputs/1_sine_zero_flux_topo_until_D_0.25_set_closed_boundaries_at_grid_edges_False_GHOST/topography.00180' u ($1):(abs((($4)-$3)/($4)*100.)) ls 3 with linespoints t 't=180'