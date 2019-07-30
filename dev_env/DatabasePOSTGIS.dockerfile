FROM postgres:9.6

# Updating
RUN apt-get update

# Installing PostGis
RUN apt-get install --assume-yes postgresql-9.6-postgis postgresql-contrib-9.6
