#!/usr/bin/python
'''
 Program : start_nmon.py
 Author  : Konstantin Yovchev
 Date    : 18/03/2019
 Ver      : 3.0
 Desc    : Collects nmon stats of a Linux to a file on daily bases, compresses them and keeps them for some time.
         :
         : Installation instructions:
         :  1. Download and install nmon
         :  2. Add the following reccord in root's crontab:
         :     ----------------------------------------------
         :     0 0 * * * /<pathtoscript>/nmon_start.py >/dev/null 2>&1   # Gather information using nmon
         :     ----------------------------------------------
'''
import os,socket,datetime,time,glob,gzip,shutil,signal,subprocess

nmon_exe="/usr/bin/nmon"                  # nmon executable
nmon_sleep_seconds="300"                  # sleep time between nmon iterations
nmon_stats_count="288"                    # number or nmon iterations
nmon_file_mask="RPI"                      # output filename mask
rasp_nmon_dir="/nmon/logs"                # output direcroty for Linux server (will be created if doesn't exists)
days_to_keep=30                           # how many days to keep nmon.gz files, before delete them

def check_output_file(file_part):
    count=1
    while glob.glob(file_part+"_"+str(count).zfill(2)+".*"):
        count=count+1
    return file_part+"_"+str(count).zfill(2)+".nmon"

def main():
    if not os.path.isdir(rasp_nmon_dir):
        print "\nCreating "+rasp_nmon_dir
        os.mkdir(rasp_nmon_dir)

    hostname=socket.gethostname()
    todays_date=datetime.datetime.now().strftime("%y%m%d")
    nmon_file_pattern=rasp_nmon_dir+"/"+nmon_file_mask+"_"+hostname

    print "\nGenerating nmon log file."
    out_file=check_output_file(nmon_file_pattern+"_"+todays_date)
    print "\t- "+out_file

    print "\nStopping old nmon processes."
    pids=[pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            param=open(os.path.join('/proc',pid,'cmdline'),'rb').read().split('\0')[2]
            if nmon_file_pattern in param:
                os.kill(int(pid),signal.SIGKILL)
                #print "pid to kill "+pid
        except:
            pass

    print "\nStarting NMON in background ..."
    subprocess.Popen([nmon_exe,'-F',out_file,'-N','-s',nmon_sleep_seconds,'-c',nmon_stats_count])
    time.sleep(10)
    os.chmod(out_file,0644)

    print "\nCompressing previous nmon data files."
    time.sleep(10)
    nmon_files=[nmon_file for nmon_file in glob.glob(nmon_file_pattern+"_*.nmon") if nmon_file != out_file]
    for nmon_file in nmon_files:
        with open(nmon_file,"rb") as f_in, gzip.open(nmon_file+".gz","wb") as f_out:
            shutil.copyfileobj(f_in,f_out)
        if os.path.isfile(nmon_file+".gz") and os.path.getsize(nmon_file+".gz") >0:
            os.remove(nmon_file)
            print "\t- "+nmon_file+" -> gzipped"

    print "\nCleaning old archives"
    time.sleep(5)
    nmon_files_gz=[nmon_file_gz for nmon_file_gz in glob.glob(nmon_file_pattern+"_*.nmon.gz") if (time.time()-os.path.getmtime(nmon_file_gz))/86400 > days_to_keep]
    for nmon_file_gz in nmon_files_gz:
        os.remove(nmon_file_gz)
        print "\t- "+nmon_file+" -> deleted"

if __name__ == "__main__":
    main()
