# Device to be limited
DEVICE=eth0

# Average rate you want
RATE=500mbit

# Amount of burst data. I suggest RATE / 10
BURST=50mbit
tc qdisc del dev $DEVICE root
tc qdisc add dev $DEVICE root handle 1: tbf rate $RATE burst $BURST latency 1s
tc qdisc add dev $DEVICE parent 1: handle 11: pfifo_fast