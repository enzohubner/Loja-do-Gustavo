import sqlite3
import pandas
import numpy


class DataBase(object):
	# connects (or creates) to the database
	def __init__(self):
		self.connection = sqlite3.connect('components/messages.db', check_same_thread=False)
		self.cursor = self.connection.cursor()

	# creates table for user if not exists
	def create_table(self, user):
		command = f"CREATE TABLE IF NOT EXISTS {user}_table (id INTEGER PRIMARY KEY AUTOINCREMENT, \
						user VARCHAR(20), message TEXT, date DATE, read INTEGER DEFAULT 0)"
		self.cursor.execute(command)

	def mark_as_read(self, client_user):
					command = f"UPDATE {client_user}_table SET read = 1 WHERE read = 0"
					self.cursor.execute(command)
					self.connection.commit()

	def get_client_info(self):
		command = "SELECT id, client_access FROM admin_table"
		self.cursor.execute(command)
		clients_data = self.cursor.fetchall()
		chats = []
		
		for client_id, client_user in clients_data:
			if (self.table_exists("admin") and self.table_exists(client_user)):
			# Get last message and time for each client
				last_msg_command = f"SELECT user, date FROM {client_user}_table ORDER BY id DESC LIMIT 1"
				self.cursor.execute(last_msg_command)
				last_msg = self.cursor.fetchone()
				
				
				unread_command = f"SELECT COUNT(*) FROM {client_user}_table WHERE read = 0 AND user != 'admin'"
				self.cursor.execute(unread_command)
				unread_count = self.cursor.fetchone()[0]
				
				chat_info = {
					'client_name': client_user,
					'id': client_id,  # Now using the actual id from admin_table
					'last_message': last_msg[0] if last_msg else "",
					'last_message_time': last_msg[1] if last_msg else "",
					'unread_messages': unread_count
				}
				chats.append(chat_info)
			
		return chats
	
	'''def create_admin_table(self):
		command = f"CREATE TABLE IF NOT EXISTS admin_table (id INTEGER PRIMARY KEY AUTOINCREMENT, \
			admin_name VARCHAR(20), client_access VARCHAR(20))"
		self.cursor.execute(command)'''

	# appends new message to table
	def append(self, user, msg, date, adm):
		command = f"INSERT INTO {user}_table (user, message, date) VALUES (?, ?, ?)"
		if msg != "":
			if adm:
				self.cursor.execute(command, ("admin", msg, date))
			else:
				self.cursor.execute(command, (user, msg, date))
			self.connection.commit()

	def adm_append(self, cliente):
		command = f"INSERT INTO admin_table (admin_name, client_access) VALUES (?, ?)"
		if cliente != "":
			self.cursor.execute(command, ("admin", cliente))
			self.connection.commit()

	def adm_drop(self, cliente):
		command = f"DELETE FROM admin_table WHERE client_access = ?"
		if cliente != "":
			self.cursor.execute(command, (cliente,))
			self.connection.commit()
			
	# returns all messages sent by the user
	def get(self, user):
		command = f"SELECT * FROM {user}_table"
		messages = pandas.read_sql_query(command, self.connection)
		return numpy.array(messages)

	# deletes all records from user
	def drop_table(self, user):
		command = f"DROP TABLE {user}_table"
		self.cursor.execute(command)
	
	def table_exists(self, user):
		command = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
		self.cursor.execute(command, (f"{user}_table",))
		return self.cursor.fetchone() is not None

	def update_message_status(self, user, id):
		command = f"UPDATE {user}_table SET read = 1 WHERE id = ?"
		self.cursor.execute(command, (id,))
		self.connection.commit()