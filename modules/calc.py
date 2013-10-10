#!/usr/bin/env python
# coding=utf-8
"""
calc.py - Phenny Calculator Module
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re, time
import web

r_result = re.compile(r'(?i)<A NAME=results>(.*?)</A>')
r_tag = re.compile(r'<\S+.*?>')

subs = [
   (' in ', ' -> '), 
   (' over ', ' / '), 
   (u'£', 'GBP '), 
   (u'€', 'EUR '), 
   ('\$', 'USD '), 
   (r'\bKB\b', 'kilobytes'), 
   (r'\bMB\b', 'megabytes'), 
   (r'\bGB\b', 'kilobytes'), 
   ('kbps', '(kilobits / second)'), 
   ('mbps', '(megabits / second)')
]

def calc(phenny, input): 
   """Google calculator."""
   if not input.group(2):
      return phenny.reply("Nothing to calculate.")
   q = input.group(2).encode('utf-8')
   q = q.replace('\xcf\x95', 'phi') # utf-8 U+03D5
   q = q.replace('\xcf\x80', 'pi') # utf-8 U+03C0
   uri = 'http://www.google.com/ig/calculator?q='
   bytes = web.get(uri + web.urllib.quote(q))
   parts = bytes.split('",')
   answer = [p for p in parts if p.startswith('rhs: "')][0][6:]
   if answer: 
      answer = answer.decode('unicode-escape')
      answer = ''.join(chr(ord(c)) for c in answer)
      answer = answer.decode('utf-8')
      answer = answer.replace(u'\xc2\xa0', ',')
      answer = answer.replace('<sup>', '^(')
      answer = answer.replace('</sup>', ')')
      answer = web.decode(answer)
      phenny.say(answer)
   else: phenny.say('Sorry, no result.')
calc.commands = ['calc','c']
calc.example = '.c 5 + 3'

def py(phenny, input): 
   """Python web evaluator."""
   query = input.group(2).encode('utf-8')
   if input.nick not in phenny.ident_admin:
      if not input.sender.startswith('#'): return phenny.notice(input.nick,input.nick + ": You are not permitted to use this outside a channel")
      if 'sys' in query or 'os' in query: return
      if 'sleep' in query or 'while' in query: return phenny.notice(input.nick,input.nick + ": Fuck off. You're not funny, you're not cool. Nobody likes you.")
   uri = 'http://tumbolia.appspot.com/py/'
   answer = web.get(uri + web.urllib.quote(query))
   if input.nick not in phenny.ident_admin:
      if len(answer) > 150: return phenny.notice(input.nick,input.nick + ": Fuck off. You're not funny, you're not cool. Nobody likes you.")
   if answer:
      if input.nick in phenny.ident_admin:
         phenny.say(answer)
      elif (time.time() - (py.lastused + py.throttle)) > 30:
         py.throttle = 2
         py.lastused = time.time()
         py.warned = False
         phenny.say(answer)
      elif (time.time() - py.lastused) > py.throttle:
         py.throttle = 2*py.throttle
         py.lastused = time.time()
         py.warned = False
         phenny.say(answer)
      elif not py.warned:
         py.warned = True
         phenny.say(".py has been throttled: limit 1 use per " + str(py.throttle) + " seconds")
      else: return
   else: phenny.reply('Sorry, no result.')
   # __import__('time').sleep(1)
   # phenny.say('Error: API quota exceeded')
py.commands = ['py']
py.lastused = 0.0
py.throttle = 2
py.warned = False


def irb(phenny, input):
    query = input.group(2).encode('utf-8')
    uri = 'https://eval.in/'
    data = {"utf8": "\xce", "execute": "1", "private": "0", "lang": "ruby/mri-2.0.0",
        "input": "", "code": query}
    raw_answer = web.post(uri, data)
    try:
      _, _, answer = raw_answer.partition("<h2>Program Output</h2>")
      answer = answer.lstrip()
      answer = answer[5: answer.index("</pre>")]
      answer = web.decode(answer)
    except ValueError as e:
      phenny.notice(input.nick, "ValueError " + e + ": " + answer[:100])
    if input.nick not in phenny.ident_admin:
        if len(answer) > 150: return phenny.notice(input.nick,input.nick + ": Fuck off. You're not funny, you're not cool. Nobody likes you.")
    if answer:
        if input.nick in phenny.ident_admin:
            phenny.say(answer)
        elif (time.time() - (irb.lastused + irb.throttle)) > 30:
            irb.throttle = 2
            irb.lastused = time.time()
            irb.warned = False
            phenny.say(answer)
        elif (time.time() - irb.lastused) > irb.throttle:
            irb.throttle = 2*irb.throttle
            irb.lastused = time.time()
            irb.warned = False
            phenny.say(answer)
        elif not irb.warned:
            irb.warned = True
            phenny.say(".irb has been throttled: limit 1 use per " + str(irb.throttle) + " seconds")
        else: return
    else: phenny.reply('Sorry, no result.')
irb.commands = ['irb']
irb.lastused = 0.0
irb.throttle = 2
irb.warned = False

def wa(phenny, input): 
   """Wolfram|Alpha."""
   if not input.group(2):
      return phenny.reply("No search term.")
   query = input.group(2).encode('utf-8')
   uri = 'http://tumbolia.appspot.com/wa/'
   answer = web.get(uri + web.urllib.quote(query.replace('+', '%2B')))
   if answer: 
      phenny.say(answer)
   else: phenny.reply('Sorry, no result.')
wa.commands = ['wa']
wa.example = '.wa age of Miley Cyrus'

if __name__ == '__main__': 
   print __doc__.strip()
