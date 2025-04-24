import shutil, os, argparse


parser = argparse.ArgumentParser()
parser.add_argument("--delay", type=int, default=1, help="Network delay in milliseconds")
parser.add_argument("--loss", type=int, default=1, help="Network package loss rate in percent")
parser.add_argument("--bandwidth", type=str, default="100kbit", help="Network bandwith of each hosts in kbit, mbit or gbit")
parser.add_argument("--num-subnets", type=int, default=2, help="Number of subnets. Default is 2, starting from 10.0.1.0/24")
parser.add_argument("--num-subnet-hosts", type=int, default=2, help="Number of hosts per subnet. Default is 2, starting from 10.0.1.101-102")
parser.add_argument("--out-dir", type=str, default="generic-lab", help="Output directory")
args = parser.parse_args()

OUT_PATH=os.path.join(os.getcwd(), args.out_dir)
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
PREFIX_TARGET_NET="10.0."
PREFIX_SCANNER_NET="172.18."
NUM_SUBNET=args.num_subnets
NUM_SERVER_IN_SUBNET=args.num_subnet_hosts

# create lab folder
print (f"Generate lab files to '{OUT_PATH}'")
if os.path.exists(OUT_PATH):
    shutil.rmtree(OUT_PATH)
os.mkdir(OUT_PATH)

# create file containing all lab-hosts
print (f"Create {HOSTSFILE}")
with open(os.path.join(OUT_PATH, HOSTSFILE), "w") as f:
    for subnet_index in range(1, NUM_SUBNET + 1):     
        for host_index in range(101,NUM_SERVER_IN_SUBNET + 101):            
            f.write(f"{PREFIX_TARGET_NET}{subnet_index}.{host_index}\n")


# create file containing all class-C networks containing hosts
print (f"Create {NETWORKSFILE}")
with open(os.path.join(OUT_PATH, NETWORKSFILE), "w") as f:
    for subnet_index in range(1, NUM_SUBNET + 1):            
        f.write(f"{PREFIX_TARGET_NET}{subnet_index}.0/24\n")            


# create dockerfile if scannable host
print (f"Create {DOCKERFILE}")
with open(os.path.join(OUT_PATH, DOCKERFILE), "w") as f:
    f.write("FROM php:8-apache\n")
    #f.write("FROM mattrayner/lamp:latest-1804")
    f.write("RUN apt-get update\n")
    f.write("RUN apt install iproute2 apache2 -y\n")
    f.write("RUN service apache2 start\n")

# generate dummy webserver content
HTDOCS_PATH=os.path.join(OUT_PATH, HTDOCS_DIR)
os.mkdir(HTDOCS_PATH)
# generate big file for download 
with open(os.path.join(HTDOCS_PATH, "bigfile.zip"), "wb") as f:
    # 50 MB
    f.truncate(50 * 1024 * 1024)
# generate basic landing page
with open(os.path.join(HTDOCS_PATH, "index.php"), "w") as f:    
    f.write(f'<h1><u><?php echo gethostname(); ?></u> says hello!</h2>\n')
    f.write(f'<p><a href="/bigfile.zip">Click here</a> to download bigfile.zip.</p>\n')
    f.write(f'<p>It\'s a ZIP-file containing random bytes and can only be downloaded with limited speed.</p>\n')


