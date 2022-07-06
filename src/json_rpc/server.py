""" Example of json-rpc usage with Wergzeug and requests.

NOTE: there are no Werkzeug and requests in dependencies of json-rpc.
NOTE: server handles all url paths the same way (there are no different urls).

"""

import datetime
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from pathlib import Path
from jsonrpc import JSONRPCResponseManager, dispatcher
from connect.nfs_connect import Mount
from connect.sftp_connect import AsyncExample
from db_back.db_back import DbBack
from db_back.db_rollback import DbRollback
from modules import *
from loguru import logger

logger.add(
    Path("/tmp/db_back_{}.log".format(datetime.datetime.now().strftime("%Y_%m_%d"))),
    rotation="100 MB",
    retention="10 days",
    compression="zip",
)


@dispatcher.add_method
def CheckNFS(**kwargs):
    """
    args: {'storetype': '1', 'storeServerAddr': '192.168.100.224', 'storePath': '/opt/nfstest'}
    """
    print(kwargs)
    logger.info("CheckNFS: {args}", args=kwargs)
    mount = Mount(
        mount_remote=kwargs.get("storePath"), domain=kwargs.get("storeServerAddr")
    )
    result = mount()
    return result


@dispatcher.add_method
def CheckSftp(**kwargs):
    """
    argvs: AsyncExample(username, password, host,localpath = Path(__file__), remotepath = path)
        out args: '{"storeServerAddr":"192.168.100.224","account":"root","password":"Ruijie@@20171","storePath":"/"}'
    """
    print(kwargs)
    logger.info("CheckSftp: {args}", args=kwargs)
    sftp = AsyncExample(
        kwargs.get("account"),
        kwargs.get("password"),
        kwargs.get("storeServerAddr"),
        localpath=Path(__file__),
        remotepath=kwargs.get("storePath"),
    )
    result = sftp()
    return result


@dispatcher.add_method
def DBBack(**kwargs):

    logger.info("DBBack: {args}", args=kwargs)
    print(kwargs)
    dbback = DbBack(
        mode=kwargs.get("mode"),
        account=kwargs.get("account"),
        password=kwargs.get("password"),
        host=kwargs.get("storeServerAddr"),
        remotepath=kwargs.get("storePath"),
        action=kwargs.get("action"),
    )

    result = dbback.run()
    return result


@dispatcher.add_method
def DBRollback(**kwargs):

    logger.info("DBRollback: {args}", args=kwargs)
    print(kwargs)
    dbrollback = DbRollback(
        mode=kwargs.get("mode"),
        account=kwargs.get("account"),
        password=kwargs.get("password"),
        host=kwargs.get("storeServerAddr"),
        remotepath=kwargs.get("storePath"),
        record_id=kwargs.get("id"),
        pkgname=kwargs.get("pkgName"),
        action=kwargs.get("action"),
        bkrolltime=kwargs.get("BkRollTime"),
    )

    result = dbrollback.run()
    return result


@dispatcher.add_method
def SystemInfo(**kwargs):
    # return system info
    logger.info(System().check_system())
    return System().check_system()


@dispatcher.add_method
def UnInfo(**kwargs):
    # return untis info
    logger.info(System().check_units())
    return System().check_units()


@dispatcher.add_method
def UnOperate(**kwargs):
    # units start
    logger.info("UnitsOperate: {args}", args=kwargs)
    UnitsOperate(**kwargs).restartUnits


# python3 db_back.py '{"mode":"1","storeServerAddr":"192.168.100.224","account":"root","password":"Ruijie@@2017","storePath":"/root"}'
# python3 db_back.py '{"mode":"2","storeServerAddr":"192.168.100.224","account":"","password":"","storePath":"/opt/nfstest"}'


# python3 db_rollback.py '{"mode":"1","storeServerAddr":"192.168.100.224","account":"root","password":"Ruijie@@2017","storePath":"/root","id":"915ad67f-1763-4495-afc5-e26b6062f61e","pkgName":"2022_06_25_915ad67f-1763-4495-afc5-e26b6062f61e_dbbak.tar.gz"}'
# python3 db_rollback.py '{"mode":"2","storeServerAddr":"192.168.100.224","account":"","password":"","storePath":"/opt/nfstest","id":"f3a6ea61-0488-49b4-a95b-e3b2e5cd60be","pkgName":"2022_06_25_f3a6ea61-0488-49b4-a95b-e3b2e5cd60be_dbbak.tar.gz"}'


@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["echo"] = lambda s: s
    dispatcher["add"] = lambda a, b: a + b

    response = JSONRPCResponseManager.handle(
        request.get_data(cache=False, as_text=True), dispatcher
    )

    return Response(response.json, mimetype="application/json")


if __name__ == "__main__":
    run_simple("localhost", 4000, application, threaded=True)
