# -*- encoding: utf-8 -*-
#
# Copyright © 2012 New Dream Network, LLC (DreamHost)
#
# Author: Julien Danjou <julien@danjou.info>
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
"""Tests for ceilometer.network.notifications
"""

import unittest

from ceilometer.network import notifications

NOTIFICATION_NETWORK_CREATE = {
    u'_context_roles': [u'anotherrole',
                        u'Member'],
    u'_context_read_deleted': u'no',
    u'event_type': u'network.create.end',
    u'timestamp': u'2012-09-27 14:11:27.086575',
    u'_context_tenant_id': u'82ed0c40ebe64d0bb3310027039c8ed2',
    u'payload': {u'network':
                 {u'status': u'ACTIVE',
                  u'subnets': [],
                  u'name': u'abcedf',
                  u'router:external': False,
                  u'tenant_id': u'82ed0c40ebe64d0bb3310027039c8ed2',
                  u'admin_state_up': True,
                  u'shared': False,
                  u'id': u'7fd4eb2f-a38e-4c25-8490-71ca8800c9be'}},
    u'priority': u'INFO',
    u'_context_is_admin': False,
    u'_context_timestamp': u'2012-09-27 14:11:26.924779',
    u'_context_user_id': u'b44b7ce67fc84414a5c1660a92a1b862',
    u'publisher_id': u'network.ubuntu-VirtualBox',
    u'message_id': u'9e839576-cc47-4c60-a7d8-5743681213b1'}


NOTIFICATION_SUBNET_CREATE = {
    u'_context_roles': [u'anotherrole',
                        u'Member'],
    u'_context_read_deleted': u'no',
    u'event_type': u'subnet.create.end',
    u'timestamp': u'2012-09-27 14:11:27.426620',
    u'_context_tenant_id': u'82ed0c40ebe64d0bb3310027039c8ed2',
    u'payload': {
        u'subnet': {
            u'name': u'mysubnet',
            u'enable_dhcp': True,
            u'network_id': u'7fd4eb2f-a38e-4c25-8490-71ca8800c9be',
            u'tenant_id': u'82ed0c40ebe64d0bb3310027039c8ed2',
            u'dns_nameservers': [],
            u'allocation_pools': [{u'start': u'192.168.42.2',
                                   u'end': u'192.168.42.254'}],
            u'host_routes': [],
            u'ip_version': 4,
            u'gateway_ip': u'192.168.42.1',
            u'cidr': u'192.168.42.0/24',
            u'id': u'1a3a170d-d7ce-4cc9-b1db-621da15a25f5'}},
    u'priority': u'INFO',
    u'_context_is_admin': False,
    u'_context_timestamp': u'2012-09-27 14:11:27.214490',
    u'_context_user_id': u'b44b7ce67fc84414a5c1660a92a1b862',
    u'publisher_id': u'network.ubuntu-VirtualBox',
    u'message_id': u'd86dfc66-d3c3-4aea-b06d-bf37253e6116'}


NOTIFICATION_PORT_CREATE = {
    u'_context_roles': [u'anotherrole',
                        u'Member'],
    u'_context_read_deleted': u'no',
    u'event_type': u'port.create.end',
    u'timestamp': u'2012-09-27 14:28:31.536370',
    u'_context_tenant_id': u'82ed0c40ebe64d0bb3310027039c8ed2',
    u'payload': {
        u'port': {
            u'status': u'ACTIVE',
            u'name': u'',
            u'admin_state_up': True,
            u'network_id': u'7fd4eb2f-a38e-4c25-8490-71ca8800c9be',
            u'tenant_id': u'82ed0c40ebe64d0bb3310027039c8ed2',
            u'device_owner': u'',
            u'mac_address': u'fa:16:3e:75:0c:49',
            u'fixed_ips': [{
                u'subnet_id': u'1a3a170d-d7ce-4cc9-b1db-621da15a25f5',
                u'ip_address': u'192.168.42.3'}],
            u'id': u'9cdfeb92-9391-4da7-95a1-ca214831cfdb',
            u'device_id': u''}},
    u'priority': u'INFO',
    u'_context_is_admin': False,
    u'_context_timestamp': u'2012-09-27 14:28:31.438919',
    u'_context_user_id': u'b44b7ce67fc84414a5c1660a92a1b862',
    u'publisher_id': u'network.ubuntu-VirtualBox',
    u'message_id': u'7135b8ab-e13c-4ac8-bc31-75e7f756622a'}


