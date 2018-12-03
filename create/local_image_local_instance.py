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
r"""LocalImageLocalInstance class.

Create class that is responsible for creating a local instance AVD with a
local image.
"""

from __future__ import print_function
import logging
import os
import subprocess
import sys

from acloud import errors
from acloud.create import base_avd_create
from acloud.create import create_common
from acloud.internal import constants
from acloud.internal.lib import utils
from acloud.public import report

logger = logging.getLogger(__name__)

_BOOT_COMPLETE = "VIRTUAL_DEVICE_BOOT_COMPLETED"
_CMD_LAUNCH_CVD_ARGS = (" --daemon --cpus %s --x_res %s --y_res %s --dpi %s "
                        "--memory_mb %s --blank_data_image_mb %s "
                        "--data_policy always_create "
                        "--system_image_dir %s "
                        "--vnc_server_port %s")
_CONFIRM_RELAUNCH = ("\nCuttlefish AVD is already running. \n"
                     "Enter 'y' to terminate current instance and launch a new "
                     "instance, enter anything else to exit out [y]: ")
_ENV_ANDROID_HOST_OUT = "ANDROID_HOST_OUT"


class LocalImageLocalInstance(base_avd_create.BaseAVDCreate):
    """Create class for a local image local instance AVD."""

    @utils.TimeExecute(function_description="Total time: ",
                       print_before_call=False, print_status=False)
    def _CreateAVD(self, avd_spec):
        """Create the AVD.

        Args:
            avd_spec: AVDSpec object that tells us what we're going to create.
        """
        self.PrintDisclaimer()
        local_image_path, launch_cvd_path = self.GetImageArtifactsPath(avd_spec)

        cmd = self.PrepareLaunchCVDCmd(launch_cvd_path,
                                       avd_spec.hw_property,
                                       local_image_path)
        try:
            self.CheckLaunchCVD(cmd, os.path.dirname(launch_cvd_path))
        except errors.LaunchCVDFail as launch_error:
            raise launch_error

        result_report = report.Report(constants.LOCAL_INS_NAME)
        result_report.SetStatus(report.Status.SUCCESS)
        result_report.AddData(key="devices",
                              value={"adb_port": constants.DEFAULT_ADB_PORT,
                                     constants.VNC_PORT: constants.DEFAULT_VNC_PORT})
        # Launch vnc client if we're auto-connecting.
        if avd_spec.autoconnect:
            utils.LaunchVNCFromReport(result_report, avd_spec)
        return result_report

    @staticmethod
    def GetImageArtifactsPath(avd_spec):
        """Get image artifacts path.

        This method will check if local image and launch_cvd are exist and
        return the tuple path where they are located respectively.
        For remote image, RemoteImageLocalInstance will override this method and
        return the artifacts path which is extracted and downloaded from remote.

        Args:
            avd_spec: AVDSpec object that tells us what we're going to create.

        Returns:
            Tuple of (local image file, launch_cvd package) paths.
        """
        try:
            # Check if local image is exist.
            create_common.VerifyLocalImageArtifactsExist(
                avd_spec.local_image_dir)

        # TODO(b/117306227): help user to build out images and host package if
        # anything needed is not found.
        except errors.GetLocalImageError as imgerror:
            logger.error(imgerror.message)
            raise imgerror

        # Check if launch_cvd is exist.
        launch_cvd_path = os.path.join(
            os.environ.get(_ENV_ANDROID_HOST_OUT), "bin", constants.CMD_LAUNCH_CVD)
        if not os.path.exists(launch_cvd_path):
            raise errors.GetCvdLocalHostPackageError(
                "No launch_cvd found. Please run \"m launch_cvd\" first")

        return avd_spec.local_image_dir, launch_cvd_path

    @staticmethod
    def PrepareLaunchCVDCmd(launch_cvd_path, hw_property, system_image_dir):
        """Prepare launch_cvd command.

        Create the launch_cvd commands with all the required args and add
        in the user groups to it if necessary.

        Args:
            launch_cvd_path: String of launch_cvd path.
            hw_property: dict object of hw property.
            system_image_dir: String of local images path.

        Returns:
            String, launch_cvd cmd.
        """
        launch_cvd_w_args = launch_cvd_path + _CMD_LAUNCH_CVD_ARGS % (
            hw_property["cpu"], hw_property["x_res"], hw_property["y_res"],
            hw_property["dpi"], hw_property["memory"], hw_property["disk"],
            system_image_dir, constants.DEFAULT_VNC_PORT)

        launch_cmd = utils.AddUserGroupsToCmd(launch_cvd_w_args,
                                              constants.LIST_CF_USER_GROUPS)
        logger.debug("launch_cvd cmd:\n %s", launch_cmd)
        return launch_cmd

    @staticmethod
    @utils.TimeExecute(function_description="Waiting for AVD(s) to boot up")
    def CheckLaunchCVD(cmd, host_pack_dir):
        """Execute launch_cvd command and wait for boot up completed.

        Args:
            cmd: String, launch_cvd command.
            host_pack_dir: String of host package directory.
        """
        # Cuttlefish support launch single AVD at one time currently.
        if utils.IsCommandRunning(constants.CMD_LAUNCH_CVD):
            logger.info("Cuttlefish AVD is already running.")
            if utils.GetUserAnswerYes(_CONFIRM_RELAUNCH):
                stop_cvd_cmd = os.path.join(host_pack_dir,
                                            constants.CMD_STOP_CVD)
                with open(os.devnull, "w") as dev_null:
                    subprocess.check_call(
                        utils.AddUserGroupsToCmd(
                            stop_cvd_cmd, constants.LIST_CF_USER_GROUPS),
                        stderr=dev_null, stdout=dev_null, shell=True)
            else:
                print("Exiting out")
                sys.exit()

        try:
            # Check the result of launch_cvd command.
            # An exit code of 0 is equivalent to VIRTUAL_DEVICE_BOOT_COMPLETED
            logger.debug(subprocess.check_output(cmd, shell=True,
                                                 stderr=subprocess.STDOUT))
        except subprocess.CalledProcessError as error:
            raise errors.LaunchCVDFail(
                "Can't launch cuttlefish AVD.%s. \nFor more detail: "
                "~/cuttlefish_runtime/launcher.log" % error.message)

    @staticmethod
    def PrintDisclaimer():
        """Print Disclaimer."""
        utils.PrintColorString(
            "(Disclaimer: Local cuttlefish instance is not a fully supported\n"
            "runtime configuration, fixing breakages is on a best effort SLO.)\n",
            utils.TextColors.WARNING)
