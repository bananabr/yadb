# yadb
Yet Another DNS Brute-forcer
## Installation
* Install python >=3.8
* Install jq
* pip3 install -r requirements.txt
* If you want to use yadb inside a script and have a progress bar install tqdm (pip3 install tqdm)
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
  -v, --verbose         print INFO level messages to stdout
  -w WORKERS, --workers=WORKERS
                        number of async workers
  -d, --debug           print DEBUG level messages to stdout
```
Examples:
* Basic usage
```sh
python3 yadb.py -r ./resolvers.txt -f ./names.txt -t A -t CNAME -w 512 | jq -s .
```
* With progress bar redirecting output to file
```sh
python3 yadb.py -r ./resolvers.txt -f ./names.txt -t A -t CNAME -w 512 | tqdm --total $((`wc -l ./names.txt | cut -d ' ' -f 1`*2)) | jq -s . > out.json
```