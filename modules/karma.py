#!/usr/bin/env python
"""
karma.py - Phenny karma Module
"""

import os, re
import pickle

SHOW_TOP_DEFAULT = 6

def filename(self, fname):
    name = ''.join((self.nick, '-', self.config.host, '.', fname, '.db'))
    return os.path.join(os.path.expanduser('~/.phenny'), name)

def setup(self):
    try:
        f = open(filename(self, "karma"), "r")
        self.karmas = pickle.load(f)
        f.close()
    except IOError:
        self.karmas = {}
    try:
        f = open(filename(self, "karma_contrib"), "r")
        self.karma_contrib = pickle.load(f)
        f.close()
    except IOError:
        self.karma_contrib = {}

def save_karma(self):
    try:
        f = open(filename(self, "karma"), "w")
        pickle.dump(self.karmas, f)
        f.close()
    except IOError:
        pass
    try:
        f = open(filename(self, "karma_contrib"), "w")
        pickle.dump(self.karma_contrib, f)
        f.close()
    except IOError:
        pass

def karma_me(phenny, input):
    target = input.group(1).lower()
    karma = (input.group(2) == "++") * 2 - 1
    isself = False
    sender = input.nick.lower()
    if target == sender:
        isself = True
    if not hasattr(phenny, 'karmas'):
        return phenny.say('error?')
    if target in phenny.alias_list:
        t = phenny.alias_list[target]
        if t == sender:
            isself = True
    if sender in phenny.alias_list:
        sender = phenny.alias_list[sender]
        if target == sender:
            isself = True
    if isself:
        return phenny.say("I'm sorry, "+input.nick+". I'm afraid I can't do that.")
    if target in phenny.seen:
        if target not in phenny.karmas:
            phenny.karmas[target] = karma
        else:
            phenny.karmas[target] += karma
        if sender not in phenny.karma_contrib:
            phenny.karma_contrib[sender] = [0, 0]  # +, -
        phenny.karma_contrib[sender][karma == -1] += 1
        phenny.say(target+"'s karma is now "+str(phenny.karmas[target]))
        save_karma(phenny)
    else:
        phenny.notice(input.nick, "I'm sorry. I'm afraid I do not know who that is.")
karma_me.rule = r'(\S+?)[ :,]{0,2}(\+\+|--)\s*$'

def get_karma(phenny, input):
    if not hasattr(phenny, 'karmas'):
        return phenny.say('error?')
    show_top = input.group(3)
    contrib = input.group(4)
    if show_top is not None:  # want to show the top x
        nick = None
        show_top = int(show_top)
    elif contrib is not None:  # want to show how much karma someone's changed
        lcontrib = contrib.lower()
        if lcontrib not in phenny.karma_contrib:
            phenny.say(contrib + " has not altered any karma.")
            return
        up, down = map(str, phenny.karma_contrib[lcontrib])
        phenny.say(' '.join((contrib, "has granted", up, "karma and removed", down, "karma.")))
        return
    else:
        nick = input.group(2)
        show_top = SHOW_TOP_DEFAULT
    if nick:
        nick = nick.lower()
        if nick in phenny.karmas:
            phenny.say(nick + " has " + str(phenny.karmas[nick]) + " karma.")
        else:
            phenny.say("That entity does not exist within the karmaverse")
    elif len(phenny.karmas) > 0:
        s_karm = sorted(phenny.karmas, key=phenny.karmas.get, reverse=True)
        msg = ', '.join([x + ": " + str(phenny.karmas[x]) for x in s_karm[:show_top]])
        if msg:
            phenny.say("Best karma: " + msg)
        worst_karmas = ', '.join([x + ": " + str(phenny.karmas[x])
                for x in s_karm[:-show_top-1:-1] if phenny.karmas[x] < 0])
        if worst_karmas:
            phenny.say("Worst karma: "+ worst_karmas)
    else:
        phenny.say("You guys don't have any karma apparently.")
get_karma.name = 'karma'
get_karma.rule = r'^\.(karma)(?: (top (\d)|contrib (\S+)|\S+))?$'

def nuke_karma(phenny, input):
    if input.nick not in phenny.ident_admin: return phenny.notice(input.nick, 'Requires authorization. Use .auth to identify')
    nick = input.group(2)
    if nick:
        nick = nick.lower()
        if nick in phenny.karmas:
            del phenny.karmas[nick]
            phenny.say(input.group(2) + " has been banished from the karmaverse")
            save_karma(phenny)
nuke_karma.name = 'knuke'
nuke_karma.rule = r'^\.(knuke) (\S+)$'
