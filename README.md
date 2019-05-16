# Bundlewrap - OpenVPN Bundle

## Dependencies
- [apt-Bundle](https://github.com/sHorst/bw.bundle.apt)

## Config
        'openvpn': {
            'server_ip': '127.0.0.1',
            'vpn': {
                'ip': '10.15.4.0',
                'netmask': '255.255.255.0',
            }
            'ca': {
                'key_size': '2048',
                'key_expire': '3650',
                'expire': '3650',
                'country': 'DE',
                'province': 'NRW',
                'city': 'Aachen',
                'org': 'Example',
                'email': 'info@exmaple.org',
                'ou': '',
                'name': 'X509 Subject Field'
            },
            'clients': ['daslampe', 'daslampe-smartphone'],
        }

## Suggestion
- bw.bundle.iptables (https://github.com/sHorst/bw.bundle.iptables)