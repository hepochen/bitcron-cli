#coding: utf8
from __future__ import absolute_import, print_function
import datetime
from .sync_utils import  make_sure_sync_log_path
from bitcron.utils.cli_color import print_colorful_parts


def to_str(strings):
    if isinstance(strings, unicode):
        strings = strings.encode('utf8')
    return strings

def write_logs(logs, filepath=None, root=None):
    # filepath: logs for which file, root: under which root
    if isinstance(logs, (str, unicode)):
        logs = [logs]
    if not logs:
        return # ignore
    if not root:
        return # ignore
    now = datetime.datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    log_path = make_sure_sync_log_path(root)
    with open(log_path, 'a') as f:
        for log in logs:
            log = raw_log = to_str(log)
            if filepath:
                filepath = to_str(filepath)
                log = '%s: %s %s\n' %(now_str, filepath, log)
                colorful_log = [(now_str, 'magenta'), (filepath, 'yellow'), (raw_log, 'cyan')]
            else:
                log = '%s %s\n' %(now_str, to_str(log))
                colorful_log = [(now_str, 'magenta'), (raw_log, 'cyan')]
            f.write(log)
            print_colorful_parts(colorful_log, end=' ')
