# coding=utf-8
# Copyright 2019, Rusty Bower, rustybower.com
import arrow
import requests

from sopel.formatting import bold
from sopel.module import commands, example
from sopel.tools.time import get_nick_timezone


def parse_games(date, timezone=None):
    if date:
        r = requests.get(
            "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={}".format(date)
        )
    else:
        r = requests.get("https://statsapi.mlb.com/api/v1/schedule?sportId=1")
    reply = []
    for date in r.json()["dates"]:
        # TODO - Figure out what events and matches are
        for game in date["games"]:
            # Game Is Not Started
            if game["status"]["abstractGameState"] == "Preview":
                # Localize to user timezone if possible
                if timezone:
                    game_time = arrow.get(game["gameDate"]).to(timezone).format("ddd h:mm A ZZZ")
                # Otherwise, default to US/Eastern
                else:
                    game_time = arrow.get(game["gameDate"]).to("US/Eastern").format("ddd h:mm A ZZZ")
                reply.append(
                    "{} @ {} {}".format(
                        game["teams"]["away"]["team"]["name"],
                        game["teams"]["home"]["team"]["name"],
                        game_time,
                    )
                )
            elif game["status"]["abstractGameState"] == "Final":
                # Away Team Win
                if int(game["teams"]["away"]["score"]) > int(
                    game["teams"]["home"]["score"]
                ):
                    reply.append(
                        "{} {} {} {} Final".format(
                            bold(game["teams"]["away"]["team"]["name"]),
                            bold(str(game["teams"]["away"]["score"])),
                            game["teams"]["home"]["team"]["name"],
                            str(game["teams"]["home"]["score"]),
                        )
                    )
                # Home Team Win
                elif int(game["teams"]["home"]["score"]) > int(
                    game["teams"]["away"]["score"]
                ):
                    reply.append(
                        "{} {} {} {} Final".format(
                            game["teams"]["away"]["team"]["name"],
                            str(game["teams"]["away"]["score"]),
                            bold(game["teams"]["home"]["team"]["name"]),
                            bold(str(game["teams"]["home"]["score"])),
                        )
                    )
                # Tie Game
                else:
                    reply.append(
                        "{} {} {} {} Final".format(
                            game["teams"]["away"]["team"]["name"],
                            game["teams"]["away"]["score"],
                            game["teams"]["home"]["team"]["name"],
                            game["teams"]["home"]["score"],
                        )
                    )
    return reply


@commands("mlb")
@example(".mlb")
@example(".mlb 2019-10-29")
def mlb(bot, trigger):
    date = trigger.group(2) or None
    timezone = get_nick_timezone(bot.db, trigger.nick)

    # Get Game Data
    reply = " | ".join(parse_games(date, timezone))
    # Split if greater than 200 characters so we don't accidentally cut anything off
    if len(reply) > 200:
        length = int(len(reply.split(" | ")) / 2)
        bot.reply(" | ".join(reply.split(" | ")[0:length]))
        bot.reply(" | ".join(reply.split(" | ")[length:]))
        return
    else:
        if reply:
            return bot.reply(reply)
        else:
            return
