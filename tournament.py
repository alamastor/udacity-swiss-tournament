#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    sql = '''
        DELETE FROM matches;
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    sql = '''
        DELETE FROM players;
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()


def deleteTournaments():
    """Remove all the tournament records from the database."""
    sql = '''
        DELETE FROM tournaments;
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()


def deleteTournamentPlayers():
    """Remove all the records from the tournament_players table."""
    sql = '''
        DELETE FROM tournament_players;
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    sql = '''
        SELECT count(*) FROM players;
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchone()[0]
    conn.close()
    return result


def countTournamentPlayers(tournId):
    """Returns the number of players currently registered for tournament.

    Args:
        tournId: the id of the tournament.
    """
    sql = '''
        SELECT count(*) FROM tournament_players;
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchone()[0]
    conn.close()
    return result
    return 0


def registerTournament(name):
    """Adds a tournament to the tournament database and return it's id.

    Args:
      name: the tournament's full name (need not be unique).

    Returns:
      integer: the tournament's new id.
    """

    sql = '''
        INSERT INTO tournaments (name) VALUES (%s)
        RETURNING id;
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (name,))
    id_ = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return id_


def registerPlayer(name):
    """Adds a player to the tournament database and return their id.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).

    Returns:
      integer: the player's new id.
    """

    sql = '''
        INSERT INTO players (name) VALUES (%s)
        RETURNING id;
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (name,))
    id_ = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return id_


def registerPlayerForTournament(tournId, playerId):
    """Adds a player to a tournament.

    Args:
      tournId: a tournament's id.
      playerId: a player's id.
    """

    sql = '''
        INSERT INTO tournament_players (tourn, player)
        VALUES (%s, %s);
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (tournId, playerId))
    conn.commit()
    conn.close()


def playerStandings(tournId):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
      tournId: the tournament to get standings for.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    sql = '''
        SELECT * FROM standings;
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    conn.close()
    return results


def reportMatch(tourn, winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    sql = '''
        INSERT INTO matches (tourn, winner, loser)
        VALUES (%s, %s, %s);
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (tourn, winner, loser))
    conn.commit()
    conn.close()


def swissPairings(tournId):
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    # Check round is complete
    if not roundComplete():
        raise RuntimeError(
            'Round not complete, complete it before calling swissPairings'
        )
    standings = playerStandings(tournId)

    sql = '''
        SELECT id, name
        FROM standings
        ;
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    result = []

    pair = cur.fetchmany(2)
    while pair:
        player1, player2 = pair
        result.append(player1 + player2)
        pair = cur.fetchmany(2)
    return result


def roundComplete():
    """Returns whether all players have played the same number of games.

    Returns:
        boolean: Is the round complete?
    """

    sql = '''
        SELECT (SELECT max(matches_played) from standings) = ALL (SELECT matches_played FROM standings);
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()[0][0]
    conn.close()
    return result
