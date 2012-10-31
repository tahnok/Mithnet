#!/usr/bin/env python
"""
ping.py - Phenny Ping Module
Author: Sean B. Palmer, inamidst.com
About: http://inamidst.com/phenny/
"""

import random

def hello(phenny, input): 
   rand = random.random()
   if rand > 0.75:
      greeting = random.choice(('mm','yes?','hmm?','?'))
      phenny.say(greeting)
   elif rand > 0.3:
      greeting = random.choice(('heyy','hii','hihi','sup'))
      if rand > 0.5:
         phenny.say(greeting + ' ' + input.nick)
      else:
         phenny.say(greeting)
   else:
      greeting = random.choice(('Hi', 'Hey', 'Hello', 'Sup'))
      punctuation = random.choice(('', '!'))
      phenny.say(greeting + ' ' + input.nick + punctuation)
hello.rule = r'(?i)(hi|hello|hey|sup|yo|wassup) $nickname[ \t]*$'

def helloo(phenny, input): 
   greeting = random.choice(('I\'m doing great thanks for asking!','pretty good, just hanging out in this channel','not much, why?','decent I guess'))
   phenny.say(input.nick + ': ' + greeting)
helloo.rule = r'(?i)$nickname.* (what is|what\'s|whats|sup) ?(up|happening)?\??[ \t]*$'

def asl(phenny, input): 
   age = random.choice(('15','16','17'))
   rand = random.random()
   if rand > 0.9:
      location = random.choice(('cali','socal','tx'))
   else:
      location = random.choice(('mtl','montreal'))
   phenny.say(age + '/f/' + location)
asl.rule = r'(?i)$nickname.? *(asl)(?:[?!]+)?'

def asl2(phenny, input):
   asl(phenny, input)
asl2.rule = r'(?i)asl\W+$nickname(?:[?!]+)?'

def interjection(phenny, input): 
   phenny.say(input.nick + '!')
interjection.rule = r'$nickname!'
interjection.priority = 'high'
interjection.thread = False

if __name__ == '__main__': 
   print __doc__.strip()
