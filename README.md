# epg-script-debridio

A python script for the https://debridio.com/ live tv addon that generates an EPG xml file

Access the EPG XMl file here: TBD

## Discrepancies

Some channels across regions have the same tvg-id. This means some of the networks across countries will all erroneously share the same guide. This cannot be fixed unless the developer updates the addon to create unique ids, or you edit your own m3u8 playlist file. A list of the discrepant channels is below.

### List of discrepant channels

- ABC
- Cartoon Network
- Disney Channel
- Nickelodeon
- History
- beIN Sports
- bravo
- ESPN
- ESPN2
- Fox Sports
- FX
- MTV
- TNT

## Self-hosting

If you want to self-host the guide and customize the countries you would like to add, simply edit the `mapping.json` file to your liking or create another. You may run the command below for all the countries featured in the debridio TV addon, or specify any link to an xml (provided you create your own matchings).

Remember guides are usually updated daily so you will have to schedule the script to run yourself, such as with crontab.

```
python -m generate_epg \
--source-url "https://epgshare01.online/epgshare01/epg_ripper_AU1.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_BR2.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_CA2.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_CL1.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_ES1.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_FR1.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_IN1.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_MX1.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_NZ1.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz" "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz" \
--mapping mapping.json \
--output guide.xml
```
