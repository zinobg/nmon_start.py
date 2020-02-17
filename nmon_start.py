#!/opt/bin/python3
'''
 Program : start_nmon.py
 Author  : Konstantin Yovchev
 Date    : 17/02/2020
 Ver     : 2.4
 Desc    : Collects nmon stats to a file on daily bases, compresses them and keeps them for some time.
 OS      : Tested on AIX and Linux
         :
         : Installation instructions:
         :  1. Download and install nmon
         :  2. Add the following reccord in root's crontab:
         :     ----------------------------------------------
         :     0 0 * * * /<pathtoscript>/nmon_start.py >/dev/null 2>&1   # Gather information using nmon
         :     ----------------------------------------------
         :  3. (AIX) Add to /etc/inittab    -> $ mkitab "nmon:2:once:/nmon/scripts/nmon_start.py > /dev/console 2>&1"
         :     (Linux) Add to /etc/rc.local -> $ echo "/root/scripts/nmon_start.py/nmon_start.py" >> /etc/rc.local
'''
import os,time,stat
from subprocess import Popen as sPopen
from signal import SIGKILL as sSIGKILL
from shutil import copyfileobj as scopyfileobj
from glob import glob as gglob
from gzip import open as gopen
from socket import gethostname as ghostname
from datetime import datetime as dtime

'''
    Variables
'''
nmon_exe="/usr/bin/nmon"                  # nmon executable
nmon_sleep_seconds="300"                  # sleep time between nmon iterations
nmon_stats_count="288"                    # number or nmon iterations
nmon_prefix="PRI"                         # output filename prefix
rasp_nmon_logs="/nmon/logs"                # output direcroty for Linux server (will be created if doesn't exists)
days_to_keep=30                           # how many days to keep nmon.gz files, before delete them

'''
    Main function
'''
def main():
    '''
        Checks if dir for nmons logs exists. If not, creates it
    '''
    if not os.path.isdir(rasp_nmon_logs):
        print("\nCreating "+rasp_nmon_logs)
        os.mkdir(rasp_nmon_logs)

    hostname=ghostname()
    todays_date=dtime.now().strftime("%y%m%d")
    nmon_file_pattern=rasp_nmon_logs+"/"+nmon_prefix+"_"+hostname

    '''
           Generating nmon filename
    '''
    print("\nGenerating nmon log file.")
    count_nmons=1
    extention_nmon='.nmon'
    while gglob(nmon_file_pattern+"_"+todays_date+"_"+str(count_nmons).zfill(2)+".*"):
        count_nmons+=1
    out_file=nmon_file_pattern+"_"+todays_date+"_"+str(count_nmons).zfill(2)+extention_nmon
    print("\t- "+out_file)

    '''
        Stopping old nmon processes
    '''
    print("\nStopping old nmon processes.")
    foo=os.popen('ps -ef')
    foo_nmon_procs=[param.split()[1] for param in foo.readlines() if nmon_file_pattern in param]
    for pid in foo_nmon_procs:
        os.kill(int(pid),sSIGKILL)

    '''
        Starting NMON in background
    '''
    print("\nStarting NMON in background ...")
    sPopen([nmon_exe,'-F',out_file,'-N','-s',nmon_sleep_seconds,'-c',nmon_stats_count])
    while not os.path.isfile(out_file):
        time.sleep(1)
    os.chmod(out_file,stat.S_IREAD|stat.S_IWRITE|stat.S_IRGRP|stat.S_IROTH)

    '''
        Compressing previous nmon data files
    '''
    print("\nCompressing previous nmon data files.")
    time.sleep(1)
    nmon_files=[nmon_file for nmon_file in gglob(nmon_file_pattern+"_*.nmon") if nmon_file != out_file]
    for nmon_file in nmon_files:
        with open(nmon_file,"rb") as f_in, gopen(nmon_file+".gz","wb") as f_out:
            scopyfileobj(f_in,f_out)
        if os.path.isfile(nmon_file+".gz") and os.path.getsize(nmon_file+".gz") >0:
            os.remove(nmon_file)
            print("\t- "+nmon_file+" -> gzipped")

    '''
        Cleaning old archives
    '''
    print("\nCleaning old archives")
    time.sleep(2)
    nmon_files_gz=[nmon_file_gz for nmon_file_gz in gglob(nmon_file_pattern+"_*.nmon.gz") if (time.time()-os.path.getmtime(nmon_file_gz))/86400 > days_to_keep]
    for nmon_file_gz in nmon_files_gz:
        os.remove(nmon_file_gz)
        print("\t- "+nmon_file+" -> deleted")

if __name__ == "__main__":
    main()
