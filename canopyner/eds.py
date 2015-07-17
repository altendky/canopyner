#!/usr/bin/env python3

from od import ObjectDictionary, Index, Subindex
from configparser import ConfigParser
import re


def parse(file):
        od = ObjectDictionary('SEATV32')
        parser = ConfigParser()
        parser.read(file)

        device_info = parser['DeviceInfo']
        baudrate = 'baudrate_'
        od.baud_rates = [int(key[len(baudrate):]) for key in device_info if
                           (key.startswith('baudrate_') and int(device_info[key]) is 1)]
        print('Baud Rates: ' + ', '.join([str(b) for b in od.baud_rates]))

        od.vendor_number = int(device_info['vendornumber'], 0)
        print('Vendor Number: ' + hex(od.vendor_number))

        od.lss = bool(device_info.get('lss_supported', False))

        # od.indexes = []
        for section in parser:
            try:
                index = Index(int(section, 16), parser[section]['parametername'])
                pattern = section + 'sub(?P<sub>[0-9a-f]+)'
                subindex_re = re.compile(pattern, re.IGNORECASE)
                for s in parser:
                    match = subindex_re.fullmatch(s)
                    if match is not None:
                        # TODO   actually fill this in
                        subindex = Subindex(int(match.group('sub'), 16), parser[s]['parametername'])
                        # si.
                        index.add_subindex(subindex)
                index.pdomapping = bool(parser[section].get('pdomapping', False))
                # index.subindexes.sort()
                od.add_index(index)
            except ValueError as e:
                if not str(e).startswith('invalid literal for int()'):
                    raise

        # od.indexes.sort()

        return od


if __name__ == '__main__':
    import sys

    od = parse(sys.argv[1])
    print(od)

    sys.exit(0)
