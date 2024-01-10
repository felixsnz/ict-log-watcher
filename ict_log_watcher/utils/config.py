import configparser
config = configparser.ConfigParser()
config.read('config.ini')

ict_logs_path = config['paths']['ict_logs']
server = config['database']['server']
database = config['database']['database']
user = config['database']['user']
password = config['database']['password']
results_table_name = config['database']['results_table']

