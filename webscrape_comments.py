import pandas as pd
import glob as glob
import scipy.stats as sp
import matplotlib.pyplot as plt
import re
from bs4 import BeautifulSoup
import requests 
import time
import datetime

'''
The following code trawls through Kickstarter projects and scrapes their comments.
A comment dataframe is pickled, as well as another with general information.
Comment pages have a "Show Older Comments" button for projects with many comments,
requiring some button pushing.
Currently it filters out projects with a deadline beyond 1-1-2017.
~Zac Bullard
'''

end_2013 = 1388534400
end_2014 = 1420070400
end_2015 = 1451606400
end_2016 = 1483228800

print("Starting program...")

#csv files with our general Kickstarter data, files are 4150 lines long.
#path = './Kickstarter_2017-01-15' #Scrape of all kickstarters up to end of 2016
#path = './Kickstarter_2017-01-15/Kickstarter.csv' #Scrape of single file, for testing.
path = './small.csv' #Scrape of single file, for testing.

#Gather and load all csv files from a given directory into our Kickstarter Data Frame.
def load_all_csv(path):
    all_files = glob.glob(path + '/*.csv')
    ksdf = pd.DataFrame()
    frames_list = []
    for a_file in all_files:
        print("Reading " + a_file + "...")
        df = pd.read_csv(a_file,index_col=None, header=0)
        frames_list.append(df)
    ksdf = pd.concat(frames_list)

    #A few projects were missing names from being censored and removed by Kickstarter, making them invalid data points
    ksdf = ksdf.loc[ksdf.name.notnull()]
    return ksdf

#For testing. Load Just a single csv.
def load_a_csv(path):
    ksdf = pd.read_csv(path,index_col=None, header=0)
    #A few projects were missing names from being censored and removed by Kickstarter, making them invalid data points
    ksdf = ksdf.loc[ksdf.name.notnull()]
    return ksdf

      
def scrape_all_comments(df):
    #Need to get url from string
    url_regex = re.compile('(?<={\"web\":{\"project\":\")(.*?)(?=\?)')
    
    #cdf = pd.DataFrame(columns = ['id','reward_date','comment_dates','comments']) #Comment dataframe
    clst = []    

    for index, row in df.iterrows():

        project_url_raw =  row['urls']
        project_url = url_regex.search(project_url_raw).group(0)
    
        comment_dates = []
        comments = []
        print(len(clst),'Started scraping:',row.id)
        #Watch out, if the project has multiple reward dates will return the first one.
        reward_date = scrape_project_comments(comment_dates,comments,project_url)
    
        #If the project doesn't return a valid return date, then we are not interested.
        if reward_date is '':
            continue
        
        clst.append([row.id,reward_date,comment_dates,comments])
        
    #return cdf
    return clst

#Dates and comments are lists that are passed by value, and updated within.
def scrape_project_comments(dates,comments,project_url):
     
    #Didn't need the following line in Python3
    r = 0
    try:
        r = requests.get(project_url+"/rewards")
    except requests.exceptions.RequestException as e:
        print(e)
    soup = BeautifulSoup(r.content, "lxml")
    #Watch out for campaigns with multiple reward dates, will return blank
    reward_date = ''
    try:
        reward_date = str(soup.find('time',class_='invisible-if-js js-adjust-time')['datetime'])
    except:
        return reward_date
    
    #Converting the date into unix time
    reward_date = time.mktime(datetime.datetime.strptime(reward_date, "%Y-%m-%d").timetuple())

    project_url = project_url + "/comments"
    more_comments = True
    while more_comments:
        
        print(project_url)
        try:
            r = requests.get(project_url)
        except requests.exceptions.RequestException as e:
            print(e)
            break
    
        soup = BeautifulSoup(r.content, "lxml")

        scrape_page_comments(soup,dates,comments)

        link = soup.find('a',class_="btn btn--light-blue btn--block mt3 older_comments")
        if link is None:
            more_comments = False
            break
        project_url = "https://www.kickstarter.com"+(link['href'])
       
    return reward_date

#Dates and comments are lists that are passed by value, and updated within.
def scrape_page_comments(soup,dates,comments):

    for t in soup.findAll(class_ = "main clearfix pl3 ml3"):
        comment = str(t.findAll('p'))
        comments.append(comment)
        #if(delivered_regex.findall(comment)):
            #From the comment object we find the date tag by matching a dictionary, then returnt he raw date value.
            #Example: <data class="Comment5751663" data-format="distance_date" data-value='"2014-01-27T12:15:13-05:00"' itemprop="Comment[created_at]">
        date_raw = str(t.find(attrs = {'itemprop': "Comment[created_at]"})['data-value'])
        date = date_raw[1:11]
        dates.append(date)
        
if __name__ == '__main__':
    #Kickstarter dataframe with basic information from webrobots.io
    ksdf = load_a_csv(path)
    #ksdf = ksdf[ksdf.id == 1630512510] #This line is for if you want to scrape a specific page
    
    #Only want to scrape projects that will deliver before 2017.
    #We need further data processing to figure out reward dates, but use deadline for now.
    #ksdf = ksdf[ksdf.usd_pledged > 100000] #For testing purposes
    ksdf = ksdf[ksdf.deadline <= end_2016].reset_index(drop=True)
    
    
    all_comment_dates = []
    all_comments = []
    all_reward_dates = []
    
    #Comment dataframe.
    cmlst = scrape_all_comments(ksdf)
    cmdf = pd.DataFrame(cmlst,columns = ['id','reward_date','comment_dates','comments'])
    
    ksdf.to_pickle("all_kickstarters")
    cmdf.to_pickle("all_comments")
