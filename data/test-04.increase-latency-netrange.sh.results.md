# Results of test-04.increase-latency-netrange.sh ⏱️

This test measures the scan performance with increasing router latency. Scan targets are the entire net ranges (and not only single hosts).

## Fixed parameters 🛠️

```bash
LATENCY_START=0
LATENCY_INCREMENT=10
LATENCY_MAX=120

DELAY=10
LOSS=3
BANDWIDTH=1000mbit
NUM_SUBNETS=3
NUM_SUBNET_HOSTS=5
LAB_DIR=test-04.increase-latency-netrange.sh.lab
RESULTS_DIR=test-04.increase-latency-netrange.sh.results
SCANNER_INPUT_FILE=lab-networks.txt
SECONDS_BETWEEN_STEPS=5

NMAP_BASE_PARAMS=-T4 -Pn -v --top-ports 1000 -sV
PARALLELISM=32    # sets --min-hostgroup (nmap) or --threads (nparallel)
```

## Results 📋

| Network LATENCY in ms | Nmap scan duration in secs | Nparallel scan duration in secs | equal results | Nmap ports | Nparallel ports
|---|---|---|---|---|---|
| 0 | 24.02 | 10.05 | yes | 15 | 15 | 
| 10 | 20.40 | 10.25 | yes | 15 | 15 | 
| 20 | 22.16 | 10.23 | false | 13 | 15 | 
| 30 | 21.57 | 10.04 | false | 14 | 15 | 
| 40 | 22.71 | 10.45 | yes | 15 | 15 | 
| 50 | 23.69 | 9.27 | yes | 15 | 15 | 
| 60 | 21.97 | 10.20 | yes | 15 | 15 | 
| 70 | 21.44 | 11.33 | false | 15 | 14 | 
| 80 | 23.11 | 10.14 | yes | 15 | 15 | 
| 90 | 22.11 | 10.29 | yes | 15 | 15 | 
| 100 | 23.23 | 10.07 | yes | 15 | 15 | 
| 110 | 38.06 | 34.04 | yes | 14 | 14 | 
| 120 | 22.26 | 10.38 | yes | 15 | 15 | 
