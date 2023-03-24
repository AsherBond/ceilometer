#
# Copyright 2022 Red Hat, Inc
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

"""Simple wrapper for oslo_cache."""
import uuid

from oslo_cache import core as cache
from oslo_cache import exception
from oslo_log import log
from oslo_utils.secretutils import md5

# Default cache expiration period
CACHE_DURATION = 86400

NAME_ENCODED = __name__.encode('utf-8')
CACHE_NAMESPACE = uuid.UUID(
    bytes=md5(NAME_ENCODED, usedforsecurity=False).digest()
)

LOG = log.getLogger(__name__)


class CacheClient(object):
    def __init__(self, region):
        self.region = region

    def get(self, key):
        value = self.region.get(key)
        if value == cache.NO_VALUE:
            return None
        return value

    def set(self, key, value):
        return self.region.set(key, value)

    def delete(self, key):
        return self.region.delete(key)


def get_client(conf):
    cache.configure(conf)
    if 'cache' in conf.keys() and conf.cache.enabled:
        region = get_cache_region(conf)
        if region:
            return CacheClient(region)


def get_cache_region(conf):
    # Set expiration time to default CACHE_DURATION if missing in conf
    if not conf.cache.expiration_time:
        conf.cache.expiration_time = CACHE_DURATION

    try:
        region = cache.create_region()
        cache.configure_cache_region(conf, region)
        cache.key_mangler = cache_key_mangler
        return region
    except exception.ConfigurationError as e:
        LOG.error("failed to configure oslo_cache. %s", str(e))
        LOG.warning("using keystone to identify names from polled samples")


def cache_key_mangler(key):
    """Construct an opaque cache key."""

    return uuid.uuid5(CACHE_NAMESPACE, key).hex