# yadb
Yet Another DNS Brute-forcer
## Installation
* Install python >=3.8
* pip3 install -r requirements.txt
## Usage
```sh
Usage: yadb.py [options]

Options:
  -h, --help            show this help message and exit
  -f TARGETS_FILE, --file=TARGETS_FILE
                        file containning names to resolve
  -r RESOLVERS_FILE, --resolvers=RESOLVERS_FILE
                        file containning names to resolve
  -t TYPES, --types=TYPES
                        query types, default as `any`
  -s BAD_STRING, --bad-string=BAD_STRING
  -v, --verbose         print INFO level messages to stdout
  -d, --debug           print DEBUG level messages to stdout
```
Example:
```sh
python dns.py -r ./resolvers.txt -f ./names.txt -t A -t CNAME
```
