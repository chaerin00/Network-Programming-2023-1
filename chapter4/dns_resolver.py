import argparse

import dns.resolver


def lookup(name):
    for qtype in 'A', 'NS':
        answer = dns.resolver.resolve(name, qtype, raise_on_no_answer=False)
        if answer.rrset is not None:
            print(answer.rrset)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Resolve a name using DNS')
    parser.add_argument('name')
    lookup(parser.parse_args().name)
