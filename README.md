### Python3 script that collects nmon stats of a Linux (tested on my Raspbian at home) to a file on daily bases, compresses them and keeps them for some time. ###

**Installation instructions:**
  1. Download and install [nmon](http://nmon.sourceforge.net/)
  2. Add the following record in root's crontab:
    
    0 0 * * * /<pathtoscript>/nmon_start.py/nmon_start.py >/dev/null 2>&1   # Gather information using nmon
  
  3. 
	- Linux - Add to /etc/rc.local -> $ echo "/<pathtoscript>/nmon_start.py/nmon_start.py > /dev/console 2>&1" >> /etc/rc.local
