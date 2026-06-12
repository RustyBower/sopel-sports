# coding=utf-8
"""Tests for the World Cup plugin."""
from __future__ import unicode_literals, absolute_import, print_function, division

from unittest import mock

from sopel.formatting import bold

from sopel_sports import world_cup


def make_game(state, away, home, away_score=0, home_score=0,
              detail="", short_detail="", display_clock="",
              date="2026-06-12T19:00Z"):
    """Build a minimal ESPN-shaped event dict for parse_game."""
    def competitor(home_away, name, score):
        return {
            "homeAway": home_away,
            "score": str(score),
            "team": {
                "abbreviation": name[:3].upper(),
                "displayName": name,
                "shortDisplayName": name,
            },
        }

    return {
        "date": date,
        "competitions": [
            {
                "status": {
                    "displayClock": display_clock,
                    "type": {
                        "state": state,
                        "detail": detail,
                        "shortDetail": short_detail,
                    },
                },
                "competitors": [
                    competitor("home", home, home_score),
                    competitor("away", away, away_score),
                ],
            }
        ],
    }


# --- parse_game -------------------------------------------------------------

def test_scheduled_game():
    game = make_game("pre", "Paraguay", "United States",
                     date="2026-06-13T01:00Z")
    # Default timezone is US/Eastern
    assert world_cup.parse_game(game) == "Paraguay @ United States Fri 9:00 PM EDT"


def test_scheduled_game_localized():
    game = make_game("pre", "Paraguay", "United States",
                     date="2026-06-13T01:00Z")
    assert world_cup.parse_game(game, "US/Central") == \
        "Paraguay @ United States Fri 8:00 PM CDT"


def test_in_progress_game():
    game = make_game("in", "Bosnia-Herzegovina", "Canada",
                     away_score=1, home_score=0, detail="45'+4'")
    assert world_cup.parse_game(game) == "Bosnia-Herzegovina 1 Canada 0 45'+4'"


def test_in_progress_falls_back_to_display_clock():
    game = make_game("in", "Bosnia-Herzegovina", "Canada",
                     away_score=1, home_score=0, display_clock="67'")
    assert world_cup.parse_game(game) == "Bosnia-Herzegovina 1 Canada 0 67'"


def test_final_away_win():
    game = make_game("post", "Argentina", "France",
                     away_score=4, home_score=2, short_detail="FT")
    assert world_cup.parse_game(game) == \
        "{} {} France 2 FT".format(bold("Argentina"), bold("4"))


def test_final_home_win():
    game = make_game("post", "Argentina", "France",
                     away_score=2, home_score=4, short_detail="FT")
    assert world_cup.parse_game(game) == \
        "Argentina 2 {} {} FT".format(bold("France"), bold("4"))


def test_final_draw():
    game = make_game("post", "Argentina", "France",
                     away_score=3, home_score=3, short_detail="FT-Pens")
    assert world_cup.parse_game(game) == "Argentina 3 France 3 FT-Pens"


def test_final_defaults_phase_when_missing():
    game = make_game("post", "Argentina", "France",
                     away_score=1, home_score=0)
    assert world_cup.parse_game(game) == \
        "{} {} France 0 FT".format(bold("Argentina"), bold("1"))


# --- world_cup command ------------------------------------------------------

class FakeBot:
    def __init__(self):
        self.messages = []
        self.db = mock.Mock()

    def say(self, message):
        self.messages.append(message)


class FakeTrigger:
    def __init__(self, arg=None, nick="tester"):
        self._arg = arg
        self.nick = nick

    def group(self, n):
        return self._arg


def run_command(games, arg=None, timezone=None):
    bot = FakeBot()
    trigger = FakeTrigger(arg)
    with mock.patch.object(world_cup, "get_games", return_value=games), \
            mock.patch.object(world_cup, "get_nick_timezone",
                              return_value=timezone):
        world_cup.world_cup(bot, trigger)
    return bot.messages


def test_command_no_games():
    assert run_command([]) == ["No World Cup games found"]


def test_command_default_shows_live_only():
    live = make_game("in", "Bosnia-Herzegovina", "Canada",
                     away_score=1, home_score=0, detail="HT")
    scheduled = make_game("pre", "Paraguay", "United States")
    messages = run_command([live, scheduled])
    assert messages == ["Bosnia-Herzegovina 1 Canada 0 HT"]


def test_command_default_falls_back_when_nothing_live():
    scheduled = make_game("pre", "Paraguay", "United States",
                          date="2026-06-13T01:00Z")
    messages = run_command([scheduled])
    assert messages == ["Paraguay @ United States Fri 9:00 PM EDT"]


def test_command_all_shows_everything():
    live = make_game("in", "Bosnia-Herzegovina", "Canada",
                     away_score=1, home_score=0, detail="HT")
    scheduled = make_game("pre", "Paraguay", "United States",
                          date="2026-06-13T01:00Z")
    messages = run_command([live, scheduled], arg="all")
    assert messages == [
        "Bosnia-Herzegovina 1 Canada 0 HT | "
        "Paraguay @ United States Fri 9:00 PM EDT"
    ]


def test_command_team_filter_found():
    live = make_game("in", "Bosnia-Herzegovina", "Canada",
                     away_score=1, home_score=0, detail="HT")
    scheduled = make_game("pre", "Paraguay", "United States",
                          date="2026-06-13T01:00Z")
    messages = run_command([live, scheduled], arg="United States")
    assert messages == ["Paraguay @ United States Fri 9:00 PM EDT"]


def test_command_team_filter_by_abbreviation():
    live = make_game("in", "Bosnia-Herzegovina", "Canada",
                     away_score=1, home_score=0, detail="HT")
    messages = run_command([live], arg="can")
    assert messages == ["Bosnia-Herzegovina 1 Canada 0 HT"]


def test_command_team_not_found():
    live = make_game("in", "Bosnia-Herzegovina", "Canada",
                     away_score=1, home_score=0, detail="HT")
    assert run_command([live], arg="Brazil") == ["Team Not Found"]


def test_command_splits_long_replies():
    games = [
        make_game("post", "Country{}A".format(i), "Country{}B".format(i),
                  away_score=i, home_score=0, short_detail="FT")
        for i in range(12)
    ]
    messages = run_command(games, arg="all")
    # Reply exceeds 200 chars, so it is split across two say() calls
    assert len(messages) == 2
