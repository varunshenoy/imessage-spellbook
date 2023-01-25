from imessage_reader import fetch_data
import os
from time import sleep
import uuid
import requests
import json

NUMBER_TO_USER = {"+19168720272": "David", "+18058866285": "Michelle", "+12246195991": "Andy"}

# Refer back to the 'Message Format' section of the article
SENDER_NUMBER_INDEX = 0
MESSAGE_INDEX = 1
DATE_INDEX = 2
MESSAGE_TYPE_INDEX = 3
YOUR_NUMBER_INDEX = 4
WHO_SENT_THIS_TEXT_INDEX = 5

SENT_FROM_ME = 1
SENT_FROM_GROUP = 0

# for every prompt, include the object of what we've learned so far

# After every order
def custom_response(message, curr_order, curr_context):
	"""
	Send response body to API and get a response back
	"""
	# make API call with message
	message_body = message[MESSAGE_INDEX]

	if message_body == "CLEAR":
		order = {
			"delivery_address": "",
			"food_items": [],
			"latest_message": "",
		}
		context = []
		return "Cleared order", order, context
	
	print("here")

	to_feed = json.dumps({
			"input": message_body,
			"order": curr_order,
			"previous_messages": curr_context,
		})

	print(to_feed)

	res = requests.post(
		"https://dashboard.scale.com/spellbook/api/app/9rbz3dzr",
		headers={
			"Content-Type": "application/json",
			"Authorization ": "Basic cld6m3yvu0022sr1abh0cushi",
		},
		data=to_feed
	)


	print()
	print(res.text)

	response_body = json.loads(res.text)["text"]

	# convert to json
	print(response_body)

	response_text = json.loads(response_body)["chat_response"]
	new_order = json.loads(response_body)["new_order"]
	print(response_text)

	order_string = ""
	if "food_items" in new_order:
		for idx, item in enumerate(new_order["food_items"]):
			if "customizations" not in item:
				order_string += f'• {item["name"]}\n'
				continue
			order_string += f'• {item["customizations"][0].capitalize()} {item["name"]}'
			if (item["customizations"][0] == "chicken"):
				order_string += " 🍗"
			elif (item["customizations"][0] == "steak"):
				order_string += " 🥩"
			elif (item["customizations"][0] == "veggie"):
				order_string += " 🥦"
			
			if idx != len(new_order["food_items"]) - 1:
				order_string += "\n"

	response_text = response_text + "\n\n" + "Current Order: \n" + order_string


	curr_context.append(message_body)

	return response_text, new_order, curr_context

seen_messages = set()
order = {
	"delivery_address": "",
	"food_items": [],
	"latest_message": "",
}
context = []
while True: 
	print("Checking for new messages...")

	# We want to continuously monitor messages
	fd = fetch_data.FetchData()
	messages  = fd.get_messages()

	# Collect all the messages in your chat history with mom
	group_messages = []
	for message in messages:
		if message[SENDER_NUMBER_INDEX] in NUMBER_TO_USER.keys():
			if message not in seen_messages:
				seen_messages.add(message)
				group_messages.append(message)


	print("Found {} messages".format(len(group_messages)))

	if len(group_messages) == 0:
		sleep(3)
		continue

	last_message = group_messages[-1] 
	message_body = last_message[SENT_FROM_GROUP]
	print(last_message)
	if last_message[WHO_SENT_THIS_TEXT_INDEX] == SENT_FROM_GROUP:

		response, order, context = custom_response(last_message, order, context)
		if response:
			print("Sending message: {}".format(response))
			os.system(
				"osascript sendMessage.applescript {}"
					.format(f"\"{response}\"")
			)

	sleep(3)