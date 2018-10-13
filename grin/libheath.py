#!/usr/bin/python3

import os
import sys
import re
import subprocess


LOGFILE = "/server/grin.log"
BodySyncRE = "BodySync { current_height: (\d+), highest_height: (\d+) }"
MostWorkRE = "monitor_peers: on .*, (\d+) connected \((\d+) most_work\)"

# Itr for tailing a log file
class PopenItr:
    def __init__(self, command):
        self.cmd = command
        self.proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=False)

    def __iter__(self):
        return self

    def __next__(self):
        line = self.proc.stdout.readline().decode('utf-8')
        if line == '' and self.proc.poll() is not None:
            raise StopIteration
        return line

def current_height_is_highest_height():
    global LOGFILE
    log_itr = PopenItr(["tail", "-f", LOGFILE])
    for msg in log_itr:
        # Parse this message and check if our current_height == highest_height
        # BodySyncRE
        m = re.search(BodySyncRE, msg)
        if m:
            current_height = m.group(1)
            highest_height = m.group(2)
            print("current_height: {}, highest_height: {}".format(current_height, highest_height))
            return current_height == highest_height

def has_peers_with_most_work():
    global LOGFILE
    log_itr = PopenItr(["tail", "-f", LOGFILE])
    for msg in log_itr:
        # Parse this message and check if we have any peers with most_work
        # MostWorkRE
        m = re.search(MostWorkRE, msg)
        if m:
            num_connected = m.group(1)
            num_mostwork = m.group(2)
            print("num_connected: {}, num_mostwork: {}".format(num_connected, num_mostwork))
            return int(num_mostwork) >= 1


def is_ready():
    is_highest = current_height_is_highest_height()
    return is_highest

def is_healthy():
    has_good_peers = has_peers_with_most_work()
    return has_good_peers


if __name__ == '__main__':
  # Could be a request for ready, or health
  if sys.argv[1] == "ready":
      sys.exit(is_ready())
  else:
      sys.exit(is_healthy())
