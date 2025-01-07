import random


# checks if username is valid
def check_username(user):
	if user.replace(' ', '').isalpha():
		return True
	return False


# generates random code for new room
def generate_code(rooms):
	print("generate", rooms)
	code = ''
	for i in range(4):
		code += str(random.choice(range(10)))
		print(code)
	if code not in rooms:
		print("entrou")
		return code
	else:
		print("passou")
		return generate_code(rooms)


# checks if user is in another room
def check_online(rooms, current_code, username):
	validator = True
	print("check", rooms)
	for room_code in rooms:
		print(room_code)
		if username in rooms[room_code] and room_code != current_code:
			print(username, rooms[room_code], room_code, "passou", current_code)
			return False
		print("passou")
	return True


# checks if room code is valid
def check_valid(code):
	if code.isnumeric() and len(code) == 4:
		return True
	return False


# checks if room is empty
def check_empty(rooms, code):
	if rooms[code] == []:
		return True
	return False

