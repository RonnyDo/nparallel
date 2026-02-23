# Results of test-06.increase-subnet-netrange.sh ⏱️

This test measures the scan performance while increasing the number of subnets. Scan targets are the entire net ranges (and not only single hosts).

## Fixed parameters 🛠️

```bash
NUM_SUBNET_START=3
NUM_SUBNET_INCREMENT=3
NUM_SUBNET_MAX=15

DELAY=10
LATENCY=200
LOSS=3
BANDWIDTH=1000mbit
NUM_SUBNET_HOSTS=5
LAB_DIR=test-06.increase-subnet-netrange.sh.lab
RESULTS_DIR=test-06.increase-subnet-netrange.sh.results
SCANNER_INPUT_FILE=lab-networks.txt
SECONDS_BETWEEN_STEPS=5

NMAP_BASE_PARAMS=-T4 -Pn -v --top-ports 1000 -sV
PARALLELISM=32    # sets --min-hostgroup (nmap) or --threads (nparallel)
```

## Results 📋 🕒

| Number of subnets | Hosts total | Nmap scan duration in secs | Nparallel scan duration in secs | equal results | Nmap ports | Nparallel ports
|---|---|---|---|---|---|---|
| 3 | 15 | 22.84 | 11.12 | false | 14 | 15 | 
| 6 | 30 | 38.81 | 11.62 | yes | 30 | 30 | 
| 9 | 45 | 57.64 | 18.39 | yes | 45 | 45 | 
| 12 | 60 | 72.13 | 19.64 | false | 60 | 58 | 
| 15 | 75 | 100.92 | 28.29 | false | 75 | 74 | 
