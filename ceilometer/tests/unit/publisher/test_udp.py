#
# Copyright 2013-2014 eNovance
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Tests for ceilometer/publisher/udp.py"""

from unittest import mock

import msgpack
from oslo_utils import netutils
from oslo_utils import timeutils
from oslotest import base

from ceilometer.publisher import udp
from ceilometer.publisher import utils
from ceilometer import sample
from ceilometer import service


COUNTER_SOURCE = 'testsource'


class TestUDPPublisher(base.BaseTestCase):
    test_data = [
        sample.Sample(
            name='test',
            type=sample.TYPE_CUMULATIVE,
            unit='',
            volume=1,
            user_id='test',
            project_id='test',
            resource_id='test_run_tasks',
            timestamp=timeutils.utcnow().isoformat(),
            resource_metadata={'name': 'TestPublish'},
            source=COUNTER_SOURCE,
        ),
        sample.Sample(
            name='test',
            type=sample.TYPE_CUMULATIVE,
            unit='',
            volume=1,
            user_id='test',
            project_id='test',
            resource_id='test_run_tasks',
            timestamp=timeutils.utcnow().isoformat(),
            resource_metadata={'name': 'TestPublish'},
            source=COUNTER_SOURCE,
        ),
        sample.Sample(
            name='test2',
            type=sample.TYPE_CUMULATIVE,
            unit='',
            volume=1,
            user_id='test',
            project_id='test',
            resource_id='test_run_tasks',
            timestamp=timeutils.utcnow().isoformat(),
            resource_metadata={'name': 'TestPublish'},
            source=COUNTER_SOURCE,
        ),
        sample.Sample(
            name='test2',
            type=sample.TYPE_CUMULATIVE,
            unit='',
            volume=1,
            user_id='test',
            project_id='test',
            resource_id='test_run_tasks',
            timestamp=timeutils.utcnow().isoformat(),
            resource_metadata={'name': 'TestPublish'},
            source=COUNTER_SOURCE,
        ),
        sample.Sample(
            name='test3',
            type=sample.TYPE_CUMULATIVE,
            unit='',
            volume=1,
            user_id='test',
            project_id='test',
            resource_id='test_run_tasks',
            timestamp=timeutils.utcnow().isoformat(),
            resource_metadata={'name': 'TestPublish'},
            source=COUNTER_SOURCE,
        ),
    ]

    @staticmethod
    def _make_fake_socket(published):
        def _fake_socket_socket(family, type):
            def record_data(msg, dest):
                published.append((msg, dest))

            udp_socket = mock.Mock()
            udp_socket.sendto = record_data
            return udp_socket

        return _fake_socket_socket

    def setUp(self):
        super().setUp()
        self.CONF = service.prepare_service([], [])
        self.CONF.publisher.telemetry_secret = 'not-so-secret'

    def test_published(self):
        self.data_sent = []
        with mock.patch('socket.socket',
                        self._make_fake_socket(self.data_sent)):
            publisher = udp.UDPPublisher(
                self.CONF,
                netutils.urlsplit('udp://somehost'))
        publisher.publish_samples(self.test_data)

        self.assertEqual(5, len(self.data_sent))

        sent_counters = []

        for data, dest in self.data_sent:
            counter = msgpack.loads(data, raw=False)
            sent_counters.append(counter)

            # Check destination
            self.assertEqual(('somehost', 4952), dest)

        # Check that counters are equal
        def sort_func(counter):
            return counter['counter_name']

        counters = [utils.meter_message_from_counter(d, "not-so-secret")
                    for d in self.test_data]
        counters.sort(key=sort_func)
        sent_counters.sort(key=sort_func)
        self.assertEqual(counters, sent_counters)

    @staticmethod
    def _raise_ioerror(*args):
        raise OSError

    def _make_broken_socket(self, family, type):
        udp_socket = mock.Mock()
        udp_socket.sendto = self._raise_ioerror
        return udp_socket

    def test_publish_error(self):
        with mock.patch('socket.socket',
                        self._make_broken_socket):
            publisher = udp.UDPPublisher(
                self.CONF,
                netutils.urlsplit('udp://localhost'))
        publisher.publish_samples(self.test_data)
