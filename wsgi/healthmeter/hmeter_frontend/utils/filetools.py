# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

import io


class ChainFile(object):
    """
    Virtual file object that acts like itertools.chain()
    """
    def __init__(self, *files):
        self.files = list(files)

    def read(self, size=-1):
        if size < 0:
            return ''.join(f.read() for f in self.files)

        buf = io.StringIO()
        while self.files and size > 0:
            s = self.files[0].read(size)

            if len(s) < size:   # EOF
                self.files.pop(0).close()

            size -= len(s)

            buf.write(s)

        return buf.getvalue()


__all__ = ['ChainFile']
