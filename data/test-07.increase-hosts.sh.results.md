# Results of test-07.increase-hosts.sh ⏱️

This test measures the scan performance with an increasing number of hosts in each subnet. The number of subnets is 3 and stays constant. Scan targets are the exact hosts (and not the network range).

## Fixed parameters 🛠️

```bash
NUM_SUBNET_HOSTS_START=5
NUM_SUBNET_HOSTS_INCREMENT=5
NUM_SUBNET_HOSTS_MAX=25

DELAY=10
LOSS=3
BANDWIDTH=1000mbit
NUM_SUBNETS=3
LAB_DIR=test-07.increase-hosts.sh.lab
RESULTS_DIR=test-07.increase-hosts.sh.results
SCANNER_INPUT_FILE=lab-hosts.txt
SECONDS_BETWEEN_STEPS=5

NMAP_BASE_PARAMS=-T4 -Pn -v --top-ports 1000 -sV
PARALLELISM=32    # sets --min-hostgroup (nmap) or --threads (nparallel)
```

## Results 📋

| Host per subnet | Hosts total | Nmap scan duration in secs | Nparallel scan duration in secs | equal results | Nmap ports | Nparallel ports
|---|---|---|---|---|---|---|
| 5 | 15 | 22.57 | 12.05 | yes | 15 | 15 | 
| 10 | 30 | 38.04 | 10.55 | yes | 30 | 30 | 
| 15 | 45 | 60.26 | 18.55 | yes | 45 | 45 | 
| 20 | 60 | 75.47 | 20.59 | false | 60 | 58 | 
| 25 | 75 | 100.82 | 26.65 | yes | 75 | 75 | 
