# coding=utf-8
# Copyright 2019, Rusty Bower, rustybower.com
from __future__ import unicode_literals, absolute_import, print_function, division

from sopel.formatting import bold
from sopel.module import commands, example
from sopel.tools.time import get_nick_timezone

import arrow
import json
import requests
import time
import uuid


def get_token(bot):
    # Get token expiration time (or 0 if we haven't saved it yet)
    expiresIn = bot.memory.get("expiresIn", 0)

    # Check if current time is later than token expiration, if so, get new token
    if time.time() > expiresIn:
        data = {
            "ClientType": "WEB_DESKTOP_DESKTOP",
            "DeviceId": str(uuid.uuid4()),
            "DeviceInfo": None,
            "NetworkType": None,
            "UserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }

        headers = {
            "Content-type": "application/json",
        }

        r = requests.post(
            "https://www.nfl.com/oauth/nfl/token/client",
            data=json.dumps(data),
            headers=headers,
        )

        # Set accessToken and expiresIn in Sopel memory
        bot.memory["expiresIn"] = r.json()["expiresIn"]
        bot.memory["accessToken"] = r.json()["accessToken"]

        # Return access token to the bot
        return r.json()["accessToken"]
    # Otherwise, return existing token in memory
    else:
        return bot.memory.get("accessToken")


def get_current_week(bot) -> dict:
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer {}".format(get_token(bot)),
    }

    r = requests.get(
        "https://api.nfl.com/football/v2/weeks/date/2021-09-08", headers=headers
    )

    # TODO - Handle API errors
    return r.json()


def get_games(bot, current_week) -> dict:
    # Extract necessary values
    season = current_week["season"]
    seasonType = current_week["seasonType"]
    week = current_week["week"]

    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer {}".format(get_token(bot)),
    }

    r = requests.get(
        f"https://api.nfl.com/experience/v1/games?season={season}&seasonType={seasonType}&week={week}",
        headers=headers,
    )

    # TODO - Handle API errors
    return r.json()["games"]


def parse_game(game, timezone=None):
    # Localize to user timezone if possible
    if timezone:
        game_time = (
            arrow.get(game["time"]).to(timezone).format("ddd h:mm A ZZZ")
        )  # Mon 3:25 PM CDT
    # Otherwise, default to US/Eastern
    else:
        game_time = (
            arrow.get(game["time"]).to("US/Eastern").format("ddd h:mm A ZZZ")
        )  # Mon 4:25 PM EST

    # Scheduled Games
    # If detail isn't in the game json, the game hasn't started yet
    if "detail" not in game.keys():
        # DEN @ NYG Sun 4:25 PM EDT
        return "{} @ {} {}".format(
            game["awayTeam"]["abbreviation"],
            game["homeTeam"]["abbreviation"],
            game_time,
        )

    # Halftime
    elif game["detail"]["phase"] == "HALFTIME":
        # DEN 0 KC 6 Halftime
        return "{} {} {} {} {}".format(
            game["awayTeam"]["abbreviation"],
            game["detail"]["visitorPointsTotal"],
            game["homeTeam"]["abbreviation"],
            game["detail"]["homePointsTotal"],
            game["detail"]["phase"],
        )

    # Final
    elif game["detail"]["phase"] == "FINAL":  # TODO - Figure out Final Overtime
        # KC 17 JAX 7 Final
        # KC 17 JAX 7 Final OT
        if game["detail"]["visitorPointsTotal"] > game["detail"]["homePointsTotal"]:
            return "{} {} {} {} {}".format(
                bold(game["awayTeam"]["abbreviation"]),
                bold(str(game["detail"]["visitorPointsTotal"])),
                game["homeTeam"]["abbreviation"],
                game["detail"]["homePointsTotal"],
                game["detail"]["phase"],
            )
        elif game["detail"]["visitorPointsTotal"] < game["detail"]["homePointsTotal"]:
            return "{} {} {} {} {}".format(
                game["awayTeam"]["abbreviation"],
                game["detail"]["visitorPointsTotal"],
                bold(game["homeTeam"]["abbreviation"]),
                bold(str(game["detail"]["homePointsTotal"])),
                game["detail"]["phase"],
            )
        else:
            return "{} {} {} {} {}".format(
                game["awayTeam"]["abbreviation"],
                game["detail"]["visitorPointsTotal"],
                game["homeTeam"]["abbreviation"],
                game["detail"]["homePointsTotal"],
                game["detail"]["phase"],
            )

    # In Progress
    else:
        # DEN 0 KC 6 09:42 Q1
        return "{} {} {} {} {} Q{}".format(
            game["awayTeam"]["abbreviation"],
            game["detail"]["visitorPointsTotal"],
            game["homeTeam"]["abbreviation"],
            game["detail"]["homePointsTotal"],
            game["detail"]["gameClock"],
            game["detail"]["period"],
        )


