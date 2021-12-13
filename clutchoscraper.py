import csv
from math import ceil
from bs4 import BeautifulSoup
import time
from random import uniform
from random import randint
import cloudscraper
from datetime import date
from datetime import datetime

from helheim.exceptions import (
    HelheimException,
    HelheimSolveError,
    HelheimRuntimeError,
    HelheimSaaSError,
    HelheimSaaSBalance,
    HelheimVersion,
    HelheimAuthError
)
import helheim
helheim.auth('')

def injection(session, response):
    '''
    if helheim.isChallenge(
        response,
        ignore=[
            {
                'status_code': [403, 503], # list or int
                'text': ['text on page to match', ...] # list of strings.. or string of regex to match
            },
            {
                ...
            }
        ]
    ):
    '''
    if helheim.isChallenge(session, response):
        return helheim.solve(session, response)
    else:
        return response

def link_creator(url):
    global per_page
    r = session.get(url)
    soup = BeautifulSoup(r.text,"html.parser")
    per_page = soup.select("ul.directory-list.shortlist li.provider.provider-row")
    per_page = len(per_page)
    print(f"{per_page} per page" )
    pages = ceil((int((soup.select_one("div.firms-count div.tabs-info").text).replace(",","").split(" ")[0]))/per_page)
    pages_links.append(url)
    if ("=" not in url):
        for x in range(1,pages):
            page_link = f"{url}?page={x}"
            pages_links.append(page_link)
    elif ("=" in url):
        for x in range(1,pages):
            page_link = f"{url}&page={x}"
            pages_links.append(page_link)
    print(f"{len(pages_links)} pages")

def half_records_scraper(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text,"html.parser")
    all_objects = soup.select("ul.directory-list.shortlist li.provider.provider-row")
    if (len(all_objects)) < per_page:
        print(len(all_objects))
        print(url)
    for object in all_objects:
        detailed_link = f'https://clutch.co{object.select_one("li.website-profile a")["href"]}'
        website_link = (object.select_one("a.website-link__item")["href"]).split("?")[0]
        name = (object.select_one("h3.company_info a").text).replace("  ","").replace("\n","")
        try:
            tagline = object.select_one("div.row.provider-info--header p.company_info__wrap.tagline").text
        except:
            tagline = None 
        verification = object.select_one("div.verification span.verification_icon")
        try:
            service_focus = (object.select_one("div.directory-graph.directory-main-bar div.chart-label.hidden-xs span").text).replace("  ","").replace("\n","")
        except:
            service_focus = None
        if verification:
            verification = "verified"
        else:
            verification = ""
        parrent = object.select("div.module-list div span")

        min_proj_size = None
        avg_hrl_rate = None 
        employees = None 
        location = None 
        min_proj_size = parrent[0].text
        avg_hrl_rate = parrent[1].text
        employees = parrent[2].text
        location = parrent[3].text
        try:
            rating = object.select_one("div.rating-reviews span").text
            reviews = (object.select_one("div.reviews-link").text).replace("  ","").replace("\n",'')
        except:
            rating = ""
            reviews = ""
        half_record = (name,tagline,verification,rating,reviews,service_focus,min_proj_size,avg_hrl_rate,employees,location,detailed_link,website_link)
        half_records.append(half_record)


def csv_saver():
    filtered_records = []
    for x in half_records:
        if (x not in filtered_records):
            filtered_records.append(x)
    now = datetime.now()
    time_stamp = now.strftime("%H_%M")
    today = date.today()
    date_stamp = today.strftime("_%m_%d_%y")
    with open(f"{time_stamp}_{date_stamp}.csv","w",newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(['name',"tagline","verified","rating","reviews","service_focus","min_project_size","average_hourly_rate","employees","location","detailed_link","website_link"])
        writer.writerows([x for x in filtered_records])

def main_for_on_sub(url):
    global pages_links
    global records
    global session
    global count
    pages_links = []
    records = []
    print(url)
    link_creator(url)   
    print("Scraping")
    start = time.time()
    count = 0
    print(len(pages_links))
    for x in pages_links:
        half_records_scraper(x)        
        time.sleep(uniform(0.2,0.5))
        count += 1
        if count%10 == 0:
            print(f"{count} pages scraped")
    print(f"{count} pages scraped")
    print(f"{len(half_records)} records currently extracted")

    end = time.time()
    print("")
    print(f"Total runtime for this link: {end-start}")


def main(input_for_main):
    global session
    global half_records
    half_records = []
    start1 = time.time()
    print("Starting the session")
    print("")
    session = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome', 
        'mobile': False, 
        'platform': 'windows' 
    },
    requestPostHook=injection,
    captcha={
        'provider': 'vanaheim',
    }
    )
    session.get("https://clutch.co/agencies")

    list_of = input_for_main.split(",")
    print(f"{len(list_of)} links")
    error = False
    for x in list_of:
        if error:
            break
        try:
           main_for_on_sub(x)
           print("")
        except:
            print("Can't scrap further. Current link:")
            print(x)
            error = True
    print("Saving")
    csv_saver()
        

    end1 = time.time()
    print(f"Program total runtime: {end1-start1}")



with open('runmode1_input.txt') as f:
    your_input1 = f.readlines()
your_input = ""
for x in your_input1:
    your_input+=x


main(your_input.replace(" ","").replace("\n",""))
w = input("Press any button to exit the script")





