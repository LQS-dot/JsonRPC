import traceback
import os
import platform
import re
import sys
import datetime
import subprocess
import tempfile
import argparse
import json
from pathlib import Path
from loguru import logger


class Mount:
    """
    Mount share on Linx and MacOS

    """

    def __init__(
        self,
        mount_local="/mnt/nfs_connect/",
        username="",
        password="",
        mount_remote="",
        domain="",
    ):
        """
        Mount share on Liunx and MacOS

                **MacOS only requires the remote mount point in most instances, however credentials can be supplied**

        Usage:
                local = ''

                remote = '//remote/share/path'

                username = ''

                password = ''

                domain = ''

                **Initialse Class**

                share = Mount(mount_local, username, password, mount_remote, domain)

                **Mount Share**

                share._mount()

                **Unmount Share**

                share._un_mount()

        """
        self.operating_system = sys.platform
        self.mount_local = mount_local
        self.username = username
        self.password = password
        self.mount_remote = mount_remote
        self.domain = domain

    def _check_mount(self):
        """
        Check if mount already exists
        """
        found = False
        command_check = "mount"
        process_check = subprocess.Popen(
            command_check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        output_check = process_check.communicate()[0]
        line = output_check.splitlines()
        if self.mount_remote.endswith("/"):
            self.mount_remote = self.mount_remote[:-1]
        for i in line:
            pattern = "{}.*".format(self.mount_remote.replace("//", "\/")).encode()
            matches = re.search(pattern, i)
            if matches:
                mat = re.match(b".*\son\s(.*?)\s.*", i)
                if mat:
                    self.mount_local = mat.groups()[0]
                    found = True
                return found
        return found

    def _un_mount(self):
        """
        Unmount share
        """

        found = self._check_mount()
        if found:
            try:
                command = "umount -f {}".format(self.mount_local.decode())
                proc = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                )
                stdout_value = proc.communicate()[0]
                found = self._check_mount()
                if not found:
                    pass
                else:
                    return

            except Exception:
                return json.dumps({"data": 0, "message": "unmount failed"})

    def _mount(self):
        """
        Attempt to map network share
        """

        if "//" in self.mount_remote:
            self.mount_remote = self.mount_remote.replace("//", "")

        found = self._check_mount()

        if not found:

            try:

                if self.operating_system == "darwin":

                    self.mount_remote = self.mount_remote.replace(" ", "%20")

                    if not self.username:
                        self.username = "guest"
                        if not self.domain:
                            if not self.password:
                                command = "osascript -e 'mount volume \"smb://guest:guest@{r}\"'".format(
                                    r=self.mount_remote
                                )
                    else:
                        command = "osascript -e 'mount volume \"smb://{d};{u}:{p}@{r}\"'".format(
                            r=self.mount_remote,
                            u=self.username,
                            p=self.password,
                            d=self.domain,
                            m=self.mount_local,
                        )

                if self.operating_system == "linux":

                    now = datetime.datetime.now().strftime("%B-%d-%Y")
                    if not Path(self.mount_local).exists():
                        try:
                            Path(self.mount_local).mkdir(parents=True)
                            Path(self.mount_local).chmod(0o777)
                        except Exception as exc:
                            logger.warning("nfs connect failed,{e}", e=exc)
                            return found, json.dumps(
                                {"data": 0, "message": "mount failed"}
                            )

                    self.mount_local = self.mount_local.replace(" ", "\ ")
                    self.mount_remote = self.mount_remote.replace(" ", "\ ")
                    command = "timeout 10 mount -t nfs -o rw,soft,timeo=30,retry=1 {domain}:{remote} {local}".format(
                        domain=self.domain,
                        remote=self.mount_remote,
                        local=self.mount_local,
                    )

                proc = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True,
                )
                stdout_value = proc.communicate()[0].decode()

                found = self._check_mount()

            except Exception as exc:
                logger.warning("nfs connect failed,{e}", e=exc)
                return found, json.dumps(
                    {"data": 0, "message": "mount failed,{ms}".format(ms=stdout_value)}
                )

        if found:
            logger.success("nfs connect success")
            return found, json.dumps({"data": 1, "message": ""})
        else:
            logger.warning("mount failed,{ms}", ms=stdout_value)
            return found, json.dumps(
                {"data": 0, "message": "mount failed,{ms}".format(ms=stdout_value)}
            )

    def __call__(self):
        ### 测试挂载
        ret, msg = self._mount()
        if ret:
            ### 取消挂载
            self._un_mount()
            return msg
        else:
            self._un_mount()
            return msg


if __name__ == "__main__":
    """
    : return 参数解析 Command line format
    """
    # description = "you should add those parameter"
    # parser = argparse.ArgumentParser(description=description)

    # parser.add_argument('-ip', '--host', help ='this is hostname')
    # parser.add_argument('-path', '--path', help ='this is path')

    # args = parser.parse_args()

    # host = args.host
    # path = args.path + '/'

    """
       : return JSON fomat
    """
    args = json.loads(sys.argv[1])
    store_type = args.get("storetype")
    host = args.get("storeServerAddr")
    path = args.get("storePath") + "/"

    if None in [host, path, store_type]:
        print(json.dumps({"result": 0, "message": "argvs required"}))
        sys.exit(1)
    m = Mount(mount_remote=path, domain=host)
    result = m()
