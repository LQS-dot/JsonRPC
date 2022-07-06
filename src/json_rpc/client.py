import requests
import json


def main():
    url = "http://localhost:4000/jsonrpc"
    headers = {"content-type": "application/json"}

#    payload = {
#        "method": "SystemInfo",
#        "params": {},
#        "jsonrpc": "2.0",
#        "id": 0,
#    }
#    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
#    print(response)
#
#    payload = {
#        "method": "UnInfo",
#        "params": {},
#        "jsonrpc": "2.0",
#        "id": 0,
#    }
#    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
#    print(response)
#
#    payload = {
#        "method": "UnOperate",
#        "params": {
#            "smcfilestore": "start",
#            "smcamq": "restart",
#            "elasticsearch": "",
#        },
#        "jsonrpc": "2.0",
#        "id": 0,
#    }
#    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
#    print(response)
#
    # Example foobar method
    # payload = {
    #    "method": "CheckNFS",
    #    "params": {
    #        "storeServerAddr": "192.168.100.224",
    #        "storePath": "/opt/nfstest",
    #    },
    #    "jsonrpc": "2.0",
    #    "id": 0,
    # }
    # response = requests.post(url, data=json.dumps(payload), headers=headers).json()

    # print(response)

    # Example foobar method
    # payload = {
    #    "method": "CheckSftp",
    #    "params": {
    #        "storeServerAddr": "192.168.100.224",
    #        "account": "root",
    #        "password": "Ruijie@@2017",
    #        "storePath": "/root",
    #    },
    #    "jsonrpc": "2.0",
    #    "id": 0,
    # }
    # response = requests.post(url, data=json.dumps(payload), headers=headers).json()

    # print(response)

    # Example foobar method
    # payload = {
    #    "method": "DBBack",
    #    "params": {
    #        "storeServerAddr": "192.168.100.224",
    #        "account": "root",
    #        "password": "Ruijie@@2017",
    #        "storePath": "/root",
    #        "mode": "1",
    #        "action": "1",
    #    },
    #    "jsonrpc": "2.0",
    #    "id": 2,
    # }
    # response = requests.post(url, data=json.dumps(payload), headers=headers).json()

    # print(response)

    # payload = {
    #    "method": "DBBack",
    #    "params": {
    #        "storeServerAddr": "192.168.100.224",
    #        "account": "",
    #        "password": "",
    #        "storePath": "/opt/nfstest",
    #        "mode": "2",
    #        "action": "1",
    #    },
    #    "jsonrpc": "2.0",
    #    "id": 2,
    # }
    # response = requests.post(url, data=json.dumps(payload), headers=headers).json()

    # print(response)

    # payload = {
    #    "method": "DBRollback",
    #    "params": {
    #        "storeServerAddr": "192.168.100.224",
    #        "account": "root",
    #        "password": "Ruijie@@2017",
    #        "storePath": "/root/",
    #        "mode": "1",
    #        "id": "0c976f7a-4ade-4f37-bafa-251933da93f0",
    #        "pkgName": "2022_06_27_0c976f7a-4ade-4f37-bafa-251933da93f0_dbbak.tar.gz",
    #        "action": "1",
    #        "bkrolltime": "2022-06-28 10:42:53",
    #    },
    #    "jsonrpc": "2.0",
    #    "id": 3,
    # }
    # response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    # print(response)

    # payload = {
    #    "method": "DBRollback",
    #    "params": {
    #        "storeServerAddr": "192.168.100.224",
    #        "account": "",
    #        "password": "",
    #        "storePath": "/opt/nfstest",
    #        "mode": "2",
    #        "id": "6e443ba0-b801-457b-a887-87e2364f7c21",
    #        "pkgName": "2022_06_27_6e443ba0-b801-457b-a887-87e2364f7c21_dbbak.tar.gz",
    #    },
    #    "jsonrpc": "2.0",
    #    "id": 3,
    # }
    # response = requests.post(url, data=json.dumps(payload), headers=headers).json()
    # print(response)


if __name__ == "__main__":
    main()
