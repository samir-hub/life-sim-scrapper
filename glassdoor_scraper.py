from lxml import html, etree
import requests
import re
import os
import sys
import unicodecsv as csv
import argparse
import json

def parse(keyword, place):

	headers = {	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
				'accept-encoding': 'gzip, deflate, sdch, br',
				'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6',
				'referer': 'https://www.glassdoor.com/',
				'upgrade-insecure-requests': '1',
				'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
				'Cache-Control': 'no-cache',
				'Connection': 'keep-alive'
	}

	location_headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.01',
		'accept-encoding': 'gzip, deflate, sdch, br',
		'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6',
		'referer': 'https://www.glassdoor.com/',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
		'Cache-Control': 'no-cache',
		'Connection': 'keep-alive'
	}
	data = {"term": place,
			"maxLocationsToReturn": 10}

	location_url = "https://www.glassdoor.co.in/findPopularLocationAjax.htm?"
	try:
		# Getting location id for search location
		print("Fetching location details")
		location_response = requests.post(location_url, headers=location_headers, data=data).json()
		place_id = location_response[0]['locationId']
		print(place_id)
		job_litsting_url = 'https://www.glassdoor.com/Salaries/company-salaries.htm'
		# Form data to get job results
		data = {
			'clickSource': 'searchBtn',
			'sc.keyword': keyword,
			'locT': 'C',
			'locId': place_id,
			'jobType': ''
		}

		job_listings = []
		if place_id:
			response = requests.post(job_litsting_url, headers=headers, data=data)
			parser = html.fromstring(response.text)
			# Making absolute url 
			base_url = "https://www.glassdoor.com"
			parser.make_links_absolute(base_url)

			raw_salary = parser.xpath('//*[@id="OccMedianChart"]/div[1]/div[2]/span[1]/text()')

			jobs = {
				"Salary": raw_salary
				}
			job_listings.append(jobs)

			return job_listings
		else:
			print("location id not available")

	except:
		print("Failed to load locations")

if __name__ == "__main__":

	''' eg-:python 1934_glassdoor.py "Android developer", "new york" '''

	argparser = argparse.ArgumentParser()
	argparser.add_argument('keyword', help='job name', type=str)
	argparser.add_argument('place', help='job location', type=str)
	args = argparser.parse_args()
	keyword = args.keyword
	place = args.place
	print("Fetching job details")
	scraped_data = parse(keyword, place)
	print("Writing data to output file")

	with open('%s-%s-job-results.csv' % (keyword, place), 'wb')as csvfile:
		fieldnames = ['Salary']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames,quoting=csv.QUOTE_ALL)
		writer.writeheader()
		if scraped_data:
			for data in scraped_data:
				writer.writerow(data)
		else:
			print("Your search for %s, in %s does not match any jobs"%(keyword,place))