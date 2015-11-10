#!/usr/bin/env python3

from configparser import ConfigParser
import re
import os

from canopyner.od import ObjectDictionary, Index, Subindex


def parse(file):
    name = os.path.splitext(os.path.basename(file))[0]
    od = ObjectDictionary(name)
    parser = ConfigParser()
    parser.read(file)

    device_info = parser['DeviceInfo']
    baud_rate = 'baudrate_'
    od.baud_rates = [int(key[len(baud_rate):]) for key in device_info if
                     (key.startswith('baudrate_') and int(
                         device_info[key]) is 1)]

    od.vendor_number = int(device_info['vendornumber'], 0)

    od.lss = bool(device_info.get('lss_supported', False))

    for section in parser:
        try:
            index = Index(int(section, 16), parser[section]['parametername'])
            pattern = section + 'sub(?P<sub>[0-9a-f]+)'
            subindex_re = re.compile(pattern, re.IGNORECASE)
            for s in parser:
                match = subindex_re.fullmatch(s)
                if match is not None:
                    subindex = Subindex(int(match.group('sub'), 16),
                                        parser[s]['parametername'])
                    index.add_subindex(subindex)
            index.pdo_mapping = bool(parser[section].get('pdomapping', False))
            od.add_index(index)
        except ValueError as e:
            if not str(e).startswith('invalid literal for int()'):
                raise

    return od


if __name__ == '__main__':
    import sys

    od = parse(sys.argv[1])
    print(od)

    sys.exit(0)
