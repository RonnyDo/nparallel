#!/bin/bash

# get the name of the script
test_name=$(basename "$0")

# network parameter
NUM_SUBNET_START=1
NUM_SUBNET_INCREMENT=1
NUM_SUBNET_MAX=10

DELAY=20
LATENCY=500
LOSS=3
BANDWIDTH=1000mbit
NUM_SUBNET_HOSTS=5
LAB_DIR=$test_name.lab
RESULTS_DIR=$test_name.results
SCANNER_INPUT_FILE=lab-networks.txt
SECONDS_BETWEEN_STEPS=5 # seconds to sleep between each command; 10 secs should a save


# scan parameter
#NMAP_BASE_PARAMS="-T4 -Pn -v --top-ports 100 -sV -O"
NMAP_BASE_PARAMS="-T4 -Pn -v --top-ports 1000 -sV"
PARALLELISM=100     # sets --min-hostgroup (nmap) or --threads (nparallel)

# clean up all results
sudo rm -rf $RESULTS_DIR
mkdir $RESULTS_DIR

# generate result file
cat <<EOT >> $RESULTS_DIR/$test_name.results.md
# Results of $test_name

This test measures the scan performance while increasing the number of subnets. Scan targets are the entire net ranges (and not only single hosts).

## Fixed parameters:

\`\`\`bash
NUM_SUBNET_START=$NUM_SUBNET_START
NUM_SUBNET_INCREMENT=$NUM_SUBNET_INCREMENT
NUM_SUBNET_MAX=$NUM_SUBNET_MAX

DELAY=$DELAY
LATENCY=$LATENCY
LOSS=$LOSS
BANDWIDTH=$BANDWIDTH
NUM_SUBNET_HOSTS=$NUM_SUBNET_HOSTS
LAB_DIR=$LAB_DIR
RESULTS_DIR=$RESULTS_DIR
SCANNER_INPUT_FILE=$SCANNER_INPUT_FILE
SECONDS_BETWEEN_STEPS=$SECONDS_BETWEEN_STEPS

NMAP_BASE_PARAMS=$NMAP_BASE_PARAMS
PARALLELISM=$PARALLELISM    # sets --min-hostgroup (nmap) or --threads (nparallel)
\`\`\`

## Results

| NUM_SUBNET | Nmap scan duration in secs | Nparallel scan duration in secs |
|---|---|---|
EOT


for ((CURRENT_NUM_SUBNET = NUM_SUBNET_START ; CURRENT_NUM_SUBNET <= NUM_SUBNET_MAX ; CURRENT_NUM_SUBNET=CURRENT_NUM_SUBNET+NUM_SUBNET_INCREMENT )) 
do 
    # generate lab
    echo -e "\n\n\n###### Generate lab files with NUM_SUBNET=$CURRENT_NUM_SUBNET ######\n"
    sudo rm -rf $LAB_DIR
    sleep $SECONDS_BETWEEN_STEPS
    python ./generate-lab.py --delay $DELAY --latency $LATENCY --loss $LOSS --bandwidth $BANDWIDTH --num-subnets $CURRENT_NUM_SUBNET --num-subnet-hosts $NUM_SUBNET_HOSTS --out-dir $LAB_DIR

    cd $LAB_DIR

    echo -e "\n\n\n###### Clean up old docker environment ######\n"
    sudo docker-compose down --remove-orphans
    sudo docker container prune --force
    sudo docker network prune --force
    sleep $SECONDS_BETWEEN_STEPS

    echo -e "\n\n\n###### Build new hosts ######\n"
    sudo docker-compose build
    sleep $SECONDS_BETWEEN_STEPS

    echo -e "\n\n\n###### Start hosts ######\n"
    sudo docker-compose up -d
    sleep 15 # manually set because a to short time would lead to the following error when running "sh ./traffic-control.sh"
    # OCI runtime exec failed: exec failed: unable to start container process: exec: "tc": executable file not found in $PATH: unknown

    echo -e "\n\n\n###### apply network traffic ######\n"
    sh ./traffic-control.sh add
    sleep $SECONDS_BETWEEN_STEPS


    echo -e "\n\n\n###### run nmap ######\n"
    sudo docker-compose exec scanner bash -c "nmap $NMAP_BASE_PARAMS --min-hostgroup=$PARALLELISM -oN /opt/data/nmap.results.txt -iL /opt/data/lab-hosts.txt"
    cp data/nmap.results.txt ../$RESULTS_DIR/nmap.results.delay_${CURRENT_DELAY}ms.txt
    sleep $SECONDS_BETWEEN_STEPS

    echo -e "\n\n\n###### run nparallel ######\n"
    #nparallel nmap ${NMAP_BASE_PARAMS} --threads $PARALLELISM --force-scan -iL /opt/data/lab-hosts.txt | tee /opt/data/nparallel.results.txt
    sudo docker-compose exec scanner bash -c "python3 /opt/nparallel/nparallel.py nmap $NMAP_BASE_PARAMS --threads $PARALLELISM --force-scan -iL /opt/data/lab-hosts.txt | tee /opt/data/nparallel.results.txt"
    cp data/nparallel.results.txt ../$RESULTS_DIR/nparallel.results.delay_${CURRENT_DELAY}ms.txt
    sleep $SECONDS_BETWEEN_STEPS

    echo -e "\n\n\n###### extract scan duration ######\n"
    echo "| ${CURRENT_DELAY} | $(cat data/nmap.results.txt | grep "scanned in" | cut -d " " -f 19) | $(cat data/nparallel.results.txt | grep "Finished" | cut -d " " -f 6) |" >> ../$RESULTS_DIR/$test_name.results.md

    echo -e "\n\n\n###### Cleanup docker environment ######\n"
    sudo docker-compose down --remove-orphans
    sudo docker container prune --force
    sudo docker network prune --force
    sleep $SECONDS_BETWEEN_STEPS
    
    # navigate back
    cd ..


done