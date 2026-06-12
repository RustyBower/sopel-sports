# coding=utf-8
# Copyright 2026, Rusty Bower, rustybower.com
from __future__ import unicode_literals, absolute_import, print_function, division

from sopel import plugin
from sopel.formatting import bold
from sopel.tools.time import get_nick_timezone

import arrow
import requests


def get_games(bot) -> list:
    r = requests.get(
        "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard",
    )
    data = r.json()

    # TODO - Handle API errors
    games = data["events"]

    return games


def parse_game(game, timezone=None):
    competition = game["competitions"][0]
    status = competition["status"]["type"]

    # ESPN lists competitors as home/away; pull each out explicitly
    home = next(
        c for c in competition["competitors"] if c["homeAway"] == "home"
    )
    away = next(
        c for c in competition["competitors"] if c["homeAway"] == "away"
    )

    # Scheduled Games
    if status["state"] == "pre":
        # Localize to user timezone if possible
        if timezone:
            game_time = arrow.get(game["date"]).to(timezone).format("ddd h:mm A ZZZ")
        # Otherwise, default to US/Eastern
        else:
            game_time = arrow.get(game["date"]).to("US/Eastern").format("ddd h:mm A ZZZ")

        # Bosnia-Herzegovina @ Canada Fri 3:00 PM EDT
        return "{} @ {} {}".format(
            away["team"]["displayName"],
            home["team"]["displayName"],
            game_time,
        )

    # Completed Games (Full Time)
    elif status["state"] == "post":
        # Use the API's detail (e.g. FT, AET, FT-Pens) so shootouts read correctly
        phase = status.get("shortDetail") or "FT"

        # Away Team Win
        if int(away["score"]) > int(home["score"]):
            return "{} {} {} {} {}".format(
                bold(away["team"]["displayName"]),
                bold(str(away["score"])),
                home["team"]["displayName"],
                str(home["score"]),
                phase,
            )
        # Home Team Win
        elif int(home["score"]) > int(away["score"]):
            return "{} {} {} {} {}".format(
                away["team"]["displayName"],
                str(away["score"]),
                bold(home["team"]["displayName"]),
                bold(str(home["score"])),
                phase,
            )
        # Draw
        else:
            return "{} {} {} {} {}".format(
                away["team"]["displayName"],
                str(away["score"]),
                home["team"]["displayName"],
                str(home["score"]),
                phase,
            )

    # In Progress (including Halftime)
    else:
        # Bosnia-Herzegovina 1 Canada 0 45'+4'
        return "{} {} {} {} {}".format(
            away["team"]["displayName"],
            away["score"],
            home["team"]["displayName"],
            home["score"],
            status.get("detail") or competition["status"]["displayClock"],
        )


@plugin.command("worldcup", "wc")
@plugin.example(".worldcup")
@plugin.example(".worldcup all")
@plugin.example(".worldcup USA")
@plugin.example(".worldcup United States")
def world_cup(bot, trigger):
    """.worldcup <team/all> - Show current World Cup scores, or scores for an optionally specified team."""
    team = trigger.group(2)
    timezone = get_nick_timezone(bot.db, trigger.nick)

    games = get_games(bot)

    if not games:
        return bot.say("No World Cup games found")

    # If no team is specified, only return active games
    if not team:
        active_games = [
            game
            for game in games
            if game["competitions"][0]["status"]["type"]["state"] == "in"
        ]

        # If nothing is live, fall back to everything on the slate
        games_to_show = active_games or games

        reply = " | ".join([parse_game(game, timezone) for game in games_to_show])

    # If all is specified, return all games
    elif team.lower() == "all":
        reply = " | ".join([parse_game(game, timezone) for game in games])

    # Otherwise, return specific team
    else:
        team_game = None

        for game in games:
            for competitor in game["competitions"][0]["competitors"]:
                if team.lower() in [
                    competitor["team"]["abbreviation"].lower(),
                    competitor["team"]["displayName"].lower(),
                    competitor["team"]["shortDisplayName"].lower(),
                ]:
                    team_game = game

        if not team_game:
            return bot.say("Team Not Found")

        reply = parse_game(team_game, timezone)

    # Split if greater than 200 characters so we don't accidentally cut anything off
    if len(reply) > 200:
        length = int(len(reply.split(" | ")) / 2)
        bot.say(" | ".join(reply.split(" | ")[0:length]))
        bot.say(" | ".join(reply.split(" | ")[length:]))
        return
    else:
        return bot.say(reply)
