# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2010 Openstack, LLC.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
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

"""
Simple Scheduler
"""

from nova import db
from nova import flags
from nova.scheduler import driver
from nova.scheduler import chance

FLAGS = flags.FLAGS
flags.DEFINE_integer("max_instances", 16,
                     "maximum number of instances to allow per host")
flags.DEFINE_integer("max_volumes", 100,
                     "maximum number of volumes to allow per host")
flags.DEFINE_integer("max_networks", 1000,
                     "maximum number of networks to allow per host")

class SimpleScheduler(chance.ChanceScheduler):
    """
    Implements Naive Scheduler that tries to find least loaded host
    """

    def schedule_run_instance(self, context, _instance_id, *_args, **_kwargs):
        """
        Picks a host that is up and has the fewest running instances
        """

        results = db.service_get_all_compute_sorted(context)
        for result in results:
            (service, instance_count) = result
            if instance_count >= FLAGS.max_instances:
                raise driver.NoValidHost("All hosts have too many instances")
            if self.service_is_up(service):
                return service['host']
        raise driver.NoValidHost("No hosts found")

    def schedule_create_volume(self, context, _volume_id, *_args, **_kwargs):
        """
        Picks a host that is up and has the fewest volumes
        """

        results = db.service_get_all_volume_sorted(context)
        for result in results:
            (service, instance_count) = result
            if instance_count >= FLAGS.max_volumes:
                raise driver.NoValidHost("All hosts have too many volumes")
            if self.service_is_up(service):
                return service['host']
        raise driver.NoValidHost("No hosts found")

    def schedule_set_network_host(self, context, _network_id, *_args, **_kwargs):
        """
        Picks a host that is up and has the fewest networks
        """

        results = db.service_get_all_network_sorted(context)
        for result in results:
            (service, instance_count) = result
            if instance_count >= FLAGS.max_networks:
                raise driver.NoValidHost("All hosts have too many networks")
            if self.service_is_up(service):
                return service['host']
        raise driver.NoValidHost("No hosts found")
