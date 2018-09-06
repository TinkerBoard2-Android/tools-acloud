#!/usr/bin/env python
#
# Copyright 2018 - The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""BaseAVDCreate class.

Parent class that will hold common logic for AVD creation use cases.
"""

from __future__ import print_function


class BaseAVDCreate(object):
    """Base class for all AVD intance creation classes."""

    # pylint: disable=no-self-use
    def Create(self, avd_spec):
        """Create the AVD.

        Args:
            avd_spec: AVDSpec object that tells us what we're going to create.
        """
        raise NotImplementedError