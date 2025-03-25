import concurrent.futures
import os
import tempfile
from threading import Lock
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime

import subprocess
import ipaddress
import hashlib
import socket
import shutil
import sys
from itertools import repeat



import operator ## for grouping operation
import itertools ## for grouping operation
import collections ## for creating a defaultdict

class NmapCommand: 
    cmd_str = ""

    def __init__(self, cmd_str:str):
        self.cmd_str = cmd_str
        
    def get_id (self) -> str:
        """Get a unique command ID based on the used nmap command.
        Returns:
            A unique command ID.
        """        
        # sort nmap commands, to calculate same hash value, even if only 
        # the place of single parameters have changed.
        cmd_list_sorted = self.cmd_str.split(" ")
        cmd_list_sorted.sort()
        cmd_list_sorted_str = ' '.join(cmd_list_sorted)

        # calculate hash_value and trunace
        command_id = hashlib.sha256(cmd_list_sorted_str.encode()).hexdigest()[:8]
        return command_id

        

class NmapScan:
    ip = None
    nmap_cmd = None
    result = None

    def __init__(self, ip, nmap_cmd:NmapCommand):
        self.ip = ip
        self.nmap_cmd = nmap_cmd

    def get_id (self):
        return f"{str(self.ip)}_{self.nmap_cmd.get_id()}"

    def run (self, scan_cache_path):
        scan_id = self.get_id()
        # crat command
        command = "{} -oX {} -oN {} -oG {} {}".format(
            self.nmap_cmd.cmd_str,
            os.path.join(scan_cache_path, scan_id + ".xml"),
            os.path.join(scan_cache_path, scan_id + ".txt"),
            os.path.join(scan_cache_path, scan_id + ".grep"),
            self.ip,
        )
        # run command     
        with open(os.path.join(scan_cache_path, scan_id + ".log"), 'w') as log_file:
            self.result = subprocess.run(command.split(), shell=False, stdout=log_file, stderr=log_file)



