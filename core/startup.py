#!/usr/bin/env python
"""
startup.py - Phenny Startup Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import time, datetime

def setup(self):
   try:
      if not self.starttime:
         self.starttime = datetime.datetime.utcnow()
   except AttributeError:
      self.starttime = datetime.datetime.utcnow()

def startup(phenny, input): 
   if hasattr(phenny.config, 'nickpass'): 
      phenny.msg('NickServ', 'IDENTIFY %s' % phenny.config.nickpass)
      time.sleep(5)
   
   for channel in phenny.channels: 
      phenny.write(('JOIN', channel))
startup.rule = r'(.*)'
startup.event = '251'
startup.priority = 'low'

def nicktaken(phenny, input): 
   phenny.bot.nick = phenny.bot.nick + '_'
   phenny.write(('NICK', phenny.bot.nick))
nicktaken.rule = r'(.*)'
nicktaken.event = '433'
nicktaken.priority = 'low'

def ghost(phenny, input):
   if input.nick == 'NickServ' and phenny.bot.nick != phenny.config.nick:
      phenny.bot.nick = phenny.config.nick
      phenny.msg('NickServ', 'GHOST %s' % phenny.config.nick)
ghost.rule = r'You are now identified.*'
ghost.event = 'NOTICE'
ghost.priority = 'low'

def reclaim(phenny, input):
   if input.nick == 'NickServ':
      phenny.nick = phenny.config.nick
      phenny.write(('NICK', phenny.nick))
reclaim.rule = r'.*has been ghosted.'
reclaim.event = 'NOTICE'
reclaim.priority = 'low'

def rejoin(phenny, input): 
   phenny.write(('JOIN', input.sender))
rejoin.rule = r'(.*)'
rejoin.event = 'KICK'
rejoin.priority = 'low'

def uptime(phenny, input): 
   phenny.say('Last reconnect: %s' % prettydelta(phenny.starttime))
uptime.commands = ['uptime']
uptime.priority = 'low'

def prettydelta(d):
   diff = datetime.datetime.utcnow() - d
   s = diff.seconds
   if diff.days > 7:
      return d.strftime('%d %b')
   elif diff.days == 1:
      return '1 day ago'
   elif diff.days > 1:
      return '%d days ago' % diff.days
   elif s <= 1:
      return 'just now'
   elif s < 60:
      return '%d seconds ago' % s
   elif s < 120:
      return '1 minute ago'
   elif s < 3600:
      return '%d minutes ago' % (s/60)
   elif s < 7200:
      return '1 hour ago'
   else:
      return '%d hours ago' % (s/3600)

if __name__ == '__main__': 
   print __doc__.strip()
