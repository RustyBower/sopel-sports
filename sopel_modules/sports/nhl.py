# coding=utf-8
# Copyright 2019, Rusty Bower, rustybower.com
import arrow
import requests

from sopel.formatting import bold
from sopel.module import commands, example


def parse_games(date):
    if date:
        r = requests.get(
            "https://statsapi.web.nhl.com/api/v1/schedule?date={}&expand=schedule.linescore".format(
                date
            )
        )
    else:
        r = requests.get(
            "https://statsapi.web.nhl.com/api/v1/schedule?expand=schedule.linescore"
        )
    reply = []
    for date in r.json()["dates"]:
        # TODO - Figure out what events and matches are
        for game in date["games"]:
            # Game Is Not Started
            if game["status"]["abstractGameState"] == "Preview":
                reply.append(
                    "{} @ {} {}".format(
                        game["teams"]["away"]["team"]["name"],
                        game["teams"]["home"]["team"]["name"],
                        arrow.get(game["gameDate"]).to("US/Eastern").format("HH:mm"),
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
            elif game["status"]["abstractGameState"] == "Live":
                reply.append(
                    "{} {} {} {} {} {}".format(
                        game["teams"]["away"]["team"]["name"],
                        game["teams"]["away"]["score"],
                        game["teams"]["home"]["team"]["name"],
                        game["teams"]["home"]["score"],
                        game["linescore"]["currentPeriodOrdinal"],
                        game["linescore"]["currentPeriodTimeRemaining"],
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
