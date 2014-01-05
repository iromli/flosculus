"""
Real-time log files watcher supporting log rotation.
Works with Python >= 2.6 and >= 3.2, on both POSIX and Windows.

Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
License: MIT
"""

import os
import time
import errno
import stat

import logbook

logger = logbook.Logger(__name__)


class LogWatcher(object):
    """Looks for changes in all files of a directory.
    This is useful for watching log file changes in real-time.
    It also supports files rotation.
    """

    def __init__(self, files, callback, tail_lines=0, sizehint=1048576):
        """Arguments:

        :param files: the files to watch
        :param callback: a function which is called every time one of
            the file being watched is updated; this is called with
            "filename" and "lines" arguments.
        :param tail_lines: read last N lines from files being watched
            before starting
        :param sizehint: passed to file.readlines(), represents an
            approximation of the maximum number of bytes to read from
            a file on every ieration (as opposed to load the entire
            file in memory until EOF is reached). Defaults to 1MB.
        """
        self._files = files
        self._files_map = {}
        self._callback = callback
        self._sizehint = sizehint

        self.update_files()
        for _, file_ in self._files_map.iteritems():
            file_.seek(os.path.getsize(file_.name))  # EOF
            if tail_lines:
                try:
                    lines = self.tail(file_.name, tail_lines)
                    if lines:
                        self._callback(file_.name, lines)
                except IOError as err:
                    if err.errno != errno.ENOENT:
                        raise

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __del__(self):
        self.close()

    def loop(self, interval=0.1, blocking=True):
        """Start a busy loop checking for file changes every *interval*
        seconds. If *blocking* is False make one loop then return.
        """
        # May be overridden in order to use pyinotify lib and block
        # until the directory being watched is updated.
        # Note that directly calling readlines() as we do is faster
        # than first checking file's last modification times.
        while True:
            self.update_files()
            for _, file_ in self._files_map.iteritems():
                self.readlines(file_)
            if not blocking:
                return
            time.sleep(interval)

    def log(self, line):
        """Log when a file is un/watched"""
        logger.info(line)

    @classmethod
    def open(cls, file_):
        """Wrapper around open().
        By default files are opened in binary mode and readlines()
        will return bytes on both Python 2 and 3.
        This means callback() will deal with a list of bytes.
        Can be overridden in order to deal with unicode strings
        instead, like this:

        .. sourcecode:: python

            import codecs
            import locale

            return codecs.open(
                file,
                'r',
                encoding=locale.getpreferredencoding(),
                errors='ignore',
            )
        """
        return open(file_, 'rb')

    @classmethod
    def tail(cls, fname, window):
        """Read last N lines from file fname."""
        if window <= 0:
            raise ValueError('invalid window value {!r}'.format(window))

        with cls.open(fname) as f:
            BUFSIZ = 1024

            # True if open() was overridden and file was opened in text
            # mode. In that case readlines() will return unicode strings
            # instead of bytes.
            encoded = getattr(f, 'encoding', False)
            CR = '\n' if encoded else b'\n'
            data = '' if encoded else b''

            f.seek(0, os.SEEK_END)
            fsize = f.tell()

            block = -1
            exit = False

            while not exit:
                step = (block * BUFSIZ)
                if abs(step) >= fsize:
                    f.seek(0)
                    newdata = f.read(BUFSIZ - (abs(step) - fsize))
                    exit = True
                else:
                    f.seek(step, os.SEEK_END)
                    newdata = f.read(BUFSIZ)

                data = newdata + data
                if data.count(CR) >= window:
                    break
                else:
                    block -= 1
            return data.splitlines()[-window:]

    def update_files(self):
        ls = []
        for name in self._files:
            try:
                st = os.stat(name)
                if not stat.S_ISREG(st.st_mode):
                    continue
                fid = self.get_file_id(st)
                ls.append((fid, name))
            except EnvironmentError as err:
                if err.errno != errno.ENOENT:
                    raise

        # check existent files
        for fid, file_ in self._files_map.iteritems():
            try:
                st = os.stat(file_.name)
                if fid != self.get_file_id(st):
                    # same name but different file (rotation);
                    # reload it.
                    self.unwatch(file_, fid)
                    self.watch(file_.name)
            except EnvironmentError as err:
                if err.errno != errno.ENOENT:
                    raise
                self.unwatch(file_, fid)

        # add new ones
        for fid, fname in ls:
            if fid not in self._files_map:
                self.watch(fname)

    def readlines(self, file_):
        """Read file lines since last access until EOF is reached and
        invoke callback.
        """
        while True:
            lines = file_.readlines(self._sizehint)
            if not lines:
                break
            self._callback(file_.name, lines)

    def watch(self, fname):
        try:
            file_ = self.open(fname)
            fid = self.get_file_id(os.stat(fname))
            self.log("watching logfile {}".format(fname))
            self._files_map[fid] = file_
        except EnvironmentError as err:
            if err.errno != errno.ENOENT:
                raise

    def unwatch(self, file_, fid):
        # File no longer exists. If it has been renamed try to read it
        # for the last time in case we're dealing with a rotating log
        # file.
        self.log("un-watching logfile {}".format(file_.name))
        del self._files_map[fid]

        with file_:
            lines = self.readlines(file_)
            if lines:
                self._callback(file_.name, lines)

    @staticmethod
    def get_file_id(st):
        if os.name == 'posix':
            return "{:x}g{:x}".format(st.st_dev, st.st_ino)
        return "{:f}".format(st.st_ctime)

    def close(self):
        for _, file_ in self._files_map.iteritems():
            file_.close()
        self._files_map.clear()
