import sys
import os
import unittest

from verify import verify_json_file

file_name = os.path.basename(__file__)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: "python {file_name} <json_file>" or "python {file_name} --test"')
        sys.exit(1)

    if sys.argv[1] == '--test':
        loader = unittest.TestLoader()
        suite = loader.discover('.')
        runner = unittest.TextTestRunner(descriptions=True, verbosity=2)
        runner.run(suite)
        sys.exit(0)

    try:
        print(verify_json_file(sys.argv[1]))
    except ValueError as e:
        print(f'Invalid policy definition: \n{e}')
        sys.exit(1)
