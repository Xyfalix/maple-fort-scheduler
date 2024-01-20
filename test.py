import json

# Specify the file name
file_name = "bf5.json"

# Use the with open statement to open and read the file
with open(file_name, "r") as file:
    json_data = file.read()

# Parse the JSON data
data = json.loads(json_data)

# Iterate through each section and remove "ign" and "role" properties
for section in data:
    if isinstance(data[section], list):
        for user in data[section]:
            user["attendance"] = user.pop("acknowledged")

# Convert the modified data back to JSON
modified_json_data = json.dumps(data, indent=2)

# Write the modified JSON data back to the original file
with open(file_name, "w") as file:
    file.write(modified_json_data)

print("Original JSON file has been overwritten with the modified data.")
