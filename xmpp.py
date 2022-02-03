__filename__ = "xmpp.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.3.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Profile Metadata"


def get_xmpp_address(actor_json: {}) -> str:
    """Returns xmpp address for the given actor
    """
    if not actor_json.get('attachment'):
        return ''
    for property_value in actor_json['attachment']:
        if not property_value.get('name'):
            continue
        name_lower = property_value['name'].lower()
        if not (name_lower.startswith('xmpp') or
                name_lower.startswith('jabber')):
            continue
        if not property_value.get('type'):
            continue
        if not property_value.get('value'):
            continue
        if property_value['type'] != 'PropertyValue':
            continue
        if '@' not in property_value['value']:
            continue
        if '"' in property_value['value']:
            continue
        return property_value['value']
    return ''


def set_xmpp_address(actor_json: {}, xmpp_address: str) -> None:
    """Sets an xmpp address for the given actor
    """
    not_xmpp_address = False
    if '@' not in xmpp_address:
        not_xmpp_address = True
    if '.' not in xmpp_address:
        not_xmpp_address = True
    if '"' in xmpp_address:
        not_xmpp_address = True
    if '<' in xmpp_address:
        not_xmpp_address = True

    if not actor_json.get('attachment'):
        actor_json['attachment'] = []

    # remove any existing value
    property_found = None
    for property_value in actor_json['attachment']:
        if not property_value.get('name'):
            continue
        if not property_value.get('type'):
            continue
        if not (property_value['name'].lower().startswith('xmpp') or
                property_value['name'].lower().startswith('jabber')):
            continue
        property_found = property_value
        break
    if property_found:
        actor_json['attachment'].remove(property_found)
    if not_xmpp_address:
        return

    for property_value in actor_json['attachment']:
        if not property_value.get('name'):
            continue
        if not property_value.get('type'):
            continue
        name_lower = property_value['name'].lower()
        if not (name_lower.startswith('xmpp') or
                name_lower.startswith('jabber')):
            continue
        if property_value['type'] != 'PropertyValue':
            continue
        property_value['value'] = xmpp_address
        return

    new_xmpp_address = {
        "name": "XMPP",
        "type": "PropertyValue",
        "value": xmpp_address
    }
    actor_json['attachment'].append(new_xmpp_address)
