#!/usr/bin/env python
"""
karma.py - Phenny karma Module
"""

import os, re
import pickle

SHOW_TOP_DEFAULT = 6

def filename(self): 
   name = self.nick + '-' + self.config.host + '.karma.db'
   return os.path.join(os.path.expanduser('~/.phenny'), name)

def setup(self):
    try:
        f = open(filename(self), "r")
        self.karmas = pickle.load(f)
        f.close()
    except IOError:
        self.karmas = {}

def save_karma(self):
    try:
        f = open(filename(self), "w")
        pickle.dump(self.karmas, f)
        f.close()
    except IOError:
        pass

def karma_me(phenny, input):
    target = input.group(1).lower()
    karma = (input.group(2) == "++") * 2 - 1
    isself = False
    if target == input.nick.lower():
        isself = True
    if not hasattr(phenny, 'karmas'): 
        return phenny.say('error?')
    if target in phenny.alias_list:
        t = phenny.alias_list[target]
        if t == input.nick.lower():
            isself = True
    if input.nick.lower() in phenny.alias_list:
        if target == phenny.alias_list[input.nick.lower()]:
            isself = True
    if isself:
        return phenny.say("I'm sorry, "+input.nick+". I'm afraid I can't do that.")
    if target in phenny.seen:
        if target not in phenny.karmas:
            phenny.karmas[target] = karma
        else:
            phenny.karmas[target] += karma
        phenny.say(target+"'s karma is now "+str(phenny.karmas[target]))
        save_karma(phenny)
    else:
        phenny.notice(input.nick, "I'm sorry. I'm afraid I do not know who that is.")
karma_me.rule = r'(\S+?)[ :,]{0,2}(\+\+|--)\s*$'

def get_karma(phenny, input):
    if not hasattr(phenny, 'karmas'): 
        return phenny.say('error?')
    show_top = input.group(3)
    if show_top is not None:  # want to show the top x
        nick = None
        show_top = int(show_top)
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
get_karma.rule = (['karma'], r'(top (\d)|\S+)$')

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
nuke_karma.rule = (['knuke'], r'(\S+)')
