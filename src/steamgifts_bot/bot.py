import textwrap
import requests
import json
import pickle
import logging
from datetime import datetime, timedelta

from random import randint as rand 
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from time import sleep
from bs4 import BeautifulSoup
from src.steamgifts_bot.discord_webhook import DiscordNotifications
from src.steamgifts_bot.configuration import Configuration

constant = json.load(open('res/constant.json', 'r', encoding='utf-8'))

logger = logging.getLogger()

# Silence requests and discord_webhook internals as otherwise this example will be too noisy
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

stream_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_format)

logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

class Bot:
    def __init__(self):
        config = Configuration()
        self.cookie = { 'PHPSESSID' : config.getCookie() }
        self.minPoint = 1
        self.maxPoint = config.getMaxPoint()
        self.check_quick_games = config.getCheckQuickGames()
        self.types_to_check = config.getTypesToCheck()
        self.priority_point_games_all = config.getPriorityPointGamesAll()
        self.priority_point_games_wishlist = config.getPriorityPointGamesWishlist()
        self.priority_point_games_copies = config.getPriorityPointGamesCopies()
        self.priority_point_games_recommended = config.getPriorityPointGamesRecommended()
        self.priority_point_games_dlc = config.getPriorityPointGamesDLC()
        self.priority_point_games_new = config.getPriorityPointGamesNew()
        self.priority_point_games_group = config.getPriorityPointGamesGroup()
        self.session = requests.Session()
        self.baseURL = constant['url']
        self.filterURL = constant['filterURL']
        self.discord = DiscordNotifications(config.getDiscordWebhook())
        self.discord_username_id = config.getDiscordUsernameId()
    
    def requestsRetrySession(self, retries=5, backoffFactor=0.3):
        session = self.session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries, 
            connect=retries,
            backoff_factor=backoffFactor, 
            status_forcelist=(500, 502, 504)
        )
        session.headers.update({'User-Agent': constant['userAgent']})
        adapter = HTTPAdapter(max_retries=retry)
        session.mount(constant['http'], adapter)
        session.mount(constant['https'], adapter)
        return session
    
    def getPage(self, url):
        res_soup = requests.get(url, cookies=self.cookie)
        return BeautifulSoup(res_soup.text, 'html.parser')
    
    def updateInfo(self):
        soup = self.getPage(self.baseURL)
        try:
            self.xsrfToken         = soup.find('input', {'name': 'xsrf_token'})['value']
            self.points            = int(soup.find('span', {'class': 'nav__points'}).text)
            self.profileUrl        = soup.find('a', {'class': 'nav__avatar-outer-wrap'})['href']
            self.profilePic        = soup.find('div', {'class': 'nav__avatar-inner-wrap'})['style'].split('background-image:url(')[1].split(')')[0].replace('medium', 'full')
            self.giveaways_entered = self.getGiveawaysEntered()
            self.username          = self.profileUrl.split('/')[2]
            # you can set your own username and avatar for the webhook if you want
            #self.discord.set_webhook_avatar(self.profilePic)
            #self.discord.set_webhook_username(f"{self.username} - {self.points}P")
        except TypeError:
            logger.info("Cookie is not valid ")
            exit()
    
    def entryGift(self, id):
        payload = {
        'xsrf_token' : self.xsrfToken, 
        'do'        : 'entry_insert',
        'code'      : id
        }
        jsonData = json.loads(
            (requests.post('https://www.steamgifts.com/ajax.php',
                          data=payload,
                          cookies=self.cookie
            )).text
        )
        if jsonData['type'] == 'success' :
            return True 
        
    def getGiveawaysEntered(self):
        soup = self.getPage(self.baseURL + self.profileUrl)
        
        summary_table = soup.find('div', {'class': 'featured__table'})
        summary_table_rows = summary_table.find_all('div', {'class': 'featured__table__row'})
        
        for row in summary_table_rows:
            row_left = row.find('div', {'class': 'featured__table__row__left'}).text
            row_right = row.find('div', {'class': 'featured__table__row__right'}).text
            if row_left == 'Giveaways Entered':
                return row_right
            
    def checkNewWonGames(self):
        won_url = f"{self.baseURL}/giveaways/won"
        soup = self.getPage(won_url)
        won_games = soup.find_all('div', {'class': 'table__row-outer-wrap'})
        new_won_games = []
        try:
            with open('wongames.pkl', 'rb') as f:
                stored_games = pickle.load(f)
        except Exception as e:
            with open('wongames.pkl', 'wb') as f:
                pickle.dump([], f)
                stored_games = []
        logger.info(f"Checking for new won games...")
        for game in won_games:
            game_name = game.find('a', {'class': 'table__column__heading'}).text
            if game_name in stored_games:
                logger.info(f"Game already won: {game_name}")
                continue
            else:
                new_won_games.append(game_name)
                stored_games.append(game_name)
                with open('wongames.pkl', 'wb') as f:
                    pickle.dump(stored_games, f)
        for game in new_won_games:
            logger.info(f"Game won: {game} 🎉🎉🎉")
            self.discord.send_message(f"<@{self.discord_username_id}>")
            self.discord.send_embed_info(f"Game won: {game} 🎉🎉🎉", f"[Go check it out]({self.baseURL}/giveaways/won)")
                
    def getGameContent(self):
        processed_count_total = 0
        processed_count_wishlist = 0
        processed_count_copies = 0
        processed_count_recommended = 0
        processed_count_dlc = 0
        processed_count_new = 0
        processed_count_group = 0
        processed_count_all = 0

        for _type in self.types_to_check:
            if self.points == 0:
                break
            self.type = _type
            logger.info(f"Checking {self.type} games...")
            
            if self.type == 'WishList':
                processed_count_wishlist += self.processType(self.type, self.priority_point_games_wishlist)
                processed_count_total += processed_count_wishlist
            elif self.type == 'Copies':
                processed_count_copies += self.processType(self.type, self.priority_point_games_copies)
                processed_count_total += processed_count_copies
            elif self.type == 'Recommended':
                processed_count_recommended += self.processType(self.type, self.priority_point_games_recommended)
                processed_count_total += processed_count_recommended
            elif self.type == 'DLC':
                processed_count_dlc += self.processType(self.type, self.priority_point_games_dlc)
                processed_count_total += processed_count_dlc
            elif self.type == 'New':
                processed_count_new += self.processType(self.type, self.priority_point_games_new)
                processed_count_total += processed_count_new
            elif self.type == 'Group':
                processed_count_group += self.processType(self.type, self.priority_point_games_group)
                processed_count_total += processed_count_group
            elif self.type == 'All':
                processed_count_all += self.processType(self.type, self.priority_point_games_all, 1)
                processed_count_total += processed_count_all
        logger.info(f"Processed {processed_count_total} games")

        description_count = ""
        if processed_count_wishlist > 0:
            description_count += f"Wishlist: {processed_count_wishlist}\n"
        if processed_count_copies > 0:
            description_count += f"Copies: {processed_count_copies}\n"
        if processed_count_recommended > 0:
            description_count += f"Recommended: {processed_count_recommended}\n"
        if processed_count_dlc > 0:
            description_count += f"DLC: {processed_count_dlc}\n"
        if processed_count_new > 0:
            description_count += f"New: {processed_count_new}\n"
        if processed_count_group > 0:
            description_count += f"Group: {processed_count_group}\n"
        if processed_count_all > 0:
            description_count += f"All: {processed_count_all}\n"
    
        if processed_count_total == 0:
            logger.info("No games found, waiting for new games...")
            self.discord.send_embed_red(f"No games found", f"Checking for new games in 15 minutes")
        else:
            self.discord.send_embed_info(f"Processed {processed_count_total} games", description_count)
    
    def processType(self, _type, priority_point_games, days_left=2):
            game_list = self.getAllGameListFromType(_type)
            # filter games before date
            time_left = datetime.now() + timedelta(days=days_left)
            game_list = self.filterGameListBeforeDate(game_list, time_left)
            processed_count = 0      
            for priority_point in priority_point_games:
                
                if self.points == 0:
                    break
                  
                priority_game_list = []
                for game in game_list:
                    game_cost = game.find_all('span', {'class': 'giveaway__heading__thin'})[-1]
                    if game_cost:
                        game_cost = game_cost.getText().replace('(', '').replace(')', '').replace('P', '')
                    else:
                        continue
                    if int(game_cost) <= priority_point:
                        priority_game_list.append(game)
                        game_list.remove(game)
                    
                if len(priority_game_list) == 0:
                    continue

                processed_count += self.processGameList(priority_game_list, _type)
            return processed_count

    def checkIfPointsEnough(self, game_list):
        game_cost_list = []
        for item in game_list:
            game_cost = item.find_all('span', {'class': 'giveaway__heading__thin'})[-1]
            if game_cost:
                game_cost = game_cost.getText().replace('(', '').replace(')', '').replace('P', '')
            else:
                continue
            game_cost_list.append(int(game_cost))
        if len(game_cost_list) > 0:
            self.minPoint = min(game_cost_list)    
    
    def getAllGameListFromType(self, _type, check_one_page=False):
        _page = 1
        game_list_all = []
        while True:
            filtered_url = self.filterURL[_type] % _page
            paginated_url = f"{self.baseURL}/giveaways/{filtered_url}"
            soup = self.getPage(paginated_url)
            pagination_navigation = soup.find('div', {'class': 'pagination__navigation'})

            if not pagination_navigation and _page > 1:
                break

            game_list = soup.find_all('div', {'class': 'giveaway__row-inner-wrap'})
            game_list_faded = soup.find_all('div', {'class': 'giveaway__row-inner-wrap is-faded'})

            for item in game_list:
                if any(item == _item for _item in game_list_faded):
                    continue
                game_list_all.append(item)

            if check_one_page:
                break
            
            _page += 1
        return game_list_all
    
    def getQuickGameList(self):
        game_list = self.getAllGameListFromType('quickCheck', True)
        
        self.checkIfPointsEnough(game_list)
        
        if self.points == 0 or self.points < self.minPoint:
            return
        
        before_date = datetime.now() + timedelta(minutes=30)
        quick_game_list = self.filterGameListBeforeDate(game_list, before_date)
        
        if len(quick_game_list) == 0:
            logger.info("No quick games found")
            self.discord.send_embed_info(f"No quick games found", f"Checking for new quick games in 15 minutes")
            return
        else:
            logger.info(f"Quick games found: {len(quick_game_list)}")
            self.discord.send_embed_info(f"Quick games found: {len(quick_game_list)}", f"Checking for new quick games in 15 minutes")
            if(self.processGameList(quick_game_list, 'Quick') == 0):
                logger.info("No quick games entered")
                self.discord.send_embed_info(f"No quick games entered", f"Not enough points to enter games")
            else:
                logger.info("Quick games entered")
    
    def processGameList(self, game_list, _type):
        processed_count = 0
        for item in game_list:
            if len(item.get('class', [])) == 2 and not self.pinned:
                continue
                
            game_cost = item.find_all('span', {'class': 'giveaway__heading__thin'})[-1]
            if game_cost:
                game_cost = game_cost.getText().replace('(', '').replace(')', '').replace('P', '')
            else:
                continue

            game_name = item.find('a', {'class': 'giveaway__heading__name'}).text
            if self.points - int(game_cost) < 0:
                continue

            elif self.points - int(game_cost) >= 0:
                game_id = item.find('a', {'class': 'giveaway__heading__name'})['href'].split('/')[2]
                game_name_url = item.find('a', {'class': 'giveaway__heading__name'})['href'].split('/')[3]
                logger.info(f"Game url: {self.baseURL}/giveaway/{game_id}/{game_name_url}")
                # check if the game has a thumbnail
                if item.find('a', {'class': 'giveaway_image_thumbnail'}):
                    game_thumbnail = item.find('a', {'class': 'giveaway_image_thumbnail'})['style'].split('background-image:url(')[1].split(')')[0].replace('capsule_184x69', 'header')
                else:
                    game_thumbnail = None
                game_author = item.find('a', {'class': 'giveaway__username'}).text
                game_author_profile_pic = item.find('a', {'class': 'giveaway_image_avatar'})['style'].split('background-image:url(')[1].split(')')[0]
                res = self.entryGift(game_id)
                if res:
                    self.points -= int(game_cost)
                    game_name = item.find('h2', {'class': 'giveaway__heading'}).text
                    logger.info(f"One more game 🎉: {game_name} ({game_cost}P)")
                    self.giveaways_entered = str(int(self.giveaways_entered.replace(',', '')) + 1)
                    processed_count += 1
                    ga_time_end = item.find('div', {'class': 'giveaway__columns'}).find_all('div')[0].find('span')['data-timestamp']
                    ga_time_posted = item.find('div', {'class': 'giveaway__columns'}).find_all('div')[1].find('span')['data-timestamp']
                    ga_entries = item.find('div', {'class': 'giveaway__links'}).findAll('a')[0].text
                    ga_copies = item.find_all('span', {'class': 'giveaway__heading__thin'})[0].text
                    ga_win_chance = self.calculateWinChance(ga_time_end, ga_time_posted, ga_entries, ga_copies)
                    self.discord.send_embed_new_entry(f"{game_name}", game_author, game_author_profile_pic, f"{self.baseURL}/user/{game_author}", f'{int(self.giveaways_entered):,}', _type, self.points,f"{self.baseURL}/giveaway/{game_id}/{game_name_url}", game_thumbnail,ga_time_end,ga_entries,ga_win_chance)
                    sleep(rand(3, 7))
        
        #logger.info(f"Points left: {self.points}")
        return processed_count
    
    def filterGameListBeforeDate(self, game_list, date):
        filtered_game_list = []
        for item in game_list:
            # Extract epoch time left for the giveaway
            time_left = item.find('div', {'class': 'giveaway__columns'}).find_all('div')[0].find('span')['data-timestamp']
            time_left = datetime.fromtimestamp(int(time_left))
            if time_left < date:
                filtered_game_list.append(item)
        return filtered_game_list
    
    def calculateWinChance(self, time_end, time_posted, entries, copies):
        time_left = datetime.fromtimestamp(int(time_end)) - datetime.now()
        time_passed = datetime.now() - datetime.fromtimestamp(int(time_posted))
        num_entries = int(entries.split(' ')[1].replace(',', ''))
        num_copies = 1
        # copies example: '(5,000 Copies)'
        if 'Copies' in copies:
            num_copies = int(copies.split(' ')[0].replace(',', '').replace('(', ''))
        # calculate win chance
        entries_prediction = (num_entries / time_passed.total_seconds()) * time_left.total_seconds()
        win_chance = (1 / (num_entries + 1 + entries_prediction)) * 100 * num_copies
        #truncate to 3 decimal places
        return "{:.3f}".format(win_chance)
    
    def waitForMaxPoints(self):
        while self.points < self.maxPoint:
            logger.info(f"Sleeping 💤 to get {self.maxPoint} points. We have {self.points} points.")
            self.discord.send_embed_red(f"Sleeping 💤", f"Points: {self.points}\nGiveaways entered: {self.giveaways_entered}\nWaiting for {self.maxPoint} points...")
            # Sleep for 15 minutes
            sleep(900)
            self.updateInfo()
            self.session = self.requestsRetrySession()
            if self.points < self.maxPoint and self.check_quick_games:
                self.getQuickGameList()
    
    def start(self):
        while True:
            self.updateInfo()
            logger.info(f"Bot started with {self.points} points")
            self.discord.send_embed_info(f"Bot started", f"Points: {self.points}\nChecking for new games...")
            self.session = self.requestsRetrySession()
            self.checkNewWonGames()
            logger.info("Giveaways Entered: " + self.giveaways_entered + "")
            self.getGameContent()
            self.waitForMaxPoints()
    
