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
"""Common code for working with volumes
"""

from ceilometer.polling import plugin_base
from ceilometer import sample


class _Base(plugin_base.PollsterBase):
    def extract_metadata(self, obj):
        metadata = dict((k, getattr(obj, k)) for k in self.FIELDS)
        if getattr(obj, "volume_image_metadata", None):
            metadata["image_id"] = obj.volume_image_metadata.get("image_id")
        else:
            metadata["image_id"] = None
        if getattr(obj, "attachments", None):
            metadata["instance_id"] = obj.attachments[0]["server_id"]
        else:
            metadata["instance_id"] = None
        return metadata


class VolumeSizePollster(_Base):
    @property
    def default_discovery(self):
        return 'volumes'

    FIELDS = ['name',
              'status',
              'volume_type',
              'volume_type_id',
              'availability_zone',
              'os-vol-host-attr:host',
              'migration_status',
              'attachments',
              'snapshot_id',
              'source_volid']

    def get_samples(self, manager, cache, resources):
        for volume in resources:
            yield sample.Sample(
                name='volume.size',
                type=sample.TYPE_GAUGE,
                unit='GB',
                volume=volume.size,
                user_id=volume.user_id,
                project_id=getattr(volume,
                                   'os-vol-tenant-attr:tenant_id'),
                resource_id=volume.id,
                resource_metadata=self.extract_metadata(volume),
            )


class VolumeSnapshotSize(_Base):
    @property
    def default_discovery(self):
        return 'volume_snapshots'

    FIELDS = ['name',
              'volume_id',
              'status',
              'description',
              'metadata',
              'os-extended-snapshot-attributes:progress',
              ]

    def get_samples(self, manager, cache, resources):
        for snapshot in resources:
            yield sample.Sample(
                name='volume.snapshot.size',
                type=sample.TYPE_GAUGE,
                unit='GB',
                volume=snapshot.size,
                user_id=snapshot.user_id,
                project_id=getattr(
                    snapshot,
                    'os-extended-snapshot-attributes:project_id'),
                resource_id=snapshot.id,
                resource_metadata=self.extract_metadata(snapshot),
            )


class VolumeBackupSize(_Base):
    @property
    def default_discovery(self):
        return 'volume_backups'

    FIELDS = ['name',
              'is_incremental',
              'object_count',
              'container',
              'volume_id',
              'status',
              'description']

    def get_samples(self, manager, cache, resources):
        for backup in resources:
            yield sample.Sample(
                name='volume.backup.size',
                type=sample.TYPE_GAUGE,
                unit='GB',
                volume=backup.size,
                user_id=backup.user_id,
                project_id=getattr(
                    backup, 'os-backup-project-attr:project_id', None),
                resource_id=backup.id,
                resource_metadata=self.extract_metadata(backup),
            )
