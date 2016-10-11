-- Table definitions for the tournament project.


-- Records all players registered in the system.
CREATE TABLE players (
    id      serial PRIMARY KEY,
    name    varchar(40) NOT NULL
);


-- Records all tournaments in the system.
CREATE TABLE tournaments (
    id      serial PRIMARY KEY,
    name    varchar(40) NOT NULL,
    winner  integer REFERENCES players (id)
);


-- Records players registered in individual tournaments.
CREATE TABLE tournament_players (
    tourn   integer REFERENCES tournaments NOT NULL,
    player  integer REFERENCES players (id) NOT NULL,
    UNIQUE (tourn, player)
);


-- Records the all matches played.
-- Player0 must have greater value than Player1, to make it easier to check for uniqueness.
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


-- Represents current standings.
CREATE VIEW standings AS
SELECT id, name, wins, matches_played, tourn
FROM players JOIN (
    SELECT
        tournament_players.player,
        count(CASE WHEN tournament_players.player = matches.winner then 1 END) AS wins,
        count(matches.id) AS matches_played,
        tournament_players.tourn
    FROM tournament_players LEFT JOIN matches
    ON tournament_players.player = matches.player0
    OR tournament_players.player = matches.player1
    GROUP BY tournament_players.tourn, tournament_players.player
) AS id_standings
ON players.id = id_standings.player
ORDER BY wins DESC, tourn;
