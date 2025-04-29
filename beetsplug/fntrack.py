import os
import sys

import beets
import beets.util
from beets.plugins import BeetsPlugin
from beets.ui import Subcommand

command = Subcommand('fntrack', help='file tracking')
command.parser.add_option('-s', dest='show', action='store_true')
command.parser.add_option('-c', dest='clear', action='store_true')

class FilenameTracker(BeetsPlugin):
    def __init__(self):
        super().__init__()
        self.changes = []
        self.config.add({"log":None})
        self.fn = self.config["log"].as_path()
        self.fo = None
        if self.fn:
            self.register_listener('item_copied', self.record)
            self.register_listener('item_moved', self.record)

    def record(self, item, source, destination):
        if not self.fo:
            self.fo = open(self.fn, "a", encoding="utf8")
        self.fo.write(os.fsdecode(source))
        self.fo.write("\n")
        self.fo.write("    ")
        self.fo.write(os.fsdecode(destination))
        self.fo.write("\n")

    def commands(self):
        command.func = self.cmd
        return [command]

    def cmd(self,lib, opts, args):
        if opts.show:
            if self.fn:
                fo = open(self.fn, "r", encoding="utf8")
                for line in fo:
                    line = line.rstrip()
                    print(line)

        if opts.clear:
            if self.fn:
                open(self.fn, "w", encoding="utf8")

        if not args:
            return

        d = {}
        s = None
        t = None
        fo = open(self.fn, "r", encoding="utf8")
        while True:
            if not s:
                s = fo.readline().rstrip()
                if not s:
                    break
                if s.startswith(" "):
                    continue
            t = fo.readline().rstrip()
            if not t:
                break
            if not t.startswith(" "):
                s = t
                continue
            t = t.lstrip()
            d[s] = t
            s = None
            t = None


        def iter_fns():
            for fn in args:
                if fn == "-":
                    for line in sys.stdin:
                        line = line.rstrip()
                        yield line
                else:
                    yield fn

        for fn in iter_fns():
            fnn = fn
            while fnn in d:
                fnn = d[fnn]
            print(f"{fn} -> {fnn}")
