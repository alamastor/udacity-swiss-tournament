#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import random

import psycopg2
import psycopg2.extras

from mwmatching import maxWeightMatching


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
        SELECT count(*)
        FROM tournament_players
        WHERE tourn=%s;
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (tournId,))
    result = cur.fetchone()[0]
    conn.close()
    return result


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
        SELECT id, name, wins, matches_played
        FROM standings
        WHERE tourn=%s;
    '''
    conn = connect()
    cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cur.execute(sql, (tournId,))
    results = cur.fetchall()
    conn.close()
    return results


def reportMatch(tourn, winner, loser=None):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost, if not passed will be
        null, representing a bye
    """

    sql = '''
        INSERT INTO matches (tourn, player0, player1, winner)
        VALUES (%s, %s, %s, %s);
    '''

    player0, player1 = max(winner, loser), min(winner, loser)

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (tourn, player0, player1, winner))
    conn.commit()
    conn.close()


def swissPairings(tournId):
    """Returns a list of pairs of players for the next round of a match.

    Each player is paired with another player with an equal or nearly-equal
    win record, that is, a player adjacent to him or her in the standings.
    Rematches are guaranteed not to occur, and if there is an odd number of
    players then one player will randomly be selected to have bye (automatic
    win). Each play will only recieve one bye per tournament.

    To find optimal pairings, all non-rematch pairings are represented as edges
    in graph of player nodes, with edges weighted inversely proportionaly to the
    difference in wins between the two players. The maximum weighted pairings
    are then calculated use the algorithm found at:
    http://jorisvr.nl/article/maximum-matching
    This approach was inspired by this article:
    https://www.leaguevine.com/blog/18/swiss-tournament-scheduling-leaguevines-new-algorithm/
    NOTE: This algorithm is O(n^3)

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    # Check round is complete
    if not roundComplete(tournId):
        raise RuntimeError(
            'Round not complete, complete it before calling swissPairings'
        )
    standings = playerStandings(tournId)
    pairings = []

    # Give one player bye if neccesary.
    if len(standings) % 2 != 0:
        players = set(standings)
        while players:
            # Randomly select player for bye.
            player = random.sample(players, 1)[0]
            if not hadBye(tournId, player.id):
                byePlayer = player
                break
            else:
                # Player has already had bye, try again.
                players.remove(player)
        else:
            # For some all players have had bye, should never happen!
            raise RuntimeError('Could not find player who has not had bye')

        # Remove the bye player from standings list
        standings.pop(standings.index(byePlayer))
        pairings.append([byePlayer.id, byePlayer.name, None, None])


    # Generate edges
    edges = []
    # Iterate of all possible matchups, to build edges in graph.
    for i in range(len(standings)):
        for j in range(i + 1, len(standings)):
            player = standings[i]
            opponent = standings[j]
            if not haveAlreadyPlayed(tournId, player.id, opponent.id):
                # Using maximum weighted pairings algorithm,
                # weight = matches_played - difference_in_wins, for fairest matches.
                difference_in_wins = abs(player.wins - opponent.wins)
                weight = player.matches_played - difference_in_wins
                edges.append((i, j, weight))

    # Algorithm returns results as list, where the each value represents
    # the opponent of each index, eg.
    # [2, 3, 0, 1] mean player 0 plays player 2 and player 1 plays player 3.
    # Now convert this list into list of pairings.
    matches_list = maxWeightMatching(edges, maxcardinality=True)
    for player_idx, opponent_idx in enumerate(matches_list):
        if player_idx > opponent_idx:
            # Pair will have been created in previous iteration.
            continue
        player, opponent = standings[player_idx], standings[opponent_idx]
        pairings.append((player.id, player.name, opponent.id, opponent.name))
    return pairings


def roundComplete(tourn):
    """Returns whether all players have played the same number of games.

    Returns:
        boolean: Is the round complete?
    """

    sql = '''
        SELECT (
            SELECT max(matches_played) from standings
            WHERE tourn = %s
        ) = ALL (
            SELECT matches_played FROM standings
            WHERE tourn = %s
        );
    '''

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (tourn, tourn))
    result = cur.fetchall()[0][0]
    conn.close()
    return result


def haveAlreadyPlayed(tourn, playerA, playerB):
    """Returns whether two players have already played.

    Args:
        tourn: tournament id
        playerA: id of player
        playerB: id of other player

    Returns:
        boolean: Have players played already?
    """
    sql = """
        SELECT EXISTS (
            SELECT *
            FROM matches
            WHERE tourn = %s
            AND player0 = %s
            AND player1 = %s
        );
    """

    player0, player1 = max(playerA, playerB), min(playerA, playerB)

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (tourn, player0, player1))
    result = cur.fetchall()[0][0]
    conn.close()
    return result


def hadBye(tourn, player):
    """Returns whether player has already had a bye.

    Args:
        tourn: tournament id
        player: id of player

    Returns:
        boolean: Has player already had a bye?
    """
    sql = """
        SELECT EXISTS (
            SELECT *
            FROM matches
            WHERE tourn = %s
            AND player0 = %s
            AND player1 IS NULL
        );
    """

    conn = connect()
    cur = conn.cursor()
    cur.execute(sql, (tourn, player))
    result = cur.fetchall()[0][0]
    conn.close()
    return result