class Nparallel:
    CACHE_DIR = '.cache'
    COMMAND_FILE_PREFIX = "_nmap_command_"

    def __init__(self):
        self.args = self.get_args()

    def run_nmap(self, scan:NmapScan, tmp_dir):
        scan.run(tmp_dir)
        return scan

    def get_args(self):
        "Parse and return command line arguments"
        parser = argparse.ArgumentParser(
            prog="Nparallel",
            description="Speed up Nmap scans by running them in parallel",
#            usage="\n Run Nmap scan:\n" \
#                  " > nparallel nmap [nmap-args] -iL FILE \n"\
#                  " > nparallel nmap -v --top-ports 100 -oX results.xml -iL targets.txt "
        )

        sub_parsers = parser.add_subparsers(help='command', dest="command")        

        parser_run = sub_parsers.add_parser('nmap', 
            help='Run scan',                                            
            usage="\n" \
                " > nparallel nmap [args below / arbitrary nmap args] -iL targets.txt\n" \
                " > nparallel nmap -v --top-ports 100 -oX results.xml -iL targets.txt")
        
        parser_run.add_argument('-iL', '--input-list', required=True, help='Input from list of hosts/networks')
        parser_run.add_argument('--force-scan', action='store_true', help='Scan hosts even if cache entry exists. Updates cache.')
        parser_run.add_argument('-t', '--threads', type=int, default=100, help="Number of parallel nmap threads")
        parser_run.add_argument('-oA', '--out-all', default=None, help='Output in the three major formats at once (normal, XML and grepable)')
        parser_run.add_argument('-oN', '--out-normal', default=None, help='Output scan in Normal format')
        parser_run.add_argument('-oG', '--out-grepable', default=None, help='Output scan in Grepable format')
        parser_run.add_argument('-oX', '--out-xml', default=None, help='Output scan in XML')
        parser_run.add_argument('-oL', '--out-log', default=None, help='Output scan in Log format')

        parser_cache = sub_parsers.add_parser('cache', help='Cache operations')

        cache_sub_parsers = parser_cache.add_subparsers(title='subcommands', dest="cache_command")

        parser_cache_list = cache_sub_parsers.add_parser('ls', help='List cache entries')
        parser_cache_list.add_argument('-v', '--verbose', action='store_true', help='Show full IP ranges')
        parser_cache_remove = cache_sub_parsers.add_parser('rm', help='Remove one or more cache entries')
        parser_cache_remove.add_argument('cmd_id', nargs='+', help='Nmap command ID(s) of the entries to be deleted')
        parser_cache_list = cache_sub_parsers.add_parser('clear', help='Clear entire cache')                   
        
        args, unknown = parser.parse_known_args()
        args.nmap_command = f"nmap {' '.join(unknown)}"        

        return args       
    

    def resolve_to_ip_addresses(self, targets_file) -> list[ipaddress.IPv4Address]:
        """Resolve hosts, which are in CIDR notation or hostnames, to IP addresses. Removes doubling.
        Args:
            targets_file: The file containing the target hosts in CIDR notation.
        Returns:
            An ordererd list of IP addresses.
        """
        resolved_ips = set()
        with open(os.path.expanduser(targets_file), 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    try:
                        network = ipaddress.ip_network(line, strict=False)
                        for ip in network.hosts():
                            resolved_ips.add(ip)
                    except ValueError:
                        try: 
                            # try resolving string if it isn't an IP
                            resolved_ip = socket.gethostbyname(line)
                            resolved_ips.add(ipaddress.ip_address(resolved_ip))
                        except:
                            print(f"Invalid network address '{line}' in '{targets_file}")
                            print(f"QUITTING!")
                            exit (1)
        return sorted(resolved_ips)
    
    def get_scaninfo_path (self, cmd_id:str):
        return os.path.join (self.CACHE_DIR, cmd_id, f"{self.COMMAND_FILE_PREFIX}{cmd_id}")
    
    def get_scan_cache_path (self, cmd_id:str):
        return os.path.join (self.CACHE_DIR, cmd_id)

    def get_nmap_base_cmd(self, cmd_id:str):  
        "reads nmap base command from scaninfo file. Returns None if scan_id does not exist"  
        nmap_base_cmd = None
        scaninfo_path = self.get_scaninfo_path(cmd_id)
        if os.path.exists(scaninfo_path):         
            with open(scaninfo_path, 'r') as scaninfo_file:
                nmap_base_cmd = scaninfo_file.readline()
        return nmap_base_cmd

    def get_scans(self, cmd_id, resolved_ips, force_scan):
        "Get lists of finished and unfinished scans based on resolved_ips"
        scans = []
        scans_open = []
        scans_finished = []

        # use scans from cache, if force_scan is false
        if force_scan == False:
            scans_finished = [f for f in os.listdir(self.get_scan_cache_path(cmd_id)) if f.endswith(".xml")]
        for ip in resolved_ips:
            nmap_scan = NmapScan(
                ip = ip,
                nmap_cmd = NmapCommand(self.get_nmap_base_cmd(cmd_id))
            )    
            if f"{nmap_scan.get_id()}.xml" not in scans_finished:
                scans_open.append(nmap_scan)
            scans.append(nmap_scan)
        return scans, scans_open
    
    def get_finished_scans (self, cmd_id):
        scan_cache_path = self.get_scan_cache_path(cmd_id)
        scans_finished = [f for f in os.listdir(scan_cache_path) if f.endswith(".xml")]
        return scans_finished
      
    
    def init_scan_cache(self):
        "Init cache directory for specific command"
        nmap_cmd = NmapCommand(self.args.nmap_command)
        cache_dir = os.path.join(os.getcwd(), self.CACHE_DIR, nmap_cmd.get_id())

        # init scan folder
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # create scan info file
        scaninfo_file_path = os.path.join (cache_dir, f"{self.COMMAND_FILE_PREFIX}{nmap_cmd.get_id()}")
        if not os.path.exists(scaninfo_file_path):         
            with open(scaninfo_file_path, 'w') as scaninfo_file:
                scaninfo_file.write(nmap_cmd.cmd_str)

        return cache_dir


    def merge_files (self, cache_dir, nmap_cmd, start_time:datetime, end_time:datetime, cache_file_type:str, out_file_path):
        "Merge scan files in cache dir to one single file"
        files = set()

        for f in os.listdir(cache_dir):
            if f.endswith(cache_file_type):
                file_path = os.path.join(cache_dir, f)
                files.add(file_path)

        file_content_raw = ""
        match cache_file_type:
            case ".xml":
                file_content_raw = self.merge_xml_files (files, nmap_cmd, start_time, end_time)
            case ".txt":
                file_content_raw = self.merge_normal_files (files, nmap_cmd, start_time, end_time)
            case ".grep":
                file_content_raw = self.merge_grepable_files (files, nmap_cmd, start_time, end_time)
            case ".log":
                file_content_raw = self.merge_log_files (files, nmap_cmd, start_time, end_time)
            case _:
                s_print ("[!] cache_file_type '{cache_file_type}' unkown")

        with open(out_file_path, "w") as out_file_xml:
            out_file_xml.writelines(file_content_raw)


    def merge_xml_files (self, files:set, nmap_cmd:NmapCommand, start_time:datetime, end_time:datetime) -> str:
        "Merge all files in set to one single XML file and return content as string"
        out_str = ""        

        # add header
        with open (list(files)[0], 'r', encoding='utf-8') as xml_file:        
            xml = ET.parse(xml_file)
            out_str += '<?xml version="1.0" encoding="UTF-8"?>\n'
            out_str += '<!DOCTYPE nmaprun>\n'
            out_str += '<?xml-stylesheet href="file:///usr/share/nmap/nmap.xsl" type="text/xsl"?>\n'
            out_str += '<!-- Nmap result merged with nparallel.py https://github.com/ronnydo/nparallel -->\n'
            out_str += '<nmaprun scanner="nmap" args="{}" start="{}" startstr="{}" version="7.80" xmloutputversion="1.04">\n'.format(
                nmap_cmd.cmd_str,
                int(start_time.timestamp()), # Linux timestamp
                start_time.strftime("%a %b %d %H:%M:%S %Y"), #Fri Mar 21 22:11:16 2025
            )
            scaninfo_tag = xml.find('scaninfo')
            out_str += ET.tostring(scaninfo_tag, encoding='unicode', method='xml')
            verbose_tag = xml.find('verbose')
            out_str += ET.tostring(verbose_tag, encoding='unicode', method='xml')
            debugging_tag = xml.find('debugging')
            out_str += ET.tostring(debugging_tag, encoding='unicode', method='xml')
        
        # add hosts
        host_number = 0
        for xml_file_path in files:
            with open (xml_file_path, 'r', encoding='utf-8') as xml_file:
                xml = ET.parse(xml_file)
                for host in xml.findall('host'):
                    out_str += ET.tostring(host, encoding='unicode', method='xml')
                    host_number += 1
        
        # add footer
        out_str += ('<runstats><finished time="{}" timestr="{}" elapsed="{}" summary="Nmap done at {}; ' + str(host_number) + ' IP address scanned in {} seconds" exit="success"/>\n').format(
            int(end_time.timestamp()), # Linux timestamp
            end_time.strftime("%a %b %d %H:%M:%S %Y"),
            "{:.2f}".format((end_time - start_time).total_seconds()),
            end_time.strftime("%a %b %d %H:%M:%S %Y"),
            "{:.2f}".format((end_time - start_time).total_seconds()),
        )
        out_str += '</runstats>\n'
        out_str += '</nmaprun>'

        return out_str


    def merge_normal_files (self, files:set, nmap_cmd:NmapCommand, start_time:datetime, end_time:datetime) -> str:
        "Merge all files in set to one single txt file and return content as string"
        out_str = ""        

        # add header
        out_str += f'# Nmap scan initiated {start_time.strftime("%a %b %d %H:%M:%S %Y")} as: {nmap_cmd.cmd_str}\n'
        
        # add hosts
        hosts_total = len(files)
        hosts_up = len(files)
        for file_path in files:
            with open (file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                # remove first line
                lines.pop(0)
                # read all lines from first and second block
                block = 1                    
                for line in lines:
                    out_str += line                       
                    if line.startswith ("Nmap scan report for") and line.strip().endswith("[host down]"):
                        # decrease hosts_up of results are empty
                        hosts_up -= 1                     
                    if line.strip() == "":
                        block += 1
                    if block == 3:
                        break
        
        # add footer
        out_str += "# Nmap done at {} -- {} IP addresses ({} hosts up) scanned in {} seconds".format(
            end_time.strftime("%a %b %d %H:%M:%S %Y"),
            hosts_total,
            hosts_up,           
            "{:.2f}".format((end_time - start_time).total_seconds()),
        )

        return out_str
    

    def merge_grepable_files (self, files:set, nmap_cmd:NmapCommand, start_time:datetime, end_time:datetime) -> str:
        "Merge all files in set to one single grepable file and return content as string"
        out_str = ""        

        # add header
        with open (list(files)[0], 'r', encoding='utf-8') as file:
            # read first line but set line manually
            file.readline()
            out_str += f'# Nmap scan initiated {start_time.strftime("%a %b %d %H:%M:%S %Y")} as: {nmap_cmd.cmd_str}\n'
            # read second line with scanned ports information
            out_str += file.readline()            
        
        # add hosts
        hosts_total = len(files)
        hosts_up = len(files)
        for file_path in files:
            with open (file_path, 'r', encoding='utf-8') as file:
                for line in file.readlines():
                    if line.startswith("# ") == False:
                        out_str += line
                        # decrease hosts_up of host is down
                        if line.strip().endswith("Status: Down"):
                            hosts_up -= 1
        
        # add footer
        out_str += "# Nmap done at {} -- {} IP addresses ({} hosts up) scanned in {} seconds".format(
            end_time.strftime("%a %b %d %H:%M:%S %Y"),
            hosts_total,
            hosts_up,           
            "{:.2f}".format((end_time - start_time).total_seconds()),
        )

        return out_str


    def merge_log_files (self, files:set, nmap_cmd:NmapCommand, start_time:datetime, end_time:datetime) -> str:
        "Merge all files in set to one single log file and return content as string"        
        out_str = ""        

        # add header
        out_str += f'Starting Nmap ( https://nmap.org ) at {start_time.strftime("%a %b %d %H:%M:%S %Y")}\n'
        
        # add hosts
        hosts_total = len(files)
        hosts_up = len(files)
        for file_path in files:
            with open (file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                # remove first line
                lines.pop(0)
                # read all lines from first and second block
                block = 1                    
                for line in lines:
                    out_str += line                        
                    if line.startswith ("Nmap scan report for") and line.strip().endswith("[host down]"):
                        # decrease hosts_up of results are empty
                        hosts_up -= 1
                    if line.strip() == "":
                        block += 1
                    if block == 3:
                        break
        
        # add footer
        out_str += 'Read data files from: /usr/bin/../share/nmap\n'
        out_str += 'Nmap done: {} IP addresses ({} hosts up) scanned in {} seconds'.format(
            hosts_total,
            hosts_up,           
            "{:.2f}".format((end_time - start_time).total_seconds()),
        )

        return out_str

    def get_cache_info(self):
        scans = {} 
        base_cache_dir = os.path.join(os.getcwd(), self.CACHE_DIR)
        if (os.path.exists(base_cache_dir)):
            for cmd_id in os.listdir(base_cache_dir):
                scaninfo_path = self.get_scaninfo_path(cmd_id)
                            
                ip_adresses = list()
                for scan in self.get_finished_scans(cmd_id):
                    ip = ipaddress.IPv4Address(scan.split("_")[0])
                    ip_adresses.append(ip)

                if os.path.exists(scaninfo_path):         
                    with open(scaninfo_path, 'r') as scaninfo_file:
                        scans[cmd_id] = {
                            "cmd_id": cmd_id,
                            "nmap_base_cmd": self.get_nmap_base_cmd(cmd_id),
                            "scans_finished": self.get_finished_scans(cmd_id),
                            "scan_groups": self.group_ip_addresses(ip_adresses)
                        }
        return scans
    

    def group_ip_addresses(self, ip_addresses):
        groups = []
        for _, g in itertools.groupby(enumerate(sorted(ip_addresses)), lambda ix: ix[0] - int(ix[1])):
            group = list(map(operator.itemgetter(1), g))
            if len(group) > 1:
                groups.append(f"{group[0]}-{str(group[-1]).split('.')[-1]}")
            else:
                groups.append(str(group[0]))
        return groups

    def print_cache_info(self, scans, verbose):
        if len (scans) > 0: 
            print (f"[*] Cache contains {len(scans)} scans:\n")  
            if verbose == False:  
                print (f"cmd_id     finished\tNmap command")
                print (f"---        ---     \t---")
                for entry in scans.values():
                        print (f"{entry['cmd_id']}   {len(entry['scans_finished'])}    \t{entry['nmap_base_cmd']}")
            else:
                print (f"cmd_id     finished      \tNmap command")
                print (f"---        ---           \t---")
                for entry in scans.values():       
                    is_first_line = True
                    for group in entry['scan_groups']: 
                        if is_first_line:
                            print (f"{entry['cmd_id']}   {group}    \t{entry['nmap_base_cmd']}")
                            is_first_line = False
                        else:
                            print (f"           {group}  ")  
        else:
            print ("[*] Cache is empty")

# lock object to work thread-safe with print function
s_print_lock = Lock()

def s_print(value):
    """Thread safe print function"""
    s_print_lock.acquire()
    print(value)
    s_print_lock.release()    


def main(cli_args=None):
    nparallel = Nparallel()    

    # Parse args
    args = nparallel.args  
    

    if args.command == "nmap":
        nmap_cmd = NmapCommand(args.nmap_command)

        # resolve IPs
        resolved_ips = nparallel.resolve_to_ip_addresses(args.input_list)  
        cache_dir = nparallel.init_scan_cache()  
        
        # check for (un)finished scans        
        scans, scans_open = nparallel.get_scans (nmap_cmd.get_id(), resolved_ips, args.force_scan)

        start_time = datetime.now()
        scans_finished = len(scans) - len(scans_open)

        print (f"[*] Cmd_id: {nmap_cmd.get_id()}  |  Cmd: {nmap_cmd.cmd_str}  |  Threads: {args.threads}")
        print (f"[*] Progress: \033[1m\033[92m{scans_finished}/{len(scans)} hosts\033[0m (Start: {start_time.strftime(f'%H:%M:%S')})")

        # TODO work in memory instead of tmp
        with tempfile.TemporaryDirectory() as tmp_dir :
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
                try:
                    # init nmap scan
                    for scan in executor.map(nparallel.run_nmap, scans_open, repeat(tmp_dir)):
                        try:
                            if (scan.result.returncode == 0):
                                # update progress
                                scans_finished += 1
                                s_print (f'\033[A                             \033[A')
                                s_print (f'[*] Progress: \033[1m\033[92m{scans_finished}/{len(scans)} hosts\033[0m (Start: {start_time.strftime(f"%H:%M:%S")})')  

                                scan_id = scan.get_id()
                                in_base_path = os.path.join(tmp_dir, scan_id)
                                out_base_path = os.path.join(cache_dir, scan_id)

                                # copy files
                                for file_ext in [".xml", ".txt", ".grep", ".log"]:
                                    shutil.copyfile(in_base_path + file_ext, out_base_path + file_ext)

                            else:                            
                                s_print(f"[!] Scan of {scan.ip} failed: Error (Result code: {scan.result.returncode})")                            
                        except Exception as exc:
                            s_print(f'[!] Catch inside: {exc}')

                except Exception as exc:
                    s_print(f'[!] Catch outside: {exc}')
                    # TODO finish processes when catched, because otherwise there will be zombie processes
            
        # TODO + #FIXME After successful scan the terminal often doesn't show a cursor anymore

        end_time = datetime.now()
        s_print (f"[+] \033[1m\033[92mFinished\033[0m in {'{:.2f}'.format((end_time - start_time).total_seconds())} sec (End: {end_time.strftime(f'%H:%M:%S')})\n")
        
        # TODO output even if scan is aborted?

        if args.out_all:
            args.out_xml = args.out_all + ".xml"
            args.out_normal = args.out_all + ".txt"
            args.out_grepable = args.out_all + ".grep"
        
        if args.out_xml:
            nparallel.merge_files (cache_dir, nmap_cmd, start_time, end_time, ".xml", args.out_xml)
            s_print (f"[+] XML file saved at '\033[1m{os.path.join(os.getcwd(), args.out_xml)}\033[0m'")
        if args.out_normal:
            nparallel.merge_files (cache_dir, nmap_cmd, start_time, end_time, ".txt", args.out_normal)
            s_print (f"[+] Normal file saved at '\033[1m{os.path.join(os.getcwd(), args.out_normal)}\033[0m'")
        if args.out_grepable:
            nparallel.merge_files (cache_dir, nmap_cmd, start_time, end_time, ".grep", args.out_grepable)
            s_print (f"[+] Grepable file saved at '\033[1m{os.path.join(os.getcwd(), args.out_grepable)}\033[0m'")
        if args.out_log:
            nparallel.merge_files (cache_dir, nmap_cmd, start_time, end_time, ".log", args.out_log)
            s_print (f"[+] Log file saved at '\033[1m{os.path.join(os.getcwd(), args.out_log)}\033[0m'")
        
        if args.out_all == False and args.out_xml == False and args.out_normal == False and args.out_grepable == False and args.out_log == False:
            s_print (f"No output file location provided - run same command again with -oX/-oG/-oN/-oL/-oA option")
    
    elif args.command == "cache":
        # list cache entries
        if args.cache_command == "ls":
            scans = nparallel.get_cache_info()
            nparallel.print_cache_info(scans, args.verbose)
        # delete single entries
        elif args.cache_command == "rm":
            for cmd_id in args.cmd_id:
                scan_cache = nparallel.get_scan_cache_path(cmd_id)
                if os.path.exists(scan_cache):
                    shutil.rmtree(scan_cache)
                    print (f"[+] Entry with cmd_id '{cmd_id}' removed")
                else:
                    print (f"[!] Entry for cmd_id '{cmd_id}' not found") 
        # clear cache
        elif args.cache_command == "clear":
            shutil.rmtree(nparallel.CACHE_DIR)
            print ("[+] Cache cleared.")

        # leave some space at the end
        print ()

    
if __name__ == '__main__':
    main()

