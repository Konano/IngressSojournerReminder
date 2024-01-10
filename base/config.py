import configparser

config = configparser.RawConfigParser()
config.read('config.ini')

owner = config['BOT'].getint('owner')
accessToken = config['BOT']['accesstoken']
heartbeatURL = config['BOT'].get('heartbeaturl')

WEBHOOK: dict = config._sections['WEBHOOK']
WEBHOOK['port'] = int(WEBHOOK['port'])
