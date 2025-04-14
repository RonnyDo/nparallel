#!/bin/bash

# scans hosts with growing network delay

# netowrk parameter
DELAY=10
LOSS=03
BANDWIDTH=100mbit
NUM_SUBNETS=3
NUM_SUBNET_HOSTS=5

# scan parameter
NMAP_BASE_PARAMS="-T4 -Pn -v --top-ports 100 -sV -O"
PARALLELISM=100 # either --min-hostgroup or --threads


# generate result file
echo "DELAY in ms\tnmap in secs\tnparallel in secs\n" > results.csv

DELAY_INCREMENT=20
for ((i_DELAY = 0 ; i_DELAY <= 100 ; i_DELAY=i_DELAY+DELAY_INCREMENT )) 
do 
    # generate lab
    echo "Generate lab files with DELAY=$i_DELAY"
    python ./generate-lab.py --delay $i_DELAY --loss $LOSS --bandwidth $BANDWIDTH --num-subnets $NUM_SUBNETS --num-subnet-hosts $NUM_SUBNET_HOSTS

    echo "Clean up old docker environment"
    sudo docker-compose down --remove-orphans
    sleep 10

    echo "Build new hosts"
    sudo docker-compose build
    sleep 10

    echo "Start hosts"
    sudo docker-compose up -d
    sleep 10

    echo "apply network traffic control"
    sudo sh ./traffic-control.sh add
    sleep 10


    # run scans
    echo "Testing nmap:"
    sudo nmap ${NMAP_BASE_PARAMS} --min-hostgroup=$PARALLELISM -oN log_nmap.txt -iL lab-networks.txt
    sleep 10

    echo "Testing nparallel:"
    sudo nparallel nmap ${NMAP_BASE_PARAMS} --threads $PARALLELISM --force-scan -iL lab-networks.txt | tee log_nparallel.txt
    # | grep "Finished" | cut -d " " -f 6
    sleep 10


    echo "Store results:"
    echo "${i_DELAY}\t$(cat log_nmap.txt | grep "scanned in" | cut -d " " -f 19)\t$(cat log_nparallel.txt | grep "Finished" | cut -d " " -f 6)" >> results.csv


    echo "Cleanup docker environment"
    sudo docker-compose down --remove-orphans > /dev/null
done