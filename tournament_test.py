#!/usr/bin/env python
#
# Test cases for tournament.py
# These tests are not exhaustive, but they should cover the majority of cases.
#
# If you do add any of the extra credit options, be sure to add/modify these test cases
# as appropriate to account for your module's added functionality.

from tournament import *

def testCount():
    """
    Test for initial player count,
             player count after 1 and 2 players registered,
             player count after players deleted.
    """
    deleteMatches()
    deleteTournamentPlayers()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deletion, countPlayers should return zero.")
    testSuccess("countPlayers() returns 0 after initial deletePlayers() execution.")
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1. Got {c}".format(c=c))
    testSuccess("countPlayers() returns 1 after one player is registered.")
    registerPlayer("Jace Beleren")
    c = countPlayers()
    if c != 2:
        raise ValueError(
            "After two players register, countPlayers() should be 2. Got {c}".format(c=c))
    testSuccess("countPlayers() returns 2 after two players are registered.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError(
            "After deletion, countPlayers should return zero.")
    testSuccess("countPlayers() returns zero after registered players are deleted.")
    testSuccess("Player records successfully deleted.")


def testCountTounamentPlayers():
    """
    Test for initial player count,
             player count after 1 and 2 players registered,
             player count after players deleted.
    """
    deleteMatches()
    deletePlayers()
    tournId = registerTournament('Grand Tournament')
    c = countTournamentPlayers(tournId)
    if c != 0:
        raise ValueError("After deletion, countPlayers should return zero.")
    testSuccess("countTournamentPlayers() returns 0 after "
          "initial deleteTournamentPlayers() execution.")
    playerId = registerPlayer("Chandra Nalaar")
    registerPlayerForTournament(tournId, playerId)
    c = countTournamentPlayers(tournId)
    if c != 1:
        raise ValueError(
            "After one player registers, countTournamentPlayers() should be 1. Got {c}".format(c=c))
    testSuccess("countTournamentPlayers() returns 1 after one player is registered.")
    playerId = registerPlayer("Jace Beleren")
    registerPlayerForTournament(tournId, playerId)
    c = countTournamentPlayers(tournId)
    if c != 2:
        raise ValueError(
            "After two players register, countTournamentPlayers() should be 2. Got {c}".format(c=c))
    testSuccess("countTournamentPlayers() returns 2 after two players are registered.")
    deleteTournamentPlayers()
    c = countTournamentPlayers(tournId)
    if c != 0:
        raise ValueError(
            "After deletion, countPlayers should return zero.")
    testSuccess("countTournamentPlayers() returns zero after registered players are deleted.")
    testSuccess("Tournament player records successfully deleted.")


def testStandingsBeforeMatches():
    """
    Test to ensure players are properly represented in standings prior
    to any matches being reported.
    """
    deleteMatches()
    deleteTournamentPlayers()
    deleteTournaments()
    deletePlayers()
    tournId = registerTournament('Le Tournament')
    registerPlayerForTournament(tournId, registerPlayer("Melpomene Murray"))
    registerPlayerForTournament(tournId, registerPlayer("Randy Schwartz"))
    standings = playerStandings(tournId)
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    testSuccess("Newly registered players appear in the standings with no matches.")


def testReportMatches():
    """
    Test that matches are reported properly.
    Test to confirm matches are deleted properly.
    """
    deleteTournamentPlayers()
    deleteMatches()
    deleteTournaments()
    deletePlayers()
    tournId = registerTournament('Classic Tournament')
    playerIds = []
    playerStandings
    playerIds.append(registerPlayer("Bruno Walton"))
    playerIds.append(registerPlayer("Boots O'Neal"))
    playerIds.append(registerPlayer("Cathy Burton"))
    playerIds.append(registerPlayer("Diane Grant"))
    for id_ in playerIds:
        registerPlayerForTournament(tournId, id_)
    reportMatch(tournId, playerIds[0], playerIds[1])
    reportMatch(tournId, playerIds[2], playerIds[3])
    standings = playerStandings(tournId)
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (playerIds[0], playerIds[2]) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (playerIds[1], playerIds[3]) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    testSuccess("After a match, players have updated standings.")
    deleteMatches()
    standings = playerStandings(tournId)
    if len(standings) != 4:
        raise ValueError("Match deletion should not change number of players in standings.")
    for (i, n, w, m) in standings:
        if m != 0:
            raise ValueError("After deleting matches, players should have zero matches recorded.")
        if w != 0:
            raise ValueError("After deleting matches, players should have zero wins recorded.")
    testSuccess("After match deletion, player standings are properly reset.")
    testSuccess("Matches are properly deleted.")