NOTIFICATION_PORT_UPDATE = {
    u'_context_roles': [u'anotherrole',
                        u'Member'],
    u'_context_read_deleted': u'no',
    u'event_type': u'port.update.end',
    u'timestamp': u'2012-09-27 14:35:09.514052',
    u'_context_tenant_id': u'82ed0c40ebe64d0bb3310027039c8ed2',
    u'payload': {
        u'port': {
            u'status': u'ACTIVE',
            u'name': u'bonjour',
            u'admin_state_up': True,
            u'network_id': u'7fd4eb2f-a38e-4c25-8490-71ca8800c9be',
            u'tenant_id': u'82ed0c40ebe64d0bb3310027039c8ed2',
            u'device_owner': u'',
            u'mac_address': u'fa:16:3e:75:0c:49',
            u'fixed_ips': [{
                u'subnet_id': u'1a3a170d-d7ce-4cc9-b1db-621da15a25f5',
                u'ip_address': u'192.168.42.3'}],
            u'id': u'9cdfeb92-9391-4da7-95a1-ca214831cfdb',
            u'device_id': u''}},
    u'priority': u'INFO',
    u'_context_is_admin': False,
    u'_context_timestamp': u'2012-09-27 14:35:09.447682',
    u'_context_user_id': u'b44b7ce67fc84414a5c1660a92a1b862',
    u'publisher_id': u'network.ubuntu-VirtualBox',
    u'message_id': u'07b0a3a1-c0b5-40ab-a09c-28dee6bf48f4'}


NOTIFICATION_NETWORK_EXISTS = {
    u'_context_roles': [u'anotherrole',
                        u'Member'],
    u'_context_read_deleted': u'no',
    u'event_type': u'network.exists',
    u'timestamp': u'2012-09-27 14:11:27.086575',
    u'_context_tenant_id': u'82ed0c40ebe64d0bb3310027039c8ed2',
    u'payload': {u'network':
                 {u'status': u'ACTIVE',
                  u'subnets': [],
                  u'name': u'abcedf',
                  u'router:external': False,
                  u'tenant_id': u'82ed0c40ebe64d0bb3310027039c8ed2',
                  u'admin_state_up': True,
                  u'shared': False,
                  u'id': u'7fd4eb2f-a38e-4c25-8490-71ca8800c9be'}},
    u'priority': u'INFO',
    u'_context_is_admin': False,
    u'_context_timestamp': u'2012-09-27 14:11:26.924779',
    u'_context_user_id': u'b44b7ce67fc84414a5c1660a92a1b862',
    u'publisher_id': u'network.ubuntu-VirtualBox',
    u'message_id': u'9e839576-cc47-4c60-a7d8-5743681213b1'}


class TestNotifications(unittest.TestCase):
    def test_network_create(self):
        v = notifications.Network()
        counters = v.process_notification(NOTIFICATION_NETWORK_CREATE)
        self.assertEqual(len(list(counters)), 2)

    def test_subnet_create(self):
        v = notifications.Subnet()
        counters = v.process_notification(NOTIFICATION_SUBNET_CREATE)
        self.assertEqual(len(list(counters)), 2)

    def test_port_create(self):
        v = notifications.Port()
        counters = v.process_notification(NOTIFICATION_PORT_CREATE)
        self.assertEqual(len(list(counters)), 2)

    def test_port_update(self):
        v = notifications.Port()
        counters = v.process_notification(NOTIFICATION_PORT_UPDATE)
        self.assertEqual(len(list(counters)), 2)

    def test_network_exists(self):
        v = notifications.Network()
        counters = v.process_notification(NOTIFICATION_NETWORK_EXISTS)
        self.assertEqual(len(list(counters)), 1)


class TestEventTypes(unittest.TestCase):

    def test_network(self):
        v = notifications.Network()
        events = v.get_event_types()
        assert events

    def test_subnet(self):
        v = notifications.Subnet()
        events = v.get_event_types()
        assert events

    def test_port(self):
        v = notifications.Port()
        events = v.get_event_types()
        assert events
