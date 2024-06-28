# steamgifts-bot

![](https://i.imgur.com/yNatDAl.png)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install dependencies.

```bash
pip install -r requirements.txt
```

## Usage

Fill config/configure.ini file with your details

```markdown
[DEFAULT]
; PHPSESSID cookie from the browser (required for the bot to work)
cookie = 
; Discord webhook URL (optional)
discord_webhook = 
; Discord id of the user to send the message to (optional)
discord_username_id = 
; Max points to start entering giveaways
maxPoint = 60
; Check for games cheaper than 5P and end in less than 30 minutes
check_quick_games = true
; Recognized types: WishList, Copies, Recommended, DLC, All, New, Group
; Games will be checked in the order they are listed here
types_to_check = WishList,Copies,Recommended,DLC,All
; Priority points for each type
; The bot will check the games with points in the order they are listed here
priority_point_games_all = 5, 10, 15, 20, 25, 30, 40, 50
priority_point_games_wishlist = 50
priority_point_games_copies = 50
priority_point_games_recommended = 50
priority_point_games_dlc = 50
priority_point_games_new = 50
priority_point_games_group = 50
```

Execute main.py
```bash
python main.py
```
Enjoy!!

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.
