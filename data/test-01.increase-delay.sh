#!/bin/bash

# get the name of the script
test_name=$(basename "$0")

# network parameter
DELAY_START=0
DELAY_INCREMENT=10
DELAY_MAX=100

LATENCY=200
LOSS=3
BANDWIDTH=1000mbit
NUM_SUBNETS=3
NUM_SUBNET_HOSTS=5
LAB_DIR=$test_name.lab
RESULTS_DIR=$test_name.results
SCANNER_INPUT_FILE=lab-hosts.txt
SECONDS_BETWEEN_STEPS=5 # seconds to sleep between each command; 10 secs should a save

# scan parameter
#NMAP_BASE_PARAMS="-T4 -Pn -v --top-ports 100 -sV -O"
NMAP_BASE_PARAMS="-T4 -Pn -v --top-ports 1000 -sV"
PARALLELISM=32     # sets --min-hostgroup (nmap) or --threads (nparallel)

# clean up all results
sudo rm -rf $RESULTS_DIR
mkdir $RESULTS_DIR

# generate result file
cat <<EOT >> $test_name.results.md
# Results of $test_name ⏱️

This test measures the scan performance with increasing router delay. Scan targets are the exact hosts (and not the network range).

## Fixed parameters 🛠️

\`\`\`bash
DELAY_START=$DELAY_START
DELAY_INCREMENT=$DELAY_INCREMENT
DELAY_MAX=$DELAY_MAX

LOSS=$LOSS
LATENCY=$LATENCY
BANDWIDTH=$BANDWIDTH
NUM_SUBNETS=$NUM_SUBNETS
NUM_SUBNET_HOSTS=$NUM_SUBNET_HOSTS
LAB_DIR=$LAB_DIR
RESULTS_DIR=$RESULTS_DIR
SCANNER_INPUT_FILE=$SCANNER_INPUT_FILE
SECONDS_BETWEEN_STEPS=$SECONDS_BETWEEN_STEPS

NMAP_BASE_PARAMS=$NMAP_BASE_PARAMS
PARALLELISM=$PARALLELISM    # sets --min-hostgroup (nmap) or --threads (nparallel)
\`\`\`

## Results 📋

| Network DELAY in ms | Nmap scan duration in secs | Nparallel scan duration in secs | equal results | Nmap ports | Nparallel ports
|---|---|---|---|---|---|
EOT


for ((CURRENT_DELAY = DELAY_START ; CURRENT_DELAY <= DELAY_MAX ; CURRENT_DELAY=CURRENT_DELAY+DELAY_INCREMENT )) 
do 
    # generate lab
    echo -e "\n\n\n###### Generate lab files with DELAY=$CURRENT_DELAY ######\n"
    sudo rm -rf $LAB_DIR
    sleep $SECONDS_BETWEEN_STEPS
    python ./generate-lab.py --delay $CURRENT_DELAY --latency $LATENCY --loss $LOSS --bandwidth $BANDWIDTH --num-subnets $NUM_SUBNETS --num-subnet-hosts $NUM_SUBNET_HOSTS --out-dir $LAB_DIR

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

    echo -e "\n\n\n###### apply network traffic (DELAY=${CURRENT_DELAY}ms) ######\n"
    sh ./traffic-control.sh add
    sleep $SECONDS_BETWEEN_STEPS


    echo -e "\n\n\n###### run nmap ######\n"
    sudo docker-compose exec scanner bash -c "nmap $NMAP_BASE_PARAMS --min-hostgroup=$PARALLELISM -oN /opt/data/nmap.results.txt -iL /opt/data/lab-hosts.txt"
    cp data/nmap.results.txt ../$RESULTS_DIR/nmap.results.delay_${CURRENT_DELAY}ms.txt
    sleep $SECONDS_BETWEEN_STEPS


    echo -e "\n\n\n###### run nparallel ######\n"
    #nparallel nmap ${NMAP_BASE_PARAMS} --threads $PARALLELISM --force-scan -iL /opt/data/lab-hosts.txt | tee /opt/data/nparallel.results.txt
    sudo docker-compose exec scanner bash -c "python3 /opt/nparallel/nparallel.py nmap $NMAP_BASE_PARAMS -oN /opt/data/nparallel.results.txt --threads $PARALLELISM --force-scan -iL /opt/data/lab-hosts.txt | tee /opt/data/nparallel.log"
    cp data/nparallel.results.txt ../$RESULTS_DIR/nparallel.results.delay_${CURRENT_DELAY}ms.txt
    cp data/nparallel.log ../$RESULTS_DIR/nparallel.delay_${CURRENT_DELAY}ms.log
    sleep $SECONDS_BETWEEN_STEPS


    echo -e "\n\n\n###### extract scan duration ######\n"
    # compare tests by checking if the same amount of ports have been found
    NUM_NMAP_PORTS=$(cat "data/nmap.results.txt" | grep "/tcp open" | wc -l)
    NUM_NPARALLEL_PORTS=$(cat "data/nparallel.results.txt" | grep "/tcp open" | wc -l)
    EQUAL_NUM_PORTS=$(if [ $NUM_NMAP_PORTS -eq $NUM_NPARALLEL_PORTS ]; then echo "yes"; else echo "false"; fi)
    echo "| ${CURRENT_DELAY} | $(cat data/nmap.results.txt | grep "scanned in" | cut -d " " -f 19) | $(cat data/nparallel.log | grep "Finished" | cut -d " " -f 6) | $EQUAL_NUM_PORTS | $NUM_NMAP_PORTS | $NUM_NPARALLEL_PORTS | " >> ../$test_name.results.md


    echo -e "\n\n\n###### Cleanup docker environment ######\n"
    sudo docker-compose down --remove-orphans
    sudo docker container prune --force
    sudo docker network prune --force
    sleep $SECONDS_BETWEEN_STEPS
    
    # navigate back
    cd ..

done