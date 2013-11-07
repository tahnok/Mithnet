#!/usr/bin/env python
"""
karma.py - Phenny karma Module
"""

import os, re
import pickle

SHOW_TOP_DEFAULT = 6
KVERSION = "0.1.6"

class KarmaNode(object):
    def __init__(self):
        # organizational
        self._parent = None  # the parent/children distinction is arbitrary
        self._children = set()
        # linked values, may hold junk if not root
        self._reset_linked()
        # raw values
        self._karma = 0
        self._contrib_plus = 0
        self._contrib_minus = 0

    def _set_and_link(attr):
        def anon(self, value):
            diff = value - getattr(self.root(), "_linked" + attr)
            setattr(self.root(), "_linked" + attr, value)
            setattr(self, attr, getattr(self, attr) + diff)
        return anon

    karma = property(
        lambda self: self.root()._linked_karma,
        _set_and_link("_karma"))
    contrib_plus = property(
        lambda self: self.root()._linked_contrib_plus,
        _set_and_link("_contrib_plus"))
    contrib_minus = property(
        lambda self: self.root()._linked_contrib_minus,
        _set_and_link("_contrib_minus"))

    def recalculate_karma(self):
        """Assumes self is root"""
        self._linked_karma = 0
        self._linked_contrib_plus = 0
        self._linked_contrib_minus = 0
        # BFS with acyclical guarantee
        q = set([self])
        while q:
            t = q.pop()
            self._add_to_linked(t)
            q |= t._children

    def root(self):
        while self._parent is not None:
            self = self._parent
        return self

    def _set_parent(self, parent):
        """Only sets the link, does no checks or updates"""
        self._parent = parent
        parent._children.add(self)

    def is_alias(self, other):
        """Returns true if self and other are in the same alias group, else false"""
        return self.root() == other.root()

    def add_alias(self, other):
        r1, r2 = self.root(), other.root()
        if r1 is r2:  # graph must be acyclical
            return False
        if self._parent is None:
            self._set_parent(other)
            r2._add_linked(self)
        elif other._parent is None:
            other._set_parent(self)
            r1._add_linked(other)
        else:  # decide on one to be the parent
            r1._add_linked(r2)
            new_parent = self
            current = other
            while current is not None:
                current._children.discard(new_parent)
                new_parent._children.add(current)
                # my parent becomes new_parent, my old parent becomes current, and current is the new parent
                current._parent, current, new_parent = new_parent, current._parent, current
        return True

    def remove_alias(self, other):
        if self._parent is other:
            other, self = self, other
        if other._parent is self:
            other._parent = None
            self._children.remove(other)
            other.recalculate_karma()
            self.root()._sub_linked(other)
            return True
        return False

    def __str__(self):
        return "".join((hex(id(self)), "(", hex(id(self._parent)), " [",
            ", ".join(map(lambda q: hex(id(q)), self._children)), "])"))


def _generic_linked(value_fn):
    def anon(self, other=None):
        for name in (
                "_karma",
                "_contrib_plus",
                "_contrib_minus"):
            setattr(self, "_linked" + name, value_fn(self, other, name))
    return anon

setattr(KarmaNode, "_reset_linked", _generic_linked(lambda _, __, ___: 0))
setattr(KarmaNode, "_sub_linked", _generic_linked(
    lambda self, other, name: getattr(self, "_linked" + name) - getattr(other, "_linked" + name)))
setattr(KarmaNode, "_sub_from_linked", _generic_linked(
    lambda self, other, name: getattr(self, "_linked" + name) - getattr(other, name)))
setattr(KarmaNode, "_add_linked", _generic_linked(
    lambda self, other, name: getattr(self, "_linked" + name) + getattr(other, "_linked" + name)))
setattr(KarmaNode, "_add_to_linked", _generic_linked(
    lambda self, other, name: getattr(self, "_linked" + name) + getattr(other, name)))


def filename(self, fname):
    name = ''.join((self.nick, '-', self.config.host, '.', fname, '.db'))
    return os.path.join(os.path.expanduser('~/.phenny'), name)

