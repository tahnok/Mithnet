#!/usr/bin/env python
"""
karma.py - Phenny karma Module
"""

import os, re
import pickle

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
        try:
            f = open(filename(phenny), "w")
            pickle.dump(phenny.karmas, f)
            f.close()
        except IOError:
            pass
    else:
        phenny.notice(input.nick, "I'm sorry. I'm afraid I do not know who that is.")
karma_me.rule = r'(\S+?)[ :,]{0,2}(\+\+|--)\s*$'

def get_karma(phenny, input):
    if not hasattr(phenny, 'karmas'): 
        return phenny.say('error?')
    nick = input.group(2)
    if nick:
        nick = nick.lower()
        if nick in phenny.karmas:
            phenny.say(input.group(2) + " has " + str(phenny.karmas[nick]) + " karma.")
        else:
            phenny.say("That entity does not exist within the karmaverse")
    elif len(phenny.karmas) > 0:
        s_karm = sorted(phenny.karmas, key=phenny.karmas.get, reverse=True)
        msg = "Best karma: "+ ', '.join([x + ": " + str(phenny.karmas[x]) for x in s_karm[:3]])
        phenny.say(msg)
        msg = "Worst karma: "+ ', '.join([x + ": " + str(phenny.karmas[x]) for x in s_karm[:-4:-1]])
        phenny.say(msg)
    else:
        phenny.say("You guys don't have any karma apparently.")
get_karma.name = 'karma'
get_karma.rule = (['karma'], r'(\S+)')

def nuke_karma(phenny, input):
    if input.nick not in phenny.ident_admin: return phenny.notice(input.nick, 'Requires authorization. Use .auth to identify')
    nick = input.group(2)
    if nick:
        nick = nick.lower()
        if nick in phenny.karmas:
            del phenny.karmas[nick]
            phenny.say(input.group(2) + " has been banished from the karmaverse")
nuke_karma.name = 'knuke'
nuke_karma.rule = (['knuke'], r'(\S+)')