# epg-script-debridio

A python script for the https://debridio.com/ live tv addon that generates an EPG xml file

Access the EPG XML file here: https://epg.100519.xyz/guide.xml.gz

## Self-hosting

By default every country in the addon is included. If you only need a subset, you can self-host and run the command below excluding any country you do not want. This may improve loading times for the EPG in IPTV apps.

```py
python -m generate_epg \
--source-url "https://epgshare01.online/epgshare01/epg_ripper_AU1.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_BR2.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_CA2.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_CL1.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_ES1.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_FR1.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_IN1.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_MX1.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_NZ1.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_US_LOCALS1.xml.gz" \
             "https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz" \
--ids ids.txt \
--output guide.xml
```

Remember guides are usually updated daily so you will have to schedule the script to run yourself, such as with the included crontab.

## Docker

A Dockerfile and cron is included for scheduling a container to run the script every day at 06:00 EST. If you would like to change this please edit the `crontab` file and change the `TZ` env in the dockerfile.

### Docker Compose

An example docker compose for users who don't want to clone the repo.

```yaml
services:
  epg-generator:
    build:
      context: https://github.com/evanesce345/epg-script-debridio.git
      dockerfile: Dockerfile
    volumes:
      - epg_data:/app/epg
    container_name: epg-generator
    restart: unless-stopped

  epg-server:
    image: nginx:alpine
    ports:
      - 1776:1776
    volumes:
      - .conf:/etc/nginx/conf.d/default.conf:ro
      - epg_data:/usr/share/nginx/html
    command: sh -c "rm -f /usr/share/nginx/html/index.html && rm -f /usr/share/nginx/html/50x.html && nginx -g 'daemon off;'"
    # for traefik
    # labels:
    #  - "traefik.enable=true"
    #  - "traefik.http.routers.epg.rule=Host(`${INSERT_HOST_NAME_HERE}`)"
    #  - "traefik.http.routers.epg.entrypoints=websecure"
    #  - "traefik.http.routers.epg.tls.certresolver=letsencrypt"
    # - "traefik.http.services.epg.loadbalancer.server.port=1776"
    container_name: epg-server
    restart: unless-stopped

volumes:
  epg_data:
```

### Nginx Config

An example Nginx Config for use with the aforementioned compose file.

```nginx
server {
    listen 1776;
    root /usr/share/nginx/html;

    gzip off;
    gunzip off;

    location / {
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
        try_files $uri $uri/ =404;
        add_header Access-Control-Allow-Origin "*";
    }

    location ~* \.xml\.gz$ {
        default_type application/octet-stream;
        add_header Content-Disposition "attachment; filename=guide.xml.gz";
        add_header Cache-Control "public, max-age=300";
        expires 23h;
        etag on;
    }
}
```
