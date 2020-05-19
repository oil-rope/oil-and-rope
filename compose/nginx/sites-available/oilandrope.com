server {
  listen 80;
  listen [::]:80;
  charset utf-8;

  server_name localhost;

  location / {
    # Ensure the IP of the client sending requests to the NGINX is stored in the request header
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    # Host header to be NGINX server
    proxy_set_header Host $host;

    proxy_pass  http://gunicorn_server;
  }

  location /static/ {
    autoindex on;
    alias /static/;
  }

  location /media/ {
    autoindex on;
    alias /media/;
  }
}

upstream gunicorn_server {
  # Sticky session
  ip_hash;
  server django:5000;
}
