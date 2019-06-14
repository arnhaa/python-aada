import os
import sys
import logging
import argparse

from botocore.session import Session, get_session
from . import __version__
from .login import Login
from .configure import Configure

LOG = logging.getLogger('aada')
LOG_FORMAT = (
    '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')


class Cli(object):
    COMMAND_CHOICES = ('login', 'configure')

    def __init__(self, args=None):
        if args is None:
            self.args = sys.argv[1:]
        else:
            self.args = args
        self._session = None
        self._parsed_args = None
        self._role = None
        self._account = None
        self._debug = False
        self._headless = True

    def _create_parser(self):
        parser = argparse.ArgumentParser(
            prog='aada',
            description='Azure AD AWS CLI Authentication',
            usage='aada <command> [<args>].\n\nAllowed commands are:\n'
                  'login       Login to Azure AD and assume AWS Role\n'
                  'configure   Configure Azure AD and profile')
        parser.add_argument("-v", "--version", action="version",
                            version="{}".format(__version__))
        parser.add_argument('-d', '--debug', help='Debugging output',
                            action='store_true')
        parser.add_argument('-n', '--no-headless', help='Not in headless mode',
                            action='store_true')
        parser.add_argument('-p', '--profile', help='AWS Profile')
        parser.add_argument('-r', '--role', help='Role to pick')
        parser.add_argument('-a', '--account', help='Account to pick')
        parser.add_argument('command', choices=self.COMMAND_CHOICES)
        return parser

    def _login(self):
        login = Login(self._session, self._role, self._account, self._debug,
                      self._headless)
        return login()

    def _configure(self):
        configure = Configure(self._session)
        return configure(self._parsed_args)

    def main(self):
        parser = self._create_parser()
        self._parsed_args = parser.parse_args(self.args)

        homed = os.getenv("HOME")
        LOGFILEN = os.path.join(homed, "clivy.txt")
        f = open(LOGFILEN, "a+")
        f.write("starts \n")

        if self._parsed_args.profile:
            self._session = Session(profile=self._parsed_args.profile)
            f.write("session \n" + self._session)
        else:
            self._session = get_session()
            f.write("elsesession \n" + self._session)

        if self._parsed_args.debug:
            self._debug = True
            f.write("debug \n" + self._debug)

        if self._parsed_args.no_headless:
            self._headless = False
            f.write("headless \n" + self._headless)

        if self._parsed_args.role:
            self._role = self._parsed_args.role
            f.write("role \n" + self._role)

        if self._parsed_args.account:
            self._account = self._parsed_args.account
            f.write("account \n" + self._account)

        f.close()

        return self.__getattribute__('_{}'.format(self._parsed_args.command))()


def main():
    cli = Cli()
    return cli.main()


if __name__ == "__main__":
    sys.exit(main())
