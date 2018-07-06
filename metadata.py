@metadata_processor
def add_iptables_rule(metadata):
    if node.has_bundle("iptables"):
        interfaces = ['main_interface']
        interfaces += metadata.get('openvpn', {}).get('additional_interfaces', [])

        #Add Tun Device
        metadata += repo.libs.iptables.accept().input('tun0')

        for interface in interfaces:
            metadata += repo.libs.iptables.accept(). \
                input(interface). \
                state_new(). \
                udp(). \
                dest_port(metadata.get('openvpn', {}).get('port', '1194'))

    return metadata, DONE
