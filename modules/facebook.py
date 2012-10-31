#!/usr/bin/env python
"""
facebook.py - MithBot facebook search module

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
   if query.startswith('me') or query.startswith('514719084') or query.startswith('michael.fu'):
      return False
   uri = 'https://graph.facebook.com/'
   args = web.urllib.quote(query.encode('utf-8')) + '?access_token=245062872172460|bc67e3f85e6ec52109d9f7ca.1-514719084|jkDwqgaoEbjuH5UxSXJIq68Hps8'
   handler = web.urllib._urlopener
   web.urllib._urlopener = Grab()
   bytes = web.get(uri + args)
   web.urllib._urlopener = handler
   return web.json(bytes)

# def count(query): 
   # results = search(query)
   # if not results.has_key('responseData'): return '0'
   # if not results['responseData'].has_key('cursor'): return '0'
   # if not results['responseData']['cursor'].has_key('estimatedResultCount'): 
      # return '0'
   # return results['responseData']['cursor']['estimatedResultCount']

def formatnumber(n): 
   """Format a number with beautiful commas."""
   parts = list(str(n))
   for i in range((len(parts) - 3), 0, -3):
      parts.insert(i, ',')
   return ''.join(parts)

def fb(phenny, input): 
   """Queries Facebook for the specified input."""
   query = input.group(2)
   if not query: 
      return phenny.reply('.fb what?')
   result = search(query)
   if not result or 'error' in result:
      return phenny.say("No results found for '%s'." % query)
   if 'link' not in result:
      return phenny.say("Got data from facebook, but no links found for '%s'." % query)
   msg = ''
   if 'name' in result: 
      msg = msg + result['name'] + ' '
   elif 'type' in result:
      msg = msg + result['type'] + ': '
   msg = msg + result['link'].replace('\/','/')
   phenny.say(msg)
fb.commands = ['fb']
fb.priority = 'high'
fb.example = '.fb AMYKiNZ'

if __name__ == '__main__': 
   print __doc__.strip()
