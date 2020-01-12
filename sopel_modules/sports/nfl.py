# coding=utf-8
# Copyright 2019, Rusty Bower, rustybower.com
from __future__ import unicode_literals, absolute_import, print_function, division

from sopel.formatting import bold, color, colors
from sopel.module import commands, example

from datetime import datetime
from dateutil.parser import parse

import re
import requests
import xml.etree.ElementTree as ET


# TODO - This is bad and gross and needs a refactor
class NFLTeam:
    city = ""
    team = ""
    bg = ""
    fg = ""
    stadium = ""
    short = ""

    def __init__(self, city, team, fg, bg, stadium, short):
        self.city = city
        self.team = team
        self.fg = fg
        self.bg = bg
        self.stadium = stadium
        self.short = short


nfl_teams = {
    'ARI': NFLTeam('Arizona', 'Cardinals', colors.WHITE, colors.RED, 'University of Phoenix Stadium', 'ARI'),
    'ARZ': NFLTeam('Arizona', 'Cardinals', colors.WHITE, colors.RED, 'University of Phoenix Stadium', 'ARI'),
    'ATL': NFLTeam('Atlanta', 'Falcons', colors.BLACK, colors.RED, 'Georgia Dome', 'ATL'),
    'BAL': NFLTeam('Baltimore', 'Ravens', colors.YELLOW, colors.LIGHT_BLUE, 'M&T Bank Stadium', 'BAL'),
    'BUF': NFLTeam('Buffalo', 'Bills', colors.RED, colors.BLUE, 'Rogers Centre', 'BUF'),
    'CAR': NFLTeam('Carolina', 'Panthers', colors.LIGHT_BLUE, colors.BLACK, 'Bank of America Stadium', 'CAR'),
    'CHI': NFLTeam('Chicago', 'Bears', colors.ORANGE, colors.LIGHT_BLUE, 'Soldier Field', 'CHI'),
    'CIN': NFLTeam('Cincinnati', 'Bengals', colors.BLACK, colors.ORANGE, 'Paul Brown Stadium', 'CIN'),
    'CLE': NFLTeam('Cleveland', 'Browns', colors.WHITE, colors.ORANGE, 'Cleveland Browns Stadium', 'CLE'),
    'CLV': NFLTeam('Cleveland', 'Browns', colors.WHITE, colors.ORANGE, 'Cleveland Browns Stadium', 'CLE'),
    'DAL': NFLTeam('Dallas', 'Cowboys', colors.BLUE, colors.LIGHT_GREY, 'Cowboys Stadium', 'DAL'),
    'DEN': NFLTeam('Denver', 'Broncos', colors.ORANGE, colors.LIGHT_BLUE, 'INVESCO Field at Mile High', 'DEN'),
    'DET': NFLTeam('Detroit', 'Lions', colors.WHITE, colors.LIGHT_BLUE, 'Ford Field', 'DET'),
    'GB': NFLTeam('Green Bay', 'Packers', colors.YELLOW, colors.GREEN, 'Lambeau Field', 'GB'),
    'HOU': NFLTeam('Houston', 'Texans', colors.RED, colors.BLUE, 'Reliant Stadium', 'HOU'),
    'HST': NFLTeam('Houston', 'Texans', colors.RED, colors.BLUE, 'Reliant Stadium', 'HOU'),
    'IND': NFLTeam('Indianapolis', 'Colts', colors.WHITE, colors.LIGHT_BLUE, 'Lucas Oil Stadium', 'IND'),
    'JAC': NFLTeam('Jacksonville', 'Jaguars', colors.WHITE, colors.BLUE, 'Jacksonville Municipal Stadium', 'JAX'),
    'JAX': NFLTeam('Jacksonville', 'Jaguars', colors.WHITE, colors.BLUE, 'Jacksonville Municipal Stadium', 'JAX'),
    'KC': NFLTeam('Kansas City', 'Chiefs', colors.WHITE, colors.RED, 'Arrowhead Stadium', 'KC'),
    'LA': NFLTeam('Los Angeles', 'Rams', colors.BLUE, colors.ORANGE, 'Edward Jones Dome', 'LA'),
    'LAC': NFLTeam('Los Angeles', 'Chargers', colors.YELLOW, colors.BLUE, 'Qualcomm Stadium', 'LAC'),
    'MIA': NFLTeam('Miami', 'Dolphins', colors.ORANGE, colors.TEAL, 'Land Shark Stadium', 'MIA'),
    'MIN': NFLTeam('Minnesota', 'Vikings', colors.WHITE, colors.PURPLE, 'Hubert H. Humphrey Metrodome', 'MIN'),
    'NE': NFLTeam('New England', 'Patriots', colors.BLUE, colors.RED, 'Gillette Stadium', 'NE'),
    'NO': NFLTeam('New Orleans', 'Saints', colors.BLACK, colors.ORANGE, 'Louisiana Superdome', 'NO'),
    'NYG': NFLTeam('New York', 'Giants', colors.BLUE, colors.RED, 'New Meadowlands Stadium', 'NYG'),
    'NYJ': NFLTeam('New York', 'Jets', colors.WHITE, colors.GREEN, 'New Meadowlands Stadium', 'NYJ'),
    'OAK': NFLTeam('Oakland', 'Raiders', colors.BLACK, colors.WHITE, 'Oakland-Alameda County Coliseum', 'OAK'),
    'PHI': NFLTeam('Philadelphia', 'Eagles', colors.BLACK, colors.TEAL, 'Lincoln Financial Field', 'PHI'),
    'PIT': NFLTeam('Pittsburgh', 'Steelers', colors.BLACK, colors.YELLOW, 'Heinz Field', 'PIT'),
    'SEA': NFLTeam('Seattle', 'Seahawks', colors.LIGHT_GREY, colors.BLUE, 'Qwest Field', 'SEA'),
    'SF': NFLTeam('San Francisco', '49ers', colors.RED, colors.ORANGE, 'Candlestick Park', 'SF'),
    'TB': NFLTeam('Tampa Bay', 'Buccaneers', colors.RED, colors.GREY, 'Raymond James Stadium', 'TB'),
    'TEN': NFLTeam('Tennessee', 'Titans', colors.LIGHT_CYAN, colors.BLUE, 'LP Field', 'TEN'),
    'WAS': NFLTeam('Washington', 'Redskins', colors.WHITE, colors.RED, 'FedExField', 'WAS'),

    'AFC': NFLTeam('AFC', 'Pro Bowl NFLTeam', colors.WHITE, colors.RED, '', 'AFC'),
    'NFC': NFLTeam('NFC', 'Pro Bowl NFLTeam', colors.BLUE, colors.WHITE, '', 'NFC'),
}


