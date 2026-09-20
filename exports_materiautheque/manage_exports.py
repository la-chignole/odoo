#!/usr/bin/env python3
"""manage_exports -- command-line client for the exports_materiautheque
Odoo module.

Talks to a running Odoo server over its standard XML-RPC external API (the
same API used for scripted imports) -- nothing beyond the Python standard
library, and no code needs to run on the Odoo server itself.

Examples
--------
  ./manage_exports list-templates

  ./manage_exports upload-template --name "Bilan mensuel" --file bilan.xlsx

  ./manage_exports generate --template-id 3 \\
      --date-from 2026-09-01 --date-to 2026-09-30 --output bilan-sept.xlsx

Run with --help, or "<command> --help", for the full option list.

Connection settings (url/db/username/api key) can be passed as flags, or
left out and picked up the same way other scripts here do -- from the
environment, or a ".env" file in the current directory:

  ODOO_URL            e.g. https://odoo.example.org
  ODOO_DB             database name
  ODOO_USERNAME       Odoo login
  ODOO_API_KEY        Odoo API key (Settings > Users > your user >
                      Account Security > New API key) or account password
  ODOO_INSECURE_SSL   1/true to skip TLS certificate verification
                      (self-signed dev servers)

A flag always overrides its environment variable, which always overrides
the .env file. --timeout and --debug have no environment equivalent.
"""
import argparse
import base64
import os
import socket
import ssl
import sys
import traceback
import xmlrpc.client as xmlrpc
from pathlib import Path


class CliError(Exception):
    """A problem clear enough to report without a Python stack trace."""


# -- .env / environment -----------------------------------------------------

