from docopt import docopt
import mocker

if __name__ == '__main__':
    arguments = docopt(mocker.__doc__, version=mocker.__version__)
    print(arguments)