def parse_game(game):
    # F - Final || FO - Final Overtime
    if game.attrib['q'] == 'F' or game.attrib['q'] == 'FO':
        if game.attrib['q'] == 'F':
            status = 'Final'
        else:
            status = 'Final Overtime'
        # KC 17 JAX 7 Final
        if int(game.attrib['vs']) > int(game.attrib['hs']):
            return '{} {} {} {} {}'.format(bold(game.attrib['v']),
                                           bold(game.attrib['vs']),
                                           game.attrib['h'],
                                           game.attrib['hs'],
                                           status)
        elif int(game.attrib['vs']) < int(game.attrib['hs']):
            return '{} {} {} {} {}'.format(game.attrib['v'],
                                           game.attrib['vs'],
                                           bold(game.attrib['h']),
                                           bold(game.attrib['hs']),
                                           status)
        else:
            return '{} {} {} {} {}'.format(game.attrib['v'],
                                           game.attrib['vs'],
                                           game.attrib['h'],
                                           game.attrib['hs'],
                                           status)
    # H - Halftime
    if game.attrib['q'] == 'H':
        # KC 17 JAX 7 Final
        if int(game.attrib['vs']) > int(game.attrib['hs']):
            return '{} {} {} {} {}'.format(bold(game.attrib['v']),
                                           bold(game.attrib['vs']),
                                           game.attrib['h'],
                                           game.attrib['hs'],
                                           'Halftime')
        elif int(game.attrib['vs']) < int(game.attrib['hs']):
            return '{} {} {} {} {}'.format(game.attrib['v'],
                                           game.attrib['vs'],
                                           bold(game.attrib['h']),
                                           bold(game.attrib['hs']),
                                           'Halftime')
        else:
            return '{} {} {} {} {}'.format(game.attrib['v'],
                                           game.attrib['vs'],
                                           game.attrib['h'],
                                           game.attrib['hs'],
                                           'Halftime')
    # P - Pending
    elif game.attrib['q'] == 'P':
        # DEN @ OAK Mon 10:20PM
        return '{} @ {} {} {}PM'.format(color(game.attrib['v'], nfl_teams[game.attrib['v']].fg, nfl_teams[game.attrib['v']].bg),
                                        color(game.attrib['h'], nfl_teams[game.attrib['h']].fg, nfl_teams[game.attrib['h']].bg),
                                        game.attrib['d'],
                                        game.attrib['t'])
    # Active Game
    else:
        # KC 17 JAX 7 15:00 Q2
        if int(game.attrib['vs']) > int(game.attrib['hs']):
            return '{} {} {} {} {} Q{}'.format(
                color(bold(game.attrib['v']), nfl_teams[game.attrib['v']].fg, nfl_teams[game.attrib['v']].bg),
                bold(game.attrib['vs']),
                color(game.attrib['h'], nfl_teams[game.attrib['h']].fg, nfl_teams[game.attrib['h']].bg),
                game.attrib['hs'],
                game.attrib['k'],
                game.attrib['q'])
        elif int(game.attrib['vs']) > int(game.attrib['hs']):
            return '{} {} {} {} {} Q{}'.format(
                color(game.attrib['v'], nfl_teams[game.attrib['v']].fg, nfl_teams[game.attrib['v']].bg),
                game.attrib['vs'],
                color(bold(game.attrib['h']), nfl_teams[game.attrib['h']].fg, nfl_teams[game.attrib['h']].bg),
                bold(game.attrib['hs']),
                game.attrib['k'],
                game.attrib['q'])
        else:
            return '{} {} {} {} {} Q{}'.format(
                color(game.attrib['v'], nfl_teams[game.attrib['v']].fg, nfl_teams[game.attrib['v']].bg),
                game.attrib['vs'],
                color(game.attrib['h'], nfl_teams[game.attrib['h']].fg, nfl_teams[game.attrib['h']].bg),
                game.attrib['hs'],
                game.attrib['k'],
                game.attrib['q'])


