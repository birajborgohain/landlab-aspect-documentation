reset
set term png
set output 'Topography_error_benchmark_1_topo_untill.png'

set xrange [0:1]
set yrange [0:2]

set xlabel 'X [-]'
set ylabel 'Error topography [%]'

set title 'Surface topography error for benchmark 1'

set style line 1 lw 2 lc rgb "black"
set style line 2 lw 3 lc rgb "black"
set style line 3 lw 4 lc rgb "black"

set key top center

plot \
     'outputs/1_sine_zero_flux_topo_until/topography.00060' \
     u ($1):(abs((($4)-$3)/($4)*100.)) \
     ls 1 with linespoints t 't60', \
\
     'outputs/1_sine_zero_flux_topo_until/topography.00120' \
     u ($1):(abs((($4)-$3)/($4)*100.)) \
     ls 2 with linespoints t 't120', \
\
     'outputs/1_sine_zero_flux_topo_until/topography.00180' \
     u ($1):(abs((($4)-$3)/($4)*100.)) \
     ls 3 with linespoints t 't180'