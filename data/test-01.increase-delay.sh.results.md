# Results of test-01.increase-delay.sh ⏱️

This test measures the scan performance with increasing router delay. Scan targets are the exact hosts (and not the network range).

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
LAB_DIR=test-01.increase-delay.sh.lab
RESULTS_DIR=test-01.increase-delay.sh.results
SCANNER_INPUT_FILE=lab-hosts.txt
SECONDS_BETWEEN_STEPS=5

NMAP_BASE_PARAMS=-T4 -Pn -v --top-ports 1000 -sV
PARALLELISM=32    # sets --min-hostgroup (nmap) or --threads (nparallel)
```

## Results 📋

| Network DELAY in ms | Nmap scan duration in secs | Nparallel scan duration in secs | equal results | Nmap ports | Nparallel ports
|---|---|---|---|---|---|
| 0 | 12.85 | 10.09 | yes | 15 | 15 | 
| 10 | 23.07 | 10.44 | false | 15 | 14 | 
| 20 | 30.19 | 10.89 | false | 14 | 15 | 
| 30 | 49.62 | 13.73 | false | 15 | 14 | 
| 40 | 47.14 | 12.09 | false | 14 | 15 | 
| 50 | 54.31 | 12.74 | yes | 15 | 15 | 
| 60 | 61.42 | 13.83 | yes | 15 | 15 | 
| 70 | 69.88 | 14.98 | false | 14 | 15 | 
| 80 | 77.76 | 14.97 | yes | 15 | 15 | 
| 90 | 85.74 | 16.98 | yes | 15 | 15 | 
| 100 | 98.59 | 16.87 | yes | 15 | 15 | 
