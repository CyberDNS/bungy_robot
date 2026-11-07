#!/bin/bash
# Logs load, temperature and throttling of the Pi every few seconds (run it on the Pi).
#   tools/log_load.sh [interval_s] [outfile]
# Columns: time, load1, cpu% (all cores), temp, arm clock, get_throttled
interval=${1:-5}
out=${2:-$HOME/load_$(date +%Y%m%d_%H%M%S).csv}
echo "time,load1,cpu_percent,temp_c,arm_mhz,throttled" | tee "$out"
read -r _ u1 n1 s1 i1 w1 q1 sq1 _ < /proc/stat
while true; do
    sleep "$interval"
    read -r _ u2 n2 s2 i2 w2 q2 sq2 _ < /proc/stat
    busy=$(( (u2+n2+s2+q2+sq2) - (u1+n1+s1+q1+sq1) ))
    total=$(( busy + (i2+w2) - (i1+w1) ))
    cpu=$(( total > 0 ? 100 * busy / total : 0 ))
    u1=$u2; n1=$n2; s1=$s2; i1=$i2; w1=$w2; q1=$q2; sq1=$sq2
    temp=$(vcgencmd measure_temp | sed "s/temp=//;s/'C//")
    clk=$(( $(vcgencmd measure_clock arm | cut -d= -f2) / 1000000 ))
    thr=$(vcgencmd get_throttled | cut -d= -f2)
    echo "$(date +%T),$(cut -d' ' -f1 /proc/loadavg),$cpu,$temp,$clk,$thr" | tee -a "$out"
done
