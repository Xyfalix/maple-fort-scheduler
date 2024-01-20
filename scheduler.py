from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ConversationHandler
from telegram.error import TelegramError
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, time
import pytz

load_dotenv()
TOKEN = os.environ.get('TOKEN')
BOT_USERNAME: os.environ.get('BOT_USERNAME')
MONGO_URI = os.environ.get('DATABASE_URL')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
FORT_SCHEDULE_ARRAY = ["BF1", "BF3", "BF5", "BF5"]
# set states for ConversationHandler for user replacement
SELECT_SECTION, SELECT_USER_TO_REPLACE, TYPE_IN_REPLACEMENT = range(3)
# set state for ConversationHandler for fort acknowledgement
MARK_ATTENDANCE = 0
EXILES_ADMIN_CHAT_ID = -1001646346699
EXILES_MAIN_CHAT_ID = -1001866482989
NICHOLAS_CHAT_ID = 622759708
index = 0 # index to determine which bf list the temp list will be drawing data from

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Commands
# user initiated command
async def add_user_command(update:Update, context: ContextTypes.DEFAULT_TYPE):
    command_text = update.message.text
    print(command_text)
    username = command_text.replace("/adduser", "").strip()

    new_user = User(username=username)
    new_user.save_to_db()

    response = f"User {username} added successfully!"
    print(f"Bot: {response}")
    await update.message.reply_text(response)

# user initiated command
async def view_fort_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await generate_temp_fort_list(context)

    fort_list = context.bot_data.get('fort_list', 'fort list not found')
    await update.message.reply_text(fort_list)

# user initiated command
async def check_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.users
    username = update.message.from_user.username
    user = users.find_one({"username": username})
    check_role = user.get('role')
    print(f"user's role is {check_role}")
    if check_role == "admin":
        try:
            # create blank lists to store telehandles of users who have not acknowledged/cannot attend
            not_acknowledged = []
            cannot_attend = []

            fortlist = db.fortlists
            print("Pulling fort list...")
            # Find the document with the specified name
            temp_fortlist = fortlist.find_one({"name": "temp"})

            if temp_fortlist:
                # Access the data from the BFList document
                for section_name, users in temp_fortlist.items():
                    if section_name not in ['_id', 'name']:
                        # Check for users who have not acknowledged or cannot attend
                        for user in users:
                            if user.get('attendance') == "No":
                                cannot_attend.append(user.get('telehandle'))
                            elif user.get('attendance') == "":
                                not_acknowledged.append(user.get('telehandle'))
                # generate list of non-attendees and mbrs who have not acked
                print(f"list of members who have not acknowledged: {not_acknowledged}")
                print(f"list of members who cannot attend: {cannot_attend}") 
                # Format the list of ppl who cmi
                cmi_list = f"{datetime.today().strftime('%d %b %Y')} Fort\n\n"
                # list of people who cannot attend
                cmi_list += "Mbrs unable to attend:\n"
                for i, user in enumerate(cannot_attend, start=1):
                    cmi_list += f"{i}) @{user}\n"
                cmi_list += "\n"

                # list of people who have not acknowledged
                cmi_list += "Mbrs who have not acknowledged attendance:\n"
                for i, user in enumerate(not_acknowledged, start=1):
                    cmi_list += f"{i}) @{user}\n"
                cmi_list += "\n"

                await update.message.reply_text(cmi_list)

            else:
                print("temp fort list not found in the database")

        except Exception as e:
            print(f"Error querying MongoDB: {e}")
    else:
        # Handle the case where the user doesn't have the role attribute
        await update.message.reply_text("You don't have the necessary privileges to use this command.")
        return ConversationHandler.END  # End the conversation

