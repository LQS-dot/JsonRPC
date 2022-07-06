#!/usr/bin/python3
#
# Copyright (c) 2015-2021 by Ron Frederick <lucifer19961225@163.com> and others.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v2.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-2.0/
#
# This program may also be made available under the following secondary
# licenses when the conditions for such availability set forth in the
# Eclipse Public License v2.0 are satisfied:
#
#    GNU General Public License, Version 2.0, or any later versions of
#    that license
#
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later
#
# Contributors:
#     Ron Frederick - initial implementation, API, and documentation
import asyncio, asyncssh, sys, os
import argparse
import uuid
import json, datetime
import subprocess
import shutil
from typing import NoReturn, Dict, List
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from connect.nfs_connect import Mount


Found = True


class redirect:
    content = ""

    def write(self, str):
        self.content += str

    def flush(self):
        self.content = ""


class AsyncTrans:
    """
    - The transmission adopts the asyncssh method,
        and a new transmission class is created for the Dbback call to transmit
    """

    def __init__(
        self, username: str, password: str, host: str, localpath: str, remotepath: str
    ) -> NoReturn:
        self.username = username
        self.password = password
        self.host = host
        self.localpath = localpath
        self.remotepath = remotepath
        self.ret = dict()

    async def connect(self, username: str, password: str, host: str) -> NoReturn:
        conn = await asyncssh.connect(
            host=host, username=username, password=password, known_hosts=None
        )
        async with conn.start_sftp_client() as sftp:
            try:
                await sftp.put(localpaths=self.localpath, remotepath=self.remotepath)
            except Exception as exc:
                """
                result: 0 -> failed 1 -> success
                message: cause
                """
                global Found
                Found = False
        conn.close()

    async def gather(self):
        tasks = []
        try:
            tasks.append(self.connect(self.username, self.password, self.host))
            await asyncio.gather(*tasks)
        except (OSError, asyncssh.Error) as exc:
            global Found
            Found = False

    def __call__(self):
        async def main():
            await self.gather()

        asyncio.run(main())
        return Found


