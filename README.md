Collects nmon stats of a Linux to a file on daily bases, compresses them and keeps them for some time.

Installation instructions:
  1. Download and install nmon (http://nmon.sourceforge.net/)
  2. Add the following reccord in root's crontab:
     ----------------------------------------------
     0 0 * * * /<pathtoscript>/nmon_start.py >/dev/null 2>&1   # Gather information using nmon
     ----------------------------------------------
