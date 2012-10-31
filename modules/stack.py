#!/usr/bin/env python
"""
stack.py - MithBot public stack

"""

import time

def setup(self):
   self.userstack = []
   self.stackban = []

def pop(bot, input): 
   """Pops the top item off the stack"""
   nick = input.nick.encode('utf-8').lower()
   if nick in bot.alias_list:
      nick = bot.alias_list[nick]
   if nick in bot.stackban:
      return bot.reply("You are banned from using the stack");
   if len(bot.userstack) == 0:
      return bot.say("The stack is empty")
   if not input.sender.startswith('#'): return bot.notice(input.nick,"You are not permitted to use this outside a channel")
   msg = bot.userstack.pop()
   bot.say(msg)
pop.commands = ['pop']

def peek(bot, input): 
   """Pops the top item off the stack"""
   nick = input.nick.encode('utf-8').lower()
   if nick in bot.alias_list:
      nick = bot.alias_list[nick]
   if nick in bot.stackban:
      return bot.reply("You are banned from using the stack");
   if len(bot.userstack) == 0:
      return bot.say("The stack is empty")
   msg = bot.userstack[-1]
   bot.say(msg)
peek.commands = ['peek']

def push(bot, input): 
   """Pushes an item onto the stack"""
   if not input.group(2):
      return bot.reply(".push what?")
   nick = input.nick.encode('utf-8').lower()
   if nick in bot.alias_list:
      nick = bot.alias_list[nick]
   if nick in bot.stackban:
      return bot.reply("You are banned from using the stack");
   if push.lastnick == nick and (time.time() - push.lastused) < 10:
      push.lastused = time.time()
      push.count += 1
      print str(push.count)
      if push.count > 3:
         bot.stackban.append(nick)
         bot.userstack = bot.userstack[:-3]
         return bot.reply("You have been banned from using the stack");
   else:
      push.lastnick = nick
      push.lastused = time.time()
      push.count = 1
   bot.userstack.append(input.group(2).encode('utf-8'))
   bot.notice(input.nick,'Pushed %s onto the stack' % input.group(2))
push.commands = ['push']
push.lastused = 0.0
push.lastnick = ''
push.count = 0

def stackunban(bot, input):
    if input.group(2) in bot.stackban:
        bot.stackban.remove(input.group(2))
stackunban.commands = ['stackunban']

if __name__ == '__main__': 
   print __doc__.strip()