@commands('nfl')
@example('.nfl')
@example('.nfl all')
@example('.nfl DEN')
@example('.nfl Denver Broncos')
def nfl(bot, trigger):
    """.nfl <team/all> - Show current game score or next game for an optionally specified team."""
    team = trigger.group(2)

    # Figure out if we're in regular or postseason
    r = requests.get('http://www.nfl.com/liveupdate/scorestrip/ss.xml')
    root = ET.fromstring(r.text)

    # If week is 17 and it's been a day since the last game, display postseason
    if root[0].attrib['w'] == '17' and (datetime.now() - parse(root[0].findall('g')[-1].attrib['eid'][:8])).days > 1:
        # Postseason Games
        r = requests.get('http://static.nfl.com/liveupdate/scorestrip/postseason/ss.xml')
        root = ET.fromstring(r.text)
        # Get games within 7 days and no older than 3 days
        reply = ' | '.join([parse_game(game) for game in root.iter('g') if game.attrib['h'] != 'TBD' if game.attrib['v'] != 'TBD' if (datetime.now() - parse(game.attrib['eid'][:8])).days >= -7 if (datetime.now() - parse(game.attrib['eid'][:8])).days <= 3])
        return bot.reply(reply)
    # Otherwise, it's regular season
    else:
        # Get current/all scores
        if not team or team.lower() == 'all':
            # I think there's a bug here when the London games happen. Since we're assuming 1:00 is in PM
            # Get current games
            if not team:
                reply = ' | '.join([parse_game(game) for game in root.iter('g') if game.attrib['q'] != 'F' if game.attrib['q'] != 'FO' if game.attrib['q'] != 'P'])
            # Get all games
            else:
                reply = ' | '.join([parse_game(game) for game in root.iter('g')])

            # Split the message if it's > 200 characters
            if len(reply) > 200:
                length = int(len(reply.split(' | ')) / 2)
                bot.say(' | '.join(reply.split(' | ')[0:length]))
                bot.say(' | '.join(reply.split(' | ')[length:]))
            else:
                bot.say(reply)
            return

        # Get score for specific team
        else:
            # If initial aren't specified, try to guess what team it is
            match = re.match(r'^\S{2,3}$', team)
            if not match:
                for k, v in nfl_teams.items():
                    if team.lower() == v.team.lower() or team.lower() == v.city.lower() or team.lower() == '{0} {1}'.format(v.city.lower(), v.team.lower()):
                        team = k

            game = root.find("./gms/g[@h='{}']".format(team.upper()))
            if game is None:
                game = root.find("./gms/g[@v='{}']".format(team.upper()))

            if game is not None:
                return bot.reply(parse_game(game))
            else:
                return bot.reply('Team Not Found')