# scheduled command
# duplicate either BF1, BF3, or BF5 depending on week and set as temp list for viewing and editing
async def duplicate_fort_list(context: ContextTypes.DEFAULT_TYPE):
    global index
    try:
        fortlist = db.fortlists
        print("Pulling fort list...")

        # Find the fort for the week
        fort_list = fortlist.find_one({"name": FORT_SCHEDULE_ARRAY[index]})

        temp_fort_list = fort_list.copy()

        temp_fort_list["name"] = "temp"
        temp_fort_list["_id"] = "temp"

        result = fortlist.insert_one(temp_fort_list)

        index = (index + 1) % len(FORT_SCHEDULE_ARRAY)

        if result.inserted_id:
            print(f"Successfully duplicated BFList. New name: temp")
        else:
            print("Error inserting duplicated BFList into the database")

    except Exception as e:
        print(f"Error querying MongoDB: {e}")
    

# scheduled command
# generate fort list for display on telegram                
async def generate_temp_fort_list(context: ContextTypes.DEFAULT_TYPE):
    try:
        fortlist = db.fortlists
        print("Pulling fort list...")

        # Find the document with the specified name
        bf_list_document = fortlist.find_one({"name": "temp"})

        if bf_list_document:
            # Access the data from the BFList document
            name = FORT_SCHEDULE_ARRAY[index]

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
            
            # store the fort list in context for view and edit user functions
            context.bot_data['fort_list'] = message

        else:
            print("BFList not found in the database")

    except Exception as e:
        print(f"Error querying MongoDB: {e}")


# scheduled command
async def send_fort_list(context: ContextTypes.DEFAULT_TYPE):
    fort_list = context.bot_data.get('fort_list', 'fort list not found')
    # change chat_id to the group that you want to send it to
    await context.bot.send_message(chat_id=622759708, text=fort_list)


# scheduled command
async def delete_temp_fort_list(context: ContextTypes.DEFAULT_TYPE):

    try:
        # Specify the collection (assuming your collection is named 'bf_lists')
        fortlist = db.fortlists
        print("Deleting temporary fort list...")

        # Delete the document with the specified name
        result = fortlist.delete_one({"name": "temp"})

        if result.deleted_count > 0:
            print(f"Successfully deleted temporary BFList with name: temp")
        else:
            print(f"Temporary BFList with name 'temp' not found in the database")
        

    except Exception as e:
        print(f"Error deleting temporary BFList from MongoDB: {e}")

