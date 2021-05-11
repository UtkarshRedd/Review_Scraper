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

mydb = mysql.connector.connect(
  host="localhost",
  user="maheshavel",
  password="2308",
  database='scrapedb'
)

def scrape_amazon(data):
    URL=data["link"]+"&reviewerType=all_reviews&pageNumber="
    dic=dict()
    print("hello")
    print(URL)
    job = get_current_job()
    mycursor=mydb.cursor()
    sql_insert="insert into review1 (jod_id,time,url,retailer,status) values(%s,%s,%s,%s,%s)"
    val=(str(job.id),str(getTimeStamp()),URL,"amazon",1)
    mycursor.execute(sql_insert,val)
    mydb.commit()
    dic["Review text"]=[]
    dic["Amazon Rating"]=[]
    dic["Date of Review"]=[]
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
    print(dic)
    df = pd.DataFrame(data=dic)
    filename='amazon_review_data'+str(getTimeStamp())+'.csv'
    df.to_csv(os.path.abspath(os.path.dirname(__file__)+"/results/"+ filename),index=False)
    #mycursor = mydb.cursor()
    sql_update="update review1 set filename=%s,status=%s where jod_id=%s"
    val_update = (filename,2,str(job.id))
    mycursor.execute(sql_update, val_update)
    mydb.commit()
    return {
        "job_id": job.id,
        "job_enqueued_at": job.enqueued_at.isoformat(),
        "job_started_at": job.started_at.isoformat(),
    }


def getTimeStamp():
	gmt=time.gmtime()
	return calendar.timegm(gmt)




def scrape_shopee(data):
    job = get_current_job()
    URL=data["link"]
    temp=data["link"].split(".")
    shopid=temp[-2]
    itemid=temp[-1]
    #content = requests.get("https://shopee.com.my/api/v4/search/search_items?by=relevancy&keyword=huggies&limit=20&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2")
    #products=json.loads(content.text)
    mycursor=mydb.cursor()
    sql_insert="insert into review1 (jod_id,time,url,retailer,status) values(%s,%s,%s,%s,%s)"
    val=(str(job.id),str(getTimeStamp()),URL,"amazon",1)
    mycursor.execute(sql_insert,val)
    mydb.commit()
    #print(products)
    dic={}
    dic["Review"]=[]
    dic["Shopee Rating"]=[]
    for _ in range(1):
        #shopid=item["item_basic"]["shopid"]
        #itemid=item["item_basic"]["itemid"]
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
            time.sleep(3)
        #time.sleep(2)
    df = pd.DataFrame(data=dic)
    print(dic)
    filename='shopee_review_data'+str(getTimeStamp())+'.csv'
    df.to_csv(os.path.abspath(os.path.dirname(__file__)+"/results/"+ filename),index=False)
    mycursor = mydb.cursor()
    sql_update="update review1 set filename=%s,status=%s where jod_id=%s"
    val_update = (filename,2,str(job.id))
    mycursor.execute(sql_update, val_update)
    mydb.commit()
    return {
        "job_id": job.id,
        "job_enqueued_at": job.enqueued_at.isoformat(),
        "job_started_at": job.started_at.isoformat(),
    }




