"""Define functions to use in redis queue."""

import calendar
import time

from rq import get_current_job

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import os

import mysql.connector

from .mysql_connection import mydb



#  Function logic to scrape amazon page

def scrape_amazon(data):
    try:
        #  String manipulation to change the entered URL to the all reviews page
        s=data["link"].replace("dp","product-reviews")
        s="/".join(s.split("/")[:-1])
        URL=s+"/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&pageNumber="
        
        # To get the current running job in redis queue
        job = get_current_job()
        
        # Initializing dictionary to store the scrapped data
        dic=dict()
        dic["Review text"]=[]
        dic["Amazon Rating"]=[]
        dic["Date of Review"]=[]
        
        #looping through 250 pages for a given product
        for i in range(1,250):
            req = requests.get(URL + str(i))
            soup = bs(req.text, 'html.parser')
            for row in soup.findAll("div",attrs={"class":"a-section review aok-relative"}):
                text=row.find("span",attrs={"class":"a-size-base review-text review-text-content"}).get_text()
                text=text.encode('unicode-escape').decode('utf-8')
                rating=row.find("span",attrs={"class":"a-icon-alt"}).get_text()
                date=row.find("span",attrs={"class":"a-size-base a-color-secondary review-date"}).get_text()
                dic["Review text"].append(text)
                dic["Amazon Rating"].append(rating)
                dic["Date of Review"].append(date)
                
                # To show the progess of fetch
                job.meta['progress'] = (i/250)*100
                job.save_meta()
        
        # progress made to 100 percent after fetch ends
        job.meta['progress'] = 100.0
        job.save_meta()
        print(dic)
        
        # converting python dictionary to dataframe
        df = pd.DataFrame(data=dic)
        
        # dataframe is saved as a CSV file
        filename='amazon_review_data'+str(getTimeStamp())+'.csv'
        df.to_csv(os.path.abspath(os.path.dirname(__file__)+"/results/"+ filename),index=False)
        
        # Updation is done to the mysql database
        sql_update="update review1 set filename=%s,status=%s where jod_id=%s"
        val_update = (filename,2,str(job.id))
        mycursor = mydb.cursor()
        mycursor.execute(sql_update, val_update)
        mydb.commit()
        return {
            "job_id": job.id,
            "job_enqueued_at": job.enqueued_at.isoformat(),
            "job_started_at": job.started_at.isoformat(),
        }
    except:
    
        # In case of any exception the DB is updated as failed status
        sql_update="update review1 set status=%s where jod_id='%s' "
        print(sql_update)
        val_update = (3,str(job.id))
        a=mycursor.execute(sql_update, val_update)
        mydb.commit()




# Function logic to fetch the Shopee review data



def scrape_shopee(data):
    try:
        
        # To get the current running job in redis queue
        job = get_current_job()
        
        # String manipulation on the given URL to get itemid and shopid
        URL=data["link"]
        temp=data["link"].split(".")
        shopid=temp[-2]
        itemid=temp[-1]
        
        
        # Initializing dictionary to store the fetched data
        dic={}
        dic["Review"]=[]
        dic["Shopee Rating"]=[]
        
        #looping through 30 pages for a given product
        for _ in range(1):
            for i in range(30):
                URL="https://shopee.com.my/api/v2/item/get_ratings?filter=0&flag=1&itemid="+str(itemid)+"&limit=6&offset="+str(i)+"&shopid="+str(shopid)+"&type=0"
                print(URL)
                content=requests.get(URL)
                decoded=json.loads(content.text)
                for rating in decoded["data"]["ratings"]:
                    Rating=rating["rating_star"]
                    comment=rating["comment"].encode('unicode-escape').decode('utf-8')
                    dic["Review"].append(comment)
                    dic["Shopee Rating"].append(Rating)
                
                # To show the progess of fetch
                job.meta['progress'] = (i/30)*100
                job.save_meta()
                time.sleep(4)
        
        # progress made to 100 percent after fetch ends
        job.meta['progress'] = 100
        job.save_meta()
        
        # converting python dictionary to dataframe
        df = pd.DataFrame(data=dic)
        print(dic)
        
        # dataframe is saved as a CSV file
        filename='shopee_review_data'+str(getTimeStamp())+'.csv'
        df.to_csv(os.path.abspath(os.path.dirname(__file__)+"/results/"+ filename),index=False)
        
        
        # Updation is done to the mysql database
        sql_update="update review1 set filename=%s,status=%s where jod_id=%s"
        print(sql_update)
        val_update = (filename,2,str(job.id))
        mycursor = mydb.cursor()
        a=mycursor.execute(sql_update, val_update)
        print(a)
        mydb.commit()
        return {
            "job_id": job.id,
            "job_enqueued_at": job.enqueued_at.isoformat(),
            "job_started_at": job.started_at.isoformat(),
        }
    except:
        
        # In case of any exception the DB is updated as failed status
        sql_update="update review1 set status=%s where jod_id='%s' "
        print(sql_update)
        val_update = (3,str(job.id))
        a=mycursor.execute(sql_update, val_update)
        mydb.commit()


#  Function to get the current time

def getTimeStamp():
    gmt=time.gmtime()
    return calendar.timegm(gmt)
    
    
    
    
    
    
 # URL where the rest APIs are being kept by Shopee developers
    
#content = requests.get("https://shopee.com.my/api/v4/search/search_items?by=relevancy&keyword=huggies&limit=20&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2")
    
    
    
