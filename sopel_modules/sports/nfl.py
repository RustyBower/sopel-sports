# coding=utf-8
# Copyright 2019, Rusty Bower, rustybower.com
from __future__ import unicode_literals, absolute_import, print_function, division

from sopel.formatting import bold
from sopel.module import commands, example
from sopel.tools.time import get_nick_timezone

import arrow
import requests


'''
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
'''


def get_games(bot) -> list:
    r = requests.get(
        "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
    )
    data = r.json()

    # TODO - Handle API errors
    games = data["events"]

    return games


def parse_game(game, timezone=None):
    # Localize to user timezone if possible
    if timezone:
        game_time = (
            arrow.get(game["date"]).to(timezone).format("ddd h:mm A ZZZ")
        )  # Mon 3:25 PM CDT
    # Otherwise, default to US/Eastern
    else:
        game_time = (
            arrow.get(game["date"]).to("US/Eastern").format("ddd h:mm A ZZZ")
        )  # Mon 4:25 PM EST

    # Scheduled Games
    if game["status"]["type"]["name"] == "STATUS_SCHEDULED":
        # DEN @ NYG Sun 4:25 PM EDT
        return "{} @ {} {}".format(
            game["competitions"][0]["competitors"][1]["team"][
                "abbreviation"
            ],  # Is 1 away? Otherwise, need to list comprehension to filter
            game["competitions"][0]["competitors"][0]["team"]["abbreviation"],
            game_time,
        )

    # Halftime
    elif game["status"]["type"]["name"] == "STATUS_HALFTIME":
        # DEN 0 KC 6 Halftime
        return "{} {} {} {} {}".format(
            game["competitions"][0]["competitors"][1]["team"]["abbreviation"],  # Away
            game["competitions"][0]["competitors"][1]["score"],
            game["competitions"][0]["competitors"][0]["team"]["abbreviation"],  # Home
            game["competitions"][0]["competitors"][0]["score"],
            game["status"]["type"]["description"],
        )

    # Final || Final Overtime
    elif game["status"]["type"]["name"] in ["STATUS_FINAL", "STATUS_FINAL_OVERTIME"]:
        phase = (
            "Final" if game["status"]["type"]["name"] == "STATUS_FINAL" else "Final OT"
        )

        # KC 17 JAX 7 Final
        # KC 17 JAX 7 Final OT
        if int(game["competitions"][0]["competitors"][1]["score"]) > int(
            game["competitions"][0]["competitors"][0]["score"]
        ):
            return "{} {} {} {} {}".format(
                bold(
                    game["competitions"][0]["competitors"][1]["team"]["abbreviation"]
                ),  # Away
                bold(str(game["competitions"][0]["competitors"][1]["score"])),
                game["competitions"][0]["competitors"][0]["team"][
                    "abbreviation"
                ],  # Home
                game["competitions"][0]["competitors"][0]["score"],
                phase,
            )
        elif int(game["competitions"][0]["competitors"][1]["score"]) < int(
            game["competitions"][0]["competitors"][0]["score"]
        ):
            return "{} {} {} {} {}".format(
                game["competitions"][0]["competitors"][1]["team"][
                    "abbreviation"
                ],  # Away
                game["competitions"][0]["competitors"][1]["score"],
                bold(
                    game["competitions"][0]["competitors"][0]["team"]["abbreviation"]
                ),  # Home
                bold(str(game["competitions"][0]["competitors"][0]["score"])),
                phase,
            )
        else:
            return "{} {} {} {} {}".format(
                game["competitions"][0]["competitors"][1]["team"][
                    "abbreviation"
                ],  # Away
                game["competitions"][0]["competitors"][1]["score"],
                game["competitions"][0]["competitors"][0]["team"][
                    "abbreviation"
                ],  # Home
                game["competitions"][0]["competitors"][0]["score"],
                phase,
            )

    # In Progress
    else:
        # DEN 0 KC 6 09:42 Q1
        return "{} {} {} {} {} Q{}".format(
            game["competitions"][0]["competitors"][1]["team"]["abbreviation"],  # Away
            game["competitions"][0]["competitors"][1]["score"],
            game["competitions"][0]["competitors"][0]["team"]["abbreviation"],  # Home
            game["competitions"][0]["competitors"][0]["score"],
            game["competitions"][0]["status"]["displayClock"],
            game["competitions"][0]["status"]["period"],
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

    # TODO - Handle Bye Games
    games = get_games(bot)

    # If no team is specified, only return active games
    if not team:
        active_games = [
            game
            for game in games
            if game["status"]["type"]["name"]
            not in ["STATUS_SCHEDULED", "STATUS_FINAL", "STATUS_FINAL_OVERTIME"]
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
        team_game = None

        for game in games:
            for competitor in game["competitions"][0]["competitors"]:
                if team.lower() in [
                    # competitor["team"]["name"],  # Washington Football Team breaks this because they don't have a name?
                    competitor["team"]["abbreviation"].lower(),
                    competitor["team"]["displayName"].lower(),
                    competitor["team"]["shortDisplayName"].lower(),
                ]:
                    team_game = game

        if team_game:
            print("game found")
            return bot.say(parse_game(team_game, timezone))
        # Otherwise, team not found
        else:
            return bot.say("Team Not Found")
