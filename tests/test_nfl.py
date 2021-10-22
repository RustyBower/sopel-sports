from sopel_modules.sports.nfl import get_current_week, get_token, parse_game
from sopel.tests import rawlist

import json
import pytest
import requests
import requests_mock
import time

MOCK_GAME_SCHEDULED = {
    "id": "c5722300-b37c-11eb-9617-afa9727fab42",
    "homeTeam": {
        "id": "10404900-d59e-b449-ef75-961e09ca027e",
        "currentLogo": "https://static.www.nfl.com/{formatInstructions}/league/api/clubs/logos/TB",
        "fullName": "Tampa Bay Buccaneers",
        "abbreviation": "TB",
        "season": "2021",
        "conferenceAbbr": "NFC",
        "conferenceFullName": "National Football Conference",
        "divisionFullName": "NFC South",
        "league": "National Football League",
        "location": "Tampa Bay",
        "nickName": "Buccaneers",
        "primaryColor": "#A71930",
        "secondaryColor": "#322F2B",
        "yearEstablished": 1976,
        "nflShopUrl": "https://www.nflshop.com/tampa-bay-buccaneers/t-47049490+z-9658530-4203348785?_s=bm-nflcom-team-page-buy-gear-052220-Buccaneers",
        "officialWebsiteUrl": "https://www.buccaneers.com/",
        "owners": "Bryan Glazer, Edward Glazer, Joel Glaze",
        "teamType": "TEAM",
        "socials": [
            {
                "platform": "Facebook",
                "link": "https://www.facebook.com/tampabaybuccaneers",
            },
            {"platform": "Instagram", "link": "https://www.instagram.com/buccaneers"},
            {"platform": "Snapchat", "link": "https://www.snapchat.com/add/bucsnfl"},
            {"platform": "Twitter", "link": "https://twitter.com/Buccaneers"},
        ],
        "venues": [
            {
                "id": "00083697-451e-88a5-6695-aa32961fba3a",
                "name": "Raymond James Stadium",
            }
        ],
    },
    "awayTeam": {
        "id": "10401200-a308-98ca-ad5f-95df2fefea68",
        "currentLogo": "https://static.www.nfl.com/{formatInstructions}/league/api/clubs/logos/DAL",
        "fullName": "Dallas Cowboys",
        "abbreviation": "DAL",
        "season": "2021",
        "conferenceAbbr": "NFC",
        "conferenceFullName": "National Football Conference",
        "divisionFullName": "NFC East",
        "league": "National Football League",
        "location": "Dallas",
        "nickName": "Cowboys",
        "primaryColor": "#002244",
        "secondaryColor": "#B0B7BC",
        "yearEstablished": 1960,
        "nflShopUrl": "https://www.nflshop.com/dallas-cowboys/t-36717995+z-9349787-1633145182?_s=bm-nflcom-team-page-buy-gear-052220-Cowboys",
        "officialWebsiteUrl": "https://www.dallascowboys.com/",
        "owners": "Jerry Jones",
        "teamType": "TEAM",
        "socials": [
            {"platform": "Facebook", "link": "https://www.facebook.com/DallasCowboys"},
            {
                "platform": "Instagram",
                "link": "https://www.instagram.com/DallasCowboys",
            },
            {
                "platform": "Snapchat",
                "link": "https://www.snapchat.com/add/dallascowboys",
            },
            {"platform": "Twitter", "link": "https://twitter.com/DallasCowboys"},
        ],
        "venues": [
            {"id": "00084948-addf-5f39-b283-02455f77c178", "name": "AT&T Stadium"}
        ],
    },
    "category": "SNF",
    "date": "2021-09-10",
    "time": "2021-09-10T00:20:00Z",
    "broadcastInfo": {
        "homeNetworkChannels": ["NBC"],
        "awayNetworkChannels": ["NBC"],
        "internationalWatchOptions": [
            {"countryCode": "GB", "broadcasters": ["Sky Sports", "NFL Game Pass"]}
        ],
        "territory": "NATIONAL",
    },
    "venue": {
        "id": "00083697-451e-88a5-6695-aa32961fba3a",
        "name": "Raymond James Stadium",
    },
    "season": 2021,
    "seasonType": "REG",
    "status": "SCHEDULED",
    "week": 1,
    "weekType": "REG",
    "externalIds": [
        {"source": "gsis", "id": "58503"},
        {"source": "elias", "id": "2021090900"},
        {"source": "gamedetail", "id": "10160000-0585-0395-7f87-0c3334b38e2e"},
        {"source": "slug", "id": "cowboys-at-buccaneers-2021-reg-1"},
    ],
    "ticketUrl": "https://www.ticketmaster.com/event/0D005A95CCD2A636?utm_source=NFL.com&utm_medium=client&utm_campaign=NFL_LEAGUE",
}

