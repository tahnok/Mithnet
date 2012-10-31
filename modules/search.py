#!/usr/bin/env python
"""
search.py - Phenny Web Search Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re
import web

class Grab(web.urllib.URLopener):
   def __init__(self, *args):
      self.version = 'Mozilla/5.0 (Phenny)'
      web.urllib.URLopener.__init__(self, *args)
      self.addheader('Referer', 'https://github.com/sbp/phenny')
   def http_error_default(self, url, fp, errcode, errmsg, headers):
      return web.urllib.addinfourl(fp, [headers, errcode], "http:" + url)

def search(query): 
   """Search using AjaxSearch, and return its JSON."""
   uri = 'http://ajax.googleapis.com/ajax/services/search/web'
   args = '?v=1.0&safe=off&q=' + web.urllib.quote(query.encode('utf-8'))
   handler = web.urllib._urlopener
   web.urllib._urlopener = Grab()
   bytes = web.get(uri + args)
   web.urllib._urlopener = handler
   return web.json(bytes)

def result(query): 
   results = search(query)
   try: return results['responseData']['results'][0]['unescapedUrl']
   except IndexError: return None
   except TypeError: 
      print results
      return False

def count(query): 
   results = search(query)
   if not results.has_key('responseData'): return '0'
   if not results['responseData'].has_key('cursor'): return '0'
   if not results['responseData']['cursor'].has_key('estimatedResultCount'): 
      return '0'
   return results['responseData']['cursor']['estimatedResultCount']

def formatnumber(n): 
   """Format a number with beautiful commas."""
   parts = list(str(n))
   for i in range((len(parts) - 3), 0, -3):
      parts.insert(i, ',')
   return ''.join(parts)

def g(phenny, input): 
   """Queries Google for the specified input."""
   query = input.group(2)
   if not query: 
      return phenny.reply('.g what?')
   uri = result(query)
   if uri: 
      phenny.say(uri)
   elif uri is False: phenny.say("Problem getting data from Google.")
   else: phenny.say("No results found for '%s'." % query)
g.commands = ['g']
g.priority = 'high'
g.example = '.g miley cyrus'

def gc(phenny, input): 
   """Returns the number of Google results for the specified input."""
   query = input.group(2)
   if not query: 
      return phenny.reply('.gc what?')
   num = formatnumber(count(query))
   phenny.say(query + ': ' + num)
gc.commands = ['gc']
gc.priority = 'high'
gc.example = '.gc extrapolate'

r_query = re.compile(
   r'\+?"[^"\\]*(?:\\.[^"\\]*)*"|\[[^]\\]*(?:\\.[^]\\]*)*\]|\S+'
)

def gcs(phenny, input): 
   """Google fight!"""
   if not input.group(2):
      return phenny.reply("Nothing to compare.")
   queries = r_query.findall(input.group(2))
   if len(queries) > 6: 
      return phenny.reply('Sorry, can only compare up to six things.')

   results = []
   for i, query in enumerate(queries): 
      query = query.strip('[]')
      n = int((formatnumber(count(query)) or '0').replace(',', ''))
      results.append((n, query))
      if i >= 2: __import__('time').sleep(0.25)
      if i >= 4: __import__('time').sleep(0.25)

   results = [(term, n) for (n, term) in reversed(sorted(results))]
   reply = ', '.join('%s (%s)' % (t, formatnumber(n)) for (t, n) in results)
   phenny.say(reply)
gcs.commands = ['gcs', 'comp']

# r_ddg = re.compile(r'nofollow" class="[^"]+" href="(.*?)">')

# def ddg(phenny, input): 
   # query = input.group(2)
   # if not query: return phenny.reply('.ddg what?')

   # query = web.urllib.quote(query.encode('utf-8'))
   # uri = 'http://duckduckgo.com/html/?q=%s&kl=uk-en' % query
   # bytes = web.get(uri)
   # m = r_ddg.search(bytes)
   # if m: 
      # uri = m.group(1)
      # phenny.reply(uri)
      # if not hasattr(phenny.bot, 'last_seen_uri'):
         # phenny.bot.last_seen_uri = {}
      # phenny.bot.last_seen_uri[input.sender] = uri
   # else: phenny.reply("No results found for '%s'." % query)
# ddg.commands = ['ddg']

if __name__ == '__main__': 
   print __doc__.strip()
