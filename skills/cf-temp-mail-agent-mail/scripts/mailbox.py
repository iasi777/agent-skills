#!/usr/bin/env python3
"""Small HTTPS mailbox client. See --help and references/api.md."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    profile_home = os.environ.get('HERMES_HOME')
    profile_config = Path(profile_home) / 'cf-temp-mail/credentials.json' if profile_home else None
    default_config = str(profile_config) if profile_config and profile_config.is_file() else '~/.cf-temp-mail/credentials.json'
    parser.add_argument('--credentials', default=default_config)
    parser.add_argument('--body-file', help='JSON request body file; credentials never belong in argv')
    parser.add_argument('--save-as', help='New credential file, required for creation/login; never overwrite')
    parser.add_argument('method', choices=['GET', 'POST', 'PATCH', 'DELETE'])
    parser.add_argument('path', help='Mailbox API path, including optional query string')
    args = parser.parse_args()
    config = json.loads(Path(args.credentials).expanduser().read_text())
    base = config['base'].rstrip('/')
    url = urllib.parse.urlsplit(base)
    if url.scheme != 'https' or not url.hostname or url.username or url.password or url.query or url.fragment:
        raise ValueError('Configure an HTTPS API base without URL credentials/query/fragment')
    path = urllib.parse.urlsplit(args.path)
    if path.scheme or path.netloc or path.fragment or not re.fullmatch(r'/(?:api/[a-z_]+(?:/[a-z_0-9]+)*|open_api/settings)', path.path):
        raise ValueError('Use an /api/ mailbox path or /open_api/settings')
    credential_response = path.path in ('/api/new_address', '/api/address_login')
    destination = None
    if credential_response:
        if args.method != 'POST' or not args.save_as:
            raise ValueError('Creation/login requires POST and --save-as')
        destination = Path(args.save_as).expanduser()
        destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        # Reserve the destination before the remote write. A failed request leaves
        # a marker so an ambiguous create cannot be repeated silently.
        with destination.open('x') as stream:
            os.chmod(destination, 0o600)
            json.dump({'status': 'pending', 'operation': path.path}, stream)
    elif args.save_as:
        raise ValueError('--save-as is only for creation/login')
    headers = {'User-Agent': 'Mozilla/5.0 cf-temp-mail-agent', 'Accept': 'application/json'}
    if config.get('site_password'):
        headers['x-custom-auth'] = config['site_password']
    if path.path == '/api/new_address' and config.get('user_token'):
        headers['x-user-token'] = config['user_token']
    if path.path.startswith('/api/') and not credential_response:
        headers['Authorization'] = 'Bearer ' + config['jwt']
    data = None
    if args.body_file:
        data = json.dumps(json.loads(Path(args.body_file).expanduser().read_text())).encode()
        headers['Content-Type'] = 'application/json'
    request = urllib.request.Request(base + args.path, data=data, headers=headers, method=args.method)
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        print(json.dumps({'error': 'HTTP error', 'status': error.code,
                          'retry_after': error.headers.get('Retry-After'),
                          'credential_file': str(destination) if destination else None}), file=sys.stderr)
        return 1
    if destination:
        if not isinstance(result, dict) or not result.get('jwt') or not result.get('address'):
            raise ValueError('Unexpected credential response; inspect pending state before retrying')
        saved = {**config, **result}
        # Persist secrets without emitting them to terminal output.
        with destination.open('w') as stream:
            json.dump(saved, stream)
        result = {'address': result['address'], 'credential_file': str(destination)}
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    os.umask(0o077)
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError):
        print('Request/configuration failed. For writes, outcome may be unknown; inspect saved state before retrying.', file=sys.stderr)
        sys.exit(1)
