from discord_webhook import DiscordWebhook, DiscordEmbed
import textwrap

class DiscordNotifications:
    def __init__(self, discord_webhook):
        self.webhook = DiscordWebhook(
            url=discord_webhook, 
            rate_limit_retry=True,
            username="SteamGifts Bot",
            avatar_url="https://cdn.discordapp.com/emojis/1250234594129739838.webp?size=128&quality=lossless"
        )
        
    def set_webhook_avatar(self, avatar_url):
        self.webhook.avatar_url = avatar_url
        
    def set_webhook_username(self, username):
        self.webhook.username = username
        
    def send_message(self, message):
        self.webhook.content = message
        self.webhook.execute()
        self.webhook.content = None
        
    def send_embed_info(self, title, description):
        embed = DiscordEmbed(title=title, description=description, color="03b2f8")
        self.webhook.add_embed(embed)
        self.webhook.execute()
        self.webhook.embeds = []
    
    def send_embed_red(self, title, description):
        embed = DiscordEmbed(title=title, description=description, color="ff0000")
        self.webhook.add_embed(embed)
        self.webhook.execute()
        self.webhook.embeds = []
        
    def send_embed_new_entry(self, title, giveaway_author, giveaway_author_profile_pic, giveaway_author_profile_url, giveaways_entered, giveaway_type, points, giveaway_url, thumbnail_url, time_left,entries, win_chance):
        embed = DiscordEmbed(title=title, color="f8f803")
        embed.set_author(name=giveaway_author, icon_url=giveaway_author_profile_pic, url=giveaway_author_profile_url)
        steam_id = thumbnail_url.split('/')[-2]
        if thumbnail_url is not None:
            steam_url = f"https://store.steampowered.com/app/{steam_id}/"
        else:
            steam_url = "https://store.steampowered.com/"
        #<:net:1250234594129739838>  [Giveaway page]({giveaway_url})
        description = textwrap.dedent(f"""
            <:steam:1250196047884456038> [Steam page]({steam_url})
            
            ⏰ Giveaway ends <t:{time_left}:R>
            🏷️{entries}
            🏆 {win_chance}%
            
        """)
        embed.set_description(description)
        embed.add_embed_field(name="Giveaways entered", value=giveaways_entered, inline=True)
        embed.add_embed_field(name="Points left", value=f"{points}P", inline=True)
        embed.add_embed_field(name="Game type", value=giveaway_type, inline=True)
        embed.set_url(giveaway_url)
        embed.set_thumbnail(url=f"https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/{steam_id}/logo.png")
        embed.set_image(url=thumbnail_url)
        embed.set_footer(text="SteamGifts Bot", icon_url="https://cdn.discordapp.com/emojis/1250234594129739838.webp?size=44&quality=lossless")
        embed.set_timestamp()
        self.webhook.add_embed(embed)
        self.webhook.execute()
        self.webhook.embeds = []
        
            
