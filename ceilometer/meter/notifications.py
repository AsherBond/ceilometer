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
import glob
import itertools
import os
import re

from ceilometer import cache_utils
from oslo_config import cfg
from oslo_log import log
from stevedore import extension

from ceilometer import declarative
from ceilometer.i18n import _
from ceilometer.pipeline import sample as endpoint
from ceilometer import sample as sample_util

OPTS = [
    cfg.MultiStrOpt('meter_definitions_dirs',
                    default=["/etc/ceilometer/meters.d",
                             os.path.abspath(
                                 os.path.join(
                                     os.path.split(
                                         os.path.dirname(__file__))[0],
                                     "data", "meters.d"))],
                    help="List directory to find files of "
                         "defining meter notifications."
                    ),
]

LOG = log.getLogger(__name__)


class MeterDefinition:

    SAMPLE_ATTRIBUTES = ["name", "type", "volume", "unit", "timestamp",
                         "user_id", "project_id", "resource_id"]

    REQUIRED_FIELDS = ['name', 'type', 'event_type', 'unit', 'volume',
                       'resource_id']

    def __init__(self, definition_cfg, conf, plugin_manager):
        self.conf = conf
        self.cfg = definition_cfg
        self._cache = cache_utils.get_client(self.conf)
        missing = [field for field in self.REQUIRED_FIELDS
                   if not self.cfg.get(field)]
        if missing:
            raise declarative.MeterDefinitionException(
                _("Required fields %s not specified") % missing, self.cfg)

        self._event_type = self.cfg.get('event_type')
        if isinstance(self._event_type, str):
            self._event_type = [self._event_type]
        self._event_type = [re.compile(etype) for etype in self._event_type]

        if ('type' not in self.cfg.get('lookup', []) and
                self.cfg['type'] not in sample_util.TYPES):
            raise declarative.MeterDefinitionException(
                _("Invalid type %s specified") % self.cfg['type'], self.cfg)

        self._fallback_user_id = declarative.Definition(
            'user_id', "ctxt.user_id|ctxt.user", plugin_manager)
        self._fallback_project_id = declarative.Definition(
            'project_id', "ctxt.project_id|ctxt.tenant_id", plugin_manager)
        self._attributes = {}
        self._metadata_attributes = {}
        self._user_meta = None

        self._name_discovery = self.conf.polling.identity_name_discovery

        for name in self.SAMPLE_ATTRIBUTES:
            attr_cfg = self.cfg.get(name)
            if attr_cfg:
                self._attributes[name] = declarative.Definition(
                    name, attr_cfg, plugin_manager)
        metadata = self.cfg.get('metadata', {})
        for name in metadata:
            self._metadata_attributes[name] = declarative.Definition(
                name, metadata[name], plugin_manager)
        user_meta = self.cfg.get('user_metadata')
        if user_meta:
            self._user_meta = declarative.Definition(None, user_meta,
                                                     plugin_manager)

        # List of fields we expected when multiple meter are in the payload
        self.lookup = self.cfg.get('lookup')
        if isinstance(self.lookup, str):
            self.lookup = [self.lookup]

    def match_type(self, meter_name):
        for t in self._event_type:
            if t.match(meter_name):
                return True

    def to_samples(self, message, all_values=False):
        # Sample defaults
        sample = {
            'name': self.cfg["name"], 'type': self.cfg["type"],
            'unit': self.cfg["unit"], 'volume': None, 'timestamp': None,
            'user_id': self._fallback_user_id.parse(message),
            'project_id': self._fallback_project_id.parse(message),
            'resource_id': None, 'message': message, 'metadata': {},
        }
        for name, parser in self._metadata_attributes.items():
            value = parser.parse(message)
            if value:
                sample['metadata'][name] = value

        if self._user_meta:
            meta = self._user_meta.parse(message)
            if meta:
                sample_util.add_reserved_user_metadata(
                    self.conf, meta, sample['metadata'])

        # NOTE(sileht): We expect multiple samples in the payload
        # so put each attribute into a list
        if self.lookup:
            for name in sample:
                sample[name] = [sample[name]]

        for name in self.SAMPLE_ATTRIBUTES:
            parser = self._attributes.get(name)
            if parser is not None:
                value = parser.parse(message, bool(self.lookup))
                # NOTE(sileht): If we expect multiple samples
                # some attributes are overridden even we don't get any
                # result. Also note in this case value is always a list
                if ((not self.lookup and value is not None) or
                        (self.lookup and ((name in self.lookup + ["name"])
                                          or value))):
                    sample[name] = value

        if self.lookup:
            nb_samples = len(sample['name'])
            # skip if no meters in payload
            if nb_samples <= 0:
                return

            attributes = self.SAMPLE_ATTRIBUTES + ["message", "metadata"]

            samples_values = []
            for name in attributes:
                values = sample.get(name)
                nb_values = len(values)
                if nb_values == nb_samples:
                    samples_values.append(values)
                elif nb_values == 1 and name not in self.lookup:
                    samples_values.append(itertools.cycle(values))
                else:
                    nb = (0 if nb_values == 1 and values[0] is None
                          else nb_values)
                    LOG.warning('Only %(nb)d fetched meters contain '
                                '"%(name)s" field instead of %(total)d.' %
                                dict(name=name, nb=nb,
                                     total=nb_samples))
                    return

            # NOTE(sileht): Transform the sample with multiple values per
            # attribute into multiple samples with one value per attribute.
            for values in zip(*samples_values):
                sample = {attributes[idx]: value
                          for idx, value in enumerate(values)}

                if self._name_discovery and self._cache:
                    # populate user_name and project_name fields in the sample
                    # created from notifications
                    if sample['user_id']:
                        sample['user_name'] = \
                            self._cache.resolve_uuid_from_cache(
                                'users', sample['user_id'])
                    if sample['project_id']:
                        sample['project_name'] = \
                            self._cache.resolve_uuid_from_cache(
                                'projects', sample['project_id'])
                yield sample
        else:
            yield sample


class ProcessMeterNotifications(endpoint.SampleEndpoint):

    event_types = []

    def __init__(self, conf, publisher):
        super().__init__(conf, publisher)
        self.definitions = self._load_definitions()

    def _load_definitions(self):
        plugin_manager = extension.ExtensionManager(
            namespace='ceilometer.event.trait_plugin')
        definitions = {}
        mfs = []
        for dir in self.conf.meter.meter_definitions_dirs:
            for filepath in sorted(glob.glob(os.path.join(dir, "*.yaml"))):
                if filepath is not None:
                    mfs.append(filepath)
        for mf in mfs:
            meters_cfg = declarative.load_definitions(
                self.conf, {}, mf)

            for meter_cfg in reversed(meters_cfg['metric']):
                if meter_cfg.get('name') in definitions:
                    # skip duplicate meters
                    LOG.warning("Skipping duplicate meter definition %s"
                                % meter_cfg)
                    continue
                try:
                    md = MeterDefinition(meter_cfg, self.conf, plugin_manager)
                except declarative.DefinitionException as e:
                    errmsg = "Error loading meter definition: %s"
                    LOG.error(errmsg, str(e))
                else:
                    definitions[meter_cfg['name']] = md
        return definitions.values()

    def build_sample(self, notification):
        for d in self.definitions:
            if d.match_type(notification['event_type']):
                for s in d.to_samples(notification):
                    yield sample_util.Sample.from_notification(**s)
