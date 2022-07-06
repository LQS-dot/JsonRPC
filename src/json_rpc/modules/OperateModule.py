#!/usr/bin/python3
import time
from sh import systemctl
from multiprocessing import Process
from loguru import logger


class MyProcess(Process):
    def __init__(self, **unit):
        super(MyProcess, self).__init__()
        self.unit = list(unit.keys())[0]
        self.action = list(unit.values())[0]

    def run(self):
        logger.info("线程{p},{a},{t}", p=self.unit, a=self.action, t=time.time())
        systemctl(self.action, self.unit, _ok_code=[0, 3]).strip()


class UnitsOperate:
    """
    Component related operations
    """

    UNITS = {
        "smc_filestore": "smcfilestore",
        "smc_es": "elasticsearch",
        "smc_mysql": "mariadb",
        "smc_mq": "smcamq",
        "smc_monitor": "smcmonitor",
    }

    def __init__(self, **units: dict[str:str]):
        self.units = units

    @property
    @logger.catch
    def restartUnits(self):
        """
        Restart the componet through parameters to determine the opening of
        multiple threads.
        """
        for unit, action in self.units.items():
            """
            params:
              key: unit
              value: action
            """
            unit_action = {unit: action}
            if not action:
                continue
            p = MyProcess(**unit_action)
            p.start()
