import sys
from argparse import ArgumentParser, Namespace
from injectark import Injectark
from ..core import Config


class Cli:
    def __init__(self, config: Config, resolver: Injectark) -> None:
        self.config = config
        self.resolver = resolver

        args = self.parse()
        args.func(args)

    def parse(self) -> Namespace:
        parser = ArgumentParser('Authark')
        subparsers = parser.add_subparsers()

        # Setup
        setup_parser = subparsers.add_parser(
            'setup', help='Prepare system environment.')
        setup_parser.set_defaults(func=self.setup)

        # Provision
        provision_parser = subparsers.add_parser(
            'provision', help='Provision new tenants.')
        provision_parser.add_argument('name')
        provision_parser.set_defaults(func=self.provision)

        # Serve
        serve_parser = subparsers.add_parser(
            'serve', help='Start HTTP server.')
        serve_parser.set_defaults(func=self.serve)

        # Terminal
        terminal_parser = subparsers.add_parser(
            'terminal', help='Open terminal interface.')
        terminal_parser.set_defaults(func=self.terminal)

        # Load
        load_parser = subparsers.add_parser(
            'load', help='Load items from file.')
        load_parser.add_argument('input_file')
        load_parser.add_argument('-s', '--source')
        load_parser.add_argument('-p', '--password_field')
        load_parser.add_argument('-t', '--tenant')
        load_parser.set_defaults(func=self.load)

        if len(sys.argv[1:]) == 0:
            parser.print_help()
            parser.exit()

        return parser.parse_args()

    def setup(self, args: Namespace) -> None:
        print('...SETUP:::', args)
        print('...END SETUP:::')

    def provision(self, args: Namespace) -> None:
        print('...PROVISION::::')
        tenant_supplier = self.resolver['TenantSupplier']
        tenant_dict = {'name': args.name}
        tenant_supplier.create_tenant(tenant_dict)
        print('...END PROVISION::::')

    def serve(self, args: Namespace) -> None:
        print('...SERVE:::', args)
        from ..web import create_app, ServerApplication

        app = create_app(self.config, self.resolver)
        gunicorn_config = self.config['gunicorn']
        ServerApplication(app, gunicorn_config).run()

    def terminal(self, args: Namespace) -> None:
        print('...TERMINAL:::', args)
        from ..terminal import Main, Context

        context = Context(self.config, self.resolver)
        app = Main(context)
        app.run()

    def load(self, args: Namespace) -> None:
        print('::::::LOAD:::::', args.input_file)
        input_file = args.input_file
        source = args.source
        if not source:
            source = 'erp.users'
        password_field = args.password_field
        if not password_field:
            password_field = 'password'
        tenant = args.tenant
        if not tenant:
            print('A tenant is required.')
            return

        tenant_supplier = self.resolver.resolve('TenantSupplier')
        tenant_dict = next(
            iter(tenant_supplier.search_tenants(
                [('slug', '=', tenant)])), None)

        session_coordinator = self.resolver.resolve('SessionCoordinator')
        session_coordinator.set_tenant(tenant_dict)

        import_coordinator = self.resolver.resolve('ImportCoordinator')
        import_coordinator.import_users(input_file, source, password_field)
