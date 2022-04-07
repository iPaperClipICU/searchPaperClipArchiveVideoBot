import yaml

class getConfig:
    '''
    获取配置文件
    '''
    def __init__(self) -> None:
        with open('config.yml', 'rb') as r:
            data = yaml.load(r, Loader=yaml.FullLoader)
        r.close()
        
        config = data['config']
        UptimeRobotConfig = data['uptimeRobotConfig']
        
        self.data = data
        # Config
        self.token = config['Token']
        self.TencentKet = {
            'SecretID': config['SecretID'],
            'SecretKEY': config['SecretKEY'],
        }
        self.chatGroup = config['ChatGroup']
        self.logsGroup = config['LogsGroup']
        self.father = config['Father']
        self.debug = config['Debug']
        self.pageMax = config['pageMax']
        # UptimeRobot
        self.UptimeRobotApiKey = UptimeRobotConfig['apiKey']
        self.UptimeRobotID = {
            'Wandering PaperClip 流浪回形针': UptimeRobotConfig['Wandering PaperClip 流浪回形针'],
            '回形针归档站|paperclip.tk': UptimeRobotConfig['回形针归档站|paperclip.tk'],
            '回形针重症监护室': UptimeRobotConfig['回形针重症监护室']
        }
        # SQL
        self.SQL = {
            'host': data['SQLConfig']['host'],
            'user': data['SQLConfig']['user'],
            'password': data['SQLConfig']['password'],
            'db': data['SQLConfig']['db'],
            'charset': data['SQLConfig']['charset']
        }
