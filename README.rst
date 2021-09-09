============
sopel-sports
============

|version| |build| |issues| |alerts| |quality| |coverage-status| |license|

Introduction
============
sopel-sports is a sports lookup module for Sopel.

Usage
=====

MLB
~~~
.. code-block::

    .mlb # Get today's games
    Washington Nationals 7 Houston Astros 2 Final
    .mlb 2019-10-30 # Get games for specific date
    Washington Nationals @ Houston Astros 20:08 Eastern

NFL
~~~
.. code-block::

    .nfl # Get current NFL games
    SEA 20 CAR 7 10:09 Q2 | NE 7 CIN 10 10:01 Q2 | TB 14 DET 0 12:40 Q2 | CHI 0 GB 7 08:38 Q2 | DEN 0 KC 9 11:48 Q2 | MIA 7 NYG 7 08:01 Q2 | HOU 7 TEN 0 09:59 Q2 | PHI 10 WAS 7 08:21 Q2
    .nfl all # Get all NFL games for the week
    WAS 9 MIN 19 Final | SEA 27 ATL 20 Final | PHI 31 BUF 13 Final | LAC 17 CHI 16 Final | NYG 26 DET 31 Final | DEN 13 IND 15 Final | NYJ 15 JAX 29 Final | CIN 10 LA 24 Final | ARI 9 NO 31 Final | TB 23 TEN 27 Final | CAR 13 SF 51 Final | OAK 24 HOU 27 Final | CLE 13 NE 27 Final | GB @ KC Sun 8:20PM | MIA @ PIT Mon 8:15PM
    .nfl <team> # Get latest score for specific team
    DEN 0 KC 6 09:42 Q1

NHL
~~~
.. code-block::

    .nhl # Get today's games
    San Jose Sharks @ Boston Bruins 19:00 | Washington Capitals @ Toronto Maple Leafs 19:00 | Philadelphia Flyers @ Pittsburgh Penguins 19:00 | Calgary Flames @ Carolina Hurricanes 19:00 | Tampa Bay Lightning @ New York Rangers 19:30 | Edmonton Oilers @ Detroit Red Wings 19:30 | Chicago Blackhawks @ Nashville Predators 20:00 | Minnesota Wild @ Dallas Stars 20:30 | Winnipeg Jets @ Anaheim Ducks 22:00
    .nhl 2019-09-27 # Get games for specific date
    New Jersey Devils 2 Columbus Blue Jackets 0 Final | Nashville Predators 2 Carolina Hurricanes 1 Final | Toronto Maple Leafs 4 Detroit Red Wings 3 Final | Washington Capitals 3 St. Louis Blues 4 Final | Los Angeles Kings 3 Vegas Golden Knights 2 Final

Requirements
============

Python Requirements
~~~~~~~~~~~~~~~~~~~
.. code-block::

    arrow
    requests
    sopel

.. |version| image:: https://img.shields.io/pypi/v/sopel-modules.sports.svg
   :target: https://pypi.python.org/pypi/sopel-modules.sports
.. |build| image:: https://travis-ci.com/RustyBower/sopel-sports.svg?branch=master
   :target: https://travis-ci.com/RustyBower/sopel-sports
.. |issues| image:: https://img.shields.io/github/issues/RustyBower/sopel-sports.svg
   :target: https://travis-ci.com/RustyBower/sopel-sports/issues
.. |alerts| image:: https://img.shields.io/lgtm/alerts/g/RustyBower/sopel-sports.svg
   :target: https://lgtm.com/projects/g/RustyBower/sopel-sports/alerts/
.. |quality| image:: https://img.shields.io/lgtm/grade/python/g/RustyBower/sopel-sports.svg
   :target: https://lgtm.com/projects/g/RustyBower/sopel-sports/context:python
.. |coverage-status| image:: https://coveralls.io/repos/github/RustyBower/sopel-sports/badge.svg?branch=master
   :target: https://coveralls.io/github/RustyBower/sopel-sports?branch=master
.. |license| image:: https://img.shields.io/pypi/l/sopel-modules.sports.svg
   :target: https://github.com/RustyBower/sopel-sports/blob/master/LICENSE