@commands("nfl")
@example(".nfl")
@example(".nfl all")
@example(".nfl DEN")
@example(".nfl Denver Broncos")
def nfl(bot, trigger):
    """.nfl <team/all> - Show current game score or next game for an optionally specified team."""
    team = trigger.group(2)
    timezone = get_nick_timezone(bot.db, trigger.nick)

    current_week = get_current_week(bot)
    games = get_games(bot, current_week)

    # Active games
    """
    https://developer.sportradar.com/docs/read/american_football/NFL_v6#frequently-asked-questions

    scheduled – The game is scheduled to occur.
    created – Game data (rosters, officials, etc) are being pre-loaded in preparation for the game.
    inprogress – The game is in progress.
    halftime – The game is currently at halftime.
    complete – The game is over, but stat validation is not complete.
    closed – The game is over and the stats have been validated.
    cancelled – The game has been cancelled. No makeup game will be played as a result.
    postponed – The game has been postponed, to be made up at another day and time. Once the makeup game is announced, a new game and ID will be created and scheduled on the announced makeup date. You should request the scheduled feed(s) regularly to identify the re-scheduled makeup game(s).
    delayed – The scheduled game, or a game that was in progress, is now delayed for some reason.
    flex-schedule – The game is currently scheduled to occur on a specific date and time, however, it will more than likely be moved to a different time for broadcast purposes.
    time-tbd – The game has been scheduled, but a time has yet to be announced.
    """

    # If no team is specified, only return active games
    if not team:
        active_games = [
            game
            for game in games
            if "detail" in game.keys()
            if game["detail"]["phase"] not in ["FINAL"]
        ]

        # Split across multiple lines if we have enough games
        bot.say(" | ".join([parse_game(game, timezone) for game in active_games][0:7]))
        if len(active_games) >= 8:
            bot.say(
                " | ".join([parse_game(game, timezone) for game in active_games][7:14])
            )
        if len(active_games) >= 14:
            bot.say(
                " | ".join([parse_game(game, timezone) for game in active_games][14:])
            )
        return

    # If all is specified, return all teams
    elif team.lower() == "all":
        # Split across multiple lines if we have enough games
        bot.say(" | ".join([parse_game(game, timezone) for game in games][0:7]))
        if len(games) >= 8:
            bot.say(" | ".join([parse_game(game, timezone) for game in games][7:14]))
        if len(games) >= 14:
            bot.say(" | ".join([parse_game(game, timezone) for game in games][14:]))
        return

    # Otherwise, return specific team
    else:
        team_games = [
            game
            for game in games
            if team.lower()
            in [
                game["homeTeam"]["fullName"].lower(),
                game["homeTeam"]["abbreviation"].lower(),
                game["homeTeam"]["location"].lower(),
                game["homeTeam"]["nickName"].lower(),
                game["awayTeam"]["fullName"].lower(),
                game["awayTeam"]["abbreviation"].lower(),
                game["awayTeam"]["location"].lower(),
                game["awayTeam"]["nickName"].lower(),
            ]
        ]

        # If a team was found, return data
        if team_games:
            # Get first (and hopefully only) element of this list
            # TODO - Error checking if len(team_games) != 1
            team_game = team_games[0]

            return bot.say(parse_game(team_game, timezone))
        # Otherwise, team not found
        else:
            return bot.say("Team Not Found")
