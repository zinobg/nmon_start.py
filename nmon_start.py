#!/usr/bin/python
################################################################
# Program : start_nmon.py
# Author  : Konstantin Yovchev
# Date    : 18/03/2019
# Ver     : 3.0
# Desc    : Collects nmon stats to a file on daily bases, compresses them and keeps them for some time.
#         : Add following reccord in root's crontab:
#         : ----------------------------------------------
#         : 0 0 * * * /<pathtoscript>/nmon_start.py >/dev/null 2>&1   # Gather information using nmon
#         : ----------------------------------------------
################################################################

import os,socket,datetime,time,glob,gzip,shutil,signal,subprocess

#
# Tunable Variables
#

nmon_exe="/usr/bin/nmon"                  # nmon executable
nmon_sleep_seconds="300"                  # sleep time between nmon iterations
nmon_stats_count="288"                    # number or nmon iterations
nmon_file_mask="RPI"                      # output filename mask
rasp_nmon_dir="/nmon/logs_test"                # output direcroty for Linux server
days_to_keep=30                         # how many days to keep *.nmon.gz files, before delete them

# Flags for topas_nmon are:
#       d for disk service times
#       N for NFS stats
#       ^ for adapter stats

flags="-N"                   # RPI settings

if not os.path.isdir(rasp_nmon_dir):
    os.mkdir(rasp_nmon_dir)

#
# Functions
#

def check_output_file(file_part):
    count=1
    while glob.glob(file_part+"_"+str(count).zfill(2)+".*"):
        count=count+1
    return file_part+"_"+str(count).zfill(2)+".nmon"

#
# Main
#

hostname=socket.gethostname()
todays_date=datetime.datetime.now().strftime("%y%m%d")

#
# Figure out the nmon output file name - Allow for nmon restarts
#
out_file=check_output_file(rasp_nmon_dir+"/"+nmon_file_mask+"_"+hostname+"_"+todays_date)

#
# Stop any existing nmons writing to monitor
#

pids=[pid for pid in os.listdir('/proc') if pid.isdigit()]
for pid in pids:
    try:
        param=open(os.path.join('/proc',pid,'cmdline'),'rb').read().split('\0')[2]
        if rasp_nmon_dir+"/"+nmon_file_mask+"_"+hostname in param:
            os.kill(int(pid),signal.SIGKILL)
            #print "pid to kill "+pid
    except: # proc has already terminated
        pass

#
# Start-up nmon
#

subprocess.Popen([nmon_exe,'-F',out_file,flags,'-s',nmon_sleep_seconds,'-c',nmon_stats_count])
time.sleep(10)
os.chmod(out_file,0644)

#
# Compress previous nmon data files.
#

print "Compressing previous nmon data files."
time.sleep(10)

for nmon_file in glob.glob(rasp_nmon_dir+"/"+nmon_file_mask+"_*.nmon"):
    if nmon_file != out_file:
        with open(nmon_file,"rb") as f_in, gzip.open(nmon_file+".gz","wb") as f_out:
            shutil.copyfileobj(f_in,f_out)
        if os.path.isfile(nmon_file+".gz") and os.path.getsize(nmon_file+".gz") >0:
            os.remove(nmon_file)

#
# Housekeeping
#

for nmon_file_gz in glob.glob(rasp_nmon_dir+"/"+nmon_file_mask+"_*.nmon.gz"):
    if (time.time()-os.path.getmtime(nmon_file_gz))/86400 > days_to_keep:
        os.remove(nmon_file)

exit()
