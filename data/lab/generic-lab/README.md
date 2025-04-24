# Nparallal Lab 🧪

The nparallel lab simulates a network with different subnets and hosts. It's meant to compare performance of nparallel with other network tools, like nmap.

The lab not only simulates the structure of a network but also real-life parameters like bandwidth and response delay. This is done by a router which connects the scanner-network with the target-network. The router can be artificially slowed down using different delaying and bandwidth parameters, like shown below. 

## Generate a custom lab

Use ```python generate-lab.py``` to generate a docker lab enviroment with custom parameters:
```
usage: generate-lab.py [-h] [--delay DELAY] [--loss LOSS] [--bandwidth BANDWIDTH] [--num-subnets NUM_SUBNETS]
                       [--num-subnet-hosts NUM_SUBNET_HOSTS] [--out-dir OUT_DIR]

options:
  -h, --help            show this help message and exit
  --delay DELAY         Network delay in milliseconds
  --loss LOSS           Network package loss rate in percent
  --bandwidth BANDWIDTH
                        Network bandwith of each hosts in kbit, mbit or gbit
  --num-subnets NUM_SUBNETS
                        Number of subnets. Default is 2, starting from 10.0.1.0/24
  --num-subnet-hosts NUM_SUBNET_HOSTS
                        Number of hosts per subnet. Default is 2, starting from 10.0.1.101
  --out-dir OUT_DIR     Output directory of generated files
```
The following tools are required:
```bash
# on Debian
apt update && apt install docker.io docker-compose
```

## Example
### Generate lab files

The following command generates a lab environment with **3 subnets** and **10 hosts in each subnet**. Each host has a limited **bandwidth of 100kbit**, a response **delay of 200ms** and a **20% chance of package-loss**:
```
python ./generate-lab.py --num-subnets 3 --num-subnet-hosts 10 --bandwidth 100kbit --delay 200 --loss 20
```
### Spin up infrastructure

```bash
# switch to lab directory
cd ./generic-lab
# clean up old containers and networks
sudo docker-compose down --remove-orphans
sudo docker network prune --force
# build images
sudo docker-compose build
# spin up environment
sudo docker-compose up -d 
# apply network traffic limitations to containers 
sudo sh ./traffic-control.sh add
```

### Test setup (optional)
To check if it worked, log in to the ```scanner```-container and use curl, to request the webpage on http://10.0.1.101:
```bash
sudo docker exec -it scanner /bin/bash
curl http://10.0.1.101
```

To check if the bandwidth limitation is active, try to download the file http://10.0.1.101/bigfile.zip.

```bash
curl -L http://10.0.1.101/bigfile.zip --output /tmp/bigfile.zip
```
The download speed should be very limited.

To see if the response delay and package loss is active, you can use a ping command:

```bash
ping 10.0.1.101
```
The response time is exactly 200ms and some packages get lost, like package #3 in the following example:
```bash
PING 10.0.1.101 (10.0.1.101) 56(84) bytes of data.
64 bytes from 10.0.1.101: icmp_seq=1 ttl=64 time=200 ms
64 bytes from 10.0.1.101: icmp_seq=2 ttl=64 time=200 ms
64 bytes from 10.0.1.101: icmp_seq=4 ttl=64 time=200 ms
64 bytes from 10.0.1.101: icmp_seq=5 ttl=64 time=200 ms
```

### Run tests
Use the lab environment to run tests from your host system, like:
```bash
nparallel nmap -T4 -Pn --top-ports 1000 -sV -O --force-scan -iL lab-networks.txt
```

## Predifined tests

The lab comes also with some predefinied tests, which compares the performance of nmap with nparallel in different network setups.

The tests can simply be run from the terminal, like:
```bash
./test.compare_delay.sh
```
During the test, the lab environment will repeatly be build up and cleaned up.