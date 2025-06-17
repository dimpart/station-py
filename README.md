# Decentralized Instant Messaging Station (Python)

[![License](https://img.shields.io/github/license/dimpart/station-py)](https://github.com/dimpart/station-py/blob/master/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/dimpart/station-py/pulls)
[![Platform](https://img.shields.io/badge/Platform-Python%203-brightgreen.svg)](https://github.com/dimpart/station-py/wiki)
[![Issues](https://img.shields.io/github/issues/dimpart/station-py)](https://github.com/dimpart/station-py/issues)
[![Repo Size](https://img.shields.io/github/repo-size/dimpart/station-py)](https://github.com/dimpart/station-py/archive/refs/heads/main.zip)
[![Tags](https://img.shields.io/github/tag/dimpart/station-py)](https://github.com/dimpart/station-py/tags)

[![Watchers](https://img.shields.io/github/watchers/dimpart/station-py)](https://github.com/dimpart/station-py/watchers)
[![Forks](https://img.shields.io/github/forks/dimpart/station-py)](https://github.com/dimpart/station-py/forks)
[![Stars](https://img.shields.io/github/stars/dimpart/station-py)](https://github.com/dimpart/station-py/stargazers)
[![Followers](https://img.shields.io/github/followers/station)](https://github.com/orgs/station/followers)


Demo project for [pypi/dimp](https://pypi.org/project/dimp/).

## Dependencies

* Latest Versions

| Name | Version | Description |
|------|---------|-------------|
| [Ming Ke Ming (名可名)](https://github.com/dimchat/mkm-py) | [![Version](https://img.shields.io/pypi/v/mkm)](https://pypi.org/project/mkm) | Decentralized User Identity Authentication |
| [Dao Ke Dao (道可道)](https://github.com/dimchat/dkd-py) | [![Version](https://img.shields.io/pypi/v/dkd)](https://pypi.org/project/dkd) | Universal Message Module |
| [DIMP (去中心化通讯协议)](https://github.com/dimchat/core-py) | [![Version](https://img.shields.io/pypi/v/dimp)](https://pypi.org/project/dimp) | Decentralized Instant Messaging Protocol |
| [DIM SDK](https://github.com/dimchat/sdk-py) | [![Version](https://img.shields.io/pypi/v/dimsdk)](https://pypi.org/project/dimsdk) | Software Development Kit |
| [DIM Plugins](https://github.com/dimchat/sdk-dart) | [![Version](https://img.shields.io/pypi/v/dimplugins)](https://pypi.org/project/dimplugins) | Cryptography & Account Plugins |

## Installation

### 0. Clone source codes & install requirements

```
$ cd ~/
$ mkdir -p github.com/dimpart/
$ cd github.com/dimpart/

$ git clone https://github.com/dimpart/station-py.git
$ cd station-py

$ pip3 install -r requirements.txt
```

### 1. Create Accounts

#### 1.0. Usages

```
$ tests/register.py --help
or
$ dimid --help

    DIM account generate/modify

usages:
    dimid [--config=<FILE>] generate
    dimid [--config=<FILE>] modify <ID>
    dimid [-h|--help]

actions:
    generate        create new ID, meta & document
    modify <ID>     edit document with ID

optional arguments:
    --config        config file path (default: "/etc/dim/config.ini")
    --help, -h      show this help message and exit
```

#### 1.1. Create station account (define your ID.name)

Input address type **2**: Station (Server Node)

```
$ tests/register.py generate
or
$ dimid generate

Generating DIM account...
--- address type(s) ---
    0: User
    1: Group (User Group)
    2: Station (Server Node)
    3: ISP (Service Provider)
    4: Bot (Business Node)
    5: ICP (Content Provider)
    6: Supervisor (Company President)
    7: Company (Super Group for ISP/ICP)
>>> please input address type: 2
!!! address type: 2
!!! meta type: 1
>>> please input ID.name (default is "test_station"): 
!!! ID.name (meta seed): test_station
!!!
!!! ========================================================================
!!!   Editing document for: test_station@285QzP9cXkXjk1Mx3cCLni4g4m6diDzqS4
!!! ------------------------------------------------------------------------
!!!
>>>   please input station name (default is "Base Station"): 
<<<   name = Base Station;
!!!
>>>   please input station host (default is "127.0.0.1"): 193.123.232.100
<<<   host = 193.123.232.100;
!!!
>>>   please input station port (default is 9394): 
<<<   port = 9394;
!!!
!!! ------------------------------------------------------------------------
!!!   Done!
!!! ========================================================================
!!!
!!!
!!! ID: test_station@285QzP9cXkXjk1Mx3cCLni4g4m6diDzqS4
!!!
!!! meta type: 1, document type: visa, name: "Base Station"
!!!
!!! private key: ECC, msg keys: ['RSA']
!!!
```

copy the new ID (e.g.: ```test_station@285QzP9cXkXjk1Mx3cCLni4g4m6diDzqS4```)

you can modify the station name, host & port later:

```
$ tests/register.py modify {NewID}
or
$ dimid modify {NewID}

!!!
!!! ========================================================================
!!!   Editing document for: test_station@285QzP9cXkXjk1Mx3cCLni4g4m6diDzqS4
!!! ------------------------------------------------------------------------
!!!
>>>   please input station name (default is "Base Station"): Relay Station
<<<   name = Relay Station;
!!!
>>>   please input station host (default is "193.123.232.100"): 
<<<   host = 193.123.232.100;
!!!
>>>   please input station port (default is 9394): 
<<<   port = 9394;
!!!
!!! ------------------------------------------------------------------------
!!!   Done!
!!! ========================================================================
!!!
!!!
!!! ID: test_station@285QzP9cXkXjk1Mx3cCLni4g4m6diDzqS4
!!!
!!! meta type: 1, document type: visa, name: "Relay Station"
!!!
!!! private key: ECC, msg keys: ['RSA']
!!!
```

#### 1.2. Create search bot

Input address type **4**: Bot (Business Node)

```
$ tests/register.py generate
or
$ dimid generate

Generating DIM account...
--- address type(s) ---
    0: User
    1: Group (User Group)
    2: Station (Server Node)
    3: ISP (Service Provider)
    4: Bot (Business Node)
    5: ICP (Content Provider)
    6: Supervisor (Company President)
    7: Company (Super Group for ISP/ICP)
>>> please input address type: 4
!!! address type: 4
!!! meta type: 1
>>> please input ID.name (default is "test_bot"): 
!!! ID.name (meta seed): test_bot
!!!
!!! ========================================================================
!!!   Editing document for: test_bot@31F21FEH634W8npUezzxQBPgj9hUUfuNuX
!!! ------------------------------------------------------------------------
!!!
>>>   please input bot name (default is "Service Bot"): Search Engine
<<<   name = Search Engine;
!!!
>>>   please input avatar url (default is ""): 
<<<   avatar = ;
!!!
!!! ------------------------------------------------------------------------
!!!   Done!
!!! ========================================================================
!!!
!!!
!!! ID: test_bot@31F21FEH634W8npUezzxQBPgj9hUUfuNuX
!!!
!!! meta type: 1, document type: visa, name: "Search Engine"
!!!
!!! private key: ECC, msg keys: ['RSA']
!!!
```

### 2. Configuration

Edit "config.ini"

```
$ mkdir -p /etc/dim/
$ cp etc/config.ini /etc/dim/
$ vi /etc/dim/config.ini
```

modify config contents:

```ini
#
#   2.1. Replace your relay station ID here
#
[station]
host = 193.123.232.100
port = 9394
id   = test_station@285QzP9cXkXjk1Mx3cCLni4g4m6diDzqS4

#
#   2.2. Replace your search bot ID here
#
[ans]
archivist = test_bot@31F21FEH634W8npUezzxQBPgj9hUUfuNuX
```

create links to ```config.ini``` in ```/etc/dim/```

```
$ ls -l /etc/dim/
total 12
-rw-rw-r--. 1 opc opc 1157 May 23 10:37 config.ini
lrwxrwxrwx. 1 opc opc   10 May 23 10:39 edge.ini -> config.ini
lrwxrwxrwx. 1 opc opc   10 May 23 10:39 station.ini -> config.ini
```

### 3. Run

```
chmod a+x *.sh
./start_all.sh
```

## Architecture

```

        /----------------\                     /----------------\
        |  User1 (moki)  |                     |  User2 (hulk)  |
        \----------------/                     \----------------/
                |                                      ^
                |                                      |
    ============|======================================|=============
                |                                      |
                V                                      |
        .....................               .....................
        :  RequestHandler1  : ---+     +--> :  RequestHandler2  :
        .....................    |     |    .....................
              |                  V     |                 |
              |              /-------------\             |
        ..............       |  TCPServer  |       ..............
        :  Session1  :        >...........<        :  Session2  :
        ..............       |   Station   |       ..............
              |              \-------------/             |
              |                     |                    |
              |          /---------------------\         |
              |          |      Database       |         |
              |           >...................<          |
              |          |  Barrack, KeyStore  |         |
              |          \---------------------/         |
              |                                          |
              |            /-----------------\           |
              \----------> |  Session Server | <---------/
                           \-----------------/
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                  DIMP
                               (DKD, MKM)
    
```

Copyright &copy; 2018-2025 Albert Moky
[![Followers](https://img.shields.io/github/followers/moky)](https://github.com/moky?tab=followers)
