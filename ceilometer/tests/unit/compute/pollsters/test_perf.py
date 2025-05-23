# Copyright 2016 Intel
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from ceilometer.compute.pollsters import instance_stats
from ceilometer.compute.virt import inspector as virt_inspector
from ceilometer.polling import manager
from ceilometer.tests.unit.compute.pollsters import base


class TestPerfPollster(base.TestPollsterBase):

    def test_get_samples(self):
        self._mock_inspect_instance(
            virt_inspector.InstanceStats(cpu_cycles=7259361,
                                         instructions=8815623,
                                         cache_references=74184,
                                         cache_misses=16737)
        )

        mgr = manager.AgentManager(0, self.CONF)
        cache = {}

        def _check_perf_events_cpu_cycles(expected_usage):
            pollster = instance_stats.PerfCPUCyclesPollster(self.CONF)

            samples = list(pollster.get_samples(mgr, cache, [self.instance]))
            self.assertEqual(1, len(samples))
            self.assertEqual({'perf.cpu.cycles'},
                             {s.name for s in samples})
            self.assertEqual(expected_usage, samples[0].volume)

        def _check_perf_events_instructions(expected_usage):
            pollster = instance_stats.PerfInstructionsPollster(self.CONF)
            samples = list(pollster.get_samples(mgr, cache, [self.instance]))
            self.assertEqual(1, len(samples))
            self.assertEqual({'perf.instructions'},
                             {s.name for s in samples})
            self.assertEqual(expected_usage, samples[0].volume)

        def _check_perf_events_cache_references(expected_usage):
            pollster = instance_stats.PerfCacheReferencesPollster(
                self.CONF)

            samples = list(pollster.get_samples(mgr, cache, [self.instance]))
            self.assertEqual(1, len(samples))
            self.assertEqual({'perf.cache.references'},
                             {s.name for s in samples})
            self.assertEqual(expected_usage, samples[0].volume)

        def _check_perf_events_cache_misses(expected_usage):
            pollster = instance_stats.PerfCacheMissesPollster(self.CONF)

            samples = list(pollster.get_samples(mgr, cache, [self.instance]))
            self.assertEqual(1, len(samples))
            self.assertEqual({'perf.cache.misses'},
                             {s.name for s in samples})
            self.assertEqual(expected_usage, samples[0].volume)

        _check_perf_events_cpu_cycles(7259361)
        _check_perf_events_instructions(8815623)
        _check_perf_events_cache_references(74184)
        _check_perf_events_cache_misses(16737)

    def test_get_samples_with_empty_stats(self):
        self._mock_inspect_instance(virt_inspector.NoDataException())
        mgr = manager.AgentManager(0, self.CONF)
        pollster = instance_stats.PerfCPUCyclesPollster(self.CONF)

        def all_samples():
            return list(pollster.get_samples(mgr, {}, [self.instance]))
