#!/usr/bin/python3
#
# Copyright (c) 2015-2021 by Ron Frederick <ronf@timeheart.net> and others.
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
import json
from typing import NoReturn, Dict, List
from pathlib import Path


class redirect:
    content = ""

    def write(self, str):
        self.content += str

    def flush(self):
        self.content = ""


class AsyncExample:
    def __init__(
        self, username: str, password: str, host: str, localpath: str, remotepath: str
    ) -> NoReturn:
        self.username = username
        self.password = password
        self.host = host
        self.localpath = localpath
        self.remotepath = remotepath + "/"
        self.ret = dict()

    async def connect(self, username: str, password: str, host: str) -> NoReturn:
        conn = await asyncssh.connect(
            host=host, username=username, password=password, known_hosts=None
        )
        async with conn.start_sftp_client() as sftp:
            # 测试传输
            try:
                await sftp.put(localpaths=self.localpath, remotepath=self.remotepath)
            except Exception as exc:
                """
                result: 0 -> failed 1 -> success
                message: cause
                """
                print(
                    json.dumps(
                        {
                            "data": 0,
                            "message": "connect failed, maybe no directory or connect refused",
                        }
                    )
                )

        print(json.dumps({"data": 1, "message": ""}))

        ### 清理传输文件
        try:
            conenct_file = Path(self.remotepath) / Path(self.localpath).name
            res = await conn.run(command="rm -rf %s" % (conenct_file))
        except Exception as exc:
            pass

        conn.close()

    async def gather(self):
        tasks = []
        try:
            tasks.append(self.connect(self.username, self.password, self.host))
            await asyncio.gather(*tasks)
        except (OSError, asyncssh.Error) as exc:
            print(
                json.dumps(
                    {
                        "data": 0,
                        "message": "connect failed, maybe no directory or connect refused",
                    }
                )
            )

    def __call__(self):
        # print string -> r
        r = redirect()
        sys.stdout = r

        async def main():
            await self.gather()

        asyncio.run(main())
        return r.content.replace("\n", "")
