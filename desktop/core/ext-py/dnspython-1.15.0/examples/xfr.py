#!/usr/bin/env python

from __future__ import print_function

import dns.query
import dns.resolver
import dns.zone

soa_answer = dns.resolver.query('dnspython.org', 'SOA')
main_answer = dns.resolver.query(soa_answer[0].mname, 'A')

z = dns.zone.from_xfr(dns.query.xfr(main_answer[0].address, 'dnspython.org'))
names = z.nodes.keys()
names.sort()
for n in names:
    print(z[n].to_text(n))
