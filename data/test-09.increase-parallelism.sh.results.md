# Results of test-09.increase-parallelism.sh ⏱️

This test measures the scan performance with increasing scanner parallelism (--min-hostgroup (nmap) or --threads (nparallel)). Scan targets are the exact hosts (and not the network range).

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
LAB_DIR=test-09.increase-parallelism.sh.lab
RESULTS_DIR=test-09.increase-parallelism.sh.results
SCANNER_INPUT_FILE=lab-hosts.txt
SECONDS_BETWEEN_STEPS=5

NMAP_BASE_PARAMS=-T4 -Pn -v --top-ports 100 -sV
```

## Results 📋

| threads/hostgroup-size | Nmap scan duration in secs | Nparallel scan duration in secs | equal results | Nmap ports | Nparallel ports
|---|---|---|---|---|---|
| 2 | 12.39 | 61.43 | yes | 15 | 15 | 
| 4 | 10.36 | 31.83 | false | 15 | 14 | 
| 6 | 9.52 | 23.25 | yes | 15 | 15 | 
| 8 | 11.52 | 16.88 | yes | 15 | 15 | 
| 10 | 12.14 | 16.42 | yes | 15 | 15 | 
| 12 | 11.45 | 15.40 | yes | 15 | 15 | 
| 14 | 11.39 | 16.32 | yes | 15 | 15 | 
| 16 | 10.84 | 8.93 | yes | 15 | 15 | 
| 18 | 12.61 | 9.11 | yes | 15 | 15 | 
| 20 | 10.46 | 9.89 | yes | 15 | 15 | 
| 22 | 13.51 | 9.00 | yes | 15 | 15 | 
| 24 | 11.06 | 10.34 | false | 15 | 14 | 
| 26 | 13.37 | 8.84 | yes | 15 | 15 | 
| 28 | 11.46 | 9.92 | yes | 15 | 15 | 
| 30 | 9.65 | 9.66 | yes | 15 | 15 | 
| 32 | 12.76 | 9.87 | yes | 15 | 15 | 
