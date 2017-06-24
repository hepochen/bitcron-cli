#/usr/bin/env python
#coding: utf8
from __future__ import absolute_import, print_function
from bitcron import version
from bitcron.sync.sync_worker import do_sync_from, do_sync_to
from bitcron.sync.core.settings import  get_sync_configs
from bitcron.utils.path import join, get_parent_folders, make_sure_path
from bitcron.utils.file_utils import delete_file
from bitcron.utils.cli_color import print_with_color
import os
import sys

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

site_token_filename = '.sync/site_token.config'
site_node_filename = '.sync/site_node.config'
site_token_length = 22

def get_site_token(site_folder):
    if not site_folder:
        return
    token_filepath = join(site_folder, site_token_filename)
    if os.path.isfile(token_filepath):
        try:
            with open(token_filepath) as f:
                token_content = f.read().strip()
            if len(token_content) == site_token_length:
                return token_content
        except:
            pass

def is_site_folder(site_folder):
    if not site_folder:
        return False
    site_token = get_site_token(site_folder)
    return bool(site_token)



def get_site_folder_from_parents(current_folder):
    parent_folders = get_parent_folders(current_folder)
    for parent_folder in parent_folders:
        if is_site_folder(parent_folder):
            return parent_folder


def delete_site_folder_token(site_folder):
    if not os.path.isdir(site_folder):
        return # ignore
    site_token_filepath = join(site_folder, site_token_filename)
    try:
        os.remove(site_token_filepath)
    except:
        pass

def delete_sync_meta_folder(site_folder):
    delete_site_folder_token(site_folder)
    meta_folder = join(site_folder, '.sync')
    delete_file(meta_folder)

def show_info(site_folder):
    site_token = get_site_token(site_folder)
    print_with_color('Version: %s' % version, 'green')
    if not site_token:
        print_with_color('current folder is not a site of Bitcron', 'red')
    else:
        print_with_color('Site Token: %s (do not tell anyone else!)' % site_token, 'magenta')
        site_sync_configs = get_sync_configs(site_folder, site_token)
        if site_sync_configs:
            domain = site_sync_configs.get('domain')
            main_node = site_sync_configs.get('main_node')
            if domain:
                print_with_color('Domain: %s'%domain, 'green')
            if main_node:
                print_with_color('MainNode: %s'%main_node, 'yellow')
            site_node_config_filepath = join(site_folder, site_node_filename)
            try:
                with open(site_node_config_filepath) as f:
                    user_node_info = f.read().strip().strip('/').split('/')[-1]
                    if user_node_info:
                        print_with_color('MyNode: %s (current server)'%user_node_info, 'cyan')
            except:
                pass



def open_site_in_browser(site_folder):
    try:
        import webbrowser
    except:
        return
    site_token = get_site_token(site_folder)
    if not site_token:
        return
    site_sync_configs = get_sync_configs(site_folder, site_token)
    if site_sync_configs and site_sync_configs.get('domain'):
        homepage_url = 'http://%s' % site_sync_configs.get('domain')
        if homepage_url:
            try:
                webbrowser.open(homepage_url)
                return homepage_url
            except:
                pass


def show_help():
    print_with_color('1, bitcron XXXXXXXXXXXXXXX<The TOKEN> : bind site token', 'magenta')
    print_with_color('2, bitcron : sync to server', 'yellow')
    print_with_color('3, bitcron sync : sync to server', 'cyan')
    print_with_color('4, bitcron logout : remove site token', 'magenta')
    print_with_color('5, bitcron reset : reset sync metadata information and site token', 'yellow')
    print_with_color('6, bitcron open : open current site in your browser', 'cyan')



def main():
    current_folder = os.getcwd()
    argv = sys.argv

    if len(argv) == 2 and argv[1].strip('-') in ['help', 'h']:
        return show_help()


    if len(argv) == 2 and len(argv[1].strip()) == site_token_length:
        # set token
        site_token = argv[1].strip()
        site_token_filepath = join(current_folder, site_token_filename)
        make_sure_path(site_token_filepath)
        with open(site_token_filepath, 'w') as f:
            f.write(site_token)
        info = "site token is stored in %s now, do not public this file to anyone else." % site_token_filepath
        print_with_color(info, 'yellow')
    else:
        if not is_site_folder(current_folder):
            # try to match parents
            current_folder = get_site_folder_from_parents(current_folder)
        if not is_site_folder(current_folder):
            print_with_color("please run `bitcron TOKEN` first, you can find site TOKEN from your sites list page.", 'red')
        else:
            print_with_color('under %s now' % current_folder, 'green')

            # set site node
            if len(argv) == 2 and argv[1].strip().endswith('.bitcron.com'):

                site_node = argv[1].strip()
                site_node_config_filepath = join(current_folder, site_node_filename)
                with open(site_node_config_filepath, 'w') as f:
                    f.write(site_node)
                print_with_color('current node on %s now' % site_node, 'green')
                return

            action = ''
            if len(argv) == 1:
                action = 'sync_to' # sync to server
            elif len(argv) == 2:
                raw_action = argv[1]
                if raw_action in ['sync', 'sync_from', 'sync-from']:
                    action = 'sync_from'
                elif raw_action in ['logout']:
                    action = 'logout'
                elif raw_action in ['reset']:
                    action = 'reset'
                else:
                    action = raw_action

            if action == 'info':
                show_info(current_folder)
            elif action in ['site', 'open']:
                opened_url = open_site_in_browser(current_folder)
                if not opened_url:
                    print_with_color("can't handle this command", 'red')
                else:
                    print_with_color("%s is opened in your browser now" % opened_url, 'cyan')
            elif action == 'sync_to':
                do_sync_to(token=get_site_token(current_folder), root=current_folder)
            elif action == 'sync_from':
                do_sync_from(token=get_site_token(current_folder), root=current_folder)
            elif action == 'logout':
                delete_site_folder_token(current_folder)
                print_with_color("site TOKEN of current site folder is cleared on this disk.", 'red')
            elif action == 'reset':
                delete_sync_meta_folder(current_folder)
                print_with_color("metadata information files of site folder are cleared on this disk.", 'red')
            else:
                print_with_color("can't find matched command to run", 'red')

if __name__ == '__main__':
    main()