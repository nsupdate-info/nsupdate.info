# Title:   create-superuser.py
# Link:    https://gist.github.com/c00kiemon5ter/7806c1eac8c6a3e82f061ec32a55c702
# License: None (Public Domain)

from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError

class Command(createsuperuser.Command):
    help = 'Create a superuser with a password non-interactively'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--preserve', dest='preserve', default=False, action='store_true',
            help='Exit normally if the user already exists.',
        )
        parser.add_argument(
            '--password', dest='password', default=None,
            help='Specifies the password for the superuser.',
        )

    def handle(self, *args, **options):
        options.setdefault('interactive', False)
        database = options.get('database')
        password = options.get('password')
        username = options.get('username')
        email = options.get('email')

        if not password or not username or not email:
            raise CommandError(
                    "--username, --password, and --email are required options")

        if username and options.get('preserve'):
            exists = self.UserModel._default_manager.db_manager(database).filter(username=username).exists()
            if exists:
                self.stdout.write("User exists, exiting normally due to --preserve")
                return

        user_data = {
            'username': username,
            'password': password,
            'email': email,
        }

        self.UserModel._default_manager.db_manager(
                database).create_superuser(**user_data)

        if options.get('verbosity', 0) >= 1:
            self.stdout.write("Superuser created successfully.")