MOCK_GAME_PREGAME = {
    "id": "c5722300-b37c-11eb-9617-afa9727fab42",
    "homeTeam": {
        "id": "10404900-d59e-b449-ef75-961e09ca027e",
        "currentLogo": "https://static.www.nfl.com/{formatInstructions}/league/api/clubs/logos/TB",
        "fullName": "Tampa Bay Buccaneers",
        "abbreviation": "TB",
        "season": "2021",
        "conferenceAbbr": "NFC",
        "conferenceFullName": "National Football Conference",
        "divisionFullName": "NFC South",
        "league": "National Football League",
        "location": "Tampa Bay",
        "nickName": "Buccaneers",
        "primaryColor": "#A71930",
        "secondaryColor": "#322F2B",
        "yearEstablished": 1976,
        "nflShopUrl": "https://www.nflshop.com/tampa-bay-buccaneers/t-47049490+z-9658530-4203348785?_s=bm-nflcom-team-page-buy-gear-052220-Buccaneers",
        "officialWebsiteUrl": "https://www.buccaneers.com/",
        "owners": "Bryan Glazer, Edward Glazer, Joel Glaze",
        "teamType": "TEAM",
        "socials": [
            {
                "platform": "Facebook",
                "link": "https://www.facebook.com/tampabaybuccaneers",
            },
            {"platform": "Instagram", "link": "https://www.instagram.com/buccaneers"},
            {"platform": "Snapchat", "link": "https://www.snapchat.com/add/bucsnfl"},
            {"platform": "Twitter", "link": "https://twitter.com/Buccaneers"},
        ],
        "venues": [
            {
                "id": "00083697-451e-88a5-6695-aa32961fba3a",
                "name": "Raymond James Stadium",
            }
        ],
    },
    "awayTeam": {
        "id": "10401200-a308-98ca-ad5f-95df2fefea68",
        "currentLogo": "https://static.www.nfl.com/{formatInstructions}/league/api/clubs/logos/DAL",
        "fullName": "Dallas Cowboys",
        "abbreviation": "DAL",
        "season": "2021",
        "conferenceAbbr": "NFC",
        "conferenceFullName": "National Football Conference",
        "divisionFullName": "NFC East",
        "league": "National Football League",
        "location": "Dallas",
        "nickName": "Cowboys",
        "primaryColor": "#002244",
        "secondaryColor": "#B0B7BC",
        "yearEstablished": 1960,
        "nflShopUrl": "https://www.nflshop.com/dallas-cowboys/t-36717995+z-9349787-1633145182?_s=bm-nflcom-team-page-buy-gear-052220-Cowboys",
        "officialWebsiteUrl": "https://www.dallascowboys.com/",
        "owners": "Jerry Jones",
        "teamType": "TEAM",
        "socials": [
            {"platform": "Facebook", "link": "https://www.facebook.com/DallasCowboys"},
            {
                "platform": "Instagram",
                "link": "https://www.instagram.com/DallasCowboys",
            },
            {
                "platform": "Snapchat",
                "link": "https://www.snapchat.com/add/dallascowboys",
            },
            {"platform": "Twitter", "link": "https://twitter.com/DallasCowboys"},
        ],
        "venues": [
            {"id": "00084948-addf-5f39-b283-02455f77c178", "name": "AT&T Stadium"}
        ],
    },
    "category": "SNF",
    "date": "2021-09-10",
    "time": "2021-09-10T00:20:00Z",
    "broadcastInfo": {
        "homeNetworkChannels": ["NBC"],
        "awayNetworkChannels": ["NBC"],
        "internationalWatchOptions": [
            {"countryCode": "GB", "broadcasters": ["Sky Sports", "NFL Game Pass"]}
        ],
        "territory": "NATIONAL",
    },
    "venue": {
        "id": "00083697-451e-88a5-6695-aa32961fba3a",
        "name": "Raymond James Stadium",
    },
    "season": 2021,
    "seasonType": "REG",
    "status": "SCHEDULED",
    "week": 1,
    "weekType": "REG",
    "externalIds": [
        {"source": "gsis", "id": "58503"},
        {"source": "elias", "id": "2021090900"},
        {"source": "gamedetail", "id": "10160000-0585-0395-7f87-0c3334b38e2e"},
        {"source": "slug", "id": "cowboys-at-buccaneers-2021-reg-1"},
    ],
    "ticketUrl": "https://www.ticketmaster.com/event/0D005A95CCD2A636?utm_source=NFL.com&utm_medium=client&utm_campaign=NFL_LEAGUE",
    "detail": {
        "id": "10160000-0585-0395-7f87-0c3334b38e2e",
        "gameClock": "15:00",
        "homePointsTotal": 0,
        "period": 1,
        "phase": "PREGAME",
        "possessionTeam": {
            "id": "10041200-2021-6fbf-aaa9-8b50898d954e",
            "abbreviation": "DAL",
        },
        "visitorPointsTotal": 0,
    },
}

