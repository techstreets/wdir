#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import os
import yaml
from git import Repo


DEFAULT_CONFIG = {}


class Config(object):

    def __init__(self):
        self.config_file = os.path.join(os.path.expanduser('~'), '.wdir')
        self.data = {}

    def load(self):
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w'):
                self.data = DEFAULT_CONFIG
                return self
        with open(self.config_file, 'r') as conf_file:
            self.data = yaml.load(conf_file.read()) or DEFAULT_CONFIG
        return self

    def save(self, data=None):
        with open(self.config_file, 'w') as conf_file:
            conf_file.write(yaml.safe_dump(
                data or self.data, default_flow_style=False
            ))
        return self

    def add_item(self, path):
        if 'gits' not in self.data:
            self.data['gits'] = []
        if os.path.isfile(path):
            print >> sys.stderr, 'Can\'t add files, only dirs %r.' % path
            return
        if path in self.data['gits']:
            print >> sys.stderr, 'Path %r already exists.' % path
            return
        if not os.path.exists(os.path.join(path, '.git')):
            # TODO: support non git repo
            # discover and add git repos in it
            # show as warning non git sub-dirs in it
            print >> sys.stderr, 'This is not git repo %r' % path
            print >> sys.stderr, 'Adding regular dir is not yet supported!'
            return
        self.data['gits'].append(path)
        if 'meta' not in self.data:
            self.data['meta'] = {}
        self.data['meta'][path] = {
            'remotes': [{
                'name': remote.name,
                'urls': [url for url in remote.urls],
            } for remote in Repo(path).remotes]
        }
        print >> sys.stderr, 'Added path %r.' % path

    def list_items(self):
        return self.data['gits']


def list_command(args, config):
    for path in config.list_items():
        print '  %s - %s' % (
            path, 'DIRTY' if Repo.init(path).is_dirty() else 'OK'
        )
    sys.exit(0)


def add_command(args, config):
    path = os.path.abspath(args[0])
    if not os.path.exists(path):
        print >> sys.stderr, 'Path: %r doesn\'t exists!' % path
        sys.exit(1)
    config.add_item(path)
    config.save()


commands = {
    'list': list_command,
    'add': add_command,
}


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print >> sys.stderr, 'No args provided'
        sys.exit(1)
    command = args.pop(0)
    if command not in commands:
        print >> sys.stderr, 'Command not supported!'
        print >> sys.stderr, 'Options are: %r' % commands.keys()
        sys.exit(1)
    commands[command](args, Config().load())


if __name__ == '__main__':
    main()
