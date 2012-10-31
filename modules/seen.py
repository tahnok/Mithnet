#!/usr/bin/env python
"""
seen.py - Phenny Seen Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import time, datetime, random

def setup(self):
   self.seen = {}

def f_seen(phenny, input): 
   """.seen <nick> - Reports when <nick> was last seen."""
   nick = input.group(2)
   if not nick: return phenny.reply('.seen who?')
   isself = False
   nick = nick.lower()
   if nick == input.nick.lower():
      isself = True
   if not hasattr(phenny, 'seen'): 
      return phenny.say('error?')
   if nick in phenny.alias_list:
      nick = phenny.alias_list[nick]
      if nick == input.nick.lower():
         isself = True
   if input.nick.lower() in phenny.alias_list:
      if nick == phenny.alias_list[input.nick.lower()]:
         isself = True
   if isself:
      return phenny.reply(random.choice(("You're right here you asshole", "Very funny dude.", "Seriously?")))
   if nick in phenny.seen: 
      orignick, t = phenny.seen[nick]
      dt = prettydelta(datetime.datetime.utcfromtimestamp(t))
      t = time.strftime('%a %b %d, %Y, at %H:%M:%S UTC', time.gmtime(t))

      msg = "I last saw %c%s%c %s at %s" % (chr(2), orignick, chr(15), dt, t)
      phenny.say(str(input.nick) + ': ' + msg)
   else: phenny.say("Sorry, I haven't seen %s around." % nick)
f_seen.name = 'seen'
f_seen.rule = (['seen'], r'(\S+)')

def f_note(phenny, input): 
   if input.admin and input.nick not in phenny.ident_admin:
      phenny.write(['WHOIS'], input.nick)
   def note(phenny, input): 
      if input.sender.startswith('#'): 
         # if input.sender == '#inamidst': return
         if input.nick.lower() in phenny.alias_list:
            phenny.seen[phenny.alias_list[input.nick.lower()]] = (input.nick, time.time())
         else:
            phenny.seen[input.nick.lower()] = (input.nick, time.time())

      # if not hasattr(self, 'chanspeak'): 
      #    self.chanspeak = {}
      # if (len(args) > 2) and args[2].startswith('#'): 
      #    self.chanspeak[args[2]] = args[0]

   try: note(phenny, input)
   except Exception, e: print e
f_note.rule = r'(.*)'
f_note.priority = 'low'

def clearseen(phenny, input):
   if input.nick not in phenny.ident_admin: return phenny.reply('Requires authorization. Use .auth to identify')
   phenny.seen.clear()
   phenny.alias_list.clear()
   phenny.say('Seen and alias list flushed')
clearseen.commands = ['resetseen']
clearseen.priority = 'low'

def prettydelta(d):
   diff = datetime.datetime.utcnow() - d
   s = diff.seconds
   if diff.days > 7:
      return '%d weeks ago' % (diff.days/7)
   elif diff.days == 7:
      return '1 week ago'
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
