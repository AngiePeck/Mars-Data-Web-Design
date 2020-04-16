#Dependencies

from bs4 import BeautifulSoup
import pandas as pd
import requests
import pymongo
import os.path
from urllib.parse import urljoin
from splinter import Browser

def scrape_nasa():
    mars_news = {}

    #Nasa Mars News
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'

    # Retrieve page with the requests module
    response = requests.get(url)
    # Create BeautifulSoup object; parse with 'lxml'
    soup = BeautifulSoup(response.text, 'lxml')
    #print(soup.prettify())

    #Retrieve title and paragraph text with variable
    article_results = soup.find('div', class_='content_title')
    mars_news["news_title"] = article_results.find('a').text
    mars_news["news_p"] = soup.find('div', class_='rollover_description_inner').text

    #JPL Mars Space Image
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=True)

    # URL of page to be scraped
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html,'html.parser')
    base = 'http://www.jpl.nasa.gov'

    
    featured_image_partial_url = soup.find('a', class_='button fancybox')['data-fancybox-href']
    mars_news["featured_image_full_url"] = urljoin(base, featured_image_partial_url)
    mars_news["featured_text"] = soup.find('a', class_="button fancybox")['data-description']
         

    #Mars Weather
    twitter_url = 'https://twitter.com/MarsWxReport'

    # Retrieve page with the requests module
    response = requests.get(twitter_url)
    # Create BeautifulSoup object; parse with 'lxml'
    soup = BeautifulSoup(response.text, 'lxml')
    #Retrieve tweet
    mars_weather = soup.find('div', class_='js-tweet-text-container')
    mars_news["mars_tweet"] = mars_weather.find('p').text

    #Facts Table
    facts_url = 'https://space-facts.com/mars/'
    mars_facts_table = pd.read_html(facts_url)
    mars_facts_df = mars_facts_table[0]
    mars_facts_df.columns= ['Description', 'Value']
   

    mars_news["mars_facts_table"] =  mars_facts_df.to_html(index = False, classes = 'table table-sm')

  
    #Mars Hemisphere Image URLs
    raw_html = ''   
    if os.path.isfile('raw_html.txt'):
        with open('raw_html.txt', 'r') as file:
            raw_html = file.read()
    else: 
        response = requests.get(hemi_url)
        raw_html = response.text
        with open('raw_html.txt','w') as file:
            file.write(raw_html)

    soup = BeautifulSoup(raw_html, 'lxml')

    hemi_results = soup.find_all('div', class_='item')    
        
    base = 'https://astrogeology.usgs.gov'

    hemi_image_urls = []

    for result in hemi_results:
        title = result.find('h3').text
        
        image_partial_url = result.find('a', class_='itemLink')['href']
        image_full_url = urljoin(base, image_partial_url)
        
        response_hemi = requests.get(image_full_url)
        soup_hemi = BeautifulSoup(response_hemi.text,'lxml')
        downloads_result = soup_hemi.find('div', class_='downloads')
        img_url = downloads_result.find('a')['href']

        hemi_image_urls.append({'title': title, 'img_url': img_url, 'image_full_url': image_full_url})

    mars_news["hemi_image_urls"] = hemi_image_urls
    
    return mars_news

