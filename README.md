# Nparallel
Speed up Nmap scans by running them in parallel.


## Features:
**HIGHLIGHTS**:
* faster than native nmap scans (multithreaded scans with one host per thread)
* interrupt and continue scans at any time
* reduce and extend target list without having to scan finished hosts with the same command again

**even more**:
* use native nmap arguments
* depenedency free for almost all features
* additional stdout output format ```-ol/out-log```
* export all hosts with open ports as 
   * .CSV with ```-oC/out-csv```
   * .XLSX with ```-oE/out-excel``` (requires external lib)
   * .DOCX with ```-oW/out-word``` (requires external lib)

## Install
```
# Variant A: Download and install
git clone https://github.com/RonnyDo/nparallel
cd nparallel
pip install .                       # zero dependency installation
pip install .[with_office_export]   # install external libs

# Variant B: Download raw script
wget https://raw.githubusercontent.com/RonnyDo/nparallel/refs/heads/main/nparallel/nparallel.py
```

## Quickstart
### Run scan: ```nparallel nmap```
```
# Usage: nparallel nmap [nmap-args] -iL TARGETS_FILE
$ nparallel nmap -v --top-ports 100 -oX results.xml -iL targets.txt 

[*] Cmd id: cabb60dc  |  Nmap base cmd: nmap -v --top-ports 100 -oX results.xml  |  Threads: 100
[*] Start: 21:49:03
[+] Progress: 3/3 hosts
[+] End: 21:49:06 (Finished in 3.11 seconds)

[+] XML file saved at '/home/user/results.xml'
```

### Show scans (details): ```nparallel ls```
```
# show scan overview
$ nparallel ls

[*] Cache contains 3 scans:

Cmd id     Finished	Nmap base command
---        ---     	---
ab4e8efa   3    	nmap -T4 -v --top-ports 10
9d9c55a7   1    	nmap -T 5
c178e8fa   64    	nmap -T4 -v --top-ports 100
```

```
# show scan details if scan with cmd id 'ab4e8efa'
$ nparallel ls ab4e8efa

[*] Nmap base command:
nmap -T4 -v --top-ports 10

[+] Hosts finished (3):
45.33.32.156 127.0.0.1 172.1.2.3

[+] Hosts with open ports (2):
45.33.32.156 127.0.0.1

[+] Ports open TCP (2):
22,80,443

[+] Ports open UDP (0):
69
```

### Remove cache entries or delete entire cache: ```nparallel rm```
```
# Delete only scan with cmd id 'ab4e8efa'
$ python3 nparallel.py rm ab4e8efa

[+] Entry with cmd_id 'ab4e8efa' removed
```

```
# delete entire cache
$ nparallel rm

[?] Delete entire cache? [y/N]y
[+] Cache cleared.
```


## How it works
The following happens under the hood when running ```nparallel nmap -v --top-ports 100 -oX results.xml -iL targets.txt```:

1. Resolve all entries of ```targets.txt``` into single hosts. IP addresses, URLs and CIDR notation (e.g. 172.1.2.0/24) are supported. 
2. Check which hosts haven't been scanned by the provided nmap argument set yet, by checking the ```.cache/<cmd_id>``` directory. Each nmap argument set has a different id ("cmd_id"). The argument order doesn't matter. If the argument set changes, nparallel runs a new scan.
   Changing only the arguments listed ```nparallel nmap -h``` but keep the other nmap arguments untouched, does not lead to a new scan.
3. Start parallel nmap scans of all unfinished scans. Each scan/thread scans exactly one host.
4. Wait until all scans have finished.
5. If an output parameter is provided (```-oA/-oX/-oN/-oG/-oL/-oE/-oW```) the per host scan results get merged into a single output file. 
   The output file should be&trade; 99 % identical with a "normal" nmap result file. However some meta information might be shortened or missing.

