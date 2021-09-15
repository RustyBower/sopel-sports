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
    return bot.memory.get("accessToken")


def get_current_week(bot) -> dict:
    """
    {
        "season": 2021,
        "seasonType": "REG",
        "week": 2,
        "byeTeams": [],
        "dateBegin": "2021-09-15",
        "dateEnd": "2021-09-22",
        "weekType": "REG"
    }
    """
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer {}".format(get_token(bot)),
    }

    current_date = arrow.utcnow().format("YYYY-MM-DD")

    r = requests.get(
        "https://api.nfl.com/football/v2/weeks/date/{}".format(current_date),
        headers=headers,
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
    games = r.json()["games"]

    # Update in progress games
    # games = update_inprogress(bot, games)
    games = update_inprogress(bot, games)
    return games


# The /games api seems to cache randomly, and additional updates are provided via the ?query endpoint
def update_inprogress(bot, games):
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer {}".format(get_token(bot)),
    }

    game_ids = [game["detail"]["id"] for game in games if "detail" in game.keys()]
    game_ids = json.dumps(game_ids, separators=(",", ":"))

    query = (
        "query%7Bviewer%7BgameDetailsByIds(ids%3A"
        + game_ids
        + ")%7Bid%20gameClock%20period%20homeTeam%7Bid%20abbreviation%7DvisitorTeam%7Bid%20abbreviation%7DhomePointsTotal%20visitorPointsTotal%20%7D%7D%7D&variables=null"
    )

    r = requests.get(
        f"https://api.nfl.com/v3/shield/?query={query}",
        headers=headers,
    )

    active_games = [
        game
        for game in games
        if "detail" in game.keys()
        if game["detail"]["phase"] not in ["FINAL", "FINAL_OVERTIME"]
    ]

    gameDetails = r.json()["data"]["viewer"]["gameDetailsByIds"]

    # Update ongoing games
    for i, game in enumerate(active_games):
        for gameDetail in gameDetails:
            if game["detail"]["id"] == gameDetail["id"]:
                games[i]["detail"] = game["detail"].update(gameDetail)

    return games


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
    # There appears to be a bug in the API setting 'detail' to None for past game (Week 1 - TB v Dallas)
    if "detail" not in game.keys() or game["detail"] is None:
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

    # Final || Final Overtime
    elif game["detail"]["phase"] in ["FINAL", "FINAL_OVERTIME"]:
        phase = "Final" if game["detail"]["phase"] == "FINAL" else "Final OT"

        # KC 17 JAX 7 Final
        # KC 17 JAX 7 Final OT
        if game["detail"]["visitorPointsTotal"] > game["detail"]["homePointsTotal"]:
            return "{} {} {} {} {}".format(
                bold(game["awayTeam"]["abbreviation"]),
                bold(str(game["detail"]["visitorPointsTotal"])),
                game["homeTeam"]["abbreviation"],
                game["detail"]["homePointsTotal"],
                phase,
            )
        elif game["detail"]["visitorPointsTotal"] < game["detail"]["homePointsTotal"]:
            return "{} {} {} {} {}".format(
                game["awayTeam"]["abbreviation"],
                game["detail"]["visitorPointsTotal"],
                bold(game["homeTeam"]["abbreviation"]),
                bold(str(game["detail"]["homePointsTotal"])),
                phase,
            )
        else:
            return "{} {} {} {} {}".format(
                game["awayTeam"]["abbreviation"],
                game["detail"]["visitorPointsTotal"],
                game["homeTeam"]["abbreviation"],
                game["detail"]["homePointsTotal"],
                phase,
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
    # TODO - Handle Bye Games
    games = get_games(bot, current_week)

    # If no team is specified, only return active games
    if not team:
        active_games = [
            game
            for game in games
            if arrow.utcnow()
            > arrow.get(
                game["time"]
            )  # Only grab games that are scheduled to have already started
            if "detail" in game.keys()
            if game["detail"]
            if game["detail"]["phase"]
            if game["detail"]["phase"] not in ["FINAL", "FINAL_OVERTIME"]
        ]

        # Split across multiple lines if we have enough games
        # TODO - Keep all these in a single var so we don't make 3 calls to parse_game
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
        # TODO - Keep all these in a single var so we don't make 3 calls to parse_game
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
