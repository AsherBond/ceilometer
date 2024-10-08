#
# Copyright 2024 Juan Larriba
# Copyright 2024 Red Hat, Inc
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

import prometheus_client as prom

CEILOMETER_REGISTRY = prom.CollectorRegistry()


def export(prometheus_iface, prometheus_port):
    prom.start_http_server(port=int(prometheus_port),
                           addr=prometheus_iface,
                           registry=CEILOMETER_REGISTRY)


def collect_metrics(samples):
    for sample in samples:
        name = "ceilometer_" + sample['counter_name'].replace('.', '_')
        type = sample['counter_type']
        value = sample['counter_volume']
        labels = _gen_labels(sample)

        metric = CEILOMETER_REGISTRY._names_to_collectors.get(name, None)
        if metric is None:
            if type == "cumulative":
                metric = prom.Counter(name=name, documentation="",
                                      labelnames=labels['keys'],
                                      registry=CEILOMETER_REGISTRY)
                metric.labels(*labels['values']).inc(value)
            if type == "gauge" or type == "delta":
                metric = prom.Gauge(name=name, documentation="",
                                    labelnames=labels['keys'],
                                    registry=CEILOMETER_REGISTRY)
                metric.labels(*labels['values']).set(value)
        else:
            if type == 'cumulative':
                metric.labels(*labels['values']).inc(value)
            elif type == 'gauge' or type == 'delta':
                metric.labels(*labels['values']).set(value)


def _gen_labels(sample):
    labels = dict(keys=[], values=[])
    cNameShards = sample['counter_name'].split(".")
    ctype = ''

    plugin = cNameShards[0]
    pluginVal = sample['resource_id']
    if len(cNameShards) > 2:
        pluginVal = cNameShards[2]

    if len(cNameShards) > 1:
        ctype = cNameShards[1]
    else:
        ctype = cNameShards[0]

    labels['keys'].append(plugin)
    labels['values'].append(pluginVal)

    labels['keys'].append("publisher")
    labels['values'].append("ceilometer")

    labels['keys'].append("type")
    labels['values'].append(ctype)

    index = 3
    if (sample.get('counter_name', '') != '' and
            sample.get('counter_name') is not None):
        labels['keys'].append("counter")
        labels['values'].append(sample['counter_name'])
        index += 1

    if (sample.get('project_id', '') != '' and
            sample.get('project_id') is not None):
        labels['keys'].append("project")
        labels['values'].append(sample['project_id'])
        index += 1

    if (sample.get('project_name', '') != '' and
            sample.get('project_name') is not None):
        labels['keys'].append("project_name")
        labels['values'].append(sample['project_name'])
        index += 1

    if (sample.get('user_id', '') != '' and
            sample.get('user_id') is not None):
        labels['keys'].append("user")
        labels['values'].append(sample['user_id'])
        index += 1

    if (sample.get('user_name', '') != '' and
            sample.get('user_name') is not None):
        labels['keys'].append("user_name")
        labels['values'].append(sample['user_name'])
        index += 1

    if (sample.get('counter_unit', '') != '' and
            sample.get('counter_unit') is not None):
        labels['keys'].append("unit")
        labels['values'].append(sample['counter_unit'])
        index += 1

    if (sample.get('resource_id', '') != '' and
            sample.get('resource_id') is not None):
        labels['keys'].append("resource")
        labels['values'].append(sample['resource_id'])
        index += 1

    if (sample.get('resource_metadata', '') != '' and
            sample.get('resource_metadata') is not None):

        if (sample['resource_metadata'].get('host', '') != ''):
            labels['keys'].append("vm_instance")
            labels['values'].append(sample['resource_metadata']['host'])
            index += 1

        if (sample['resource_metadata'].get('display_name', '') != ''):
            labels['keys'].append("resource_name")
            labels['values'].append(sample['resource_metadata']
                                    ['display_name'])

        if (sample['resource_metadata'].get('name', '') != ''):
            labels['keys'].append("resource_name")
            if (labels['values'][index] if index < len(labels['values'])
                    else '' != ''):
                labels['values'].append(labels['values'][index] + ":" +
                                        sample['resource_metadata']['name'])
            else:
                labels['values'].append(sample['resource_metadata']['name'])

    return labels
