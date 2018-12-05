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
"""Tests for delete."""

import unittest
import mock

from acloud.delete import delete


# pylint: disable=invalid-name,protected-access,unused-argument,no-member
class DeleteTest(unittest.TestCase):
    """Test delete functions."""

    @mock.patch("os.path.exists", return_value=True)
    @mock.patch("subprocess.check_output")
    def testGetStopcvd(self, mock_subprocess, mock_path_exist):
        """Test _GetStopCvd."""
        mock_subprocess.side_effect = ["fack_id",
                                       "/tmp/bin/launch_cvd --daemon --cpus 2"]
        expected_value = "/tmp/bin/stop_cvd"
        self.assertEqual(expected_value, delete._GetStopCvd())

    @mock.patch.object(delete, "_GetStopCvd", return_value="")
    @mock.patch("subprocess.check_call")
    def testDeleteLocalInstance(self, mock_subprocess, mock_get_stopcvd):
        """Test DeleteLocalInstance."""
        mock_subprocess.return_value = True
        delete_report = delete.DeleteLocalInstance()
        self.assertEquals(delete_report.data, {
            "deleted": [
                {
                    "type": "instance",
                    "name": "local-instance",
                },
            ],
        })
        self.assertEquals(delete_report.command, "delete")
        self.assertEquals(delete_report.status, "SUCCESS")


if __name__ == "__main__":
    unittest.main()
