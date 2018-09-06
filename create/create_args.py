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
r"""Create args.

Defines the create arg parser that holds create specific args.
"""

import os

from acloud import errors
from acloud.internal import constants


CMD_CREATE = "create"


# TODO: Add this into main create args once create_cf/gf is deprecated.
def AddCommonCreateArgs(parser):
    """Adds arguments common to create parsers.

    Args:
        parser: ArgumentParser object, used to parse flags.
    """
    parser.add_argument(
        "--num",
        type=int,
        dest="num",
        required=False,
        default=1,
        help="Number of instances to create.")
    parser.add_argument(
        "--serial_log_file",
        type=str,
        dest="serial_log_file",
        required=False,
        help="Path to a *tar.gz file where serial logs will be saved "
        "when a device fails on boot.")
    parser.add_argument(
        "--logcat_file",
        type=str,
        dest="logcat_file",
        required=False,
        help="Path to a *tar.gz file where logcat logs will be saved "
        "when a device fails on boot.")
    parser.add_argument(
        "--autoconnect",
        action="store_true",
        dest="autoconnect",
        required=False,
        help=
        "For each instance created, we will automatically creates both 2 ssh"
        " tunnels forwarding both adb & vnc. Then add the device to adb.")
    parser.add_argument(
        "--no-autoconnect",
        action="store_false",
        dest="autoconnect",
        required=False)
    parser.set_defaults(autoconnect=True)


def GetCreateArgParser(subparser):
    """Return the create arg parser.

    Args:
       subparser: argparse.ArgumentParser that is attached to main acloud cmd.

    Returns:
        argparse.ArgumentParser with create options defined.
    """
    create_parser = subparser.add_parser(CMD_CREATE)
    create_parser.required = False
    create_parser.set_defaults(which=CMD_CREATE)
    create_parser.add_argument(
        "--local_instance",
        action="store_true",
        dest="local_instance",
        required=False,
        help="Create a local instance of the AVD.")
    create_parser.add_argument(
        "--avd_type",
        type=str,
        dest="avd_type",
        default=constants.TYPE_CF,
        choices=[constants.TYPE_GCE, constants.TYPE_CF, constants.TYPE_GF],
        help="Android Virtual Device type (default %s)." % constants.TYPE_CF)
    create_parser.add_argument(
        "--flavor",
        type=str,
        dest="flavor",
        default=constants.FLAVOR_PHONE,
        choices=constants.ALL_FLAVORS,
        help="The device flavor of the AVD (default %s)." % constants.FLAVOR_PHONE)
    create_parser.add_argument(
        "--build_target",
        type=str,
        dest="build_target",
        help="Android build target, e.g. aosp_cf_x86_phone-userdebug, "
        "or short names: phone, tablet, or tablet_mobile.")
    create_parser.add_argument(
        "--branch",
        type=str,
        dest="branch",
        help="Android branch, e.g. mnc-dev or git_mnc-dev")
    create_parser.add_argument(
        "--build_id",
        type=str,
        dest="build_id",
        help="Android build id, e.g. 2145099, P2804227")
    create_parser.add_argument(
        "--spec",
        type=str,
        dest="spec",
        required=False,
        help="The name of a pre-configured device spec that we are "
        "going to use. Choose from: %s" % ", ".join(constants.SPEC_NAMES))
    create_parser.add_argument(
        "--gce_image",
        type=str,
        dest="gce_image",
        required=False,
        help="Name of an existing compute engine image to reuse.")
    create_parser.add_argument(
        "--local_disk_image",
        type=str,
        dest="local_disk_image",
        required=False,
        help="Path to a local disk image to use, "
        "e.g /tmp/avd-system.tar.gz")
    create_parser.add_argument(
        "--local_image",
        type=str,
        dest="local_image",
        nargs="?",
        default="",
        required=False,
        help="Path to a local disk image folder to use, "
        "e.g /tmp/acloud/out/target/product/vsoc_x86_64")
    create_parser.add_argument(
        "--no_cleanup",
        dest="no_cleanup",
        default=False,
        action="store_true",
        help="Do not clean up temporary disk image and compute engine image. "
        "For debugging purposes.")

    AddCommonCreateArgs(create_parser)
    return create_parser


def VerifyArgs(args):
    """Verify args.

    Args:
        args: Namespace object from argparse.parse_args.

    Raises:
        errors.CreateError: Path doesn't exist.
    """
    if args.local_image and not os.path.exists(args.local_image):
        raise errors.CheckPathError(
            "Specified path doesn't exist: %s" % args.local_image)