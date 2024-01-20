import json
import requests
import logging
import os
from pymongo import MongoClient
from datetime import datetime, timedelta, time

client = MongoClient(os.environ.get('DATABASE_URL'))
db = client[os.environ.get('DATABASE_NAME')]

bot_token = os.environ.get('BOT_TOKEN')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(requests.__version__)
    
    print(event)
    try:
        body=json.loads(event['body'])
        
        print(body)
        
        # Access the user message sent in telegram
        user_message = body['message']['text']
        chat_id = body['message']['chat']['id']
        print(f'chat_id is {chat_id}')
        print(f'user_message is {user_message}')
        
        # view current fort list
        if chat_id == 622759708 and user_message == "/view":
            view_fort_list(chat_id)
            
        if chat_id == 622759708 and user_message == "/chkatd":
            send_telegram_message(chat_id, "check fort attendance requested")
            
        if chat_id == 622759708 and user_message == "/ack":
            send_telegram_message(chat_id, "mark attendance requested")
        
        if chat_id == 622759708 and user_message == "/edit":
            send_telegram_message(chat_id, "edit fort list requested")
        

        return {
            'statusCode': 200,
        }
    
    except:
        return {
            'statusCode': 200,
            'body': json.dumps('An error occurred!')
        }

def send_telegram_message(chat_id, message):
    api_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    params = {
        'chat_id': chat_id,
        'text': message
    }

    requests.post(api_url, json=params)
    
def view_fort_list(chat_id):
    try:
        fortlist = db.fortlists
        print("Pulling fort list...")

        # Find the document with the specified name
        bf_list_document = fortlist.find_one({"name": "temp"})

        if bf_list_document:
            # Access the data from the BFList document
            name = "Placeholder"

            # Process the data as needed
            print(f"Fort List Name: {name}")

            # Format the message
            message = f"{datetime.today().strftime('%d %b %Y')} Fort\n"
            message += f"Node: FS4\n"
            message += f"Buff: acc candy + 50% buffs + Ty\n\n"

            # Format top to mid
            message += "Top to Mid:\n"
            for i, user in enumerate(bf_list_document.get("TopToMid", []), start=1):
                message += f"{i}) @{user.get('telehandle', 'N/A')}\n"
            message += "\n"

            # Format top to btm
            message += "Top to Btm:\n"
            for i, user in enumerate(bf_list_document.get("TopToBtm", []), start=1):
                message += f"{i}) @{user.get('telehandle', 'N/A')}\n"
            message += "\n"

            # Format mid to top
            message += "Mid to Top:\n"
            for i, user in enumerate(bf_list_document.get("MidToTop", []), start=1):
                message += f"{i}) @{user.get('telehandle', 'N/A')}\n"
            message += "\n"

            # Format mid to btm
            message += "Mid to Btm:\n"
            for i, user in enumerate(bf_list_document.get("MidToBtm", []), start=1):
                message += f"{i}) @{user.get('telehandle', 'N/A')}\n"
            message += "\n"

             # Format btm to mid
            message += "Btm to Mid:\n"
            for i, user in enumerate(bf_list_document.get("BtmToMid", []), start=1):
                message += f"{i}) @{user.get('telehandle', 'N/A')}\n"
            message += "\n"

            # Format btm to top
            message += "Btm to Top:\n"
            for i, user in enumerate(bf_list_document.get("BtmToTop", []), start=1):
                message += f"{i}) @{user.get('telehandle', 'N/A')}\n"
            message += "\n"

            # Format Standbys
            message += "Standbys:\n"
            for i, user in enumerate(bf_list_document.get("Standbys", []), start=1):
                message += f"{i}) @{user.get('telehandle', 'N/A')}\n"
            
            # send fort list to user
            send_telegram_message(chat_id, message)

        else:
            print("BFList not found in the database")

    except Exception as e:
        print(f"Error querying MongoDB: {e}")