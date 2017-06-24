#coding: utf8
from __future__ import absolute_import
import requests
import datetime
import os
import time
from requests.exceptions import ConnectionError
from bitcron.utils import is_markdown, to_unicode, md5_for_file
from bitcron.utils.path import same_slash, join, is_a_hidden_path
from bitcron.utils.file_utils import delete_file, create_file
from bitcron.sync.core.log import write_logs
from .core.sync_utils import get_sync_cursor, store_sync_cursor, after_synced, after_sync_deleted
from bitcron.sync.core.settings import get_sync_configs



def handle_meta(token, meta, root_path, sync_content_url):
    # prefix 更多是一个范围，一般是一个 site folder
    root_path = same_slash(root_path).rstrip('/')
    relative_path = same_slash(meta['path']).lstrip('/')  # 这个是大小写敏感的, 相对于根目录下的相对路径
    site_name = relative_path.strip('/').split('/')[0]

    full_path = join(root_path, relative_path) # 本地电脑的path
    version = meta.get('version', '')
    is_deleted = meta.get('is_deleted', False)
    is_dir = meta.get('is_dir', False)

    if is_a_hidden_path(relative_path): # 隐藏文件不处理
        return

    if relative_path.startswith('_cache/') or relative_path == '_cache': # cache 文件不处理
        return

    if os.path.exists(join(root_path, site_name, '.sync_ignore')):
        return # ignore


    if is_deleted:
        if os.path.exists(full_path):
            delete_file(full_path)
            # delete
            after_sync_deleted(full_path, root=root_path)
            return 'got %s from server, delete' % relative_path
    elif is_dir:
        if not os.path.isdir(full_path):
            try:
                os.makedirs(full_path)
                after_synced(full_path, root=root_path)
            except OSError:
                return 'failed to create dir %s' % full_path
            except:
                pass
    else: # 具体的文件
        file_id = to_unicode(meta['_id'])
        need_download = True
        if os.path.isfile(full_path):
            old_version = md5_for_file(full_path)
            if old_version == version:
                need_download = False

        if need_download:
            # 需要下载具体的文件
            timeout = 20* 60
            if is_markdown(full_path):
                timeout = 2*60
            response = requests.post(sync_content_url, data=dict(token=token, id=file_id), timeout=timeout)
            if response.status_code >= 400:
                # ignore
                return 'fail to get %s, status code is %s' % (full_path, response.status_code)
            content = response.content
            try:
                create_file(full_path, content)
            except OSError:
                return 'failed to create file then ignore %s' % full_path

            after_synced(full_path, root=root_path) # 保存这个状态，这样下次同步的时候，就不会认为这个文件需要同步了
            time.sleep(0.2) # 避免过度请求被服务器封锁的情况
            return 'got %s from server' % relative_path
        else:
            return '%s same file in both client side and server side' % relative_path




def get_metas(token, prefix='', cursor=None, got=None, sync_list_url=None):
    # 做成一个递归的
    if cursor=='init': # 初始化
        cursor = None
    got = got or []
    if token:
        data = dict(token=token, prefix=prefix)
        if cursor:
            if isinstance(cursor, datetime.datetime):
                cursor = cursor.strftime('%s')
            cursor = str(cursor)
            data['cursor'] = cursor
        try:
            response = requests.post(sync_list_url, data=data)
        except ConnectionError: # 连接错误
            return None, []
        if response.status_code >= 400:
            return None, []
        try:
            cursor_got = response.json()['cursor']
            if isinstance(cursor_got, float):
                new_cursor = '%f' % cursor_got
            else:
                new_cursor = str(cursor_got)
        except:
            return None, []
        new_files = response.json()['files']
        got += new_files
        if new_cursor == cursor or not new_files: # break this function
            return new_cursor, got
        else:
            return get_metas(token, prefix, new_cursor, got, sync_list_url)
    else: # 没有token，不处理
        return None, []



def sync_from_server(root, token):
    logs = []
    root = same_slash(root)

    sync_configs = get_sync_configs(root, token)
    if not sync_configs:
        write_logs("can't get the correct sync configs from server, check your network connection and your TOKEN?")
        return

    sync_list_url = sync_configs['sync_list_url']
    sync_content_url = sync_configs['sync_content_url']

    old_cursor = get_sync_cursor(root)
    write_logs('start sync from server', root=root)
    new_cursor, metas = get_metas(token, cursor=old_cursor, sync_list_url=sync_list_url)
    if not metas:
        write_logs('no need to sync from server, it is up-to-date.', root=root)
        return
    else:
        write_logs('will try to sync %s files from server.' % len(metas), root=root)

    for meta in metas:
        handler_log = handle_meta(token, meta, root, sync_content_url)
        if handler_log:
            write_logs(handler_log, root=root)
    if new_cursor: # 处理之后，再保存cursor
        store_sync_cursor(root, new_cursor)
    if new_cursor is None and not metas:
        logs.append('syncing maybe failed, check your sync config?')
    logs.append('sync ended')
    write_logs(logs, root=root)
