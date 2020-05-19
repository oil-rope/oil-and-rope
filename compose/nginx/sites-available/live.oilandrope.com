server {
  listen 80;
  listen [::]:80;
  charset utf-8;

  server_name live.oilandrope.com;

  location /ws/ {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $host;

    proxy_pass  http://daphne_server;

    proxy_http_version 1.1;
    # Websockets only comunicate to Upgrade
    proxy_set_header Upgrade $http_upgrade;
    # Ensure connection is upgrade
    proxy_set_header Connection "Upgrade";
  }

}

upstream daphne_server {
  # Sticky session
  ip_hash;
  server channels:5001;
}