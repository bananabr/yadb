#!/usr/bin/env python

"""
This is a PoC DNS bruteforcer
"""

import json
import asyncio
from optparse import OptionParser
import logging
import socket

from async_dns.resolver import ProxyResolver
from async_dns.core import *


async def main():
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="targets_file",
                      help="file containning names to resolve")
    parser.add_option("-r", "--resolvers", dest="resolvers_file",
                      help="file containning names to resolve")
    parser.add_option('-t', '--types', action="append", default=[],
                      help='query types, default as `any`')
    parser.add_option("-s", "--bad-string", dest="bad_string", default=None,
                      help="")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="print INFO level messages to stdout")
    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="print DEBUG level messages to stdout")

    (options, _) = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.INFO)
    elif options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    RETURN_CODE_NAMES = {
        0: 'NOERROR',
        1: 'FORMERR',
        2: 'SERVFAIL',
        3: 'NXDOMAIN',
        4: 'NOTIMP',
        5: 'REFUSED',
        6: 'YXDOMAIN',
        7: 'XRRSET',
        8: 'NOTAUTH',
        9: 'NOTZONE'
    }

    class YADBDnsMessage():
        def __init__(self, qname: str, qtype, dns_message: DNSMessage):
            self.qr = dns_message.qr      # 0 for request, 1 for response
            self.qid = dns_message.qid    # id for UDP package
            self.o = dns_message.o        # opcode: 0 for standard query
            self.aa = dns_message.aa      # Authoritative Answer
            self.tc = dns_message.tc      # TrunCation, will be updated on .pack()
            self.rd = dns_message.rd      # Recursion Desired for request
            self.ra = dns_message.ra      # Recursion Available for response
            self.r = dns_message.r        # rcode: 0 for success
            self.qd = dns_message.qd
            self.an = dns_message.an      # answers
            self.ns = dns_message.ns      # authority records, aka nameservers
            self.ar = dns_message.ar      # additional records
            self.qtype = qtype
            self.qname = qname

    async def resolve_hostname(resolver, hostname, qtype):
        '''Resolve a hostname with the given resolver.'''
        for _ in range(0, 5):
            try:
                message = await resolver.query(hostname, qtype)
                if message.r == 2:
                    continue
                if hostname == 'message.acronis.com':
                    logging.debug(message)
                return YADBDnsMessage(hostname, qtype, message)
            except asyncio.CancelledError:
                continue
            except AssertionError as ex:
                if str(ex) == 'Remote server fail':
                    continue
            except asyncio.exceptions.TimeoutError:
                continue
        message = DNSMessage()
        message.r = 2
        if hostname == 'message.acronis.com':
            logging.debug(message)
        return YADBDnsMessage(hostname, qtype, message)

    args_list = []
    targets = []
    with open(options.targets_file, 'r') as targets_file:
        targets = [line.strip() for line in targets_file.readlines()]

    resolver = ProxyResolver()
    with open(options.resolvers_file, 'r') as resolvers_file:
        resolver.set_proxies([line.strip()
                              for line in resolvers_file.readlines()])
    logging.info(f"Loaded {len(resolver.ns_pairs[0][1].data)} resolvers")
    logging.debug(resolver.ns_pairs[0][1].data)

    if len(options.types) == 0:
        options.types = ['A']

    for target in targets:
        if target == 'message.acronis.com':
            logging.debug(target)
        for qtype_name in options.types:
            qtype = types.get_code(qtype_name.upper())
            if qtype is None:
                logger.warn('Unknown type: %s', qtype_name)
                continue
            args_list.append({
                'resolver': resolver,
                'hostname': target,
                'qtype': qtype
            })
    tasks = []
    logging.debug(f'# OF TASKS: {len(args_list)}')
    for args in args_list:
        task = asyncio.create_task(resolve_hostname(**args))
        tasks.append(task)

    import tqdm.asyncio
    results = []
    for f in tqdm.asyncio.tqdm.as_completed(tasks):
        results.append(await f)

    messages = []
    for message in results:
        m = {'name': message.qname,
             'type': types.get_name(message.qtype),
             'status': RETURN_CODE_NAMES[message.r],
             'data': {}
             }
        answers = []
        for answer in message.an:
            answers.append(
                {
                    'type': types.get_name(answer.qtype),
                    'name': answer.name,
                    'data': answer.data,
                    'ttl': answer.ttl
                })
        if len(answers) > 0:
            m['data']['answers'] = answers
        messages.append(m)

    print(json.dumps(messages))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Ctrl+C pressed, exiting ...")
        loop = asyncio.get_event_loop()
        # stopping the event loop
        if loop:
            print("Stopping event loop ...")
            loop.stop()
        print("Shutdown complete ...")
