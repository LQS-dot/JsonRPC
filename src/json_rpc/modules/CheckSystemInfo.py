#!/usr/bin/python3

import os
import re, json
from sh import cat, systemctl
from pathlib import Path
from loguru import logger


class System:
    """
    this is the system related module
    params: action
    """

    RUNING_STATUS = {
        "active": 1,
        "failed": 0,
        "activating": 2,
    }

    def __init__(self, **action: dict[str, str]):
        self.action = action

    @logger.catch
    def check_system(self):
        cpufile = "/proc/cpuinfo"
        memfile = "/proc/meminfo"
        disk = 'fdisk -l | grep Disk |  grep -E "/dev/[v|h|s]d"'

        # cpu info
        cpu_count = len(re.findall(r"model\s*name\s+:(.*)", Path(cpufile).read_text()))
        cpu_name = re.findall(r"model\s*name\s+:(.*)", Path(cpufile).read_text())[0]
        cpu_hz = "%.1f" % (
            int(
                "%.f"
                % float(re.findall(r"cpu\s*MHz\s+:(.*)", Path(cpufile).read_text())[0])
            )
            / 1024
        )
        # mem info
        mem_total = "%.f" % float(
            int(re.findall(r"MemTotal:\s+(\d+).*", Path(memfile).read_text())[0])
            / 1024
            / 1024
        )
        mem_count = (
            os.popen('dmidecode | grep -E "Memory Device" | wc -l').read().strip()
        )
        mem_type = (
            os.popen(
                "dmidecode -t memory | grep -E Type: | grep -v Correction | awk -F': ' '{print $2}'"
            )
            .read()
            .strip()
        )
        # disk
        disk_inter = (
            os.popen(
                "lshw -json  -c  disk | jq -r 'select(.id == \"disk\") | .handle' | head -n1"
            )
            .read()
            .strip()
        )
        disk_cap = os.popen(
            "fdisk -l |  grep -E \"Disk.*?/dev/[h|s|v]d\" | awk -F', ' '{print $2}'"
        ).read()
        disk_cap = "%.1f" % float(
            int(re.findall("(\d+)", disk_cap)[0]) / 1024 / 1024 / 1024 / 1024
        )
        # run time
        run_time = (
            os.popen(
                "mysql -uroot -p`cat /etc/juminfo.conf` -e \"select runTime ,timestampdiff(HOUR,runTime,currentTime) as RunningHours from SMC.t_cmp_server\G;\" | tail -1 | awk -F': ' '{print $2}'"
            )
            .read()
            .strip()
        )
        return json.dumps(
            {
                "cpu_name": cpu_name,
                "cpu_count": cpu_count,
                "cpu_hz": cpu_hz,
                "mem_total": mem_total,
                "mem_count": mem_count,
                "mem_type": mem_type,
                "disk_inter": disk_inter,
                "disk_cap": disk_cap,
                "run_time": run_time,
            }
        )

    @classmethod
    @logger.catch
    def check_units(cls):
        file_store = systemctl("is-active", "smcfilestore", _ok_code=[0, 3]).strip()
        elasticsearch = systemctl("is-active", "elasticsearch", _ok_code=[0, 3]).strip()
        mariadb = systemctl("is-active", "mariadb", _ok_code=[0, 3]).strip()
        smcamq = systemctl("is-active", "smcamq", _ok_code=[0, 3]).strip()
        smcmonitor = systemctl("is-active", "smcmonitor", _ok_code=[0, 3]).strip()

        return json.dumps(
            {
                "file_store": cls.RUNING_STATUS[file_store],
                "elasticsearch": cls.RUNING_STATUS[elasticsearch],
                "mariadb": cls.RUNING_STATUS[mariadb],
                "smcamq": cls.RUNING_STATUS[smcamq],
                "smcmonitor": cls.RUNING_STATUS[smcmonitor],
            }
        )
