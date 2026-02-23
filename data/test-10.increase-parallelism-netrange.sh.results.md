# Results of test-10.increase-parallelism-netrange.sh ⏱️

This test measures the scan performance with increasing scanner parallelism (--min-hostgroup (nmap) or --threads (nparallel)). Scan targets are the entire net ranges (and not only single hosts).

## Fixed parameters 🛠️

```bash
PARALLELISM_START=2
PARALLELISM_INCREMENT=2
PARALLELISM_MAX=32

DELAY=10
LOSS=3
LATENCY=200
BANDWIDTH=1000mbit
NUM_SUBNETS=3
NUM_SUBNET_HOSTS=5
LAB_DIR=test-10.increase-parallelism-netrange.sh.lab
RESULTS_DIR=test-10.increase-parallelism-netrange.sh.results
SCANNER_INPUT_FILE=lab-networks.txt
SECONDS_BETWEEN_STEPS=5

NMAP_BASE_PARAMS=-T4 -Pn -v --top-ports 100 -sV
```

## Results 📋

| threads/hostgroup-size | Nmap scan duration in secs | Nparallel scan duration in secs | equal results | Nmap ports | Nparallel ports
|---|---|---|---|---|---|
| 2 | 10.59 | 62.41 | yes | 15 | 15 | 
| 4 | 11.34 | 31.81 | false | 14 | 15 | 
| 6 | 10.45 | 23.00 | yes | 15 | 15 | 
| 8 | 11.66 | 16.76 | false | 15 | 14 | 
| 10 | 12.43 | 16.61 | yes | 15 | 15 | 
| 12 | 10.05 | 16.36 | yes | 15 | 15 | 
| 14 | 12.00 | 15.20 | yes | 15 | 15 | 
| 16 | 12.85 | 8.93 | yes | 15 | 15 | 
| 18 | 10.19 | 9.88 | yes | 15 | 15 | 
| 20 | 9.63 | 8.20 | yes | 13 | 13 | 
| 22 | 11.43 | 9.81 | false | 15 | 14 | 
| 24 | 10.59 | 8.99 | yes | 15 | 15 | 
| 26 | 9.95 | 8.80 | yes | 15 | 15 | 
| 28 | 9.46 | 9.90 | yes | 15 | 15 | 
| 30 | 13.68 | 8.88 | yes | 15 | 15 | 
| 32 | 9.88 | 9.89 | false | 15 | 14 | 
