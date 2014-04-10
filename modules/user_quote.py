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
        f = open(filename(self, "quotes"), "r")
        num, self.quotes = pickle.load(f)
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
    phenny.logs.append((input.nick.lower(), input.group(1).replace("\n", "").lstrip(" ")))
    phenny.logs = phenny.logs[-MAX_LOGS:]
log.rule = r"(.*)"


def quote_me(phenny, input):
    user, msg = input.group(2), input.group(3)
    user = re.sub(r"[\[\]<>: +@]", "", user.lower())
    if (user, msg) in phenny.logs:
        phenny.quotes.setdefault(user, []).append(msg)
        phenny.quotes[user] = phenny.quotes[user][-MAX_QUOTES:]
        save_quotes(phenny)
        phenny.say("Quote added")
    else:
        phenny.say("I'm not convinced %s ever said that." % user)
quote_me.rule = ('$nick', ['quote'], r'\[?(?:\d\d?:?\s?)*\]?(<[\[\]@+ ]?\S+>|\S+:?)\s+(.*)')


def get_quote(phenny, input):
    nick = input.group(2).lower()
    if nick in phenny.quotes:
        return phenny.say("<%s> %s" % (nick, random.choice(phenny.quotes[nick])))
    return phenny.say("%s has never said anything noteworthy." % input.group(2))
get_quote.rule = (["quote"], r"(\S+)")


def qnuke(phenny, input):
    if input.nick not in phenny.ident_admin: return phenny.notice(input.nick, 'Requires authorization. Use .auth to identify')
    nick = input.group(2).lower()
    if nick in phenny.quotes:
        del phenny.quotes[nick]
        save_quotes(phenny)
        return phenny.say("All of %s's memorable quotes erased." % nick)
    return phenny.say("Yeah whatever.")
qnuke.rule = (["qnuke"], r"(\S+)")


def debug_log(phenny, input):
    if input.nick not in phenny.ident_admin: return phenny.notice(input.nick, 'Requires authorization. Use .auth to identify')
    tor = "["
    for log in phenny.logs:
        if len(tor) + len(log) >= 490:
            phenny.notice(tor)
            tor = ""
        tor += log + ", "
    return phenny.notice(input.nick, tor + "]")
debug_log.rule = (["debuglog"], )
