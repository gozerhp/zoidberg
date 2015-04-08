import argparse
import logging
import zoidberg

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', dest='config_file',
                    default='./etc/zoidberg.yaml',
                    help='config yaml path')
parser.add_argument('-v', '--verbose', dest='verbose',
                    action='store_true')
options = parser.parse_args()

log_level = logging.INFO

if options.verbose:
	log_level = logging.DEBUG

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s', level=log_level)

server = zoidberg.Zoidberg(options.config_file)
server.run()
