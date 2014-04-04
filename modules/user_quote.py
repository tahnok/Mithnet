import pickle
import random
import re
from modules import filename

MAX_LOGS = 30
MAX_QUOTES = 10
QVERSION = 1


def setup(self):
    self.logs = []
    self.quotes = {}
    try:
        f = open(filename(self, "karma"), "r")
        self.quotes = pickle.load(f)
        f.close()
    except IOError:
        pass


def save_quotes(self):
    try:
        f = open(filename(self, "quotes"), "w")
        pickle.dump((QVERSION, self.quotes), f)
        f.close()
    except IOError:
        pass


def log(phenny, input):
    phenny.logs.append((input.nick.lower(), input.group(1)))
    phenny.logs = phenny.logs[-MAX_LOGS:]
log.rule = r"(.*)"


def quote_me(phenny, input):
    user, msg = input.group(1), input.group(2)
    user = re.sub(r"[<>:]", "", user.lower())
    if (user, msg) in phenny.quotes:
        phenny.quotes[user].append(msg)
        phenny.quotes = phenny.quotes[-MAX_QUOTES:]
        save_quotes(phenny)
        phenny.say("Quote added")
    else:
        phenny.say("I'm not convinced %s ever said that." % input.group(1))
quote_me.rule = ('$nick', ['quote'], r'(?:\d\d?:?\s?)*(<[@+ ]\S+>|\S+:?)\s+(.*)')


def get_quote(phenny, input):
    nick = input.group(1).lower()
    if nick in phenny.quotes:
        return phenny.say("<%s> %s", (nick, random.choice(phenny.quotes[nick])))
    return phenny.say("%s has ever said anything noteworthy." % input.group(1))
get_quote.rule = ([".quote"], r"(\S+)")
