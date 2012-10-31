#!/usr/bin/env python
"""
eventhandlers.py - Phenny Event Handler Module

"""

import time

def setup(self):
   self.ident_admin = [] #used by admin.py, reload.py
   self.alias_list = {} #used by seen.py

def joinhandler(phenny, input): 
   if input.admin:
      phenny.write(['WHOIS'], input.nick)
joinhandler.rule = r'(.*)'
joinhandler.event = 'JOIN'
joinhandler.priority = 'low'

def parthandler(phenny, input): 
   if input.nick in phenny.ident_admin:
      phenny.ident_admin.remove(input.nick)
   if input.nick.lower() in phenny.alias_list:
      del phenny.alias_list[input.nick.lower()]
parthandler.rule = r'(.*)'
parthandler.event = 'PART'
parthandler.priority = 'low'

def quithandler(phenny, input): 
   if input.nick in phenny.ident_admin:
      phenny.ident_admin.remove(input.nick)
   if input.nick.lower() in phenny.alias_list:
      del phenny.alias_list[input.nick.lower()]
quithandler.rule = r'(.*)'
quithandler.event = 'QUIT'
quithandler.priority = 'low'

def nickhandler(phenny, input): 
   newnick = input.encode('utf-8')
   if input.nick in phenny.ident_admin:
      phenny.ident_admin.remove(input.nick)
      phenny.ident_admin.append(newnick)
   elif input.admin:
      phenny.write(['WHOIS'], input.nick)
   if input.nick.lower() not in phenny.alias_list:
      phenny.alias_list[newnick.lower()] = input.nick.lower()
   else:
      if phenny.alias_list[input.nick.lower()] != newnick.lower():
         phenny.alias_list[newnick.lower()] = phenny.alias_list[input.nick.lower()]
      del phenny.alias_list[input.nick.lower()]
nickhandler.rule = r'(.*)'
nickhandler.event = 'NICK'
nickhandler.priority = 'low'

def debugg(phenny, input):
   if input.nick not in phenny.ident_admin: return phenny.notice(input.nick, 'Requires authorization. Use .auth to identify')
   phenny.notice(input.nick,repr(phenny.ident_admin))
   phenny.notice(input.nick,repr(phenny.alias_list))
debugg.commands = ['debug']
debugg.priority = 'low'

def whodat(phenny, input):
   nick = input.group(2)
   if nick:
      nick = nick.lower()
      if nick in phenny.alias_list:
         phenny.say(input.group(2) + " is " + phenny.alias_list[nick])
whodat.rule = r'(?i)(who is|who\'s|whos|whois) ([^?\s]+)'

def aliasto(phenny, input):
   if input.nick not in phenny.ident_admin: return phenny.notice(input.nick, 'Requires authorization. Use .auth to identify')
   alias = input.group(2)
   nick = input.group(3)
   if alias and nick:
      alias = alias.encode('utf-8').lower()
      nick = nick.encode('utf-8').lower()
      if nick in phenny.alias_list:
         if phenny.alias_list[nick] != alias:
            phenny.alias_list[alias] = phenny.alias_list[nick]
         del phenny.alias_list[nick]
      else:
         phenny.alias_list[alias] = nick
      phenny.notice(input.nick, "Alias successful")
aliasto.rule = (['aliasto'],r'(\S+) *(\S+)')

if __name__ == '__main__': 
   print __doc__.strip()
