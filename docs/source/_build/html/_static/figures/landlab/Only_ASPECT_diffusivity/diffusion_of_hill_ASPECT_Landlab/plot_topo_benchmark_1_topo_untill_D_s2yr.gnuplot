reset

# -----------------------------------------------------------------------------
# Output
# -----------------------------------------------------------------------------
set terminal pngcairo size 1800,1000 enhanced font "Helvetica,20"
set output 'Topography_benchmark_1_topo_until_D_s2yr.png'

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
set title 'Benchmark 1: Surface Topography Evolution (Coupled ASPECT-Landlab, D = 0.25 /s2yr \~ 7x10^{-9} m^2/s)' font ",26"

# -----------------------------------------------------------------------------
# Legend
# -----------------------------------------------------------------------------
set key top right box opaque spacing 1.3 font ",18"

# -----------------------------------------------------------------------------
# Matching color pairs
# Solid + points -> ASPECT
# Dashed          -> Analytical
# -----------------------------------------------------------------------------

# --- t = 60 ---------------------------------------------------
set style line 1  lt 1 lw 5 pt 7 ps 1.3 lc rgb "#1f77b4"
set style line 11 dt 2 lw 6           lc rgb "#1f77b4"

# --- t = 120 --------------------------------------------------
set style line 2  lt 1 lw 5 pt 9 ps 1.3 lc rgb "#d62728"
set style line 12 dt 2 lw 6           lc rgb "#d62728"

# --- t = 180 --------------------------------------------------
set style line 3  lt 1 lw 5 pt 5 ps 1.3 lc rgb "#2ca02c"
set style line 13 dt 2 lw 6           lc rgb "#2ca02c"

# -----------------------------------------------------------------------------
# Margins
# -----------------------------------------------------------------------------
set lmargin 10
set rmargin 4
set tmargin 3
set bmargin 5

# -----------------------------------------------------------------------------
# Plot
# -----------------------------------------------------------------------------
plot \
'outputs/1_sine_zero_flux_topo_until_D_S2yr/topography.00060' \
    u 1:3 w lp ls 1  t 'ASPECT t=60', \
\
'outputs/1_sine_zero_flux_topo_until_D_S2yr/topography.00060' \
    u 1:4 w l  ls 11 t 'Analytical t=60', \
\
'outputs/1_sine_zero_flux_topo_until_D_S2yr/topography.00120' \
    u 1:3 w lp ls 2  t 'ASPECT t=120', \
\
'outputs/1_sine_zero_flux_topo_until_D_S2yr/topography.00120' \
    u 1:4 w l  ls 12 t 'Analytical t=120', \
\
'outputs/1_sine_zero_flux_topo_until_D_S2yr/topography.00180' \
    u 1:3 w lp ls 3  t 'ASPECT t=180', \
\
'outputs/1_sine_zero_flux_topo_until_D_S2yr/topography.00180' \
    u 1:4 w l  ls 13 t 'Analytical t=180'