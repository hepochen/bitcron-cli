#coding: utf8
from __future__ import absolute_import
import sys
import os
import datetime
import requests
from dateutil.tz import tzutc
from requests.exceptions import ConnectionError, Timeout
from bitcron.utils import md5_for_file, is_markdown, to_str
from bitcron.utils.path import get_relative_path, same_slash, is_a_hidden_path, is_sub_path

from .core.sync_utils import get_sync_data


PLATFORM = sys.platform


def reason_for_not_sync(full_path):
    if os.path.isfile(full_path):
        size = os.path.getsize(full_path)
    else:
        size = 0
    if size > 15 * 1024 * 1024:
        return 'the file size is larger than 15M'
    elif is_markdown(full_path) and size > 3*1024*1024:
        return 'the post file is too big than 3M'



def sync_file_to_server(token, filepath, root, sync_should_url, sync_url):
    # return logs (list)
    # 将本地的path转为 Server side 需要的path
    logs = []
    filepath = same_slash(filepath)
    root = same_slash(root)

    if is_a_hidden_path(filepath):
        return []# ignore
    if not is_sub_path(filepath, root):
        return []

    relative_path = get_relative_path(filepath, root)


    data = {
        'source': 'cli',
        'platform': PLATFORM,
        'path': to_str(relative_path),
        'token': token,
    }

    if os.path.exists(filepath):
        reason = reason_for_not_sync(filepath)
        if reason: # 不同步处理
            return [reason]
        is_deleted = False
        is_dir = os.path.isdir(filepath)
        is_file = not is_dir
        data['client_mtime'] = str(datetime.datetime.fromtimestamp(os.path.getmtime(filepath), tz=tzutc()))
    else:
        is_deleted = True
        sync_data = get_sync_data(filepath, root=root)
        is_dir = sync_data.get('is_dir', False)
        is_file = False

    data['is_dir'] = str(is_dir).lower() # 转为str
    data['is_deleted'] = str(is_deleted).lower() # 转为str
    if not is_deleted:
        if is_dir:
            version = ''
        else:
            version = md5_for_file(filepath)
        data['version'] = version


    # 开始同步到服务器
    response = None
    if is_file:
        try:
            timeout = 20* 60
            if is_markdown(filepath):
                timeout = 2*60
            try:
                checker_response = requests.post(sync_should_url, data=data, timeout=timeout)
                if checker_response.status_code == 401:
                    return ['bad token, break now']
                if checker_response.text == 'no': # 不需要同步了，已经存在了
                    return ['exist on server side already']
                elif checker_response.text == 'no_site':
                    return ['no site matched, break now'] # will not sync...
            except:
                pass

            with open(filepath, 'rb') as f:
                response = requests.post(sync_url, data=data, files={'file': f}, timeout=timeout)
            if response.status_code == 401:
                return ['bad token, break now']
            logs.append('uploaded to server done')
        except ConnectionError:
            logs.append('uploaded to server failed because of ConnectionError')
        except Timeout:
            logs.append('uploaded to server failed because of TimeoutError')
    else: # 删除文件或者是目录的更新
        try:
            response = requests.post(sync_url, data=data)
            if is_deleted:
                logs.append('deleted on server')
            else:
                logs.append('update folder to server')
        except ConnectionError:
            if is_deleted:
                logs.append('delete on server failed because of ConnectionError')
            else:
                logs.append('update folder on server failed because of ConnectionError')

    if response:
        status_code = response.status_code
        if status_code == 200:
            if response.headers.get('content-type') == 'application/json' and response.json().get('error_code'):
                message = response.json().get('message') or ''
                error_code = response.json().get('error_code')
                try:
                    error_code = int(error_code)
                    if error_code in [503, 401, 404]:
                        info = 'error_code:%s %s' % (error_code, message)
                        logs.append(info)
                except:
                    pass

        if status_code == 401: # 授权错误，删除原来保存的token
            logs.append('bad token')

    return logs
