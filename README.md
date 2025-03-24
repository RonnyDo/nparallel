# Nparallel
Speed up Nmap scans by running them in parallel.

## Install
```
# Variant A: Download and install
git clone https://github.com/RonnyDo/nparallel
cd nparallel
pip install .

# Variant B: Download raw script
wget https://raw.githubusercontent.com/RonnyDo/nparallel/refs/heads/main/nparallel.py
```

## Quickstart
```
# Usage: nparallel nmap [nmap-args] -iL TARGETS_FILE

$ nparallel nmap -v --top-ports 100 -oX results.xml -iL targets.txt 

[*] Cmd: nmap -v --top-ports 100 // Threads: 1000 // Cache: /home/user/.cache/082e1a0f
[*] Progress: 3/3 hosts (Start: 21:49:03)
[+] Finished in 3.11 sec (End: 21:49:06)

[+] XML file saved at '/home/user/results.xml'
```

## Features:
* parallel nmap scan (one host per thread)
* interrupt and continue scans 
* reduce and extend target list without having to scan finished hosts with the same command again
* use native nmap arguments
* no external python libraries needed

## How it works
The following things happen under the hood when running ```nparallel nmap -v --top-ports 100 -oX results.xml -iL targets.txt```:

1. Resolve all entries of ```targets.txt``` into single hosts. IP addresses, URLs and CIDR notation (e.g. 172.1.2.0/24) are supported. 
2. Check which hosts haven't been scanned by the provided nmap argument set yet, by checking the ```.cache/<nmap_cmd_id>``` directory. Each nmap argument set has a different id ("nmap_cmd_id"). The argument order doesn't matter. If the argument set changes, nparallel runs a new scan.
   Changing only the arguments listed ```nparallel nmap -h``` but keep the other nmap arguments untouched, does not lead to a new scan.
3. Start parallel nmap scans of all unfinished scans. Each scan/thread scans exactly one host.
4. Wait until all scans have finished.
5. If an output parameter was provided (```-oA/-oX/-oN/-oG/oL```) the per host scan scan results get merged into a single output file. 
   The output file should be&trade; 99 % identical with a "normal" nmap result file. However some meta information might be shortened or missing.
