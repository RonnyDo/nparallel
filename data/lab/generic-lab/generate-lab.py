import shutil,os, argparse


parser = argparse.ArgumentParser()
parser.add_argument("--delay", type=int, default=1, help="Network delay in milliseconds")
parser.add_argument("--loss", type=int, default=1, help="Network package loss rate in percent")
parser.add_argument("--bandwidth", type=str, default="100kbit", help="Network bandwith of each hosts in kbit, mbit or gbit")
parser.add_argument("--num-subnets", type=int, default=1, help="Number of subnets. Default is 1, starting from 172.0.1.0/24")
parser.add_argument("--num-subnet-hosts", type=int, default=10, help="Number of hosts per subnet. Default is 10, starting from 172.0.1.1-10")
args = parser.parse_args()


DOCKERFILE="dockerfile"
HTDOCS_DIR="htdocs"
COMPOSEFILE="compose.yml"
HOSTSFILE="lab-hosts.txt"
NETWORKSFILE="lab-networks.txt"
TCFILE="traffic-control.sh"
TC_BANDWIDTH=args.bandwidth
TC_LATENCY="500ms" # packets with higher latency get dropped
TC_LOSS=str(args.loss)+"%"
TC_DELAY=str(args.delay)+"ms"
IP_PREFIX="172.0."
NUM_SUBNET=args.num_subnets
NUM_SERVER_IN_SUBNET=args.num_subnet_hosts


# create file containing all lab-hosts
print (f"Create {HOSTSFILE}")
with open(HOSTSFILE, "w") as f:
    for subnet_index in range(1, NUM_SUBNET + 1):     
        for host_index in range(1,NUM_SERVER_IN_SUBNET + 1):            
            f.write(f"{IP_PREFIX}{subnet_index}.{host_index}\n")


# create file containing all class-C networks containing hosts
print (f"Create {NETWORKSFILE}")
with open(NETWORKSFILE, "w") as f:
    for subnet_index in range(1, NUM_SUBNET + 1):            
        f.write(f"{IP_PREFIX}{subnet_index}.0/24\n")            


# create dockerfile if scannable host
print (f"Create {DOCKERFILE}")
with open(DOCKERFILE, "w") as f:
    f.write("FROM php:8-apache\n")
    #f.write("FROM mattrayner/lamp:latest-1804")
    f.write("RUN apt-get update\n")
    f.write("RUN apt install iproute2 apache2 -y\n")
    f.write("RUN service apache2 start\n")

if os.path.exists(HTDOCS_DIR):
    shutil.rmtree(HTDOCS_DIR)
os.mkdir(HTDOCS_DIR)
# generate big file for download 
with open(os.path.join(HTDOCS_DIR, "bigfile.zip"), "wb") as f:
    # 50 MB
    f.truncate(50 * 1024 * 1024)
# generate basic landing page
with open(os.path.join(HTDOCS_DIR, "index.php"), "w") as f:    
    f.write(f'<h1><u><?php echo gethostname(); ?></u> says hello!</h2>\n')
    f.write(f'<p><a href="/bigfile.zip">Click here</a> to download bigfile.zip.</p>\n')
    f.write(f'<p>It\'s a ZIP-file containing random bytes and can only be downloaded with limited speed.</p>\n')


# create docker-compose file
print (f"Create {COMPOSEFILE}")
with open(COMPOSEFILE, "w") as f:
    f.write(f"version: '3.8'\n\n")

    f.write(f"networks:\n")
    f.write(f"  lab-network:\n")
    f.write(f"    driver: bridge\n")
    f.write(f"    ipam:\n")
    f.write(f"      config:\n")
    f.write(f"        - subnet: 172.0.0.0/16\n\n")

    f.write(f"services:\n")
    for subnet_index in range(1, NUM_SUBNET + 1):     
        for host_index in range(1,NUM_SERVER_IN_SUBNET + 1):
            f.write(f"  lab-host-{subnet_index}-{host_index}:\n")
            f.write(f"    build:\n")
            f.write(f"      context: .\n")
            f.write(f"      dockerfile: {DOCKERFILE}\n")
            f.write(f"    container_name: lab-host-{subnet_index}-{host_index}\n")
            f.write(f"    hostname: lab-host-{subnet_index}-{host_index}\n")
            f.write(f"    networks:\n")
            f.write(f"      lab-network:\n")
            f.write(f"        ipv4_address: 172.0.{subnet_index}.{host_index}\n")
            f.write(f"    cap_add:\n")
            f.write(f"      - NET_ADMIN\n")
            f.write(f"    volumes:\n")
            f.write(f"      - ./htdocs/:/var/www/html\n\n")


# create traffic-control.sh
print ("Create traffic-control.sh")
with open(TCFILE, "w") as f:
    f.write(f"#!/bin/sh\n")
    f.write(f"# Limit network bandwidth on all docker hosts\n\n")

    f.write(f'if [ -z "$1" ]; then\n')
    f.write(f'  echo "Add or delete traffic control, e.g. bandwidth limitation to all containers"\n')
    f.write(f'  echo "Usage: traffic-control.sh [add|del]"\n')
    f.write(f'  exit 1\n')
    f.write(f'fi\n\n')

    f.write(f"TC_BANDWIDTH={TC_BANDWIDTH}\n")
    f.write(f"TC_LATENCY={TC_LATENCY}\n")
    f.write(f"TC_LOSS={TC_LOSS}\n")
    f.write(f"TC_DELAY={TC_DELAY}\n\n")

    f.write(f'if [ "$1" = "add" ]; then\n')
    f.write(f'  echo "adding traffic control to all containers..."\n\n')
    for subnet_index in range(1, NUM_SUBNET + 1):
        for host_index in range(1, NUM_SERVER_IN_SUBNET + 1):
            #f.write(f"  sudo docker exec -it lab-host-{subnet_index}-{host_index} tc qdisc add dev eth0 root handle 1: netem loss $TC_LOSS delay $TC_DELAY\n")
            #f.write(f"  sudo docker exec -it lab-host-{subnet_index}-{host_index} tc qdisc add dev eth0 parent 1: handle 2: tbf rate $TC_BANDWIDTH burst 16kbit latency $TC_LATENCY\n")   
            f.write(f"  sudo docker exec lab-host-{subnet_index}-{host_index} tc qdisc add dev eth0 root handle 1: netem loss $TC_LOSS delay $TC_DELAY\n")
            f.write(f"  sudo docker exec lab-host-{subnet_index}-{host_index} tc qdisc add dev eth0 parent 1: handle 2: tbf rate $TC_BANDWIDTH burst 16kbit latency $TC_LATENCY\n")   
    f.write(f'fi\n\n')

    f.write(f'if [ "$1" = "del" ]; then\n')
    f.write(f'  echo "deleting traffic control from all containers..."\n\n')
    for subnet_index in range(1, NUM_SUBNET + 1):
        for host_index in range(1, NUM_SERVER_IN_SUBNET + 1):
            f.write(f"  sudo docker exec -it lab-host-{subnet_index}-{host_index} tc qdisc del dev eth0 root 2> /dev/null\n")
    f.write(f'fi\n\n')    

    f.write(f'echo "Done."')


print ("\n")
print ("# Start lab:\n")
print ("sudo docker-compose down --remove-orphans && sudo docker-compose build && sudo docker-compose up -d && sudo sh ./traffic-control.sh add\n")