# user initiated command
# Function to handle the /ack command - start
async def start_acknowledge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("start_acknowledge functuon is running!")
    user_not_found = True
    username = update.message.from_user.username
    fortlist = db.fortlists
    temp_fortlist = fortlist.find_one({'name': "temp"})

    # Iterate through each section in searchedsection
    for section_name, users in temp_fortlist.items():
        if section_name not in ['_id', 'name']:
            # Iterate through each user in the section
            for user in users:
                if user.get('telehandle') == username:
                    # Found the user with the specified telehandle
                    print(f"User found in section {section_name}: {user}")
                    user_not_found = False
                    break
    
    if user_not_found:
        print(f"user {username} is not registered for fort today!")
    else:
        keyboard = [
            [
            InlineKeyboardButton('Yes', callback_data='Yes'),
            InlineKeyboardButton('No', callback_data='No')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Please acknowledge fort attendance by selecting Yes or No", reply_markup=reply_markup)

        return MARK_ATTENDANCE

# user initiated command
async def mark_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("mark_attendance function is running!")
    query = update.callback_query
    await query.answer()

    # Retrieve the user response of yes or no from the callback data
    user_response = update.callback_query.data

    username = update.callback_query.from_user.username

    fortlist = db.fortlists
    temp_fortlist = fortlist.find_one({'name': "temp"})

    # Iterate through each section in searchedsection
    for section_name, users in temp_fortlist.items():
        if section_name not in ['_id', 'name']:
            # Iterate through each user in the section
            for user in users:
                if user.get('telehandle') == username:
                    # find the user with the specified telehandle
                    user["attendance"] = user_response
                    break # Exit loop after acknowledgement recorded

        # Update the document in MongoDB
        fortlist.update_one({"name": "temp"}, {"$set": temp_fortlist})

    context.user_data.clear()
    await query.edit_message_text(f"Your response of {user_response} has been recorded, thanks!")  
    return ConversationHandler.END  # End the conversation after replacement


# user initiated command
# Function to handle the /edit command
async def start_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("start_edit function is running")
    # Specify the users collection
    users = db.users
    username = update.message.from_user.username
    print(f'username is {username}')
    # Check if the user has admin privileges
    user = users.find_one({"username": username})
    check_role = user.get('role')
    print(f"user's role is {check_role}")
    if check_role == "admin":
        # Ask the user which section they want to edit
        sections = ["TopToMid", "TopToBtm", "MidToTop", "MidToBtm", "BtmToMid", "BtmToTop", "Standbys", "Cancel"]
        keyboard = [[InlineKeyboardButton(section, callback_data=section)] for section in sections]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Please choose the section you want to edit", reply_markup=reply_markup)

        return SELECT_SECTION
    else:
        # Handle the case where the user doesn't have the role attribute
        await update.message.reply_text("You don't have the necessary privileges to use this command.")
        return ConversationHandler.END  # End the conversation
    

# user initiated command
async def select_mbr_to_replace(update:Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("select_mbr_to_replace function is running")
    # retrieve the section to edit and display usernames for edit
    query = update.callback_query
    await query.answer()

    print(f"query is {query}")
    print(f"query data is {query.data}")

    context.user_data['section'] = query.data

    fortlist = db.fortlists
    bf_list_document = fortlist.find_one({"name": "temp"})
    if bf_list_document:
        section_to_edit = bf_list_document.get(query.data,[])
        print(f"selected section is {section_to_edit}")

        telehandles = []

        # iterate through each object in the array section that has been queried
        for user in section_to_edit:
            print(f"user info is {user}")
            telehandle = user.get("telehandle", "")
            telehandles.append(telehandle)

        # add the cancel option inside telehandles
        telehandles.append("Cancel")
        print(f"telehandles array is {telehandles}")

        # Ask the user which telehandle they want to edit
        keyboard = [[InlineKeyboardButton(telehandle, callback_data=telehandle)] for telehandle in telehandles]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # generate buttons that correspond to the telehandles in the selected section
        await query.edit_message_text("Please select the user you want to replace", reply_markup=reply_markup)

        return SELECT_USER_TO_REPLACE
    
# user initiated command
async def select_replacement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("select_replacement function is running")
    query = update.callback_query
    await query.answer()
    # Retrieve the selected telehandle for replacement from the callback data
    selected_telehandle = update.callback_query.data
    
    # Set the state to EDIT_USER and store the selected telehandle in context
    context.user_data['selected_telehandle'] = selected_telehandle
    
    # Ask the user for the replacement telehandle
    await query.edit_message_text("Please key in the telehandle of the replacement")

    return TYPE_IN_REPLACEMENT


# user initiated command    
async def execute_replacement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("execute_replacement function is running")
    # Retrieve the replacement telehandle from the user's message
    replacement_telehandle = update.message.text
    print(f"replacement_telehandle is {replacement_telehandle}")

    section = context.user_data.get('section', '')
    print(f"selected section is {section}")

    selected_telehandle = context.user_data.get('selected_telehandle', '')
    print(f"selected telehandle is {selected_telehandle}")

    fortlist = db.fortlists
    bf_list_document = fortlist.find_one({"name": "temp"})

    if bf_list_document:
        # Search for the user in the specified section with the selected telehandle
        users_to_replace = bf_list_document.get(section, [])
        print(f"users_to_replace is {users_to_replace}")

        for user in users_to_replace:
            if user.get("telehandle") == selected_telehandle:
                user["telehandle"] = replacement_telehandle
                user["attendance"] = ""
                standbys = bf_list_document.get("Standbys", [])
                bf_list_document["Standbys"] = [user for user in standbys if user.get("telehandle") != selected_telehandle]
                break  # Exit loop after the first replacement
        
        print(f"edited user section is {users_to_replace}")

        # Update the document in MongoDB
        fortlist.update_one({"name": "temp"}, {"$set": bf_list_document})


    context.user_data.clear()
    await update.message.reply_text("User replaced successfully!")  
    return ConversationHandler.END  # End the conversation after replacement

# user initiated command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("cancel function is running")
    # Handling cancel command, reset states and clear user_data
    context.user_data.clear()
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END

# scheduled command
# Define the /send_reminders command
# async def send_ack_reminders(context: ContextTypes.DEFAULT_TYPE):
#     print(f"send_ack_reminders is running")
#     # identify the users who have not acknowledged
#     try:
#         # create blank lists to store telehandles of users who have not acknowledged
#         not_acknowledged = []

#         fortlist = db.fortlists
#         userlist = db.users

#         print("Pulling fort list...")
#         # Find the document with the specified name
#         temp_fortlist = fortlist.find_one({"name": "temp"})

#         if temp_fortlist:
#             # Access the data from the BFList document
#             for section_name, users in temp_fortlist.items():
#                 if section_name not in ['_id', 'name']:
#                     # Check for users who have not acknowledged or cannot attend
#                     for user in users:
#                         if user.get('attendance') == "":
#                             not_acknowledged.append(user.get('telehandle'))
#             # generate list of mbrs who have not acked
#             print(f"list of members who have not acknowledged: {not_acknowledged}")
#             for telehandle in not_acknowledged:
#                 user_data = userlist.find_one({'username': telehandle})
#                 if user_data:
#                     chat_id = user_data.get('chat_id')
#                     print(f"{telehandle}'s chat_id is {chat_id}")
#                     # await context.bot.send_message(chat_id=chat_id, text="Hi there, you have not acknowledged your attendance for fort, please do so ASAP :)")

#         else:
#             print("temp fort list not found in the database")


    # except Exception as e:
    #     print(f"Error querying MongoDB: {e}")

    # chat_ids = [622759708, 243938894, 1317136408]  # Replace with your list of chat IDs

    # for chat_id in chat_ids:
    #     try:
    #         await context.bot.send_message(chat_id, text="Hi there, you have not acknowledged your attendance for fort, please do so ASAP :)")
    #     except TelegramError as e:
    #         if e.message.startswith("Forbidden"):
    #             print(f"Chat ID {chat_id} has restrictions on bot-initiated conversations.")
    #         else:
    #             print(f"Error occurred while sending message to {chat_id}: {e}")


# scheduled command
# async def send_replace_reminders(context: ContextTypes.DEFAULT_TYPE):
#     print(f"send_replace_reminders is running")
#     try:
#             # create blank lists to store telehandles of users who cannot attend
#             cannot_attend = []

#             fortlist = db.fortlists
#             print("Pulling fort list...")
#             # Find the document with the specified name
#             temp_fortlist = fortlist.find_one({"name": "temp"})

#             if temp_fortlist:
#                 # Access the data from the BFList document
#                 for section_name, users in temp_fortlist.items():
#                     if section_name not in ['_id', 'name']:
#                         # Check for users who have cannot attend
#                         for user in users:
#                             if user.get('attendance') == "No":
#                                 cannot_attend.append(user.get('telehandle'))
#                 # generate list of non-attendees and mbrs who have not acked
#                 print(f"list of members who cannot attend: {cannot_attend}") 
#                 # Format the list of ppl who cmi
#                 cmi_list = f"{datetime.today().strftime('%d %b %Y')} Fort\n\n"
#                 # list of people who cannot attend
#                 cmi_list += "Mbrs unable to attend:\n"
#                 for i, user in enumerate(cannot_attend, start=1):
#                     cmi_list += f"{i}) @{user}\n"
#                 cmi_list += "\n"

#                 await context.bot.send_message(chat_id=EXILES_ADMIN_CHAT_ID, text=f"The following members are unable to attend fort, please replace them.\n\n{cmi_list} ")

#             else:
#                 print("temp fort list not found in the database")

#     except Exception as e:
#         print(f"Error querying MongoDB: {e}")
    

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


def main():
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()
    job_queue = app.job_queue
    timezone_utc8 = pytz.timezone('Asia/Singapore')

    # scheduled jobs

    # check if temp list exists and delete it if it exists
    # prod code 
    # remove_temp_fort_list = job_queue.run_daily(delete_temp_fort_list, time=time(hour=23, minute=50), days=(5, 6))

    # test code to check for functionality
    remove_temp_fort_list = job_queue.run_once(delete_temp_fort_list, 5)

    # # select correct fort list and make a copy and set as temp list for viewing and editing
    # prod code
    # make_temp_fort_list = job_queue.run_daily(delete_temp_fort_list, time=time(hour=23, minute=55), days=(5, 6))

    # test code
    make_temp_fort_list = job_queue.run_once(duplicate_fort_list, 10)


    # display fort list at 12mn on sat and sun
    # prod code
    # generate_fort_list = job_queue.run_daily(generate_temp_fort_list, time=time(hour=0, minute=0, second=0), days=(0, 6))
    # display_fort_list = job_queue.run_once(send_fort_list, time=time(hour=0, minute=0, second=40), days=(0, 6))

    # test code
    generate_fort_list = job_queue.run_once(generate_temp_fort_list, 15)
    display_fort_list = job_queue.run_once(send_fort_list, 25)

    # increment index at Mon 12am

    # send reminders to users who have not acknowledged fort from 12pm to 9pm on an hourly basis on sat and sun
    # prod code 
    # run_personal_reminder = job_queue.run_repeating(
    #     callback=send_ack_reminders,
    #     interval=3600,
    #     first=time(hour=12),
    #     last=time(hour=21),
    #     days=(6, 0)
    # )
    
    # test code
    # run_personal_reminder = job_queue.run_repeating(
    #     callback=send_ack_reminders,
    #     interval=60,
    #     first=timezone_utc8.localize(datetime.utcnow()) + timedelta(seconds=10)  # Run after 10 seconds
    # )

    # prod code
    # run_admin_reminder = job_queue.run_repeating(
    #     callback=send_replace_reminders,
    #     interval=3600,
    #     first=time(hour=12),
    #     last=time(hour=21),
    #     days=(6, 0) 
    # )

    # test code
    # run_admin_reminder = job_queue.run_repeating(
    #     callback=send_replace_reminders,
    #     interval=30,
    #     first=timezone_utc8.localize(datetime.utcnow()) + timedelta(seconds=10)  # Run after 10 seconds
    # )

    # Commands
     # Add the /adduser command handler
    app.add_handler(CommandHandler('adduser', add_user_command))
    # allow users to view current fort list
    app.add_handler(CommandHandler('view', view_fort_list))
    # allow admins to view who has not acknowledged attendance or cannot attend
    app.add_handler(CommandHandler('chkatd', check_attendance))


    ack_handler = ConversationHandler(
    entry_points=[CommandHandler("ack", start_acknowledge)],
    states={
        MARK_ATTENDANCE: [
            CallbackQueryHandler(cancel, pattern="^" + "Cancel" + "$" ),
            CallbackQueryHandler(mark_attendance),
        ],
    },
    fallbacks=[CommandHandler("ack", start_acknowledge)],
    per_message=True
    )

    edit_handler = ConversationHandler(
    entry_points=[CommandHandler("edit", start_edit)],
    states={
        SELECT_SECTION: [
            CallbackQueryHandler(cancel, pattern="^" + "Cancel" + "$" ),
            CallbackQueryHandler(select_mbr_to_replace),
            
        ],
        SELECT_USER_TO_REPLACE: [
            CallbackQueryHandler(cancel, pattern="^" + "Cancel" + "$" ),
            CallbackQueryHandler(select_replacement),
        ],
        TYPE_IN_REPLACEMENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, execute_replacement),
        ]
    },
    fallbacks=[CommandHandler("edit", start_edit)],
    per_message=True
    )

    # add fort acknowledgement functionality utilizing Conversation Handler
    app.add_handler(ack_handler)

    # add edit user functionality utilizing Conversation Handler
    app.add_handler(edit_handler)
   
    # Errors
    app.add_error_handler(error)

    # Run the bot
    app.run_polling(poll_interval=5)


if __name__ == '__main__':
    main()

