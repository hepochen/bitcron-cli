# coding: utf8
from __future__ import absolute_import
import os
import json
from bitcron.utils.path import same_slash, join, is_real, is_a_hidden_path
from bitcron.utils import md5_for_file
from .sync_utils import get_sync_data, get_sync_data_folder



def should_sync(filepath, root, check_md5=True):
    if not os.path.exists(filepath):
        return False
    elif is_a_hidden_path(filepath):
        return False
    elif not is_real(filepath):
        return False
    elif os.path.getsize(filepath) > 100*1024*1024: # 100Mb+ is not supported
        return False

    if check_md5:
        sync_data = get_sync_data(filepath, root)
        if sync_data:
            if sync_data.get('md5') == md5_for_file(filepath): # has been synced
                return False

    return True



def loop_local_filesystem(root_path, check_md5=True):
    root_path = same_slash(root_path)
    if not os.path.isdir(root_path): # 根目录不存在，不处理
        return []
    file_paths = []
    for parent, folders, files in os.walk(root_path):
        if is_a_hidden_path(parent):
            continue
        elif not is_real(parent): # link类型的不处理
            continue
        for fs in [files, folders]:
            for filename in fs:
                filepath = join(parent, filename)
                # 看是否已经在本地数据库了
                if not should_sync(filepath, root_path, check_md5):
                    continue
                file_paths.append(filepath)
    return file_paths

    #for filepath in file_paths:
    #    sync_a_filer_or_folder(filepath)



def find_files_to_delete(root_path):
    sync_data_folder = get_sync_data_folder(root_path)
    if not os.path.isdir(sync_data_folder): # never synced before
        return []
    files = loop_local_filesystem(root_path, check_md5=False) # same_path already
    data_filenames = os.listdir(sync_data_folder)
    old_file_paths = []
    for data_filename in data_filenames:
        data_filepath = join(sync_data_folder, data_filename)
        try:
            with open(data_filepath) as f:
                data = json.loads(f.read())
                filepath = data.get('filepath')
                if data.get('is_relative'):
                    filepath = join(root_path, filepath)
                if filepath:
                    old_file_paths.append(same_slash(filepath))
        except:
            pass
    return list(set(old_file_paths) - set(files))


