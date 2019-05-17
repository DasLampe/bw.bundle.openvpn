svc_systemv = {
    'openvpn': {
        'needs': [
            'pkg_apt:openvpn',
        ],
        'triggered': True,
    },
}

users = {
    'openvpn': {
        'shell': '/usr/sbin/nologin',
    }
}

files = {
    '/etc/openvpn/server.conf': {
        'source': 'etc/openvpn/server.conf',
        'content_type': 'mako',
        'context': {'vpn': node.metadata.get('openvpn', {})},
        'mode': '640',
        'owner': 'openvpn',
        'group': 'openvpn',
    },
    '/etc/openvpn/easy-rsa/vars': {
        'source': 'etc/openvpn/easy-rsa/vars',
        'content_type': 'mako',
        'context': {'ca': node.metadata.get('openvpn', {}).get('ca', {})},
        'mode': '640',
        'owner': 'openvpn',
        'group': 'openvpn',
        'triggers': [
            'action:config_easy_rsa',
        ]
    },
    '/etc/openvpn/easy-rsa/openssl.cnf': {
        'source': 'etc/openvpn/easy-rsa/openssl.cnf',
        'mode': '640',
        'owner': 'openvpn',
        'group': 'openvpn',
    },
}

directories = {
    '/etc/openvpn/easy-rsa/keys': {
        'owner': 'openvpn',
        'group': 'openvpn',
    }
}

actions = {
    'config_easy_rsa': {
        'command': '. /etc/openvpn/easy-rsa/vars && /usr/share/easy-rsa/clean-all',
        'unless': 'test -e /etc/openvpn/easy-rsa/keys/index.txt',
        'triggered': True,
        'needs': [
            'directory:/etc/openvpn/easy-rsa/keys',
            'pkg_apt:easy-rsa',
        ]
    },
    'gen_dhparam': {
        'command': 'openssl dhparam -out /etc/openvpn/dh4096.pem 4096',
        'unless': 'test -e /etc/openvpn/dh4096.pem',
        'needs': [
            'pkg_apt:openssl',
        ],
    },
    'gen_tls-auth': {
        'command': 'openvpn --genkey --secret /etc/openvpn/ta.key',
        'unless': 'test -e /etc/openvpn/ta.key',
        'needs': [
            'pkg_apt:openvpn',
        ],
    },
    'build_ca': {
        'command':  '. /etc/openvpn/easy-rsa/vars && '
                    '/usr/share/easy-rsa/pkitool --initca ca',
        'unless': 'test -e /etc/openvpn/easy-rsa/keys/ca.crt',
        'needs': [
            'directory:/etc/openvpn/easy-rsa/keys',
            'pkg_apt:easy-rsa',
            'file:/etc/openvpn/easy-rsa/openssl.cnf',
            'file:/etc/openvpn/easy-rsa/vars',
            'action:config_easy_rsa',
        ],
    },
    'build_server_key': {
        'command':  '. /etc/openvpn/easy-rsa/vars && '
                    '/usr/share/easy-rsa/pkitool --server server',
        'unless': 'test -e /etc/openvpn/easy-rsa/keys/server.crt',
        'needs': [
            'directory:/etc/openvpn/easy-rsa/keys',
            'file:/etc/openvpn/easy-rsa/openssl.cnf',
            'file:/etc/openvpn/easy-rsa/vars',
            'pkg_apt:easy-rsa',
            'action:build_ca',
            'action:config_easy_rsa',
        ],
    },
}

for client in node.metadata.get('openvpn', {}).get('clients', []):
    files['/etc/openvpn/clients/{}.ovpn'.format(client)] = {
        'source': 'etc/openvpn/clients/template.ovpn',
        'content_type': 'mako',
        'context': {'client': client},
    }

    actions['build_client_{}'.format(client)] = {
        'command':  '. /etc/openvpn/easy-rsa/vars && '
                    '/usr/share/easy-rsa/pkitool {} ' .format(client),
        'needs': [
            'pkg_apt:easy-rsa',
            'directory:/etc/openvpn/easy-rsa/keys',
            'action:build_ca',
            'action:build_server_key',
            'action:config_easy_rsa',
            ],
        'triggers': [
            'svc_systemv:openvpn:restart',
            ],
        'unless': 'test -e /etc/openvpn/easy-rsa/keys/{}.crt'.format(client),
    }

    actions['pack_client_{}'.format(client)] = {
        'command':  'cd /etc/openvpn/clients && ' 
                    'tar cfz vpn_client_{client}.tar.gz {client}.ovpn '
                    '-C /etc/openvpn/ ta.key -C /etc/openvpn/easy-rsa/keys {client}.key {client}.crt ca.crt'
                    .format(client=client),
        # Pack every time
        'unless': "false &> /dev/null",
        'needs': [
            'file:/etc/openvpn/clients/{}.ovpn'.format(client),
            'action:gen_tls-auth',
            'action:build_ca',
            'action:build_client_{}'.format(client),
            ],
    }

