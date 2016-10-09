-- Table definitions for the tournament project.


CREATE TABLE players (
    id      serial PRIMARY KEY,
    name    varchar(40) NOT NULL
);


CREATE TABLE tournaments (
    id      serial PRIMARY KEY,
    name    varchar(40) NOT NULL,
    winner  integer REFERENCES players (id)
);


CREATE TABLE tournament_players (
    tourn   integer REFERENCES tournaments NOT NULL,
    player  integer REFERENCES players (id) NOT NULL,
    UNIQUE (tourn, player)
);


CREATE TABLE matches (
    id      serial PRIMARY KEY,
    tourn   integer REFERENCES tournaments (id) NOT NULL,
    winner  integer NOT NULL,
    loser   integer,
    CHECK (winner != loser),
    FOREIGN KEY (tourn, winner) REFERENCES tournament_players (tourn, player),
    FOREIGN KEY (tourn, loser) REFERENCES tournament_players (tourn, player)
);


CREATE VIEW standings AS
SELECT players.id, players.name, count(CASE WHEN players.id = matches.winner then 1 END) AS wins, count(matches.id) AS matches_played
FROM players LEFT JOIN matches
ON players.id = matches.winner
OR players.id = matches.loser
GROUP BY players.id
ORDER BY wins DESC;
