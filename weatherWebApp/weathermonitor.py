from __future__ import with_statement
from google.appengine.api import users, files, images
import webapp2
from google.appengine.ext import ndb
import urllib
import time
import re
import jinja2
import os
import json
import webscraper
import datetime

JINJA_ENVIRONMENT = jinja2.Environment(
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions = ['jinja2.ext.autoescape'],
	autoescape = True)

class UserList(ndb.Model):
	userName = ndb.StringProperty()
	password = ndb.StringProperty()
	date = ndb.StringProperty()
	rainy = ndb.BooleanProperty()
	temperature = ndb.StringProperty()
	address = ndb.StringProperty()

class Travel(ndb.Model):
	userName = ndb.StringProperty()
	address = ndb.StringProperty()
	date = ndb.StringProperty()

class TaskQueue(ndb.Model):
	userName = ndb.StringProperty()
	content = ndb.StringProperty()
	currTemp = ndb.StringProperty()
	tmrTemp = ndb.StringProperty()

class CalendarEntry:
	def __init__(self, usrName, currDate, currAddr):
		self.usrName = usrName
		self.currDate = currDate
		self.currAddr = currAddr

class TaskEntry:
	def __init__(self, usrName, currContent, currTemp, tmrTemp):
		self.usrName = usrName
		self.currContent = currContent
		self.currTemp = currTemp
		self.tmrTemp = tmrTemp

class UserListEntry:
	def __init__(self, usrName, pwd, date, rainy, temperature, address):
		self.usrName = usrName
		self.pwd = pwd
		self.date = date
		self.rainy = rainy
		self.temperature = temperature
		self.address = address

class Threshold(ndb.Model):
	value = ndb.IntegerProperty()

InitialThreshold = Threshold(value = 10)
InitialThreshold.put()

def getTodayDate():
	todayDate = datetime.datetime.now() - datetime.timedelta(hours=6)
	todayDate = str(todayDate.date())
	todayDate = todayDate.replace('-', '/')
	return todayDate

def getTmrDate():
	tmrDate = datetime.datetime.now() + datetime.timedelta(days=1) - datetime.timedelta(hours=6)
	tmrDate = str(tmrDate.date())
	tmrDate = tmrDate.replace('-', '/')
	return tmrDate

class MainPage(webapp2.RequestHandler):
	def get(self):

		userList = []
		usrQueue = UserList.query()
		for usr in usrQueue:
			newUsrListEntry = UserListEntry(usr.userName, usr.password, usr.date, usr.rainy, usr.temperature, usr.address)
			userList.append(newUsrListEntry)

		calendarList = []
		travelQueue = Travel.query()
		for usr in travelQueue:
			newCalendarEvent = CalendarEntry(usr.userName, usr.date, usr.address)
			calendarList.append(newCalendarEvent)

		taskList = []
		taskQueue = TaskQueue.query()
		for usr in taskQueue:
			newTaskEntry = TaskEntry(usr.userName, usr.content, usr.currTemp, usr.tmrTemp)
			taskList.append(newTaskEntry)

		threshold = 0
		for t in Threshold.query():
			threshold = t.value
			break

		template_values = {
			'usrList' : userList,
			'calendarList' : calendarList,
			'taskList' : taskList,
			'threshold' : threshold
		}
		template = JINJA_ENVIRONMENT.get_template('main.html')

		self.response.write(template.render(template_values))

class CreateCalendar(webapp2.RequestHandler):
	def get(self):
		self.response.write(open('createCalendar.html').read())

class CreateUser(webapp2.RequestHandler):
	def get(self):
		self.response.write(open('createUser.html').read())

class SetThreshold(webapp2.RequestHandler):
	def get(self):

		threshold = 0
		for t in Threshold.query():
			threshold = t.value
			break

		template_values = {
			'threshold' : threshold
		}
		template = JINJA_ENVIRONMENT.get_template('setThreshold.html')

		self.response.write(template.render(template_values))

class SetThresholdHandler(webapp2.RequestHandler):
	def post(self):
		threshold = self.request.get('newThreshold')

		found = False
		for t in Threshold.query():
			found = True
			t.value = int(threshold)
			t.put()
			break

		if not found:
			newThreshold = Threshold(value = threshold)
			newThreshold.put()

		print threshold
		self.redirect('/')