# create docker-compose file
print (f"Create {COMPOSEFILE}")
with open(os.path.join(OUT_PATH, COMPOSEFILE), "w") as f:
    f.write(f"version: '3.8'\n\n")

    f.write(f"networks:\n")
    f.write(f"  net_scanner:\n")
    f.write(f"    driver: bridge\n")
    f.write(f"    ipam:\n")
    f.write(f"      config:\n")
    f.write(f"        - subnet: {PREFIX_SCANNER_NET}0.0/16\n")
    f.write(f"    driver_opts:\n")
    f.write(f"      com.docker.network.bridge.name: ethscanner\n")
    f.write(f"  net_target:\n")
    f.write(f"    driver: bridge\n")
    f.write(f"    ipam:\n")
    f.write(f"      config:\n")
    f.write(f"        - subnet: 10.0.0.0/16\n\n")

    f.write(f"services:\n")
    f.write(f"  router:\n")
    f.write(f"    image: debian\n")
    f.write(f"    hostname: router\n")
    f.write(f"    container_name: router\n")
    f.write(f"    command: sh -c 'apt-get update && apt-get install iputils-ping iproute2 iptables -y && sleep infinity'\n")
    f.write(f"    cap_add:\n")
    f.write(f"      - NET_ADMIN\n")
    f.write(f"    sysctls:\n")
    f.write(f"      - net.ipv4.ip_forward=1\n")
    f.write(f"    networks:\n")
    f.write(f"      net_scanner:\n")
    f.write(f"        ipv4_address: {PREFIX_SCANNER_NET}0.2  # Gateway for scanner\n")
    f.write(f"      net_target:\n")
    f.write(f"        ipv4_address: {PREFIX_TARGET_NET}0.2   # gateway for target net\n")

    f.write(f"  scanner:\n")
    f.write(f"    image: debian\n")
    f.write(f"    hostname: scanner\n")
    f.write(f"    container_name: scanner\n")
    f.write(f"    command: sh -c 'apt-get update && apt-get install iproute2 iputils-ping nmap wget -y && ip route add {PREFIX_TARGET_NET}0.0/16 via {PREFIX_SCANNER_NET}0.2 && sleep infinity'\n")
    f.write(f"    networks:\n")
    f.write(f"      net_scanner:\n")
    f.write(f"        ipv4_address: {PREFIX_SCANNER_NET}0.66\n")
    f.write(f"    cap_add:\n")
    f.write(f"      - NET_ADMIN\n")

    for subnet_index in range(1, NUM_SUBNET + 1):     
        for host_index in range(101,NUM_SERVER_IN_SUBNET + 101):
            f.write(f"  target-{PREFIX_TARGET_NET.replace('.','-')}{subnet_index}-{host_index}:\n")
            f.write(f"    build:\n")
            f.write(f"      context: .\n")
            f.write(f"      dockerfile: {DOCKERFILE}\n")
            f.write(f"    container_name: target-{PREFIX_TARGET_NET.replace('.','-')}{subnet_index}-{host_index}\n")
            f.write(f"    hostname: target-{PREFIX_TARGET_NET.replace('.','-')}{subnet_index}-{host_index}\n")
            f.write(f"    command: sh -c 'ip route add {PREFIX_SCANNER_NET}0.0/24 via {PREFIX_TARGET_NET}0.2 && service apache2 start && sleep infinity'\n")
            f.write(f"    networks:\n")
            f.write(f"      net_target:\n")
            f.write(f"        ipv4_address: {PREFIX_TARGET_NET}{subnet_index}.{host_index}\n")
            f.write(f"    cap_add:\n")
            f.write(f"      - NET_ADMIN\n")
            f.write(f"    volumes:\n")
            f.write(f"      - ./htdocs/:/var/www/html\n\n")


# create traffic-control.sh
print ("Create traffic-control.sh")
with open(os.path.join(OUT_PATH, TCFILE), "w") as f:
    f.write(f"#!/bin/sh\n")
    f.write(f"# Limit network bandwidth on all docker hosts\n\n")

    f.write(f'if [ -z "$1" ]; then\n')
    f.write(f'  echo "Add or delete traffic control, e.g. bandwidth limitation to all containers"\n')
    f.write(f'  echo "Usage: traffic-control.sh [add|del]"\n')
    f.write(f'  exit 1\n')
    f.write(f'fi\n\n')

    f.write(f"TC_BANDWIDTH={TC_BANDWIDTH}\n")
    f.write(f"TC_LATENCY={TC_LATENCY} # latency affects every request (not only the first)\n")
    f.write(f"TC_LOSS={TC_LOSS}\n")
    f.write(f"TC_DELAY={TC_DELAY} # delay effects ping requests also\n\n")

    f.write(f'if [ "$1" = "add" ]; then\n')
    f.write(f'  echo "adding traffic control to all containers..."\n')
    f.write(f"  sudo docker exec router tc qdisc add dev eth0 root handle 1: netem loss $TC_LOSS delay $TC_DELAY\n")
    f.write(f"  sudo docker exec router tc qdisc add dev eth0 parent 1: handle 2: tbf rate $TC_BANDWIDTH burst 16kbit latency $TC_LATENCY\n")  
    f.write(f'fi\n\n')

    f.write(f'if [ "$1" = "del" ]; then\n')
    f.write(f'  echo "deleting traffic control from all containers..."\n')
    f.write(f"  sudo docker exec router tc qdisc del dev eth0 parent 1: handle 2: tbf rate $TC_BANDWIDTH burst 16kbit latency $TC_LATENCY\n")  
    f.write(f"  sudo docker exec router tc qdisc del dev eth0 root handle 1: netem loss $TC_LOSS delay $TC_DELAY\n")
    f.write(f'fi\n\n')    

    f.write(f'echo "Done."')


print ("\n# Run the following commands to start the lab:\n")
print (f"cd {OUT_PATH}")
print ("sudo docker-compose down --remove-orphans && sudo docker network prune --force")
print ("sudo docker-compose build && sudo docker-compose up -d && sudo sh ./traffic-control.sh add")
