# coding: utf8
from __future__ import absolute_import

sync_domain = 'sync.bitcron.com'
sync_url = 'http://%s/service/sync' % sync_domain
sync_list_url = 'http://%s/service/sync_list' % sync_domain # list
sync_content_url = 'http://%s/service/sync_content' % sync_domain # get_content
should_sync_url  = 'http://%s/service/sync_should' % sync_domain # get_content


def get_server_url(base_url, node):
    if node and isinstance(node, (str, unicode)):
        node = node.lower().strip()
        is_str = True
        try:
            node = str(node)
        except:
            is_str = False
        node = node.strip().strip('/')
        if (node.endswith('.bitcron.com') or 'localhost' in node) and ' ' not in node and is_str:
            node = node.split('/')[-1]
            node_url = base_url.replace(sync_domain, node, 1)
            return node_url
    return base_url