MOCK_GAME_INPROGRESS = """
"""

MOCK_GAME_HALFTIME = """
"""

MOCK_GAME_FINAL = {
    "id": "c5722300-b37c-11eb-9617-afa9727fab42",
    "homeTeam": {
        "id": "10404900-d59e-b449-ef75-961e09ca027e",
        "currentLogo": "https://static.www.nfl.com/{formatInstructions}/league/api/clubs/logos/TB",
        "fullName": "Tampa Bay Buccaneers",
        "abbreviation": "TB",
        "season": "2021",
        "conferenceAbbr": "NFC",
        "conferenceFullName": "National Football Conference",
        "divisionFullName": "NFC South",
        "league": "National Football League",
        "location": "Tampa Bay",
        "nickName": "Buccaneers",
        "primaryColor": "#A71930",
        "secondaryColor": "#322F2B",
        "yearEstablished": 1976,
        "nflShopUrl": "https://www.nflshop.com/tampa-bay-buccaneers/t-47049490+z-9658530-4203348785?_s=bm-nflcom-team-page-buy-gear-052220-Buccaneers",
        "officialWebsiteUrl": "https://www.buccaneers.com/",
        "owners": "Bryan Glazer, Edward Glazer, Joel Glaze",
        "teamType": "TEAM",
        "socials": [
            {
                "platform": "Facebook",
                "link": "https://www.facebook.com/tampabaybuccaneers",
            },
            {"platform": "Instagram", "link": "https://www.instagram.com/buccaneers"},
            {"platform": "Snapchat", "link": "https://www.snapchat.com/add/bucsnfl"},
            {"platform": "Twitter", "link": "https://twitter.com/Buccaneers"},
        ],
        "venues": [
            {
                "id": "00083697-451e-88a5-6695-aa32961fba3a",
                "name": "Raymond James Stadium",
            }
        ],
    },
    "awayTeam": {
        "id": "10401200-a308-98ca-ad5f-95df2fefea68",
        "currentLogo": "https://static.www.nfl.com/{formatInstructions}/league/api/clubs/logos/DAL",
        "fullName": "Dallas Cowboys",
        "abbreviation": "DAL",
        "season": "2021",
        "conferenceAbbr": "NFC",
        "conferenceFullName": "National Football Conference",
        "divisionFullName": "NFC East",
        "league": "National Football League",
        "location": "Dallas",
        "nickName": "Cowboys",
        "primaryColor": "#002244",
        "secondaryColor": "#B0B7BC",
        "yearEstablished": 1960,
        "nflShopUrl": "https://www.nflshop.com/dallas-cowboys/t-36717995+z-9349787-1633145182?_s=bm-nflcom-team-page-buy-gear-052220-Cowboys",
        "officialWebsiteUrl": "https://www.dallascowboys.com/",
        "owners": "Jerry Jones",
        "teamType": "TEAM",
        "socials": [
            {"platform": "Facebook", "link": "https://www.facebook.com/DallasCowboys"},
            {
                "platform": "Instagram",
                "link": "https://www.instagram.com/DallasCowboys",
            },
            {
                "platform": "Snapchat",
                "link": "https://www.snapchat.com/add/dallascowboys",
            },
            {"platform": "Twitter", "link": "https://twitter.com/DallasCowboys"},
        ],
        "venues": [
            {"id": "00084948-addf-5f39-b283-02455f77c178", "name": "AT&T Stadium"}
        ],
    },
    "category": "SNF",
    "date": "2021-09-10",
    "time": "2021-09-10T00:20:00Z",
    "broadcastInfo": {
        "homeNetworkChannels": ["NBC"],
        "awayNetworkChannels": ["NBC"],
        "internationalWatchOptions": [
            {"countryCode": "GB", "broadcasters": ["Sky Sports", "NFL Game Pass"]}
        ],
        "territory": "NATIONAL",
    },
    "venue": {
        "id": "00083697-451e-88a5-6695-aa32961fba3a",
        "name": "Raymond James Stadium",
    },
    "season": 2021,
    "seasonType": "REG",
    "status": "SCHEDULED",
    "week": 1,
    "weekType": "REG",
    "externalIds": [
        {"source": "gsis", "id": "58503"},
        {"source": "elias", "id": "2021090900"},
        {"source": "gamedetail", "id": "10160000-0585-0395-7f87-0c3334b38e2e"},
        {"source": "slug", "id": "cowboys-at-buccaneers-2021-reg-1"},
    ],
    "ticketUrl": "https://www.ticketmaster.com/event/0D005A95CCD2A636?utm_source=NFL.com&utm_medium=client&utm_campaign=NFL_LEAGUE",
    "detail": {
        "id": "10160000-0585-0395-7f87-0c3334b38e2e",
        "gameClock": "00:02",
        "homePointsTotal": 31,
        "period": None,
        "phase": "FINAL",
        "possessionTeam": {
            "id": "10041200-2021-6fbf-aaa9-8b50898d954e",
            "abbreviation": "DAL",
        },
        "visitorPointsTotal": 29,
    },
}

