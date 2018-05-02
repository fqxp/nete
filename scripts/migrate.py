#! /usr/bin/env python3
import glob
import json
import os.path
import sys
import uuid


def migrate(base_dir):
    for filename in glob.glob(os.path.join(base_dir, '*.nete')):
        migrate_note(filename)


def migrate_note(filename):
    print('Migrating {} ...'.format(filename))

    with open(filename, 'r') as fp:
        data = json.load(fp)

    if not data.get('revision_id'):
        data['revision_id'] = str(uuid.uuid4())

    with open(filename, 'w') as fp:
        json.dump(data, fp)


if __name__ == '__main__':
    migrate(sys.argv[1])
