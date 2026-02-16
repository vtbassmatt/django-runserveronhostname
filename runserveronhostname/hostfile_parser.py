from collections import defaultdict
from collections.abc import Mapping
from typing import IO


class Hostfile(Mapping):
    def __init__(self, text_or_file: str|IO):
        if isinstance(text_or_file, str):
            self._contents = text_or_file.splitlines(keepends=True)
        else:
            self._contents = [l for l in text_or_file.readlines()]
        self._ips = defaultdict(list)
        self._hosts = defaultdict(list)

        for idx, line in enumerate(self._contents, start=1):
            line = line.strip()
            # skip comments and blank lines
            if len(line) == 0 or line[0] == '#':
                continue

            # parse lines so we can quickly answer containment questions
            ip, rest = line.split(maxsplit=1)
            hosts = rest.split()
            self._ips[ip].append(idx)
            for host in hosts:
                self._hosts[host].append(idx)
    
    def __contains__(self, x):
        "Check if a given host is present in this hostfile"
        return x in self._hosts
    
    def __getitem__(self, key):
        "Returns a list of lines where this host is defined."
        return self._hosts[key]
    
    def __iter__(self):
        "Returns an iterable of the hostnames in this hostfile"
        return iter(self._hosts)

    def __len__(self):
        "Return how many hosts are in this hostfile"
        return len(self._hosts)
    
    def ip_on_line(self, line: int):
        if line > len(self._contents):
            raise ValueError(f'line should be {len(self._contents)} or less')
        if line <= 0:
            raise ValueError('line must be 1 or greater')

        for ip, all_lines in self._ips.items():
            for haystack_line in all_lines:
                if haystack_line == line:
                    return ip
    
    def __format__(self, format_spec):
        """Returns a printable hostfile.
        
        format_spec can be one of:
        - raw - just return what we read, same as str()
        - clean - one line per line of the original, but cleaned up a bit (default)
        - simple - one line per unique IP address, strip comments
        """
        match format_spec:
            case 'raw':
                return str(self)
            case 'clean' | '' | None:
                return self._format_clean()
            case 'simple':
                return self._format_simple()
            case _:
                raise ValueError('format_spec not recognized')

    def _format_clean(self):
        results = []

        for line in self._contents:
            line = line.strip()
            # skip blank lines
            if len(line) == 0:
                continue
            # emit comments as-is
            if line[0] == '#':
                results.append(line)
                continue
            # otherwise this is a normal line
            ip, rest = line.split(maxsplit=1)
            hosts = rest.split()
            results.append(f"{ip}\t{' '.join(hosts)}")
        
        return '\n'.join(results)

    def _format_simple(self):
        results = ['# simplified to one line per IP']

        for ip, host_lines in self._ips.items():
            hosts = []
            for host_line in host_lines:
                _, raw_hosts = self._contents[host_line-1].strip().split()
                hosts.extend(raw_hosts.split())
            results.append(f"{ip}\t{' '.join(hosts)}")
        
        return '\n'.join(results)

    def __str__(self):
        return ''.join(self._contents)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {len(self._contents)} lines, {len(self._ips)} unique IPs, {len(self._hosts)} unique hosts>"


if __name__ == '__main__':
    hosts = """##
# Host Database
#
# localhost is used to configure the loopback interface
# when the system is booting.  Do not change this entry.
##
127.0.0.1	localhost
255.255.255.255	broadcasthost
::1             localhost
127.0.0.1       trivia.localhost
"""
    hf = Hostfile(hosts)

    # with open('/etc/hosts') as f:
    #     hf = Hostfile(f)

    print(hf)
    print(repr(hf))
    print(format(hf, 'clean'))
    print()
    print(format(hf, 'simple'))

    print(f"{hf['localhost']=}")
    print(f"{hf['trivia.localhost']=}")

    for h in hf:
        print(h)
        for l in hf[h]:
            print('  ', hf.ip_on_line(l))
