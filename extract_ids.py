from pymongo import MongoClient
import os

# Raw data
raw_data = """
id: 622759708 username: Niclim90
id: 144275410 username: babyshark121
id: 1578481704 username: rixsv
id: 365504788 username: BryanIsTheName
id: 1317136408 username: unicorngalore
id: 870779007 username: sKunzzz
id: 1024548217 username: Jrsss
id: 214932297 username: YewGin
id: 436114299 username: GWLeeee
id: 343252078 username: AdamT01
id: 394077209 username: jiangchuann
id: 1268786761 username: MarriedmanM
id: 872047223 username: picobes
id: 265665978 username: s3phy86
id: 154425086 username: redrust
id: 243938894 username: eesmx
id: 273066117 username: xiiintao
id: 1460775874 username: JS_192
id: 1488094423 username: b2darren
id: 709728781 username: CLY1921
id: 839419816 username: isxir
id: 570684287 username: ekimoen
id: 387679149 username: mqwrf
id: 371840086 username: imKnownasR
id: 287825814 username: royango
id: 1178742808 username: bnnpl
id: 201871786 username: dqblake
id: 738788273 username: LCYSH
id: 312053189 username: Exorbis
id: 711076447 username: snvim
id: 631226217 username: HaNNoR
id: 532856586 username: callmebolt
id: 255983599 username: mwqn98
id: 69977824 username: calvinlam
id: 171161904 username: LiewLiew
id: 307965857 username: alvincxx
id: 624926966 username: MercedesKenz
id: 934239017 username: ArthurPuay
id: 1194637227 username: GeraldW
id: 156067205 username: xinray
id: 305685073 username: ongchengwei
id: 729896587 username: Hanghang84
id: 418710182 username: justhql
id: 773208318 username: SWEEYEE
id: 631471283 username: js4896
id: 563316567 username: JWENED
id: 392116654 username: SKYTLSK
id: 785518243 username: mirellexx
id: 328349965 username: XxVelo
id: 2130200133 username: ZariusLxL
id: 139945124 username: xx1001xx
"""
MONGO_URI = os.environ.get('DATABASE_URL')
DATABASE_NAME = os.environ.get('DATABASE_NAME')


client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
users_collection = db.users

# Split the raw data into lines
lines = raw_data.strip().split('\n')

# Extract id and username from each line and create a list of tuples
user_data = [(int(line.split()[1]), line.split()[3]) for line in lines]

# Print the resulting list of user data
print(user_data)

# Insert data into MongoDB collection
for user_id, username in user_data:
    user_object = {
        "username": username,
        "chat_id": user_id,
        "role": ""  }
    users_collection.insert_one(user_object)