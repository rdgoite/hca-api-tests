#!/usr/bin/env python
import json
from os import environ
from sys import argv

import requests


dss_base_url = 'https://dss.integration.data.humancellatlas.org/v1'
dss_base_url = environ.get('DSS_BASE_URL', dss_base_url)

dss_replica = 'aws'
dss_replica = environ.get('DSS_REPLICA', dss_replica)


def _pretty_print(json_data):
    return json.dumps(json_data, indent=4)


def _retrieve_bundle(bundle_uuid):
    bundle_url = f'{dss_base_url}/bundles/{bundle_uuid}'
    bundle_json = requests.get(bundle_url, params={'replica': dss_replica}).json()
    formatted_json = _pretty_print(bundle_json)
    with open('bundle.json', 'w') as bundle_file:
        print('Writing bundle file to [bundle.json]...')
        print(formatted_json, file=bundle_file)
    return bundle_json.get('bundle')


# TODO add progress bar
def _download_file(file_uuid, file_name):
    response = requests.get(f'{dss_base_url}/files/{file_uuid}', params={'replica': dss_replica},
                            stream=True)
    with open(file_name, 'wb') as bundle_file:
        for chunk in response.iter_content(chunk_size=256):
            bundle_file.write(chunk)


def _download_bundle_files(_bundle):
    if 'files' in _bundle:
        files = _bundle.get('files')
        for count, file in enumerate(files):
            file_uuid = file.get('uuid')
            file_name = file.get('name')
            print(f'Downloading files... [{count + 1} / {len(files)}]: {file_name}')
            _download_file(file_uuid, file_name)


if __name__ == '__main__':
    assert len(argv) >= 2, f'No bundle uuid specified.'
    bundle_uuid = argv[1]
    bundle = _retrieve_bundle(bundle_uuid)
    _download_bundle_files(bundle)
