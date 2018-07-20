#!/usr/bin/python

# Copyright 2018 Blade M. Doyle
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


#
# Watches both the pool and grin logs and tries to identify cases of denial of service,
#  abuse, or badly misbehaving workers.  Add them to mysql banned_workers table.
#  Maybe include a code for the reason so bans can be lifted after appropriate time?
#
#  Examples:	Too many rapid connect/disconnects without shares submitted
#		Idle disconnect too long too many times
#		Submitting too many bad shares
#		Etc....

import sys
import subprocess
import re
import glob

xxx XXX THIS IS NOT WRITTEN YET
