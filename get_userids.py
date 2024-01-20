from telethon import TelegramClient
import asyncio

api_id = "24143587" 
api_hash = "f5cbe44c18b32dc5d54ae3e2c407d9af" # Your APP_ID
bot_token = "6986262473:AAGkbAyzypzNJ_6vsPzuUSDvY7glThxL3FA" # (via botfather, you can alternatively sign in as a user)
group_id = -1001646346699

async def get_users(client, group_id):
    async for user in client.iter_participants(group_id):
        if not user.deleted:
            print("id:", user.id, "username:", user.username) 

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

with bot:
    asyncio.get_event_loop().run_until_complete(get_users(bot, group_id))