import json
import sys
import re
import urllib2
#import dryscrape
import datetime
import time

from bs4 import BeautifulSoup

def getWeatherData(address):

	result = {
		"currTemp" : "0.0",
		"rain" : False,
		"rainToday" : False,
		"today" : "0.0",
		"tomorrow" : "0.0"
	}

	targetZipcode = 0
	
	tempAddr = address
	tempAddr = tempAddr.replace(',', ' ')
	addrList = address.split(' ')
	lastVal = addrList[-1]

	city = ""
	state = ""

	if lastVal.isdigit():
		targetZipCode = int(lastVal)
		addrList = address.split(',')

		city = ""
		for addr in addrList:
			if addr:
				if not city:
					city = addr
					break

		city = city.lstrip(' ')
		city = city.replace(' ', '-')
	else:
		addrList = address.split(',')

		city = ""
		state = ""
		for addr in addrList:
			if addr:
				if not city:
					city = addr
				elif not state:
					state = addr
				else:
					break

		city = city.lstrip(' ')
		state = state.lstrip(' ')
		city = city.replace(' ', '+')
		state = state.replace(' ', '+')
		
		zipcodeLookupURL = "http://www.zip-info.com/cgi-local/zipsrch.exe?zip=" + city + "%2C+" + state + "&Go=Go"
		zipcodeResponse = urllib2.urlopen(zipcodeLookupURL)
	
		bs = BeautifulSoup(zipcodeResponse.read())
		if not bs:
			return ""

		currZip = bs.find_all(text = re.compile("^\d{5}$"))
		if not currZip or not currZip[0].isdigit():
			return ""

		targetZipCode = int(currZip[0])
		city = city.replace('+', '-')

	
	weatherLookupURL = 'http://www.wunderground.com/cgi-bin/findweather/getForecast?query=pz:' + str(targetZipCode) + '&zip=1&MR=1'
	forecastLookupURL = 'http://www.localconditions.com/weather-' + city + '/' + str(targetZipCode) + '/forecast.php'
	currentLookupURL = 'http://www.localconditions.com/weather-' + city + '/' + str(targetZipCode)

	'''
	session = dryscrape.Session()
	session.visit(weatherLookupURL)
	response = session.body()
	'''

	response = urllib2.urlopen(weatherLookupURL).read()
	bs = BeautifulSoup(response)

	forecastResponse = urllib2.urlopen(forecastLookupURL).read()
	forecastBS = BeautifulSoup(forecastResponse)

	currentResponse = urllib2.urlopen(currentLookupURL).read()
	currentBS = BeautifulSoup(currentResponse)

	currTempList = bs.select("#curTemp")

	currTemp = currTempList[0].select(".wx-value")
	currTemp = currTemp[0].string

	result['currTemp'] = currTemp

	todayTemp = currentBS.find(class_='weather-today').find(id='temperature').contents[0]
	todayTemp = todayTemp.encode('ascii', 'ignore')
	todayTemp = todayTemp.lstrip(' ')
	todayTemp = todayTemp.rstrip(' ')
	todayTemp = todayTemp.rstrip('F')

	tmrTempLow = forecastBS.find(class_="weather-forecast-5day-col").find_all(id="temperature")[1].contents[2]
	tmrTempHigh = forecastBS.find(class_="weather-forecast-5day-col").find_all(id="temperature")[0].contents[2]

	tmrTempLow = tmrTempLow.encode('ascii', 'ignore')
	tmrTempLow = tmrTempLow.lstrip(' ')
	tmrTempLow = tmrTempLow.rstrip(' ')
	tmrTempLow = tmrTempLow.rstrip('F')

	tmrTempLow = float(str(tmrTempLow))

	tmrTempHigh = tmrTempHigh.encode('ascii', 'ignore')
	tmrTempHigh = tmrTempHigh.lstrip(' ')
	tmrTempHigh = tmrTempHigh.rstrip(' ')
	tmrTempHigh = tmrTempHigh.rstrip('F')

	tmrTempHigh = float(str(tmrTempHigh))
	tmrTemp = (tmrTempLow + tmrTempHigh) / 2
	tmrTemp = str(tmrTemp)


	rainy = str(forecastBS.find(id='forecast-full').find(id='main-condition').string)
	rainy = rainy.replace(' ', '')
	if rainy == 'Rain':
		rainy = True
	else:
		rainy = False

	rainyToday = str(currentBS.find(id='main-condition').string)
	rainyToday = rainyToday.replace(' ', '')
	if rainyToday == 'Rain':
		rainyToday = True
	else:
		rainyToday = False

	result['rain'] = rainy
	result['today'] = todayTemp
	result['tomorrow'] = tmrTemp
	result['rainToday'] = rainyToday

	return result
