import os.path
import sys
from files import connect_to_site
from files import to_share_variables as share


class MyNetStalker:
    parameters = {
        "targets": ("imgur.com", "prnt.sc"),
        "threads": 1,
        "method": {
            1: ("time", "Select the duration: "),
            2: ("links", "Select links qnt: "),
            3: ("size", "Select target size [kb]: ")
        },
        "params": []
    }

    def __init__(self):
        print(share.greeting)
        try:
            self.select_parameters()
            self.start_parse()
        except BaseException as error:
            print(f"Error (__init__): {error}")
            sys.exit(0)

    def select_parameters(self):
        try:
            print(f"{share.green}Available targets: {share.reset}")
            [print(f'{i}) {host}') for i, host in enumerate(self.parameters['targets'], start=1)]
            choice = int(input("Your choice: "))

            assert choice in (1, 2)
        except (TypeError, ValueError, AssertionError) as error:
            print(f"{share.red}Available variants: 1, 2 or 3! {error}{share.reset}")

        except KeyboardInterrupt:
            print(f"{share.red}\nHave a nice day!{share.reset}")
            sys.exit(0)

        else:
            self.parameters['params'].append(self.parameters['targets'][choice - 1])
            print(f"{share.magenta}Using {self.parameters['params'][0]}{share.reset}\n")
            self.select_threads()

    def select_threads(self):
        try:
            self.parameters['threads'] = int(input(
                f"{share.green}Select threads: {share.reset}"
            ))
        except (ValueError, TypeError) as error:
            print(f"{share.red}Value should be numeric! {error}{share.reset}")

        except KeyboardInterrupt:
            print(f"{share.red}\nHave a nice day!{share.reset}")
            sys.exit(0)

        else:
            self.parameters['params'].append(self.parameters['threads'])
            self.choose_method()

    def choose_method(self):
        try:
            print(f"\n{share.green}Choose method: {share.reset}")
            [print(f'{i}) {host[0]}') for i, host in enumerate(self.parameters['method'].values(), start=1)]
            method = int(input("Your choice: "))

            assert method in (1, 2, 3)
        except (TypeError, ValueError, AssertionError) as error:
            print(f"{share.red}Available variants: 1, 2 or 3! {error}{share.reset}")

        except KeyboardInterrupt:
            print(f"{share.red}\nHave a nice day!{share.reset}")
            sys.exit(0)

        else:
            self.parameters['params'].append(self.parameters['method'][method][0])
            print(f"{share.magenta}Using {self.parameters['params'][2]}{share.reset}\n")
            self.value_method(method)

    def value_method(self, method):
        try:
            qnt = int(input(f"{share.green}{self.parameters['method'][method][1]}{share.reset}"))

        except (TypeError, ValueError, IndexError) as error:
            print(f"{share.red}{error}{share.reset}")

        except KeyboardInterrupt:
            print(f"{share.red}\nHave a nice day!{share.reset}")
            sys.exit(0)

        else:
            self.parameters['params'].append(qnt)
            print(f"Target: {share.magenta}{self.parameters['params'][0]}{share.reset} "
                  f"with {share.magenta}{self.parameters['params'][1]} threads{share.reset} "
                  f"for {share.magenta}{self.parameters['params'][2]} {self.parameters['params'][3]}{share.reset}")

    def start_parse(self):
        if not connect_to_site.check_available_site(f"https://{self.parameters['params'][0]}"):
            print(f".....site not available. {share.red}Try another site!{share.reset}")
        else:
            print(f".....site available. {share.red}Starting stalking!{share.reset}")
            # site = parameters[0] threads = parameters[1] method = parameters[2] qnt = parameters[3]
            connect_to_site.create_url(self.parameters['params'][0], self.parameters['params'][1],
                                       self.parameters['params'][2], self.parameters['params'][3])


def create_directory():
    if not os.path.exists('pictures'):
        os.makedirs('pictures')


create_directory()
MyNetStalker()
