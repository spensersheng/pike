#
# Copyright (c) 2013, EMC Corporation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Module Name:
#
#        durable.py
#
# Abstract:
#
#        Durable handle tests
#
# Authors: Arlene Berry (arlene.berry@emc.com)
#

import pike.model
import pike.smb2
import pike.test
import random
import array

class DurableHandleTest(pike.test.PikeTest):
    def __init__(self, *args, **kwargs):
        super(DurableHandleTest, self).__init__(*args, **kwargs)
        self.share_all = pike.smb2.FILE_SHARE_READ | pike.smb2.FILE_SHARE_WRITE | pike.smb2.FILE_SHARE_DELETE
        self.lease1 = array.array('B',map(random.randint, [0]*16, [255]*16))
        self.r = pike.smb2.SMB2_LEASE_READ_CACHING
        self.rw = self.r | pike.smb2.SMB2_LEASE_WRITE_CACHING
        self.rh = self.r | pike.smb2.SMB2_LEASE_HANDLE_CACHING
        self.rwh = self.rw | self.rh

    # Request a durable handle
    @pike.test.RequireDialect(pike.smb2.DIALECT_SMB2_1)
    def test_durable(self):
        chan, tree = self.tree_connect()

        # Request rwh lease
        handle1 = chan.create(tree,
                              'durable.txt',
                              access=pike.smb2.FILE_READ_DATA | pike.smb2.FILE_WRITE_DATA | pike.smb2.DELETE,
                              share=self.share_all,
                              disposition=pike.smb2.FILE_SUPERSEDE,
                              options=pike.smb2.FILE_DELETE_ON_CLOSE,
                              oplock_level=pike.smb2.SMB2_OPLOCK_LEVEL_LEASE,
                              lease_key = self.lease1,
                              lease_state = self.rwh,
                              durable=True).result()

        self.assertEqual(handle1.lease.lease_state, self.rwh)

        chan.close(handle1)

    # Reconnect a durable handle after a TCP disconnect
    @pike.test.RequireDialect(pike.smb2.DIALECT_SMB2_1)
    def test_durable_reconnect(self):
        chan, tree = self.tree_connect()

        # Request rwh lease
        handle1 = chan.create(tree,
                              'durable.txt',
                              access=pike.smb2.FILE_READ_DATA | pike.smb2.FILE_WRITE_DATA | pike.smb2.DELETE,
                              share=self.share_all,
                              disposition=pike.smb2.FILE_SUPERSEDE,
                              options=pike.smb2.FILE_DELETE_ON_CLOSE,
                              oplock_level=pike.smb2.SMB2_OPLOCK_LEVEL_LEASE,
                              lease_key = self.lease1,
                              lease_state = self.rwh,
                              durable=True).result()

        self.assertEqual(handle1.lease.lease_state, self.rwh)

        # Close the connection
        chan.connection.close()

        chan2, tree2 = self.tree_connect()

        # Request reconnect
        handle2 = chan2.create(tree,
                               'durable.txt',
                               share=self.share_all,
                               disposition=pike.smb2.FILE_SUPERSEDE,
                               oplock_level=pike.smb2.SMB2_OPLOCK_LEVEL_LEASE,
                               lease_key = self.lease1,
                               lease_state = self.rwh,
                               durable=handle1).result()
    
        self.assertEqual(handle2.lease.lease_state, self.rwh)

        chan2.close(handle2)

    # Request a durable handle via V2 context structure
    @pike.test.RequireDialect(pike.smb2.DIALECT_SMB3_0)
    def test_durable_v2(self):
        chan, tree = self.tree_connect()
        
        # Request rwh lease
        handle1 = chan.create(tree,
                              'durable.txt',
                              access=pike.smb2.FILE_READ_DATA | pike.smb2.FILE_WRITE_DATA | pike.smb2.DELETE,
                              share=self.share_all,
                              disposition=pike.smb2.FILE_SUPERSEDE,
                              options=pike.smb2.FILE_DELETE_ON_CLOSE,
                              oplock_level=pike.smb2.SMB2_OPLOCK_LEVEL_LEASE,
                              lease_key = self.lease1,
                              lease_state = self.rwh,
                              durable=0).result()
    
        self.assertEqual(handle1.lease.lease_state, self.rwh)

        chan.close(handle1)

    # Reconnect a durable handle via V2 context structure
    @pike.test.RequireDialect(pike.smb2.DIALECT_SMB3_0)
    def test_durable_reconnect_v2(self):
        chan, tree = self.tree_connect()

        # Request rwh lease
        handle1 = chan.create(tree,
                              'durable.txt',
                              access=pike.smb2.FILE_READ_DATA | pike.smb2.FILE_WRITE_DATA | pike.smb2.DELETE,
                              share=self.share_all,
                              disposition=pike.smb2.FILE_SUPERSEDE,
                              options=pike.smb2.FILE_DELETE_ON_CLOSE,
                              oplock_level=pike.smb2.SMB2_OPLOCK_LEVEL_LEASE,
                              lease_key = self.lease1,
                              lease_state = self.rwh,
                              durable=0).result()

        self.assertEqual(handle1.lease.lease_state, self.rwh)

        # Close the connection
        chan.connection.close()

        chan2, tree2 = self.tree_connect()

        # Request reconnect
        handle2 = chan2.create(tree,
                               'durable.txt',
                               share=self.share_all,
                               disposition=pike.smb2.FILE_SUPERSEDE,
                               oplock_level=pike.smb2.SMB2_OPLOCK_LEVEL_LEASE,
                               lease_key = self.lease1,
                               lease_state = self.rwh,
                               durable=handle1).result()
    
        self.assertEqual(handle2.lease.lease_state, self.rwh)

        chan2.close(handle2)