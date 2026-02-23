# Results of test-08.increase-hosts-netrange.sh ⏱️

This test measures the scan performance with an increasing number of hosts in each subnet. The number of subnets is 5 and stays constant. Scan targets are the entire net ranges (and not only single hosts).

## Fixed parameters 🛠️

```bash
NUM_SUBNET_HOSTS_START=4
NUM_SUBNET_HOSTS_INCREMENT=4
NUM_SUBNET_HOSTS_MAX=16

DELAY=10
LOSS=3
BANDWIDTH=1000mbit
NUM_SUBNETS=5
LAB_DIR=test-08.increase-hosts-netrange.sh.lab
RESULTS_DIR=test-08.increase-hosts-netrange.sh.results
SCANNER_INPUT_FILE=lab-networks.txt
SECONDS_BETWEEN_STEPS=5

NMAP_BASE_PARAMS=-T4 -Pn -v --top-ports 1000 -sV
PARALLELISM=32    # sets --min-hostgroup (nmap) or --threads (nparallel)
```

## Results 📋

| Host per subnet | Hosts total | Nmap scan duration in secs | Nparallel scan duration in secs | equal results | Nmap ports | Nparallel ports
|---|---|---|---|---|---|---|
| 4 | 20 | 29.10 | 10.22 | yes | 20 | 20 | 
| 8 | 40 | 54.32 | 18.25 | yes | 40 | 40 | 
| 12 | 60 | 75.66 | 20.39 | yes | 59 | 59 | 
| 16 | 80 | 109.95 | 27.74 | false | 79 | 80 | 
