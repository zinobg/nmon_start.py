### Python3 script that collects nmon stats of a Linux (tested on my Raspbian at home) to a file on daily bases, compresses them and keeps them for some time. ###

**Installation instructions:**
  1. Download and install [nmon](http://nmon.sourceforge.net/)
  2. Add the following record in root's crontab:
  
	0 0 * * * /<pathtoscript>/nmon_start.py/nmon_start.py >/dev/null 2>&1
  
  3. Add the following record in /etc/rc.local:
  
	/<pathtoscript>/nmon_start.py/nmon_start.py > /dev/console 2>&1 >> /etc/rc.local

Collected nmon files are used to generate a deep performance review for the monitored server, using [nmon Analyser](http://nmon.sourceforge.net/pmwiki.php?n=Site.Nmon-Analyser)
