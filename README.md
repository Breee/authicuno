# Authicuno
- Authicuno reads a mapping  Server -> role -> rank and writes  user -> rank into a db.
- It is designed to work with [PMSF](https://github.com/pmsf/PMSF) and similar to [PMSF-Discord-AuthBot](https://github.com/pmsf/PMSF-Discord-AuthBot)


[![Breee](https://circleci.com/gh/Breee/authicuno.svg?style=svg)](https://app.circleci.com/pipelines/github/Breee/authicuno)

Questions? I'm Bree#2002 @ Discord

Docker image:  https://cloud.docker.com/repository/docker/breedocker/authicuno

# Commands
Commands consist of a `prefix` and an `alias`.

The default prefix is just your bot user: `@bot_user_name#1337`. 
You can set a custom prefix using `@bot_user_name#1337 set_prefix !`, to set the prefix to `!`. 

Utils:
- `@bot_user_name#1337 help` display help
- `@bot_user_name#1337 ping` ping the bot
- `@bot_user_name#1337 uptime` return how long the bot is operational.

Roles:
- `@bot_user_name#1337 update_members` updates all users accoring to your config.

# Setup

## 1. Requirements: 
- python 3.7
- pip3
- discord bot user (https://discordapp.com/developers/applications/me)
- A database of your choice, which is supported by sqlalchemy (https://docs.sqlalchemy.org/en/13/core/engines.html).


## 2. Configuration:
Copy the file `config.py.dist` to `config.py` (or create it). 
The configuration file is plain python and looks as follows: 

```
import os

# Directory where the log file of the bot shall be stored
LOG_PATH = os.getenv("BOT_LOG_PATH", "./log")

"""
Discord Section.
"""
# The Token of your botuser.
BOT_TOKEN = os.getenv("BOT_TOKEN", "XXXXXXX")
# Discord Status
PLAYING = os.getenv("TAG", "AUTHICUNO")

"""
CORE Section.
"""
# The host of the DB in which we store polls
CORE_DB_HOST = os.getenv("CORE_DB_HOST", "db")
# The user of the DB
CORE_DB_USER = os.getenv("CORE_DB_USER", "authicuno")
# The password of user CORE_DB_USER
CORE_DB_PASSWORD = os.getenv("CORE_DB_PASSWORD", "bestpw")
# The port of the DB-server
CORE_DB_PORT = os.getenv("CORE_DB_PORT", 3306)
# The name of the DB in which we store polls
CORE_DB_NAME = os.getenv("CORE_DB_NAME", "authicuno_db")
# The dialect of the database-server
CORE_DB_DIALECT =  os.getenv("CORE_DB_DIALECT", "mysql")
# The driver of the database-server
CORE_DB_DRIVER =  os.getenv("CORE_DB_DRIVER", "mysqlconnector")

"""
PMSF Section.
"""
# The host of the DB in which we store polls
PMSF_DB_HOST = os.getenv("PMSF_DB_HOST", "pmsf_db")
# The user of the DB
PMSF_DB_USER = os.getenv("PMSF_DB_USER", "pmsf")
# The password of user PMSF_DB_USER
PMSF_DB_PASSWORD = os.getenv("PMSF_DB_PASSWORD", "bestpw")
# The port of the DB-server
PMSF_DB_PORT = os.getenv("PMSF_DB_PORT", 3306)
# The name of the DB in which we store polls
PMSF_DB_NAME = os.getenv("PMSF_DB_NAME", "pmsf")
# The dialect of the database-server
PMSF_DB_DIALECT =  os.getenv("PMSF_DB_DIALECT", "mysql")
# The driver of the database-server
PMSF_DB_DRIVER =  os.getenv("PMSF_DB_DRIVER", "mysqlconnector")


# Mapping: guild -> { role -> access_level}
GUILDS = {
    # Bree's server
    409418083632152577: {
        # test_rolebot
        616562233475989514: 2,
        # Scanner
        594072522203463683: 1,
        # root
        461988882385207299: 3,
    }
}
```

### Access level config:
Here is an example:
``` 
GUILDS = {
    # guild:  Bree's server
    409418083632152577: {
        # role: test_rolebot
        616562233475989514: 2,
        # role: Scanner
        594072522203463683: 1,
        # role: root
        461988882385207299: 3,
    }
}
```

- We see a Dictionary GUILDS, which contains a key for each `guild`. 
- In each of the guild entries you map one or multiple `roles` to an `access level`.
- See [https://github.com/pmsf/PMSF/blob/master/config/example.access-config.php](https://github.com/pmsf/PMSF/blob/master/config/example.access-config.php) for more information which access level has which effect.


## 3. Deploy:
### Configure
Fill in everything necessary in `config.py` or set ENV variables accordingly.

### Install python3 requirements
We recommend to use a virtual environment.
```
python3 -m venv authicuno-venv
source authicuno-venv/bin/activate
```

Then install the requirements.
```
pip3 install -U -r requirements.txt
```

### Start the bot
Call:
```
python3 start_bot.py
```

## Deploy with docker
We expect you to know about docker, docker-compose and how you deploy.

There is a `docker-compose.yml` located in the root directory.
In this example, we assume you host PMSF and its manual-db in docker, and that they are accessible over the network `pmsf_network`

```yaml
version: '2.4'
services:
  authicuno:
    image: breedocker/authicuno
    restart: always
    depends_on:
      - db
    networks:
      - default
      - pmsf_network
    environment:
      - "BOT_TOKEN=XXXXXX"
      - "CORE_DB_HOST=authicuno-db"
      - "CORE_DB_PORT=3306"
      - "CORE_DB_NAME=authicuno"
      - "CORE_DB_USER=authicuno"
      - "CORE_DB_PASSWORD=bestpw"
      - "CORE_DB_DIALECT=mysql"
      - "CORE_DB_DRIVER=mysqlconnector"
      - "PMSF_DB_HOST=pmsf-manual-db"
      - "PMSF_DB_PORT=3306"
      - "PMSF_DB_NAME=pmsf"
      - "PMSF_DB_USER=pmsf"
      - "PMSF_DB_PASSWORD=bestpw"
      - "PMSF_DB_DIALECT=mysql"
      - "PMSF_DB_DRIVER=mysqlconnector"
    volumes:
      - ./authicuno/config.py:/usr/src/app/config.py

  authicuno-db:
    image: mariadb
    environment:
      - "MYSQL_ROOT_PASSWORD=root1234"
      - "MYSQL_DATABASE=authicuno_db"
      - "MYSQL_USER=authicuno"
      - "MYSQL_PASSWORD=bestpw"
    command: ['mysqld', '--character-set-server=utf8mb4', '--collation-server=utf8mb4_unicode_ci']
    volumes:
      - ./volumes/coredb:/var/lib/mysql
    restart: always
    ports:
      -  "1337:3306"
    networks:
      - default

networks:
  pmsf_network: 
    external: true
``` 

To bring the services up, simply `docker-compose up -d authicuno-db`, `docker-compose up -d authicuno`.