MOCK_GAME_FINAL_OVERTIME = {
    "id": "c59f3b56-b37c-11eb-acef-004a6dd04236",
    "homeTeam": {
        "id": "10400920-57c1-7656-e77e-1af3d900483e",
        "currentLogo": "https://static.www.nfl.com/{formatInstructions}/league/api/clubs/logos/CIN",
        "fullName": "Cincinnati Bengals",
        "abbreviation": "CIN",
        "season": "2021",
        "conferenceAbbr": "AFC",
        "conferenceFullName": "American Football Conference",
        "divisionFullName": "AFC North",
        "league": "National Football League",
        "location": "Cincinnati",
        "nickName": "Bengals",
        "primaryColor": "#FB4F14",
        "secondaryColor": "#000000",
        "yearEstablished": 1968,
        "nflShopUrl": "https://www.nflshop.com/cincinnati-bengals/t-36370248+z-9423154-598202139?_s=bm-nflcom-team-page-buy-gear-052220-Bengals",
        "officialWebsiteUrl": "https://www.bengals.com/",
        "owners": "Mike Brown",
        "teamType": "TEAM",
        "socials": [
            {"platform": "Facebook", "link": "https://www.facebook.com/bengals"},
            {"platform": "Instagram", "link": "https://www.instagram.com/bengals"},
            {
                "platform": "Snapchat",
                "link": "https://www.snapchat.com/add/officialbengals",
            },
            {"platform": "Twitter", "link": "https://twitter.com/Bengals"},
        ],
        "venues": [
            {"id": "00083530-fc9f-2795-83d8-308b54d591fe", "name": "Paul Brown Stadium"}
        ],
    },
    "awayTeam": {
        "id": "10403000-5851-f9d5-da45-78365a05b6b0",
        "currentLogo": "https://static.www.nfl.com/{formatInstructions}/league/api/clubs/logos/MIN",
        "fullName": "Minnesota Vikings",
        "abbreviation": "MIN",
        "season": "2021",
        "conferenceAbbr": "NFC",
        "conferenceFullName": "National Football Conference",
        "divisionFullName": "NFC North",
        "league": "National Football League",
        "location": "Minnesota",
        "nickName": "Vikings",
        "primaryColor": "#4F2683",
        "secondaryColor": "#FFC62F",
        "yearEstablished": 1961,
        "nflShopUrl": "https://www.nflshop.com/minnesota-vikings/t-14609251+z-9123207-2760977927?_s=bm-nflcom-team-page-buy-gear-052220-Vikings",
        "officialWebsiteUrl": "https://www.vikings.com/",
        "owners": "Zygi Wilf",
        "teamType": "TEAM",
        "socials": [
            {
                "platform": "Facebook",
                "link": "https://www.facebook.com/minnesotavikings",
            },
            {"platform": "Instagram", "link": "https://www.instagram.com/vikings"},
            {"platform": "Snapchat", "link": "https://www.snapchat.com/add/vikings"},
            {"platform": "Twitter", "link": "https://twitter.com/vikings"},
        ],
        "venues": [
            {"id": "00081652-d8a8-d698-5b3f-31487c6624f7", "name": "U.S. Bank Stadium"}
        ],
    },
    "category": None,
    "date": "2021-09-12",
    "time": "2021-09-12T17:00:00Z",
    "broadcastInfo": {
        "homeNetworkChannels": ["FOX"],
        "awayNetworkChannels": ["FOX"],
        "internationalWatchOptions": [
            {"countryCode": "GB", "broadcasters": ["NFL Game Pass"]}
        ],
        "territory": "REGIONAL",
    },
    "venue": {
        "id": "00083530-fc9f-2795-83d8-308b54d591fe",
        "name": "Paul Brown Stadium",
    },
    "season": 2021,
    "seasonType": "REG",
    "status": "SCHEDULED",
    "week": 1,
    "weekType": "REG",
    "externalIds": [
        {"source": "gsis", "id": "58507"},
        {"source": "elias", "id": "2021091203"},
        {"source": "gamedetail", "id": "10160000-0585-078e-e7ac-a2f205f45b71"},
        {"source": "slug", "id": "vikings-at-bengals-2021-reg-1"},
    ],
    "ticketUrl": "https://www.ticketmaster.com/event/16005A9242DA20F8?utm_source=NFL.com&utm_medium=client&utm_campaign=NFL_LEAGUE",
    "detail": {
        "id": "10160000-0585-078e-e7ac-a2f205f45b71",
        "gameClock": "00:00",
        "homePointsTotal": 27,
        "period": None,
        "phase": "FINAL_OVERTIME",
        "possessionTeam": {
            "id": "10040920-2021-a987-4573-9fa9ad05c0fb",
            "abbreviation": "CIN",
        },
        "visitorPointsTotal": 24,
    },
}

