"""
roulette.py - clone of a mIRC script to let users play Russian roulette
Copyright 2015-2016 dgw
"""

from __future__ import division
from sopel import module, tools
from sopel.config.types import StaticSection, ValidatedAttribute
import random
import time


class RouletteSection(StaticSection):
    timeout = ValidatedAttribute('timeout', int, default=600)
    """The timeout (in seconds) between roulette trigger pulls by the same user."""


def configure(config):
    config.define_section('roulette', RouletteSection)
    config.roulette.configure_setting(
        'timeout',
        'Timeout between roulette trigger pulls by the same user (in seconds): '
    )


def setup(bot):
    bot.config.define_section('roulette', RouletteSection)


@module.commands('roulette')
@module.require_chanmsg
def roulette(bot, trigger):
    time_since = time_since_roulette(bot, trigger.nick)
    if time_since < bot.config.roulette.timeout:
        bot.notice(
            "Next roulette attempt will be available {}.".format(
                tools.time.seconds_to_human(-(TIMEOUT - time_since))
            ), trigger.nick)
        return module.NOLIMIT
    if 6 != random.randint(1, 6):
        won = True
        bot.say("Click! %s is lucky; there was no bullet." % trigger.nick)
    else:
        won = False
        bot.say("BANG! %s is dead!" % trigger.nick)
    bot.db.set_nick_value(trigger.nick, 'roulette_last', time.time())
    update_roulettes(bot, trigger.nick, won)


@module.commands('roulettes', 'r')
def roulettes(bot, trigger):
    target = trigger.group(3) or trigger.nick
    games, wins = get_roulettes(bot, target)
    if not games:
        bot.say("%s hasn't played Russian roulette yet." % target)
        return
    g_times = 'time' if games == 1 else 'times'
    bot.say("%s has survived Russian roulette %d out of %d %s (or %.2f%%)."
            % (target, wins, games, g_times, wins / games * 100))


def update_roulettes(bot, nick, won=False):
    games, wins = get_roulettes(bot, nick)
    games += 1
    if won:
        wins += 1
    bot.db.set_nick_value(nick, 'roulette_games', games)
    bot.db.set_nick_value(nick, 'roulette_wins', wins)


def get_roulettes(bot, nick):
    games = bot.db.get_nick_value(nick, 'roulette_games') or 0
    wins = bot.db.get_nick_value(nick, 'roulette_wins') or 0
    return games, wins


def time_since_roulette(bot, nick):
    now = time.time()
    last = bot.db.get_nick_value(nick, 'roulette_last') or 0
    return abs(now - last)
