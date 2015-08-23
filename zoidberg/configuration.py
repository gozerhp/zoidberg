import logging
import re
from .gerrit import GerritClient


class Configuration(object):
    """
    Massages the yaml config into something more easily usable.

    Config ends up looking like this:

    {
        'zoidberg-gerrit': {
            'username': '',
            'project-pattern': '',
            'host': '',
            'key_filename': '',
            'events': {
                'comment-added': [
                    {'action': 'ActionClass', 'target': 'other-gerrit'},
                    {'action': 'ActionClass2', 'target': 'other-gerrit'},
                ]
            }
        }
    }

    """
    def __init__(self, cfg):
        self.gerrits = {}
        gerrit_configs = self.get_section(cfg, 'gerrits', [])
        for gerrit in gerrit_configs:
            name = gerrit.keys()[0]
            self.gerrits[name] = {
                'name': name,
                'port': gerrit[name].get('port', 29418)
            }

            to_copy = [
                'username', 'project-pattern', 'host', 'key_filename',
                'startup']
            for k in to_copy:
                self.gerrits[name][k] = gerrit[name].get(k)

            self.gerrits[name]['project_re'] = re.compile(
                gerrit[name]['project-pattern'])

            self.gerrits[name]['events'] = {}

            # this is the only time we construct a new GerritClient
            # the client does not have an active ssh connection at
            # this point. Connection details are supplied when
            # zoidberg calls activate_ssh
            self.gerrits[name]['client'] = GerritClient()

            # create a list of actions for each event type
            for event in gerrit[name]['events']:
                event_type = event['type']
                if event_type not in self.gerrits[name]['events']:
                    self.gerrits[name]['events'][event_type] = []

                # some actions may only be interested in certain branches,
                # so construct a regexp object here so the action can match
                if 'branch-pattern' in event:
                    event['branch_re'] = re.compile(event['branch-pattern'])

                self.gerrits[name]['events'][event_type].append(event.copy())

        self.plugins = self.get_section(cfg, 'plugins', [])

    def get_section(self, cfg, name, default):
        for section in cfg:
            if name == section.keys()[0]:
                return section[name]
        return default

    def close_clients(self):
        """Closes the client connections for all clients in this config."""
        for gerrit_name in self.gerrits:
            # shutting down the event stream also closes the client
            if self.gerrits[gerrit_name]['client'] is not None:
                logging.info('Shutting down client for %s' % gerrit_name)
                self.gerrits[gerrit_name]['client'].stop_event_stream()
                logging.info('Shut down client for %s' % gerrit_name)
