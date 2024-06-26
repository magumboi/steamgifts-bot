import configparser

config = configparser.ConfigParser()

class Configuration:
    def __init__(self):
        self.cookie = ''
        self.discord_webhook = ''
        self.discord_username_id = ''
        self.maxPoint = 60
        self.check_quick_games = True
        self.types_to_check = ['WishList','Copies','Recommended','DLC','All']
        self.priority_point_games_all = [ 5, 10, 15, 20, 25, 30, 40, 50]
        self.priority_point_games_wishlist = [50]
        self.priority_point_games_copies = [50]
        self.priority_point_games_recommended = [50]
        self.priority_point_games_dlc = [50]
        self.priority_point_games_new = [50]
        self.priority_point_games_group = [50]
        self.fillConfig('config/config.ini')
    
    def fillConfig(self, path):
        config.read(path)
        self.cookie = config['DEFAULT']['cookie']
        self.discord_webhook = config['DEFAULT']['discord_webhook'] if config['DEFAULT']['discord_webhook'] else self.discord_webhook
        self.discord_username_id = config['DEFAULT']['discord_username_id'] if config['DEFAULT']['discord_username_id'] else self.discord_username_id
        self.maxPoint = int(config['DEFAULT']['maxPoint']) if config['DEFAULT']['maxPoint'] else self.maxPoint
        self.check_quick_games = config['DEFAULT']['check_quick_games'] is not None and config['DEFAULT']['check_quick_games'].lower() == 'true' if True else False
        self.types_to_check = config['DEFAULT']['types_to_check'].split(',') if config['DEFAULT']['types_to_check'] else self.types_to_check
        self.priority_point_games_all = list(map(int, config['DEFAULT']['priority_point_games_all'].split(','))) if config['DEFAULT']['priority_point_games_all'] else self.priority_point_games_all
        self.priority_point_games_wishlist = list(map(int, config['DEFAULT']['priority_point_games_wishlist'].split(','))) if config['DEFAULT']['priority_point_games_wishlist'] else self.priority_point_games_wishlist
        self.priority_point_games_copies = list(map(int, config['DEFAULT']['priority_point_games_copies'].split(','))) if config['DEFAULT']['priority_point_games_copies'] else self.priority_point_games_copies
        self.priority_point_games_recommended = list(map(int, config['DEFAULT']['priority_point_games_recommended'].split(','))) if config['DEFAULT']['priority_point_games_recommended'] else self.priority_point_games_recommended
        self.priority_point_games_dlc = list(map(int, config['DEFAULT']['priority_point_games_dlc'].split(','))) if config['DEFAULT']['priority_point_games_dlc'] else self.priority_point_games_dlc
        self.priority_point_games_new = list(map(int, config['DEFAULT']['priority_point_games_new'].split(','))) if config['DEFAULT']['priority_point_games_new'] else self.priority_point_games_new
        self.priority_point_games_group = list(map(int, config['DEFAULT']['priority_point_games_group'].split(','))) if config['DEFAULT']['priority_point_games_group'] else self.priority_point_games_group
    
    def setCookie(self, cookie):
        self.cookie = cookie
        
    def setDiscordWebhook(self, discord_webhook):
        self.discord_webhook = discord_webhook
        
    def setDiscordUsernameId(self, discord_username_id):
        self.discord_username_id = discord_username_id
        
    def setMaxPoint(self, maxPoint):
        self.maxPoint = maxPoint
        
    def setCheckQuickGames(self, check_quick_games):
        self.check_quick_games = check_quick_games
        
    def setTypesToCheck(self, types_to_check):
        self.types_to_check = types_to_check
    
    def setPriorityPointGamesAll(self, priority_point_games_all):
        self.priority_point_games_all = priority_point_games_all
    
    def setPriorityPointGamesWishlist(self, priority_point_games_wishlist):
        self.priority_point_games_wishlist = priority_point_games_wishlist
    
    def setPriorityPointGamesCopies(self, priority_point_games_copies):
        self.priority_point_games_copies = priority_point_games_copies
    
    def setPriorityPointGamesRecommended(self, priority_point_games_recommended):
        self.priority_point_games_recommended = priority_point_games_recommended
    
    def setPriorityPointGamesDLC(self, priority_point_games_dlc):
        self.priority_point_games_dlc = priority_point_games_dlc
    
    def setPriorityPointGamesNew(self, priority_point_games_new):
        self.priority_point_games_new = priority_point_games_new
        
    def setPriorityPointGamesGroup(self, priority_point_games_group):
        self.priority_point_games_group = priority_point_games_group
    
    def getCookie(self):
        return self.cookie
    
    def getDiscordWebhook(self):
        return self.discord_webhook

    def getDiscordUsernameId(self):
        return self.discord_username_id
    
    def getMaxPoint(self):
        return self.maxPoint
    
    def getCheckQuickGames(self):
        return self.check_quick_games
    
    def getTypesToCheck(self):
        return self.types_to_check
    
    def getPriorityPointGamesAll(self):
        return self.priority_point_games_all
    
    def getPriorityPointGamesWishlist(self):
        return self.priority_point_games_wishlist
    
    def getPriorityPointGamesCopies(self):
        return self.priority_point_games_copies
    
    def getPriorityPointGamesRecommended(self):
        return self.priority_point_games_recommended
    
    def getPriorityPointGamesDLC(self):
        return self.priority_point_games_dlc
    
    def getPriorityPointGamesNew(self):
        return self.priority_point_games_new
    
    def getPriorityPointGamesGroup(self):
        return self.priority_point_games_group