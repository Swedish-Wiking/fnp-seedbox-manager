# FNP Seedbox Manager

For when you have a non-static IP on your seedbox and what's a script that can automagically manage it for you.

## Usage

```cmd
fnp_seedbox.py username [ip] [options]
```

## All options

- `--help`, `--print | --no-print`, `--seedbox-name`, `--delete | --no-delete`, `--cookie-file`

## Example

```cmd
python ./fnp_seedbox.py USERNAME 1.1.1.2 --no-delete --seedbox-name SeedExample1 --print

| Name                     IP                  ID   
| -----------------------------------------------------
| MainBox                  192.168.12.234      1448 
| SeedExample              1.1.1.1             1455 

Successfully added Seedbox: "SeedExample1" (1.1.1.2)
```

## Help

```cmd
usage: fnp_seedbox.py username [ip] [options] 

Automagically add or remove seedbox entries on fearnopeer.com

positional arguments:
  username              FnP username
  ip                    IP of the seedbox

options:
  -h, --help            show this help message and exit
  --print, --no-print   Prints list of seedboxes (default: False)
  --seedbox-name SEEDBOX_NAME
                        Name of the seedbox (default: PikminBox)
  --delete, --no-delete
                        Deletes all old seedbox entries (default: True)
  --cookie-file COOKIE_FILE
                        Cookies to be used when making requests (default: ./fearnopeer.cookies)

For bugs/errors, please DM me on FNP or make an issue on GitHub
```