# Delete user from user list
class DeleteUserHandler(webapp2.RequestHandler):
	def post(self):
		deletedEntryList = []
		deletedEntryList = self.request.get_all('deleteCheckbox')
		
		usrQuery = UserList.query()
		for usr in usrQuery:
			if str(usr.userName) in deletedEntryList:
				usr.key.delete()

		self.redirect('/')

# Delete user from travel calendar
class DeleteCalendarHandler(webapp2.RequestHandler):
	def post(self):
		deletedEntryList = []
		deletedEntryList = self.request.get_all('deleteCheckbox')
		
		usrQuery = Travel.query()
		for usr in usrQuery:
			if str(usr.userName) in deletedEntryList:
				usr.key.delete()

		self.redirect('/')

# Delete user from task queue
class DeleteTaskHandler(webapp2.RequestHandler):
	def post(self):
		deletedEntryList = []
		deletedEntryList = self.request.get_all('deleteCheckbox')
		
		usrQuery = TaskQueue.query()
		for usr in usrQuery:
			if str(usr.userName) in deletedEntryList:
				usr.key.delete()

		self.redirect('/')

# Create user entry
class CreateUserHandler(webapp2.RequestHandler):
	def post(self):
		usrName = self.request.get('usrName')
		usrPwd = self.request.get('pwd')
		currDate = self.request.get('date')
		rainy = self.request.get('rainy')
		currTemp = self.request.get('temperature')
		currAddr = self.request.get('addr')

		rainy = rainy.lower()
		if rainy == 'yes':
			rainy = True
		else:
			rainy = False

		usrQuery = UserList.query()
		exist = False
		for usr in usrQuery:
			if usr.userName == usrName:
				exist = True
				usr.password = usrPwd
				usr.date = currDate
				usr.rainy = rainy
				usr.temperature = currTemp
				usr.address = currAddr
				usr.put()
				break

		if not exist:
			newUsrEntry = UserList(userName = usrName, password = usrPwd, date = currDate, rainy = rainy, temperature = currTemp, address = currAddr)
			newUsrEntry.put()

		self.redirect('/')

