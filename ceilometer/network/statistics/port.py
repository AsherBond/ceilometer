#
# Copyright 2014 NEC Corporation.  All rights reserved.
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


from ceilometer.network import statistics
from ceilometer import sample


class PortPollster(statistics._Base):

    meter_name = 'switch.port'
    meter_type = sample.TYPE_GAUGE
    meter_unit = 'port'


class PortPollsterUptime(statistics._Base):

    meter_name = 'switch.port.uptime'
    meter_type = sample.TYPE_GAUGE
    meter_unit = 's'


class PortPollsterReceivePackets(statistics._Base):

    meter_name = 'switch.port.receive.packets'
    meter_type = sample.TYPE_CUMULATIVE
    meter_unit = 'packet'


class PortPollsterTransmitPackets(statistics._Base):

    meter_name = 'switch.port.transmit.packets'
    meter_type = sample.TYPE_CUMULATIVE
    meter_unit = 'packet'


class PortPollsterReceiveBytes(statistics._Base):

    meter_name = 'switch.port.receive.bytes'
    meter_type = sample.TYPE_CUMULATIVE
    meter_unit = 'B'


class PortPollsterTransmitBytes(statistics._Base):

    meter_name = 'switch.port.transmit.bytes'
    meter_type = sample.TYPE_CUMULATIVE
    meter_unit = 'B'