TMP_CONFIG = """
[core]
owner = testnick
nick = TestBot
enable =
    coretasks
    sports
"""


@pytest.fixture
def tmpconfig(configfactory):
    return configfactory("test.cfg", TMP_CONFIG)


@pytest.fixture
def mockbot(tmpconfig, botfactory):
    return botfactory.preloaded(tmpconfig, preloads=["sports"])


@pytest.fixture
def irc(mockbot, ircfactory):
    return ircfactory(mockbot)


def test_parse_game_scheduled():
    result = parse_game(MOCK_GAME_SCHEDULED)
    assert result == "DAL @ TB Thu 8:20 PM EDT"


def test_parse_game_scheduled_timezone():
    result = parse_game(MOCK_GAME_SCHEDULED, "America/Chicago")
    assert result == "DAL @ TB Thu 7:20 PM CDT"


def test_parse_game_pregame():
    result = parse_game(MOCK_GAME_PREGAME)
    assert result == "DAL 0 TB 0 15:00 Q1"


def test_parse_game_final():
    result = parse_game(MOCK_GAME_FINAL)
    assert result == "DAL 29 \x02TB\x02 \x0231\x02 Final"


def test_parse_game_final_overtime():
    result = parse_game(MOCK_GAME_FINAL_OVERTIME)
    assert result == "MIN 24 \x02CIN\x02 \x0227\x02 Final OT"


