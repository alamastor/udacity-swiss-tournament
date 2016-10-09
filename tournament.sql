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


CREATE TABLE tournaments (
    id      serial PRIMARY KEY,
    name    varchar(40) NOT NULL,
    winner  integer REFERENCES players (id)
);


CREATE VIEW standings AS
SELECT players.id, players.name, count(CASE WHEN players.id = matches.winner then 1 END) AS wins, count(matches.id) AS matches_played
FROM players LEFT JOIN matches
ON players.id = matches.winner
OR players.id = matches.loser
GROUP BY players.id
ORDER BY wins DESC;
