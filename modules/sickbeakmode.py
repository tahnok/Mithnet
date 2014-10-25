#!/usr/bin/env python
"""
sick beak mode - sick beaks for everyone
"""

def sickbeak_mode(phenny, input):
    if input.group(0) == 'sick beak mode':
        phenny.sickbeak_mode = not phenny.sickbeak_mode
    if phenny.sickbeak_mode:
        phenny.say("sick beak")

sickbeak_mode.priority = 'low'
sickbeak_mode.rule = r"(.*)"

def setup(self):
    self.sickbeak_mode = false

if __name__ == '__main__':
    print __doc__.strip()
