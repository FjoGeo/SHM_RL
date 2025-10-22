# Structured Health Monitoring with Reinforcement Learning

This project explores the application of reinforcement learning for structured health monitoring, leveraging BIM data and spatial databases.

## Recommended stack

- IfcOpenShell
- PostgreSQL + PostGIS
- Three.js

## 1. PostgreSQL setup in WSL (+arch)

### Installation

```bash
# Installation
sudo pacman -S postgresql
sudo -u postgres initdb -D /var/lib/postgres/data --locale=C.UTF-8 --encoding=UTF8
# start server
sudo systemctl start postgresql
sudo systemctl enable postgresql
# check status
sudo systemctl status postgresql
```

### Access

```bash
# Acces DB
sudo -u postgres psql

# quit
\q

```

### PostGIS

```bash
# install PostGIS
sudo pacman -S postgis

# restart PostgreSQL service
sudo systemctl restart postgresql
```

### Enable PostGIS

```bash
# create a database
sudo -u postgres createdb shm

# connect to the database
sudo -u postgres psql -d shm

# enable PostGIS extension
CREATE EXTENSION postgis;

# install topology extension
CREATE EXTENSION postgis_topology;

# verify installation
SELECT postgis_full_version();

# EXIT
\q
```

## 2. Python Setup

## 3. Neo4j Setup

```bash
# Install
yay -S neo4j-community

# WSL settings
sudo mkdir -p /var/log/neo4j
sudo mkdir -p /var/lib/neo4j
sudo chown -R neo4j:neo4j /var/log/neo4j /var/lib/neo4j

# enable service
sudo systemctl enable neo4j.service
sudo systemctl start neo4j.service

# check status
sudo systemctl status neo4j.service

# access browser
http://localhost:7474

# default credentials
neo4j:neo4j

----
# on windows
Install neo4j Desktop and add connection to WSL
Go to conf and change network settings:
    - server.default_advertised_address=<windows host IP>
    - server.http.listen_address=:7475
```

## 4. load IFC into Neo4j

## 5. Load IFC geometry information to PostgreSQL

## 6. Link Neo4J and PostgreSQL data

## 7. Visualization (maybe Three.js)

## 8. neo4j syntax

```bash
# delete everything
MATCH (n)
DETACH DELETE n;

```