def load_dotenv():
    """Fill in os.environ from a ".env" file, same convention as our other
    scripts. Real environment variables already set are left untouched --
    a .env file only ever supplies a default."""
    for candidate in (Path.cwd() / '.env', Path(__file__).resolve().parent / '.env'):
        if not candidate.is_file():
            continue
        for lineno, raw_line in enumerate(candidate.read_text().splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue  # tolerate stray lines rather than fail loading
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            if key:
                os.environ.setdefault(key, value)
        return candidate
    return None


def _bool_env(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def resolve_connection(args):
    """Raise a clear CliError if url/db/username/password ended up unset
    after flags, environment, and .env -- rather than let a None reach
    xmlrpc and fail with a confusing low-level error."""
    missing = [
        label for label, value in (
            ("--url / ODOO_URL", args.url),
            ("--db / ODOO_DB", args.db),
            ("--username / ODOO_USERNAME", args.username),
            ("--password / ODOO_API_KEY", args.password),
        )
        if not value
    ]
    if missing:
        raise CliError(
            "Missing connection settings: %s. Set them as flags, "
            "environment variables, or in a .env file." % ", ".join(missing)
        )


# -- connection ---------------------------------------------------------

def _ssl_context(insecure):
    if not insecure:
        return None
    print(
        "warning: TLS certificate verification disabled (--insecure-ssl / "
        "ODOO_INSECURE_SSL)", file=sys.stderr,
    )
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context


def connect(args):
    socket.setdefaulttimeout(args.timeout)
    proxy_kwargs = {}
    context = _ssl_context(args.insecure_ssl)
    if context is not None:
        proxy_kwargs['context'] = context

    common_url = args.url.rstrip('/') + '/xmlrpc/2/common'
    object_url = args.url.rstrip('/') + '/xmlrpc/2/object'

    try:
        common = xmlrpc.ServerProxy(common_url, **proxy_kwargs)
        common.version()
    except (xmlrpc.ProtocolError, OSError, ssl.SSLError) as exc:
        hint = ""
        if isinstance(exc, ssl.SSLError) and not args.insecure_ssl:
            hint = " (self-signed certificate? try --insecure-ssl)"
        raise CliError(
            "Could not reach %s (%s: %s)%s. Check --url and your network."
            % (args.url, type(exc).__name__, exc, hint)
        ) from exc

    try:
        uid = common.authenticate(args.db, args.username, args.password, {})
    except xmlrpc.Fault as exc:
        raise CliError(_fault_message(exc)) from exc

    if not uid:
        raise CliError(
            "Authentication failed for database '%s', user '%s'. Check "
            "--db/--username/--password (an API key works as --password too)."
            % (args.db, args.username)
        )

    models = xmlrpc.ServerProxy(object_url, **proxy_kwargs)

    def execute(model, method, *call_args, **kwargs):
        try:
            return models.execute_kw(
                args.db, uid, args.password, model, method,
                list(call_args), kwargs,
            )
        except xmlrpc.Fault as exc:
            raise CliError(_fault_message(exc)) from exc
        except (xmlrpc.ProtocolError, OSError) as exc:
            raise CliError(
                "Connection lost calling %s.%s: %s" % (model, method, exc)
            ) from exc

    return execute


def _fault_message(exc):
    # faultString carries Odoo's own error text -- for a UserError, just
    # the message; for a genuine bug, its full server-side Python
    # traceback. Show it in full either way: that's the actual point of
    # this tool.
    return "Odoo returned an error (fault %s):\n%s" % (exc.faultCode, exc.faultString)


def _unwrap_binary(result):
    if isinstance(result, xmlrpc.Binary):
        return result.data
    if isinstance(result, (bytes, bytearray)):
        return bytes(result)
    if isinstance(result, str):
        try:
            return base64.b64decode(result)
        except Exception as exc:
            raise CliError("Server returned text that isn't base64: %s" % exc) from exc
    raise CliError("Unexpected response type from the server: %r" % type(result))


# -- commands -----------------------------------------------------------

_TEMPLATE_FIELDS = [
    'id', 'name', 'is_builtin', 'active',
    'xlsx_template_filename', 'required_metric_keys', 'required_block_keys',
]


def cmd_list_templates(execute, args):
    templates = execute('exports.report.template', 'search_read', [], fields=_TEMPLATE_FIELDS)
    if not templates:
        print("No template found.")
        return
    width = max(len(t['name']) for t in templates)
    for t in templates:
        flags = [f for f, on in (('builtin', t['is_builtin']), ('archived', not t['active'])) if on]
        flag_str = ' [%s]' % ', '.join(flags) if flags else ''
        print("#%-4s %s%s" % (t['id'], t['name'].ljust(width), flag_str))
        if t['required_metric_keys']:
            print("      metrics: %s" % t['required_metric_keys'])
        if t['required_block_keys']:
            print("      blocks:  %s" % t['required_block_keys'])


def cmd_show_template(execute, args):
    templates = execute('exports.report.template', 'read', [args.id], fields=_TEMPLATE_FIELDS)
    if not templates:
        raise CliError("No template with id %s." % args.id)
    template = templates[0]
    for key in _TEMPLATE_FIELDS:
        print("%-22s %s" % (key + ':', template.get(key)))


def cmd_upload_template(execute, args):
    try:
        with open(args.file, 'rb') as f:
            content = f.read()
    except OSError as exc:
        raise CliError("Could not read %s: %s" % (args.file, exc)) from exc

    values = {
        'name': args.name,
        'xlsx_template': base64.b64encode(content).decode('ascii'),
        'xlsx_template_filename': args.file.rsplit('/', 1)[-1],
    }
    if args.id is not None:
        execute('exports.report.template', 'write', [args.id], values)
        template_id = args.id
        print("Updated template #%s." % template_id)
    else:
        template_id = execute('exports.report.template', 'create', values)
        print("Created template #%s." % template_id)

    detected = execute(
        'exports.report.template', 'read', [template_id],
        fields=['required_metric_keys', 'required_block_keys'],
    )[0]
    metric_keys = detected['required_metric_keys'] or ''
    if metric_keys.startswith('⚠'):  # the "⚠ <message>" warning
        # produced by _compute_required_keys when the file isn't a real
        # .xlsx -- surface it as this command's own error, not a quiet print.
        raise CliError(metric_keys)
    print("  metrics: %s" % (metric_keys or '(none detected)'))
    print("  blocks:  %s" % (detected['required_block_keys'] or '(none)'))


def cmd_generate(execute, args):
    # The date range is the only parameter a generate ever takes -- any
    # tag/PoS-category filtering a template needs is fixed inside the
    # template itself (a {{key["Name"]}} bracket), not chosen at run time.
    params = {
        'date_from': args.date_from,
        'date_to': args.date_to,
    }
    result = execute(
        'exports.report.template', 'action_generate', [args.template_id], params,
    )
    content = _unwrap_binary(result)
    try:
        with open(args.output, 'wb') as f:
            f.write(content)
    except OSError as exc:
        raise CliError("Could not write %s: %s" % (args.output, exc)) from exc
    print("Wrote %s (%d bytes)." % (args.output, len(content)))


def cmd_list_tags(execute, args):
    # Names here, not ids: a template's own {{key["Name"]}} bracket is the
    # only place a tag filter is ever chosen, and it's spelled by name.
    _print_id_name(execute('product.tag', 'search_read', [], fields=['id', 'name']))


def cmd_list_pos_categories(execute, args):
    _print_id_name(execute('pos.category', 'search_read', [], fields=['id', 'name']))


def _print_id_name(records):
    if not records:
        print("(none)")
        return
    for r in records:
        print("#%-4s %s" % (r['id'], r['name']))


# -- CLI wiring -----------------------------------------------------------

def build_parser():
    connection = argparse.ArgumentParser(add_help=False)
    connection.add_argument(
        '--url', default=os.environ.get('ODOO_URL'),
        help="Odoo server URL, e.g. https://odoo.example.org (env: ODOO_URL)",
    )
    connection.add_argument(
        '--db', default=os.environ.get('ODOO_DB'),
        help="Database name (env: ODOO_DB)",
    )
    connection.add_argument(
        '--username', default=os.environ.get('ODOO_USERNAME'),
        help="Odoo login (env: ODOO_USERNAME)",
    )
    connection.add_argument(
        '--password', default=os.environ.get('ODOO_API_KEY'),
        help="Odoo API key (recommended) or password (env: ODOO_API_KEY)",
    )
    connection.add_argument(
        '--insecure-ssl', action='store_true', default=_bool_env('ODOO_INSECURE_SSL'),
        help="Skip TLS certificate verification (env: ODOO_INSECURE_SSL)",
    )
    connection.add_argument('--timeout', type=float, default=30.0, help="Network timeout in seconds (default: 30)")
    connection.add_argument('--debug', action='store_true', help="Print the full Python traceback on unexpected errors")

    parser = argparse.ArgumentParser(
        prog='manage_exports',
        description="Manage exports_materiautheque templates and generate reports over Odoo's XML-RPC API.",
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    p = subparsers.add_parser('list-templates', parents=[connection], help="List every export template")
    p.set_defaults(func=cmd_list_templates)

    p = subparsers.add_parser('show-template', parents=[connection], help="Show one template's detail")
    p.add_argument('--id', type=int, required=True)
    p.set_defaults(func=cmd_show_template)

    p = subparsers.add_parser('upload-template', parents=[connection], help="Create or update a template from a local .xlsx file")
    p.add_argument('--name', required=True)
    p.add_argument('--file', required=True, help="Path to the .xlsx file")
    p.add_argument('--id', type=int, help="Update this existing template instead of creating a new one")
    p.set_defaults(func=cmd_upload_template)

    p = subparsers.add_parser('generate', parents=[connection], help="Run a template and save the generated file locally")
    p.add_argument('--template-id', type=int, required=True, help="See list-templates")
    p.add_argument('--date-from', help="YYYY-MM-DD")
    p.add_argument('--date-to', help="YYYY-MM-DD")
    p.add_argument('--output', required=True, help="Where to write the generated .xlsx")
    p.set_defaults(func=cmd_generate)

    p = subparsers.add_parser('list-tags', parents=[connection], help="List product tags, to find names for a template's {{key[\"Name\"]}} bracket")
    p.set_defaults(func=cmd_list_tags)

    p = subparsers.add_parser('list-pos-categories', parents=[connection], help="List PoS categories, to find names for a template's {{key[\"Name\"]}} bracket")
    p.set_defaults(func=cmd_list_pos_categories)

    return parser


def main(argv=None):
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        resolve_connection(args)
        execute = connect(args)
        args.func(execute, args)
    except CliError as exc:
        print("error: %s" % exc, file=sys.stderr)
        if args.debug:
            traceback.print_exc()
        return 1
    except Exception as exc:  # last resort: never fail silently
        print("error: unexpected %s: %s" % (type(exc).__name__, exc), file=sys.stderr)
        traceback.print_exc()
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
