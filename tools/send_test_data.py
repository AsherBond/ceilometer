#!/usr/bin/env python3
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Command line tool for sending test data for Ceilometer via oslo.messaging.

Usage:

Send messages with samples generated by make_test_data

source .tox/py27/bin/activate
./tools/send_test_data.py --count 1000 --resources_count 10 --topic metering
"""
import argparse
import datetime
import functools
import json
import random
import uuid

import make_test_data
import oslo_messaging
from oslo_utils import timeutils

from ceilometer import messaging
from ceilometer.publisher import utils
from ceilometer import service


def send_batch_notifier(notifier, topic, batch):
    notifier.sample({}, event_type=topic, payload=batch)


def get_notifier(conf):
    return oslo_messaging.Notifier(
        messaging.get_transport(conf),
        driver='messagingv2',
        publisher_id='telemetry.publisher.test',
        topics=['metering'],
    )


def generate_data(conf, send_batch, make_data_args, samples_count,
                  batch_size, resources_count, topic):
    make_data_args.interval = 1
    make_data_args.start = (timeutils.utcnow() -
                            datetime.timedelta(minutes=samples_count))
    make_data_args.end = timeutils.utcnow()

    make_data_args.resource_id = None
    resources_list = [str(uuid.uuid4())
                      for _ in range(resources_count)]
    resource_samples = {resource: 0 for resource in resources_list}
    batch = []
    count = 0
    for sample in make_test_data.make_test_data(conf,
                                                **make_data_args.__dict__):
        count += 1
        resource = resources_list[random.randint(0, len(resources_list) - 1)]
        resource_samples[resource] += 1
        sample['resource_id'] = resource
        # need to change the timestamp from datetime.datetime type to iso
        # format (unicode type), because collector will change iso format
        # timestamp to datetime.datetime type before recording to db.
        sample['timestamp'] = sample['timestamp'].isoformat()
        # need to recalculate signature because of the resource_id change
        sig = utils.compute_signature(sample,
                                      conf.publisher.telemetry_secret)
        sample['message_signature'] = sig
        batch.append(sample)
        if len(batch) == batch_size:
            send_batch(topic, batch)
            batch = []
        if count == samples_count:
            send_batch(topic, batch)
            return resource_samples
    send_batch(topic, batch)
    return resource_samples


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--batch-size',
        dest='batch_size',
        type=int,
        default=100
    )
    parser.add_argument(
        '--config-file',
        default='/etc/ceilometer/ceilometer.conf'
    )
    parser.add_argument(
        '--topic',
        default='perfmetering'
    )
    parser.add_argument(
        '--samples-count',
        dest='samples_count',
        type=int,
        default=1000
    )
    parser.add_argument(
        '--resources-count',
        dest='resources_count',
        type=int,
        default=100
    )
    parser.add_argument(
        '--result-directory',
        dest='result_dir',
        default='/tmp'
    )
    return parser


def main():
    args = get_parser().parse_known_args()[0]
    make_data_args = make_test_data.get_parser().parse_known_args()[0]
    conf = service.prepare_service(argv=['/', '--config-file',
                                         args.config_file])
    notifier = get_notifier(conf)
    send_batch = functools.partial(send_batch_notifier, notifier)
    result_dir = args.result_dir
    del args.config_file
    del args.result_dir

    resource_writes = generate_data(conf, send_batch, make_data_args,
                                    **args.__dict__)
    result_file = "{}/sample-by-resource-{}".format(result_dir,
                                                    random.getrandbits(32))
    with open(result_file, 'w') as f:
        f.write(json.dumps(resource_writes))
    return result_file


if __name__ == '__main__':
    main()
