#
# Copyright (c) 2013 Novell, Inc.
# All Rights Reserved.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, contact Novell, Inc.
#
# To contact Novell about this file by physical or electronic mail,
# you may find current contact information at www.novell.com
#
# ZYpp URL resolver plugin for Spacewalk-like servers
# Author: Flavio Castelli <fcastelli@suse.com>
#

from python.zypper.lock_helper import *

import os
import unittest
from tempfile import NamedTemporaryFile

class TestLockHelper(unittest.TestCase):

    def test_read_lock_file(self):
        locks = read_lock_file(
            os.path.dirname(os.path.abspath(__file__)) + '/locks.example'
        )

        self.assertEqual(3, len(locks))

    def test_add_a_new_lock(self):
        solvable_name = 'foo'
        locks         = []

        lock_solvable(locks, solvable_name)

        self.assertEqual(1, len(locks))

        lock = locks[0]
        self.assertEqual('package', lock['type'])
        self.assertEqual('exact', lock['match_type'])
        self.assertEqual('on', lock['case_sensitive'])
        self.assertEqual(solvable_name, lock['solvable_name'])

    def test_locking_solvable_should_not_affect_the_other_locks(self):
        solvable_name = 'vim'
        other_locks   = {
            'gnome-screensaver' : {
                'type'           : 'package',
                'match_type'     : 'exact',
                'case_sensitive' : 'off',
                'solvable_name'  : 'gnome-screensaver'
            },
            'kde' : {
                'type'           : 'package',
                'match_type'     : 'exact',
                'case_sensitive' : 'off',
                'solvable_name'  : 'kde'
            }
        }

        locks = other_locks.values()
        lock_solvable(locks, 'vim')

        self.assertEqual(3,len(locks))

        for lock in locks:
            if lock['solvable_name'] == solvable_name:
                # it doesn't make sense to test the values of the freshly added
                # lock, this is already covered by another test.
                continue

            expected_lock = other_locks[lock['solvable_name']]
            self.failUnless(expected_lock)
            self.assertEqual(expected_lock, lock)

    def test_overwrite_an_existing_lock(self):
        solvable_name = 'foo'
        locks         = [
            {
                'type'           : 'package',
                'match_type'     : 'exact',
                'case_sensitive' : 'off',
                'solvable_name'  : solvable_name
            }
        ]

        lock_solvable(locks, solvable_name)

        self.assertEqual(1, len(locks))

        lock = locks[0]
        self.assertEqual('package', lock['type'])
        self.assertEqual('exact', lock['match_type'])
        self.assertEqual('on', lock['case_sensitive'])
        self.assertEqual(solvable_name, lock['solvable_name'])

    def test_unlock_solvable(self):
        solvable_name = 'foo'
        locks         = [
            {
                'type'           : 'package',
                'match_type'     : 'exact',
                'case_sensitive' : 'off',
                'solvable_name'  : solvable_name
            }
        ]

        unlock_solvable(locks, solvable_name)

        self.assertEqual(0, len(locks))

    def test_unlocking_solvable_should_not_affect_the_other_locks(self):
        solvable_name = 'vim'
        other_locks   = {
            'gnome-screensaver' : {
                'type'           : 'package',
                'match_type'     : 'exact',
                'case_sensitive' : 'off',
                'solvable_name'  : 'gnome-screensaver'
            },
            'kde' : {
                'type'           : 'package',
                'match_type'     : 'exact',
                'case_sensitive' : 'off',
                'solvable_name'  : 'kde'
            }
        }

        locks = other_locks.values()
        lock_solvable(locks, 'vim')

        self.assertEqual(3,len(locks))

        for lock in locks:
            if lock['solvable_name'] == solvable_name:
                # it doesn't make sense to test the values of the freshly added
                # lock, this is already covered by another test.
                continue

            expected_lock = other_locks[lock['solvable_name']]
            self.failUnless(expected_lock)
            self.assertEqual(expected_lock, lock)

    def test_write_locks_to_file(self):
        locks = read_lock_file(
            os.path.dirname(os.path.abspath(__file__)) + '/locks.example'
        )

        tmpfile = NamedTemporaryFile(delete=False)

        try:
            write_lock_file(locks, tmpfile.name)
            actual_locks = read_lock_file(tmpfile.name)

            self.assertEqual(locks, actual_locks)
        finally:
            os.remove(tmpfile.name)

