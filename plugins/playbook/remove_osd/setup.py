#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
"""Setup script for Remove OSD plugin."""


import setuptools


NEXT_VERSION = open("NEXT_VERSION").read().strip()


def next_version(version):
    if version.distance == 0:
        return NEXT_VERSION

    return "{next_version}.dev{distance}-{tag}".format(
        next_version=NEXT_VERSION,
        distance=version.distance,
        tag=version.node)


setuptools.setup(
    name="decapod-plugin-playbook-remove-osd",
    description="Remove OSD plugin for Decapod",
    author="Sergey Arkhipov",
    author_email="sarkhipov@mirantis.com",
    url="https://github.com/Mirantis/ceph-lcm",
    packages=setuptools.find_packages(),
    entry_points={
        "decapod.playbooks": [
            "remove_osd = decapod_plugin_playbook_remove_osd.plugin:RemoveOSD"
        ]
    },
    python_requires=">= 3.4",
    include_package_data=True,
    package_data={
        "decapod_plugin_playbook_remove_osd": [
            "config.yaml",
            "playbook.yaml"
        ]
    },
    install_requires=[
        "decapod_common>=0.2,<0.3"
    ],
    setup_requires=["setuptools_scm"],
    use_scm_version={
        "version_scheme": next_version,
        "local_scheme": "dirty-tag",
        "root": "../../..",
        "relative_to": __file__
    },
    zip_safe=False
)
