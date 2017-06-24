# coding: utf8
from __future__ import absolute_import
import datetime
import json
import sys
import traceback
from bitcron.utils import get_now_str, to_str
from bitcron.utils.path import join
from .core.sync_utils import after_synced, make_sure_sync_log_path, after_sync_deleted
from .core.detect import loop_local_filesystem, find_files_to_delete
from .sync_from import  sync_from_server
from .sync_to import sync_file_to_server
from bitcron.sync.core.log import write_logs
from bitcron.sync.core.settings import get_sync_configs

def should_break_sync(logs, root):
    if logs:
        last_log = logs[-1]
        if last_log.endswith('bad token') or last_log.endswith(' break now') or last_log.endswith('Error'):
            write_logs([last_log, 'break and abort, please retry after correct your configs'], '', root)
            return True
    return False



def do_sync_from(token, root):
    sync_from_server(token=token, root=root)



def do_sync_to(token, root):
    # need to upload
    write_logs(['start to sync now'], '', root) # init
    changes_log_filepath = join(root, 'sync_changes.log')

    sync_configs = get_sync_configs(root, token)
    if not sync_configs:
        write_logs(['site TOKEN error or network connection error'], '', root) # init
        return
    sync_should_url = sync_configs['sync_should_url']
    sync_url = sync_configs['sync_url']


    try:
        file_paths = loop_local_filesystem(root)
        try:
            file_paths.remove(changes_log_filepath)
        except:
            pass

        if file_paths:
            write_logs('will try to sync %s files to server' % len(file_paths), root=root)
        for filepath in file_paths:
            logs = sync_file_to_server(token, filepath, root=root, sync_should_url=sync_should_url, sync_url=sync_url)
            if should_break_sync(logs, root):
                break
            write_logs(logs, filepath, root)
            if logs: # 不管日志上是否显示成功，都进行存档
                after_synced(filepath, root)

        files_to_delete = find_files_to_delete(root)
        if files_to_delete:
            write_logs('will try to delete %s files on server' % len(files_to_delete), root=root)
        for filepath in files_to_delete:
            # delete file
            logs = sync_file_to_server(token, filepath, root=root, sync_should_url=sync_should_url, sync_url=sync_url)
            if should_break_sync(logs, root):
                break
            write_logs(logs, filepath, root)
            after_sync_deleted(filepath, root) # no need to try again to delete on cloud

        # 将file_paths & files_to_delete 写到 root 内的某个配置文件内，以供其它调用
        if files_to_delete or file_paths:
            data = dict(
                date = get_now_str(),
                root = root,
                added = file_paths,
                deleted = files_to_delete,
            )
            with open(changes_log_filepath, 'w') as f:
                f.write(json.dumps(data))
        else:
            write_logs(['no need to sync to server, it is up-to-date.'], root=root)


    except Exception, e:
        write_logs([to_str(e)], '', root) # init
        write_logs(['unexpected errors happen, abort syncing now'], '', root) # init
        error_info = sys.exc_info()
        if error_info:
            e_type, value, tb = error_info[:3]
            traceback.print_exception(e_type, value, tb)

    write_logs(['sync ended'], '', root) # init