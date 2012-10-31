#!/usr/bin/env python
"""
head.py - Phenny HTTP Metadata Utilities
Copyright 2008, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re, urllib, urllib2, httplib, urlparse, time
from htmlentitydefs import name2codepoint
import web
from tools import deprecated

def head(phenny, input): 
   """Provide HTTP HEAD information."""
   uri = input.group(2)
   uri = (uri or '').encode('utf-8')
   if ' ' in uri: 
      uri, header = uri.rsplit(' ', 1)
   else: uri, header = uri, None

   if not uri: return phenny.say('?')

   if not uri.startswith('htt'): 
      uri = 'http://' + uri
   # uri = uri.replace('#!', '?_escaped_fragment_=')

   try: info = web.head(uri)
   except IOError: return phenny.say("Can't connect to %s" % uri)
   except httplib.InvalidURL: return phenny.say("Not a valid URI, sorry.")

   if not isinstance(info, list): 
      try: info = dict(info)
      except TypeError: 
         return phenny.reply('Try .head http://example.org/ [optional header]')
      info['Status'] = '200'
   else: 
      newInfo = dict(info[0])
      newInfo['Status'] = str(info[1])
      info = newInfo

   if header is None: 
      data = []
      if info.has_key('Status'): 
         data.append(info['Status'])
      if info.has_key('content-type'): 
         data.append(info['content-type'].replace('; charset=', ', '))
      if info.has_key('last-modified'): 
         modified = info['last-modified']
         modified = time.strptime(modified, '%a, %d %b %Y %H:%M:%S %Z')
         data.append(time.strftime('%Y-%m-%d %H:%M:%S UTC', modified))
      if info.has_key('content-length'): 
         data.append(info['content-length'] + ' bytes')
      phenny.say(', '.join(data))
   else: 
      headerlower = header.lower()
      if info.has_key(headerlower): 
         phenny.say(header + ': ' + info.get(headerlower))
      else: 
         msg = 'There was no %s header in the response.' % header
         phenny.say(msg)
head.commands = ['head']
head.example = '.head http://www.w3.org/'

r_title = re.compile(r'(?ims)<title[^>]*>(.*?)</title\s*>')
r_entity = re.compile(r'&[A-Za-z0-9#]+;')

# def noteuri(phenny, input): 
   # uri = input.group(1).encode('utf-8')
   # if not hasattr(phenny.bot, 'last_seen_uri'): 
      # phenny.bot.last_seen_uri = {}
   # phenny.bot.last_seen_uri[input.sender] = uri
# noteuri.rule = r'.*(http[s]?://[^<> "\x01]+)[,.]?'
# noteuri.priority = 'low'

if __name__ == '__main__': 
   print __doc__.strip()