class DbBack:
    """
    Initialization parameters, among which mode, host, remotepath must be passed, localpath custom, account and password in sftp mode must be passed
    : mode : nfs/ sftp
    : localpath: local db.sql
    : account: username
    : password: pwd
    : host: address
    : remotepath: remote path
    """

    CONFIG_CLASS_MAP = {
        "decypt": "/opt/smc/hardware/sbin/decypt",
        "back_dir": "/opt/data/dbBackup/record/",
        "back_json": "/opt/data/dbBackup/record/backup.json",
        "dbpwd": Path("/etc/juminfo.conf").read_text(),
    }

    def __init__(
        self,
        mode=None,
        localpath="/tmp/dbback/",
        account=None,
        password=None,
        host=None,
        remotepath=None,
    ):
        self.uuid = str(uuid.uuid4())
        self.mode = mode
        self.localpath = localpath
        self.account = account
        self.password = password
        self.host = host
        self.remotepath = remotepath
        # nfs args
        self.nfs_dict = {
            "mode": self.mode,
            "host": self.host,
            "remotepath": self.remotepath,
        }
        # sftp args
        self.sftp_dict = {
            "mode": self.mode,
            "account": self.account,
            "password": self.password,
            "host": self.host,
            "remotepath": self.remotepath,
        }

    @classmethod
    def read_json(cls):
        with open(cls.CONFIG_CLASS_MAP["back_json"], "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []

    def _sftp_trans(self):
        m = AsyncTrans(
            username=self.account,
            password=self.password,
            host=self.host,
            localpath="/tmp/" + self.pkgname,
            remotepath=self.remotepath + "/",
        )

        return m()

    def _nfs_trans(self):
        m = Mount(
            mount_remote=self.remotepath,
            domain=self.host,
        )
        ret, msg = m._mount()

        if ret:
            mount_local = m.mount_local.decode()
            if os.access(mount_local, os.R_OK) or os.access(mount_local, os.W_OK):
                try:
                    shutil.move("/tmp/" + self.pkgname, mount_local)
                    m._un_mount()
                    return True
                except Exception:
                    m._un_mount()
                    return False
            else:
                m._un_mount()
                return False
        else:
            return False

    def db_back(self):
        """
        This function dumps the sql file and records the current version number compressed for transmission
                read ini file
        """
        try:
            back_ret = os.popen(
                "mysqldump -usmc -p{pwd} SMC > /tmp/dbback/smcdb.sql".format(
                    pwd=self.CONFIG_CLASS_MAP["dbpwd"]
                )
            ).read()

            proversion = (
                os.popen(
                    "mysql -usmc -p{pwd} -e \"select paramValue from t_sys_param_init where paramName = 'ProVersion';\" SMC | tail -1".format(
                        pwd=self.CONFIG_CLASS_MAP["dbpwd"]
                    )
                )
                .read()
                .strip()
            )

            with open("/tmp/dbback/proversion", "w") as fp:
                fp.write(proversion)

        except IOError:
            global Found
            Found = False

    @classmethod
    def mk_files(cls):
        """
        This function is to generate backup record file and sql storage directory
                Notice:
                       This function will delete the old backup sql and regenerate the empty directory
        """
        db_path = Path(cls.CONFIG_CLASS_MAP["back_dir"])
        if not db_path.exists():
            db_path.mkdir(parents=True)
        Path(cls.CONFIG_CLASS_MAP["back_json"]).touch(exist_ok=True)

        # delete old data
        dbback_path = Path("/tmp/dbback/")
        if dbback_path.exists():
            for child in dbback_path.iterdir():
                child.unlink()
            dbback_path.rmdir()

        dbback_path.mkdir(parents=True, exist_ok=True)

    @property
    def add_record(self):
        """
        Since the stored file is in json format and cannot be appended, each time a new record is added,
                the old data needs to be read first and then written to the file.
        """
        record = {
            "id": self.uuid,
            "progress": "10",
            "status": "1",
            "type": self.mode,
            "dstAddr": self.host,
            "dstPath": self.remotepath,
            "dstUser": self.account,
            "bkTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pkgName": datetime.datetime.now().strftime("%Y_%m_%d")
            + "_"
            + self.uuid
            + "_"
            + "dbbak"
            + ".tar.gz",
        }
        self.pkgname = record["pkgName"]
        old_data = self.read_json()
        old_data.append(record)

        with open(self.CONFIG_CLASS_MAP["back_json"], "w", encoding="utf-8") as fp:
            json.dump(old_data, fp, indent=2, ensure_ascii=False)

    def modi_record(self, **kwargs):
        old_data = self.read_json()
        for key, val in kwargs.items():
            old_data[-1][key] = val

        with open(self.CONFIG_CLASS_MAP["back_json"], "w", encoding="utf-8") as fp:
            json.dump(old_data, fp, indent=2, ensure_ascii=False)

    @staticmethod
    def en_decypt(filename=None, passwd="1qaz@LQS", deleteSource=False):
        """
        ! Due to working hours, only system commands can be invoked, so it is not recommended
        """
        try:
            target = filename
            source = "/tmp/dbback/"
            os.popen(
                "tar -czPf - /tmp/dbback | openssl des3 -salt -k {pwd} -out /tmp/{file}".format(
                    pwd=passwd, file=filename
                )
            ).read()
        except Exception:
            global Found
            Found = False

    @staticmethod
    def msg(message):
        return json.dumps({"data": 0, "message": message})

    def run(self):
	global Found
	Found = False
        ### Entry and Scheduling
        if self.mode == "1":
            if "" in self.sftp_dict.values():
                return self.msg("connect failed, maybe args be required")
        elif self.mode == "2":
            if "" in self.nfs_dict.values():
                return self.msg("connect failed, maybe args be required")

            """
				Write the backup record first and then start backing up the database
				func: add_record
					: db_back
			"""
        self.mk_files()
        # write back record
        self.add_record
        # db back
        self.db_back()
        if not Found:
            return self.msg("db connect failed")
        """
           : Update progress
        """
        self.modi_record(progress="30")

        self.en_decypt(filename=self.pkgname)
        self.modi_record(progress="50")

        if not Found:
            self.modi_record(progress="100", status="3")
            return self.msg("encypt failed")

        """
           : Start transferring data, set return value through global variable
		     global Found
        """
        trans_result = True
        if self.mode == "1":
            trans_result = self._sftp_trans()
        elif self.mode == "2":
            trans_result = self._nfs_trans()

        # clear data
        try:
            self.mk_files()
            Path("/tmp/" + self.pkgname).unlink()
        except Exception:
            pass

        if trans_result:
            self.modi_record(progress="100", status="0")
            return json.dumps({"data": 1, "message": ""})
        else:
            self.modi_record(progress="100", status="3")
            if self.mode == "2":
                return self.msg(
                    "trans data failed,Whether the directory permissions are readable and writable"
                )
            else:
                return self.msg("trans data failed")

