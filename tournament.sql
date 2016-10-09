-- Table definitions for the tournament project.


CREATE TABLE players (
    id      serial PRIMARY KEY,
    name    varchar(40) NOT NULL
);


CREATE TABLE matches (
    id      serial PRIMARY KEY,
    player1 integer REFERENCES players (id),
    player2 integer REFERENCES players (id),
    winner  integer REFERENCES players (id),
    CHECK (player1 != player2),
    CHECK (winner = player1 or winner = player2)
);
