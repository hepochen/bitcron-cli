#coding: utf8
from __future__ import absolute_import
import requests
from bitcron.utils.path import join

sync_domain = 'sync.bitcron.com'
sync_site_info_url = 'https://%s/service/get_sync_site_info' % sync_domain

site_node_filename = '.sync/site_node.config'

def get_sync_site_info(site_token):
    if not site_token:
        return {}
    try:
        response = requests.post(sync_site_info_url, dict(token=site_token))
        info = response.json()
        if info.get('main_node'):
            return info
    except:
        return {}



def get_sync_configs(root, site_token):
    site_node_config_filepath = join(root, site_node_filename)
    user_site_node = None
    try:
        with open(site_node_config_filepath) as f:
            user_site_node = f.read().strip()
            user_site_node = user_site_node.strip('/').split('/')[-1]
    except:
        pass
    site_info = get_sync_site_info(site_token)
    if site_info:
        configs = {}
        main_node = site_info.get('main_node')
        site_domain = site_info.get('domain')
        url_fields = ['sync_url', 'sync_list_url', 'sync_content_url', 'sync_should_url']
        for url_field in url_fields:
            url = site_info.get(url_field)
            if not url:
                return {}
            if user_site_node:
                url = url.replace(main_node, user_site_node)
            configs[url_field] = url
        configs['domain'] = site_domain
        configs['main_node'] = main_node
        return configs
    return {}
