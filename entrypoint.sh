#!/bin/sh

echo "[$(date +%H:%M:%S)] [INFO] Running initial EPG generation..."

cd /app && /usr/local/bin/python3 -u -m generate_epg \
  --source-url "https://epgshare01.online/epgshare01/epg_ripper_AU1.xml.gz" \
               "https://epgshare01.online/epgshare01/epg_ripper_BR2.xml.gz" \
               "https://epgshare01.online/epgshare01/epg_ripper_ES1.xml.gz" \
               "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz"

echo "[$(date +%H:%M:%S)] [INFO] Starting cron..."

exec cron -f