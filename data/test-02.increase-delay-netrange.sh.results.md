# Results of test-02.increase-delay-netrange.sh ⏱️

This test measures the scan performance with increasing router delay. Scan targets are the entire net ranges (and not only single hosts).

## Fixed parameters 🛠️

```bash
DELAY_START=0
DELAY_INCREMENT=10
DELAY_MAX=100

LOSS=3
LATENCY=200
BANDWIDTH=1000mbit
NUM_SUBNETS=3
NUM_SUBNET_HOSTS=5
LAB_DIR=test-02.increase-delay-netrange.sh.lab
RESULTS_DIR=test-02.increase-delay-netrange.sh.results
SCANNER_INPUT_FILE=lab-networks.txt
SECONDS_BETWEEN_STEPS=5

NMAP_BASE_PARAMS=-T4 -Pn -v --top-ports 1000 -sV
PARALLELISM=32    # sets --min-hostgroup (nmap) or --threads (nparallel)
```

## Results 📋

| Network DELAY in ms | Nmap scan duration in secs | Nparallel scan duration in secs | equal results | Nmap ports | Nparallel ports
|---|---|---|---|---|---|
| 0 | 14.17 | 10.05 | false | 15 | 14 | 
| 10 | 22.81 | 10.13 | yes | 15 | 15 | 
| 20 | 31.40 | 10.70 | yes | 15 | 15 | 
| 30 | 50.00 | 12.11 | yes | 15 | 15 | 
| 40 | 55.75 | 34.13 | yes | 14 | 14 | 
| 50 | 61.09 | 34.05 | yes | 14 | 14 | 
| 60 | 60.04 | 14.02 | yes | 15 | 15 | 
| 70 | 77.71 | 34.19 | yes | 14 | 14 | 
| 80 | 81.33 | 16.09 | false | 14 | 15 | 
| 90 | 86.83 | 16.53 | yes | 15 | 15 | 
| 100 | 97.29 | 18.25 | yes | 15 | 15 | 