def setup(self):
    self.alias_tentative = {}
    try:
        f = open(filename(self, "karma"), "r")
        self.karmas = pickle.load(f)  # TODO: after the upgrade change to:
        # version, self.karmas = pickle.load
        f.close()
        # TODO: and then get rid of this upgrade code
        try:
            self.karmas[0]
        except KeyError:  # old version
            temp = {}
            for key, karma in self.karmas.items():
                temp[key] = KarmaNode()
                temp[key].karma = karma
            self.karmas = temp
            try:
                f = open(filename(self, "karma_contrib"), "r")
                kcont = pickle.load(f)
                f.close()
                for k, (plus, minus) in kcont.items():
                    kn = self.karmas.setdefault(k, KarmaNode())
                    kn.contrib_plus = plus
                    kn.contrib_minus = minus
            except IOError:
                pass
            save_karma(self)
        else:
            version, self.karmas = self.karmas  # TODO: yell (or upgrade) on version mismatch
    except IOError:
        pass

def save_karma(self):
    try:
        f = open(filename(self, "karma"), "w")
        pickle.dump((KVERSION, self.karmas), f)
        f.close()
    except IOError:
        pass

def karma_me(phenny, input):
    target = input.group(1).lower()
    karma = (input.group(2) == "++") * 2 - 1
    sender = input.nick.lower()
    if not hasattr(phenny, 'karmas'):
        return phenny.say('error?')

    target_nicks = set([target])
    sender_nicks = set([sender])
    if target in phenny.alias_list:
        target_nicks.add(phenny.alias_list[target])
    if sender in phenny.alias_list:
        sender_nicks.add(phenny.alias_list[sender])
    for t in target_nicks:  # target and sender must be disjoint
        for s in sender_nicks:
            if phenny.karmas.get(t, KarmaNode()).is_alias(phenny.karmas.get(s, KarmaNode())):
                if t == s == "benson":  # Mithorium: if you see this don't change it until benson does it once
                    return phenny.say("lol sick beak")
                return phenny.say("I'm sorry, "+input.nick+". I'm afraid I can't do that.")

    for t in target_nicks:
        if t in phenny.seen:  # i at least know who you're talking about.
            phenny.karmas.setdefault(target, KarmaNode()).karma += karma
            phenny.karmas.setdefault(sender, KarmaNode())
            if karma == -1:
                phenny.karmas[sender].contrib_minus += 1
            else:
                phenny.karmas[sender].contrib_plus += 1
            phenny.say(target+"'s karma is now "+str(phenny.karmas[target].karma))
            save_karma(phenny)
            return True
    phenny.notice(input.nick, "I'm sorry. I'm afraid I do not know who that is.")
karma_me.rule = r'(\S+?)[ :,]{0,2}(\+\+|--)\s*$'

def get_karma(phenny, input):
    """Fetch the karma of the given user. If no user is given, or with optional parameters 'top x', gives top and bottom x leaders in karma."""
    if not hasattr(phenny, 'karmas'):
        return phenny.say('error?')
    show_top = input.group(3)
    contrib = input.group(4)
    if show_top is not None:  # want to show the top x
        nick = None
        show_top = int(show_top)
    elif contrib is not None:  # want to show how much karma someone's changed
        lcontrib = contrib.lower()
        if lcontrib not in phenny.karmas or not (
                phenny.karmas[lcontrib].contrib_plus or
                phenny.karmas[lcontrib].contrib_minus):
            phenny.say(contrib + " has not altered any karma.")
            return
        up, down = map(str, (phenny.karmas[lcontrib].contrib_plus, phenny.karmas[lcontrib].contrib_minus))
        phenny.say(' '.join((contrib, "has granted", up, "karma and removed", down, "karma.")))
        return
    else:
        nick = input.group(2)
        show_top = SHOW_TOP_DEFAULT
    if nick:
        nick = nick.lower()
        if nick in phenny.karmas:
            phenny.say(nick + " has " + str(phenny.karmas[nick].karma) + " karma.")
        else:
            phenny.say("That entity does not exist within the karmaverse")
    elif len(phenny.karmas) > 0:
        karm = dict(((key.root(), kn.karma) for key, kn in phenny.karmas.items()))  # remove duplicates due to aliases
        s_karm = sorted(karm, key=karm.get, reverse=True)
        msg = ', '.join([x + ": " + str(karm[x]) for x in s_karm[:show_top]])
        if msg:
            phenny.say("Best karma: " + msg)
        worst_karmas = ', '.join([x + ": " + str(karm[x])
                for x in s_karm[:-show_top-1:-1] if karm[x] < 0])
        if worst_karmas:
            phenny.say("Worst karma: "+ worst_karmas)
    else:
        phenny.say("You guys don't have any karma apparently.")