def test_get_token(mockbot):
    with requests_mock.Mocker() as mock:
        mock.post(
            "https://www.nfl.com/oauth/nfl/token/client",
            json={
                "accessToken": "1234567890",
                "expiresIn": 0,
            },
        )
        assert get_token(mockbot) == "1234567890"


def test_get_token_from_memory(mockbot):
    mockbot.memory["accessToken"] = "1234567890"

    mockbot.memory["expiresIn"] = (
        int(time.time()) + 3600
    )  # Set an expiration an hour into the future

    assert get_token(mockbot) == "1234567890"


def test_get_week(mockbot):
    with requests_mock.Mocker() as mock:
        mockbot.memory["accessToken"] = "1234567890"

        mock.get(
            "https://api.nfl.com/football/v2/weeks/date/2021-09-08",
            json="{'season': 2021, 'seasonType': 'REG', 'week': 1, 'byeTeams': [], 'dateBegin': '2021-09-01', 'dateEnd': '2021-09-15', 'weekType': 'REG'}",
        )

        mockbot.memory["expiresIn"] = (
            int(time.time()) + 3600
        )  # Set an expiration an hour into the future

        assert (
            get_current_week(mockbot)
            == "{'season': 2021, 'seasonType': 'REG', 'week': 1, 'byeTeams': [], 'dateBegin': '2021-09-01', 'dateEnd': '2021-09-15', 'weekType': 'REG'}"
        )


def test_nfl(irc, userfactory):
    user = userfactory("TestUser")
    irc.pm(user, ".nfl")

    assert irc.bot.backend.message_sent[0] == rawlist(
        "PRIVMSG Exirel :Here is my list of commands:",
    )[0]
    assert len(irc.bot.backend.message_sent) > 1, "More than one line expected"


# def test_nfl(irc, userfactory, mockbot):
#     user = userfactory("TestUser")
#     irc.pm(user, ".nfl")

#     mockbot.memory["accessToken"] = "1234567890"

#     mockbot.memory["expiresIn"] = (
#         int(time.time()) + 3600
#     )  # Set an expiration an hour into the future

#     with requests_mock.Mocker() as mock:
#         mock.get(
#             "https://api.nfl.com/football/v2/weeks/date/2021-09-08",
#             json="{'season': 2021, 'seasonType': 'REG', 'week': 1, 'byeTeams': [], 'dateBegin': '2021-09-01', 'dateEnd': '2021-09-15', 'weekType': 'REG'}",
#         )

#     assert irc.bot.backend.message_sent[0] == rawlist(
#         "PRIVMSG Exirel :Here is my list of commands:",
#     )[0]


# def test_nfl_den(irc, userfactory, mockbot):
#     user = userfactory("TestUser")
#     irc.pm(user, ".nfl all")

#     assert irc.bot.backend.message_sent[0] == rawlist(
#         "PRIVMSG Exirel :Here is my list of commands:",
#     )[0]


# def test_nfl_all(irc, userfactory, mockbot):
#     user = userfactory("TestUser")
#     irc.pm(user, ".nfl all")

#     assert irc.bot.backend.message_sent[0] == rawlist(
#         "PRIVMSG Exirel :Here is my list of commands:",
#     )[0]
