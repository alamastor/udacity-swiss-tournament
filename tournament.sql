-- Table definitions for the tournament project.


CREATE TABLE players (
    id      serial PRIMARY KEY,
    name    varchar(40) NOT NULL
);


CREATE TABLE matches (
    id      serial PRIMARY KEY,
    winner integer REFERENCES players (id),
    loser integer REFERENCES players (id),
    CHECK (winner != loser)
);
