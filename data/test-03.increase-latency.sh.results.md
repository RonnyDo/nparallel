# Results of test-03.increase-latency.sh ⏱️

This test measures the scan performance with increasing router latency. Scan targets are the exact hosts (and not the network range).

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
LAB_DIR=test-03.increase-latency.sh.lab
RESULTS_DIR=test-03.increase-latency.sh.results
SCANNER_INPUT_FILE=lab-hosts.txt
SECONDS_BETWEEN_STEPS=5

NMAP_BASE_PARAMS=-T4 -Pn -v --top-ports 1000 -sV
PARALLELISM=32    # sets --min-hostgroup (nmap) or --threads (nparallel)
```

## Results 📋

| Network LATENCY in ms | Nmap scan duration in secs | Nparallel scan duration in secs | equal results | Nmap ports | Nparallel ports
|---|---|---|---|---|---|
| 0 | 22.45 | 11.45 | yes | 15 | 15 | 
| 10 | 21.20 | 10.16 | false | 15 | 14 | 
| 20 | 22.19 | 10.26 | false | 14 | 15 | 
| 30 | 23.30 | 10.99 | yes | 15 | 15 | 
| 40 | 24.17 | 10.16 | yes | 15 | 15 | 
| 50 | 23.61 | 10.34 | yes | 15 | 15 | 
| 60 | 39.37 | 34.16 | yes | 14 | 14 | 
| 70 | 23.04 | 12.34 | yes | 15 | 15 | 
| 80 | 24.70 | 10.33 | yes | 15 | 15 | 
| 90 | 20.43 | 10.98 | yes | 15 | 15 | 
| 100 | 21.55 | 11.27 | yes | 15 | 15 | 
| 110 | 21.99 | 9.97 | yes | 15 | 15 | 
| 120 | 23.33 | 10.25 | yes | 15 | 15 | 