def testPairings():
    """
    Test that pairings are generated properly both before and after match reporting.
    """
    deleteMatches()
    deleteTournamentPlayers()
    deleteTournaments()
    deletePlayers()
    tournId = registerTournament("Lumber Choppers Monthly")
    playerIds = []
    names = [
        "Twilight Sparkle",
        "Fluttershy",
        "Applejack",
        "Pinkie Pie",
        "Rarity",
        "Rainbow Dash",
        "Princess Celestia",
        "Princess Luna"
    ]
    for name in names:
        playerIds.append(registerPlayer(name))
    for id_ in playerIds:
        registerPlayerForTournament(tournId, id_)
    standings = playerStandings(tournId)
    pairings = swissPairings(tournId)
    if len(pairings) != 4:
        raise ValueError(
            "For eight players, swissPairings should return 4 pairs. Got {pairs}".format(pairs=len(pairings)))
    reportMatch(tournId, playerIds[0], playerIds[1])
    reportMatch(tournId, playerIds[2], playerIds[3])
    try:
        swissPairings(tournId)
    except RuntimeError:
        testSuccess("swissPairings raised error with incomplete round as expected.")
    else:
        raise ValueError('swissPairings should throw error for incomplete round')
    reportMatch(tournId, playerIds[4], playerIds[5])
    reportMatch(tournId, playerIds[6], playerIds[7])
    pairings = swissPairings(tournId)
    if len(pairings) != 4:
        raise ValueError(
            "For eight players, swissPairings should return 4 pairs. Got {pairs}".format(pairs=len(pairings)))
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), (pid5, pname5, pid6, pname6), (pid7, pname7, pid8, pname8)] = pairings
    possible_pairs = set([frozenset([playerIds[0], playerIds[2]]), frozenset([playerIds[0], playerIds[4]]),
                          frozenset([playerIds[0], playerIds[6]]), frozenset([playerIds[2], playerIds[4]]),
                          frozenset([playerIds[2], playerIds[6]]), frozenset([playerIds[4], playerIds[6]]),
                          frozenset([playerIds[1], playerIds[3]]), frozenset([playerIds[1], playerIds[5]]),
                          frozenset([playerIds[1], playerIds[7]]), frozenset([playerIds[3], playerIds[5]]),
                          frozenset([playerIds[3], playerIds[7]]), frozenset([playerIds[5], playerIds[7]])
                          ])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4]), frozenset([pid5, pid6]), frozenset([pid7, pid8])])
    for pair in actual_pairs:
        if pair not in possible_pairs:
            raise ValueError(
                "After one match, players with one win should be paired.")
    testSuccess("After one match, players with one win are properly paired.")


def testHaveAlreadyPlayed():
    """
        Test whether a haveAlreadyPlayed correctly identifies whether a match
        has already occured.
    """
    deleteMatches()
    deleteTournamentPlayers()
    deleteTournaments()
    deletePlayers()
    player1 = registerPlayer('player 1')
    player2 = registerPlayer('player 2')
    tournId = registerTournament('Classic Tournament')
    registerPlayerForTournament(tournId, player1)
    registerPlayerForTournament(tournId, player2)

    result = haveAlreadyPlayed(tournId, player1, player2)
    if result:
        raise ValueError(
            "Have already played returned %s when it "
            "should have returned False" % result
        )
    testSuccess("haveAlreadyPlayed showed returned False as expected")

    reportMatch(tournId, player1, player2)
    result = haveAlreadyPlayed(tournId, player1, player2)
    if not result:
        raise ValueError(
            "Have already played returned %s when "
            "it should have returned True" % result
        )
    testSuccess("haveAlreadyPlayed showed returned True as expected")



def testNoRematches():
    """
        Test rematch does not occur, using naive matching a rematch will
        occur, test this does not occur. Will not guatanee rematch cannot
        happen but at least check algorithm is being applied.
    """
    deleteMatches()
    deleteTournamentPlayers()
    deleteTournaments()
    deletePlayers()
    tournId = registerTournament('Classic Tournament')
    names = [
        "Twilight Sparkle",
        "Fluttershy",
        "Applejack",
        "Pinkie Pie",
        "Rarity",
        "Rainbow Dash"
    ]
    playerIds = []
    for name in names:
        playerIds.append(registerPlayer(name))

    for id_ in playerIds:
        registerPlayerForTournament(tournId, id_)

    for round_ in range(1, 4):
        pairs = swissPairings(tournId)
        print(pairs)
        for pair in pairs:
            try:
                reportMatch(tournId, pair[0], pair[2])
            except psycopg2.IntegrityError:
                raise ValueError(
                    "Rematch occured in round %i between %s "
                    "and %s" % (round_, pair[1], pair[3]))
    testSuccess("No rematches occured.")


def testHadBye():
    return
    """
        Test whether a haveAlreadyPlayed correctly identifies whether a match
        has already occured.
    """
    deleteMatches()
    deleteTournamentPlayers()
    deleteTournaments()
    deletePlayers()
    player1 = registerPlayer('player 1')
    tournId = registerTournament('Classic Tournament')
    registerPlayerForTournament(tournId, player1)

    result = haveAlreadyPlayed(tournId, player1, player2)
    if result:
        raise ValueError(
            "Have already played returned %s when it "
            "should have returned False" % result
        )
    testSuccess("haveAlreadyPlayed showed returned False as expected")

    reportMatch(tournId, player1, player2)
    result = haveAlreadyPlayed(tournId, player1, player2)
    if not result:
        raise ValueError(
            "Have already played returned %s when "
            "it should have returned True" % result
        )
    testSuccess("haveAlreadyPlayed showed returned True as expected")


TEST_COUNT = 0
def testSuccess(msg):
    global TEST_COUNT;
    TEST_COUNT += 1
    print('%i. %s' % (TEST_COUNT, msg))


if __name__ == '__main__':
    testCount()
    testCountTounamentPlayers()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    testHaveAlreadyPlayed()
    testNoRematches()
    testHadBye()
    print "Success!  All tests pass!"
