## Radius Server (Python)

This Raidus Server is writtten by Python, and is used to Authentication, Authorization, Accounting for WLAN user or PPPoE user.
Test authorization through supplicant on Windows10, Android 4.4.4 and iOS 13.

**Support authenticate method:**

- [x] [PAP](https://tools.ietf.org/search/rfc1334)

- [x] [CHAP](https://tools.ietf.org/search/rfc1994)

- [x] [MS-CHAPv2](https://tools.ietf.org/html/rfc2759)

- [x] [PEAPv0, PEAPv1: EAP-GTC](https://tools.ietf.org/html/draft-josefsson-pppext-eap-tls-eap-05)

- [x] [PEAPv0, PEAPv1: EAP-MSCHAPv2](https://tools.ietf.org/html/draft-kamath-pppext-peapv0-00)


**Support Dynamic Authorization Extensions:**

- Disconnect Messages
- Change-of-Authorization (CoA) Messages


## Installation and Usage

- Setup mysql

  start mysql:  `docker-compose -f docker-compose.yml up mysql`

  init mysql database and table data with [mysql_insert.sql](https://github.com/zeroleo12345/radius_server_python/blob/master/data/db/mysql_insert.sql)

- For authenticate

  Build the docker image

  `docker-compose build auth`

  Run the docker container

  `docker-compose up auth`

- For accouting

  similiar with authenticate, but reaplce `auth` with `acct`


## Send authenticate request with simulator

### authenticate by CHAP

enter into authenticate container: `docker-compose exec auth bash`

run simulator in container:

```bash
radclient -D /app/tools/simulator/etc/dictionary -d /app/etc/dictionary 127.0.0.1:1812  auth  'testing123'  < /app/tools/simulator/radius_test/auth/chap.conf
```

### authenticate by PAP

enter into authenticate container: `docker-compose exec auth bash`

run simulator in container:

```bash
radclient -D /app/tools/simulator/etc/dictionary -d /app/etc/dictionary 127.0.0.1:1812  auth  'testing123'  < /app/tools/simulator/radius_test/auth/pap.conf
```

### authenticate by EAP-GTC

add `USE_GTC=1` in .env and restart docker container

enter into authenticate container: `docker-compose exec auth bash`

run simulator in container:

```bash
eapol_test -c /app/tools/simulator/eap_test/eapol_test.conf.peapv1.gtc -a 127.0.0.1 -p 1812 -s testing123 -r 0 -N 30:s:FF-FF-FF-FF-FF-FF -N 32:s:AC
```

### authenticate by EAP-MSCHAPv2

remove `USE_GTC=0` in .env and restart docker container

enter into authenticate container: `docker-compose exec auth bash`

run simulator in container:

```bash
eapol_test -c /app/tools/simulator/eap_test/eapol_test.conf.peapv1.mschapv2 -a 127.0.0.1 -p 1812 -s testing123 -r 0 -N 30:s:FF-FF-FF-FF-FF-FF -N 32:s:AC
```


## Send authenticate request with simulator
enter into accounting container: `docker-compose exec acct bash`

run simulator in container:

```bash
radclient -D /app/tools/simulator/etc/dictionary -d /app/etc/dictionary 127.0.0.1:1813  acct  'testing123'  < /app/tools/simulator/radius_test/acct/i.conf

radclient -D /app/tools/simulator/etc/dictionary -d /app/etc/dictionary 127.0.0.1:1813  acct  'testing123'  < /app/tools/simulator/radius_test/acct/u.conf

radclient -D /app/tools/simulator/etc/dictionary -d /app/etc/dictionary 127.0.0.1:1813  acct  'testing123'  < /app/tools/simulator/radius_test/acct/t.conf
```


## Send Dynamic Authorization Extensions request with simulator
  
### disconnect

enter into accounting container: `docker-compose exec dae bash` 

run simulator in container:

``` bash
radclient -D /app/tools/simulator/etc/dictionary -d /app/etc/dictionary 127.0.0.1:3799  disconnect  'testing123'  < /app/tools/simulator/radius_test/dae/disconnect.conf
```


## gdb core
``` bash
gdb /root/.pyenv/shims/python -c core.1 
```
