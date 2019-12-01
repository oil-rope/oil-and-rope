FROM postgres:10

# Updating
RUN apt-get update

# Installing PostGis
RUN apt-get install --assume-yes postgresql-10*-postgis postgresql-contrib-10*
