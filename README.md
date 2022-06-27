# JsonRPC
###  This is a small project based on the JsonRPC framework, providing four internal RPC interfaces 
  - 1. nfs service detection interface 
  - 2. sftp service detection port
  - 3. Database backup based on nfs and sftp 
  - 4. Database recovery based on nfs and sftp

  # Related Services and Interpreters:
  - python3.6+ (Mainly jsonrpc requirements, I use python3.10)
  - asyncssh :
      asyncssh-2.11.0-py3-none-any.whl
  - jsonrpc:
      json_rpc-1.13.0-py2.py3-none-any.whl
  - nfs:
      nfs-utils
The system is CentOS Linux release 7.9.2009 (Core).
Code formatting is black, Project creation usingpyscaffold

Project Introduction:
  Two modules of business logic connect, db_back
----

  # CheckNFS
  ### Check if nfs service is available
  ```
  payload = {
        "method": "CheckNFS",
        "params": {
            "storeServerAddr": "192.168.100.224",
            "storePath": "/opt/nfstest",
        },
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
  ```
    
    
   # CheckSftp 
   ### check if sftp service is available

  ```
   payload = {
        "method": "CheckSftp",
        "params": {
            "storeServerAddr": "192.168.100.224",
            "account": "root",
            "password": "xxx",
            "storePath": "/root",
        },
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()
  ```

   # Back
   ###  DBBack [ mode: 1 sftp 2 nfs ]

    payload = {
        "method": "DBBack",
        "params": {
            "storeServerAddr": "192.168.100.224",
            "account": "root",
            "password": "xxx",
            "storePath": "/root",
            "mode": "1",
        },
        "jsonrpc": "2.0",
        "id": 2,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()

   # DBRollback
   ### DBRollback [ mode: 1 sftp 2 nfs ]
    payload = {
        "method": "DBRollback",
        "params": {
            "storeServerAddr": "192.168.100.224",
            "account": "root",
            "password": "xxx",
            "storePath": "/root/",
            "mode": "1",
            "id": "0c976f7a-4ade-4f37-bafa-251933da93f0",
            "pkgName": "2022_06_27_0c976f7a-4ade-4f37-bafa-251933da93f0_dbbak.tar.gz",
        },
        "jsonrpc": "2.0",
        "id": 3,
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers).json()


  
