# Nparallel
Speed up Nmap scans by running them in parallel.

## Install
```
git clone https://github.com/RonnyDo/nparallel
cd nparallel
pip install .
```

## Quickstart
```
nparallel nmap [nmap-args] -iL FILE
nparallel nmap -v --top-ports 100 -oX results.xml -iL targets.txt 

[*] Cmd: nmap -v --top-ports 100 // Threads: 1000 // Cache: /home/user/.cache/082e1a0f
[*] Progress: 3/3 hosts (Start: 21:49:03)
[+] Finished in 3.11 sec (End: 21:49:06)

[+] XML file saved at '/home/user/results.xml'
```

## Features:
* parallel nmap scan (one host per thread)
* interrupt and continue scans 
* reduce and extend target list without scanning successful scanned hosts again
* use native nmap arguments
* dependency free

## How it works
The following things happen under the hood when running ```nparallel nmap -v --top-ports 100 -oX results.xml -iL targets.txt```:

1. Resolve all entries of ```targets.txt``` into hosts. IP addresses, URLs and CIDR notation (e.g. 172.1.2.0/24) are supported. 
2. Check which hosts haven't been scanned by the provided nmap command yet, by checking the ```.cache/<nmap_cmd_id>``` directory. Each nmap argument set has a different id ("nmap_cmd_id"). A different argument set means a new scan. The argument order doesn't matter.
3. Start parallel nmap scans of all unfinished scans. Each scan/threads scans exactly one host.
4. Wait until all scans have finished.
5. If an output parameter was provided (```-oA/-oX/-oN/-oG/oL```) all single host scan results are merged into a single output file. The output file is not 100% the same as it would be in a single nmap scan, but 99 %. The scan results are identical, but some metadata might be shortened or missing.