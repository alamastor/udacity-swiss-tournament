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
    player0 integer REFERENCES players (id) NOT NULL,
    player1 integer REFERENCES players (id),
    winner  integer NOT NULL,
    CHECK (player0 > player1),
    UNIQUE (tourn, player0, player1),
    FOREIGN KEY (tourn, player0) REFERENCES tournament_players (tourn, player),
    FOREIGN KEY (tourn, player1) REFERENCES tournament_players (tourn, player),
    CHECK (winner = player0 or winner = player1)
);


CREATE VIEW standings AS
SELECT players.id, players.name, count(CASE WHEN players.id = matches.winner then 1 END) AS wins, count(matches.id) AS matches_played
FROM players LEFT JOIN matches
ON players.id = matches.player0
OR players.id = matches.player1
GROUP BY players.id
ORDER BY wins DESC;
