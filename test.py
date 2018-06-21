from configparser import ConfigParser

parser = ConfigParser()
# parser.read('config.ini')

print(parser.get('bug_tracker', 'url'))