get_karma.name = 'karma'
get_karma.rule = (["karma"], r'(?:(top +(\d)|contrib +(\S+)|\S+))?\s*$')

def nuke_karma(phenny, input):
    if input.nick not in phenny.ident_admin: return phenny.notice(input.nick, 'Requires authorization. Use .auth to identify')
    nick = input.group(2)
    if nick:
        nick = nick.lower()
        if nick in phenny.karmas:
            del phenny.karmas[nick]
            phenny.say(input.group(2) + " has been banished from the karmaverse")
            save_karma(phenny)
nuke_karma.name = 'knuke'
nuke_karma.rule = (["knuke"], r'(\S+)$')

def karma_alias(phenny, input):
    """Share your karma with another nick you use."""
    nick = input.nick
    target = input.group(2)
    phenny.alias_tentative[nick.lower()] = [0, input.sender, target.lower()]
    phenny.say("Karma merge offer initiated.")
    phenny.write(['WHOIS'], nick)  # logic continued in karma_id
karma_alias.name = 'klias'
karma_alias.rule = (["klias", "kmerge"], r"(\S+)\s?$")

def rm_karma_alias(phenny, input):
    """Remove the link between two nicks."""
    nick = input.nick
    target = input.group(2)
    phenny.alias_tentative[nick.lower()] = [-1, input.sender, target.lower()]
    phenny.say("Karma merge split initiated.")
    phenny.write(['WHOIS'], nick)  # logic continued in karma_id
rm_karma_alias.name = "rm_klias"
rm_karma_alias.rule = (["rm_klias", "kdemerge"], r"(\S+)\s?$")

def karma_id(phenny, input):
    logged_in_as = input.args[2].lower()
    if logged_in_as in phenny.alias_tentative:  # you're looking for someone
        data = phenny.alias_tentative[logged_in_as]
        verified, sender, target = data
        nick = input.args[1]
        if logged_in_as != nick.lower():  # logged in as someone else
            return phenny.msg(sender, "You must be logged in as " + nick)
        if data[0] == 0:  # add link
            data[0] = 1  # verified
            if target in phenny.alias_tentative:  # he was looking for someone too
                tverified, _, tstarget = phenny.alias_tentative[target]
                if tverified == 1 and tstarget == logged_in_as:  # done.
                    node1 = phenny.karmas[tstarget]
                    node2 = phenny.karmas[target]
                    if node1.add_alias(node2):
                        phenny.msg(sender, "You got it, " + target)
                    elif node1.is_alias(node2):
                        phenny.msg(sender, "You're already that guy.")
                    else:
                        phenny.msg(sender, "Karma alias failed.")
                    del phenny.alias_tentative[target]
                    del phenny.alias_tentative[tstarget]
        elif data[0] == -1:  # remove link
            node1 = phenny.karmas[logged_in_as]
            node2 = phenny.karmas[target]
            if node1.remove_alias(node2):
                phenny.msg(sender, "You are no longer also known as " + target)
            elif not node.is_alias(node2):
                phenny.msg(sender, "You are not that guy already.")
            else:
                phenny.msg(sender, "Karma alias removal failed.")
            del phenny.alias_tentative[logged_in_as]
karma_id.event = "330"
karma_id.rule = r"(.*)"
karma_id.priority = "low"

if __name__ == '__main__': 
   print __doc__.strip()
