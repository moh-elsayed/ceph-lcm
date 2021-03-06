# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Playbook plugin for Add monitor to the cluster."""


from decapod_common import log
from decapod_common import networkutils
from decapod_common import pathutils
from decapod_common import playbook_plugin
from decapod_common import playbook_plugin_hints
from decapod_common.models import cluster_data
from decapod_common.models import kv
from decapod_common.models import server

from . import exceptions


DESCRIPTION = "Add monitor to the cluster"
"""Plugin description."""

HINTS_SCHEMA = {
    "ceph_version_verify": {
        "description": "Verify Ceph version consistency on install",
        "typename": "boolean",
        "type": "boolean",
        "default_value": True
    }
}
"""Schema for playbook hints."""

LOG = log.getLogger(__name__)
"""Logger."""


def get_monitor_secret(secret_id):
    secret = kv.KV.find("monitor_secret", [secret_id])
    if secret:
        return secret[0]


class AddMon(playbook_plugin.CephAnsibleNewWithVerification):

    NAME = "Add monitor to the cluster"
    DESCRIPTION = DESCRIPTION
    HINTS = playbook_plugin_hints.Hints(HINTS_SCHEMA)

    def on_pre_execute(self, task):
        super().on_pre_execute(["mons"], task)

        playbook_config = self.get_playbook_configuration(task)
        config = playbook_config.configuration["inventory"]
        cluster = playbook_config.cluster

        data = cluster_data.ClusterData.find_one(cluster.model_id)
        hostvars = config.get("_meta", {}).get("hostvars", {})
        for hostname, values in hostvars.items():
            data.update_host_vars(hostname, values)
        data.save()

    def get_dynamic_inventory(self):
        if not self.playbook_config:
            raise exceptions.UnknownPlaybookConfiguration()

        configuration = self.playbook_config.configuration
        inventory = configuration["inventory"]
        secret = get_monitor_secret(configuration["global_vars"]["fsid"])
        if not secret:
            raise exceptions.SecretWasNotFound(
                configuration["global_vars"]["fsid"])

        all_hosts = set()
        for name, group_vars in inventory.items():
            if name == "_meta":
                continue
            all_hosts.update(group_vars)

        for hostname in all_hosts:
            dct = inventory["_meta"]["hostvars"].setdefault(hostname, {})
            dct["monitor_secret"] = secret.value

        return inventory

    def make_inventory(self, cluster, data, servers, hints):
        groups = self.get_inventory_groups(cluster, servers, hints)
        inventory = {"_meta": {"hostvars": {}}}
        all_servers = server.ServerModel.cluster_servers(cluster.model_id)

        for name, group_servers in groups.items():
            for srv in group_servers:
                inventory.setdefault(name, []).append(srv.ip)

                hostvars = inventory["_meta"]["hostvars"].setdefault(
                    srv.ip, {})
                hostvars.update(data.get_host_vars(srv.ip))

                if "ansible_user" not in hostvars:
                    hostvars["ansible_user"] = srv.username
                if "monitor_interface" not in hostvars:
                    if "monitor_address" not in hostvars:
                        hostvars["monitor_address"] = \
                            networkutils.get_public_network_ip(
                                srv, all_servers)

        return inventory

    def get_inventory_groups(self, cluster, servers, hints):
        cluster_servers = server.ServerModel.cluster_servers(cluster.model_id)
        cluster_servers = {item._id: item for item in cluster_servers}

        old_mons = [
            cluster_servers[item["server_id"]]
            for item in cluster.configuration.state if item["role"] == "mons"
        ]
        mons = {srv.model_id: srv for srv in old_mons}
        mons.update((srv.model_id, srv) for srv in servers)

        return {
            "oldmons": old_mons,
            "mons": sorted(mons.values(), key=lambda srv: srv.ip),
            "already_deployed": list(cluster_servers.values())
        }

    def prepare_plugin(self):
        resource_path = pathutils.resource(
            "decapod_plugin_playbook_add_mon", "roles")
        resource_path.symlink_to(
            str(playbook_plugin.PATH_CEPH_ANSIBLE.joinpath("roles")))
