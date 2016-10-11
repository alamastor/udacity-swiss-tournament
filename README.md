# Udacity Tournament Results Project
A library for running a Swiss style tournament backed with a PostgreSQL database.

## Setup
1. Install PostgreSQL.
2. Create database and add tables:
```
  $ cd path/to/project
  $ psql
  => create database tournament;
  => \c tournament
  => \i tournament.sql
```

## Run Test
``` ./tournament_test.py ```
