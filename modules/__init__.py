import os

def filename(self, fname):
    name = ''.join((self.nick, '-', self.config.host, '.', fname, '.db'))
    return os.path.join(os.path.expanduser('~/.phenny'), name)