# Create calendar entry
class CreateEntryHandler(webapp2.RequestHandler):
	def post(self):
		usrName = self.request.get('usrName')
		currDate = self.request.get('date')
		currAddr = self.request.get('address')

		found = False
		originalAddr = currAddr
		usrListQuery = UserList.query()
		for usr in usrListQuery:
			if usr.userName == usrName:
				found = True
				originalAddr = usr.address

		if not found:
			res = webscraper.getWeatherData(originalAddr)
			
			dateNow = getTodayDate()
			newUserListEntry = UserList(userName = usrName, password = "default password", date = dateNow, rainy = res['rain'], temperature = res['today'], address = originalAddr)
			newUserListEntry.put()
			newCalendarEntry = Travel(userName = usrName, address = currAddr, date = currDate)
			newCalendarEntry.put()

		else:
			newCalendarEntry = Travel(userName = usrName, address = currAddr, date = currDate)
			newCalendarEntry.put()

			tmrDate = getTmrDate()		

			threshold = 0
			for t in Threshold.query():
				threshold = t.value
				break

			if tmrDate == currDate:
				tmrRes = webscraper.getWeatherData(currAddr)
				tmrTemp = tmrRes['tomorrow']
				todayRes = webscraper.getWeatherData(originalAddr)
				todayTemp = todayRes['today']

				tmrRainy = tmrRes['rain']
				if tmrRainy:
					newTaskQueueEntry = TaskQueue(userName = usrName, content = "Raining in " + currAddr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
					newTaskQueueEntry.put()

				delta = float(float(tmrTemp) - float(todayTemp))
				if delta >= threshold:
					newTaskQueueEntry = TaskQueue(userName = usrName, content = "Hot in " + currAddr, currTemp = todayTemp, tmrTemp = tmrTemp)
					newTaskQueueEntry.put()
				elif delta <= -threshold:
					newTaskQueueEntry = TaskQueue(userName = usrName, content = "Cold in " + currAddr, currTemp = todayTemp, tmrTemp = tmrTemp)
					newTaskQueueEntry.put()

		self.redirect('/')

class PollingHandler(webapp2.RequestHandler):
	def post(self):

		currUser = self.request.get('userName')
		deleteList = []

		taskQuery = TaskQueue.query()
		for task in taskQuery:
			if task.userName == currUser:
				self.response.write(task.content)
				deleteList.append(task)

		for task in deleteList:
			task.key.delete()

# Timed execution
class WebScraper(webapp2.RequestHandler):
	def get(self):

		threshold = 0
		for t in Threshold.query():
			threshold = t.value
			break

		usrQuery = UserList.query()
		for usr in usrQuery:
			res = webscraper.getWeatherData(usr.address)
			usr.date = getTodayDate()
			usr.rainy = res['rainToday']
			usr.temperature = res['today']
			usr.put()
			
			todayTemp = res['today']
			tmrTemp = res['tomorrow']

			tmrRainy = res['rain']
			if tmrRainy:
				newTaskQueueEntry = TaskQueue(userName = usrName, content = "Raining in " + currAddr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
				newTaskQueueEntry.put()

			delta = float(tmrTemp) - float(todayTemp)
			if delta >= threshold:
				newTaskQueueEntry = TaskQueue(userName = usrName, content = "Hot in " + usr.addr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
				newTaskQueueEntry.put()
			elif delta <= -threshold:
				newTaskQueueEntry = TaskQueue(userName = usrName, content = "Cold in " + usr.addr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
				newTaskQueueEntry.put()
		

		tmrDate = getTmrDate()
		travelQuery = Travel.query()
		for travel in travelQuery:
			# About to travel
			if tmrDate == travel.date:
				tmrRes = webscraper.getWeatherData(travel.address)
				tmrTemp = tmrRes['tomorrow']

				currAddr = travel.address
				newUsrQuery = UserList.query()
				for q in newUsrQuery:
					if q.userName == travel.userName:
						currAddr = q.address
						break

				todayRes = webscraper.getWeatherData(currAddr)
				todayTemp = todayRes['today']

				delta = float(float(tmrTemp) - float(todayTemp))
				if delta >= threshold:
					newTaskQueueEntry = TaskQueue(userName = usrName, content = "Hot in " + currAddr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
					newTaskQueueEntry.put()
				elif delta <= -threshold:
					newTaskQueueEntry = TaskQueue(userName = usrName, content = "Cold in " + currAddr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
					newTaskQueueEntry.put()

				tmrRainy = tmrRes['rain']
				if tmrRainy:
					newTaskQueueEntry = TaskQueue(userName = usrName, content = "Raining in " + currAddr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
					newTaskQueueEntry.put()

		self.redirect('/')

class CalendarHandler(webapp2.RequestHandler):
	def post(self):
		username = self.request.get('userName')
		addr = self.request.get('Addr')
		dateOfTravel = self.request.get('Date')

		currAddr = addr
		currDate = dateOfTravel
		usrName = username

		found = False
		originalAddr = currAddr
		usrListQuery = UserList.query()
		for usr in usrListQuery:
			if usr.userName == usrName:
				found = True
				originalAddr = usr.address

		if not found:
			res = webscraper.getWeatherData(originalAddr)

			dateNow = getTodayDate()
			newUserListEntry = UserList(userName = usrName, password = "default password", date = dateNow, rainy = res['rain'], temperature = res['today'], address = originalAddr)
			newUserListEntry.put()
			newCalendarEntry = Travel(userName = usrName, address = currAddr, date = currDate)
			newCalendarEntry.put()

		else:
			newCalendarEntry = Travel(userName = usrName, address = currAddr, date = currDate)
			newCalendarEntry.put()

			tmrDate = getTmrDate()

			threshold = 0
			for t in Threshold.query():
				threshold = t.value
				break

			if tmrDate == currDate:

				tmrRes = webscraper.getWeatherData(currAddr)
				tmrTemp = tmrRes['tomorrow']
				todayRes = webscraper.getWeatherData(originalAddr)
				todayTemp = todayRes['today']

				tmrRainy = tmrRes['rain']
				if tmrRainy:
					newTaskQueueEntry = TaskQueue(userName = usrName, content = "Raining in " + currAddr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
					newTaskQueueEntry.put()

				delta = float(float(tmrTemp) - float(todayTemp))
				if delta >= threshold:
					newTaskQueueEntry = TaskQueue(userName = usrName, content = "Hot in " + currAddr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
					newTaskQueueEntry.put()
				elif delta <= -threshold:
					newTaskQueueEntry = TaskQueue(userName = usrName, content = "Cold in " + currAddr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
					newTaskQueueEntry.put()

		self.response.write("YES")

# Update location
class AndroidRequestHandler(webapp2.RequestHandler):
	def post(self):
		userName = self.request.get('userName')
		newAddr = self.request.get('addr')

		usrQuery = UserList.query()
		for usr in usrQuery:
			if usr.userName == userName:
				usr.address = newAddr

				tmrDate = getTmrDate()
				currDate = usr.date
		
				threshold = 0
				for t in Threshold.query():
					threshold = t.value
					break

				# Change of location might generate alarm
				if tmrDate == currDate:
					tmrRes = webscraper.getWeatherData(newAddr)
					tmrTemp = tmrRes['tomorrow']
					todayTemp = usr.temperature

					tmrRainy = tmrRes['rainy']
					if tmrRainy:
						newTaskQueueEntry = TaskQueue(userName = usrName, content = "Raining in " + currAddr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
						newTaskQueueEntry.put()

					delta = float(float(tmrTemp) - float(todayTemp))
					if delta >= threshold:
						newTaskQueueEntry = TaskQueue(userName = usrName, content = "Hot in " + newAddr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
						newTaskQueueEntry.put()
					elif delta <= -threshold:
						newTaskQueueEntry = TaskQueue(userName = usrName, content = "Cold in " + newAddr + " tomorrow!", currTemp = todayTemp, tmrTemp = tmrTemp)
						newTaskQueueEntry.put()

				usr.put()
				break

		self.response.write('YES')

class AndroidWeatherRequestHandler(webapp2.RequestHandler):
	def post(self):
		username = self.request.get('userName')
		addr = self.request.get('addr')

		res = webscraper.getWeatherData(addr)
		self.response.write(res['currTemp'])

class AndroidVerificationHandler(webapp2.RequestHandler):
	def post(self):
		username = self.request.get('userName')
		pwd = self.request.get('password')
		signUp = self.request.get('Type')
		addr = self.request.get('Addr')

		# Sign up
		if signUp == "signUp":
			usrQuery = UserList.query()
			exist = False
			for usr in usrQuery:
				if usr.userName == username:
					exist = True
					break

			if exist:
				self.response.write('NO')
				return
			else:
				currDate = getTodayDate()
				res = webscraper.getWeatherData(addr)
				
				newUsrEntry = UserList(userName = username, password = pwd, date = currDate, rainy = res['rain'], temperature = res['today'], address = addr)
				newUsrEntry.put()
				self.response.write('YES')
				return
		# Sign in
		else:
			usrQuery = UserList.query()
			exist = False
			for usr in usrQuery:
				if usr.userName == username:
					if usr.password == pwd:
						exist = True
						currDate = getTodayDate()
						res = webscraper.getWeatherData(addr)

						usr.date = currDate
						usr.rainy = res['rain']
						usr.temperature = res['today']
						usr.address = addr
						usr.put()
						self.response.write('YES')
						return
					else:
						self.response.write('NO')
						return
			
			if not exist:
				self.response.write('NO')
				return



application = webapp2.WSGIApplication([
	('/', MainPage),
	('/createUser', CreateUser),
	('/createCalendar', CreateCalendar),
	('/setThreshold', SetThreshold),
	('/createEntryHandler', CreateEntryHandler),
	('/createUserHandler', CreateUserHandler),
	('/deleteUserListHandler', DeleteUserHandler),
	('/deleteCalendarHandler', DeleteCalendarHandler),
	('/deleteTaskHandler', DeleteTaskHandler),
	('/setThresholdHandler', SetThresholdHandler),
	('/webScraper', WebScraper),
	('/calendarHandler', CalendarHandler),
	('/androidVerificationHandler', AndroidVerificationHandler),
	('/androidWeatherRequestHandler', AndroidWeatherRequestHandler),
	('/androidRequestHandler', AndroidRequestHandler),
	('/pollingHandler', PollingHandler)

], debug=True)
