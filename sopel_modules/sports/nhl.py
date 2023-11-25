# coding=utf-8
# Copyright 2019, Rusty Bower, rustybower.com
import datetime
import pytz
import requests

from dateutil import parser

from sopel.formatting import bold
from sopel.module import commands, example


def parse_games(date):
    if date:
        r = requests.get(f"https://api-web.nhle.com/v1/score/{date}")
    else:
        r = requests.get("https://api-web.nhle.com/v1/score/now")
    reply = []
    for game in r.json()["games"]:
        # Game Is Not Started
        if game["gameState"] == "FUT":
            reply.append(
                "{} @ {} {}".format(
                    game["awayTeam"]["abbrev"],
                    game["homeTeam"]["abbrev"],
                    parser.parse(game["startTimeUTC"]).astimezone(pytz.timezone("US/Central")).strftime("%H:%M"),
                )
            )
        elif game["gameState"] == "OFF" or game["gameState"] == "FINAL":  # TODO - Figure out OFF vs FINAL
            # Away Team Win
            if int(game["awayTeam"]["score"]) > int(game["homeTeam"]["score"]):
                reply.append(
                    "{} {} {} {} Final".format(
                        bold(game["awayTeam"]["abbrev"]),
                        bold(str(game["awayTeam"]["score"])),
                        game["homeTeam"]["abbrev"],
                        str(game["homeTeam"]["score"]),
                    )
                )
            # Home Team Win
            elif int(game["homeTeam"]["score"]) > int(game["awayTeam"]["score"]):
                reply.append(
                    "{} {} {} {} Final".format(
                        game["awayTeam"]["abbrev"],
                        str(game["awayTeam"]["score"]),
                        bold(game["homeTeam"]["abbrev"]),
                        bold(str(game["homeTeam"]["score"])),
                    )
                )
            # Tie Game
            else:
                reply.append(
                    "{} {} {} {} Final".format(
                        game["awayTeam"]["abbrev"],
                        game["awayTeam"]["score"],
                        game["homeTeam"]["abbrev"],
                        game["homeTeam"]["score"],
                    )
                )
        elif game["gameState"] == "LIVE":
            if game["period"] == 1:
                period = "1ST"
            elif game["period"] == 2:
                period = "2ND"
            elif game["period"] == 3:
                period = "3RD"
            elif game["period"] == 4:
                period = "OT"
            else:  # Otherwise, just OT2, OT3, etc...
                period = f"OT{game['period']-3}"

            # Print End 1st/2nd/3rd if in intermission
            if game["clock"]["inIntermission"]:
                reply.append(
                    "{} {} {} {} END {}".format(
                        game["awayTeam"]["abbrev"],
                        game["awayTeam"]["score"],
                        game["homeTeam"]["abbrev"],
                        game["homeTeam"]["score"],
                        period,
                    )
                )
            # Otherwise, print period and time remaining, e.g. 1st 15:07
            else:
                reply.append(
                    "{} {} {} {} {} {}".format(
                        game["awayTeam"]["abbrev"],
                        game["awayTeam"]["score"],
                        game["homeTeam"]["abbrev"],
                        game["homeTeam"]["score"],
                        period,
                        game["clock"]["timeRemaining"],
                    )
                )
    return reply


@commands("nhl")
@example(".nhl")
@example(".nhl 2019-10-29")
def nhl(bot, trigger):
    date = trigger.group(2) or None

    # Get Game Data
    reply = " | ".join(parse_games(date))
    # Split if greater than 200 characters so we don't accidentally cut anything off
    if len(reply) > 200:
        length = int(len(reply.split(" | ")) / 2)
        bot.say(" | ".join(reply.split(" | ")[0:length]))
        bot.say(" | ".join(reply.split(" | ")[length:]))
        return
    else:
        return bot.say(reply)
