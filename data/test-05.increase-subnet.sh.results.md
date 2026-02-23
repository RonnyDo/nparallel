# Results of test-05.increase-subnet.sh ⏱️

This test measures the scan performance while increasing the number of subnets. Scan targets are the exact hosts (and not the network range).

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
LAB_DIR=test-05.increase-subnet.sh.lab
RESULTS_DIR=test-05.increase-subnet.sh.results
SCANNER_INPUT_FILE=lab-hosts.txt
SECONDS_BETWEEN_STEPS=5

NMAP_BASE_PARAMS=-T4 -Pn -v --top-ports 1000 -sV
PARALLELISM=32    # sets --min-hostgroup (nmap) or --threads (nparallel)
```

## Results 📋

| Number of subnets | Hosts total | Nmap scan duration in secs | Nparallel scan duration in secs | equal results | Nmap ports | Nparallel ports
|---|---|---|---|---|---|---|
| 3 | 15 | 24.38 | 10.37 | yes | 15 | 15 | 
| 6 | 30 | 37.00 | 11.19 | yes | 30 | 30 | 
| 9 | 45 | 56.01 | 19.39 | false | 45 | 44 | 
| 12 | 60 | 72.84 | 19.42 | false | 59 | 60 | 
| 15 | 75 | 101.36 | 27.26 | false | 75 | 74 | 
