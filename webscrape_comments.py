import pandas as pd
import glob as glob
import scipy.stats as sp
import matplotlib.pyplot as plt
import re
from bs4 import BeautifulSoup
import requests # <div class="main clearfix pl3 ml3">
import time
import datetime

end_2013 = 1388534400
end_2014 = 1420070400
end_2015 = 1451606400
end_2016 = 1483228800

#WHY HAVEN'T I RECIEVED
#My units arrived
#Thanks for the download link
#I never received my
#work fine
#  lucky ones that received my
#I actually got shipped
# I've had mine since I can't even remember when

print("Starting program...")

#csv files are 4150 lines long.
#path = './Kickstarter_2017-01-15' #Scrape of all kickstarters up to end of 2016
path = './Kickstarter_2017-01-15/Kickstarter.csv' #Scrape of single file, for testing.
#path = './small.csv' #Scrape of single file, for testing.

#Gather and load all scv files from a given directory into our Kickstarter Data Frame.
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


#Dates and comments are lists that are passed by value, and updated within.
def scrape_comments(dates,comments,project_url):
     
    ##soup = BeautifulSoup(driver.page_source, "lxml")

    ##comments_count = int(soup.find(attrs = {'data-content': "comments"})['data-comments-count'])

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

        find_delivered(soup,dates,comments)

        link = soup.find('a',class_="btn btn--light-blue btn--block mt3 older_comments")
        if link is None:
            more_comments = False
            break
        project_url = "https://www.kickstarter.com"+(link['href'])
       
    return reward_date

#Dates and comments are lists that are passed by value, and updated within.
def find_delivered(soup,dates,comments):

    for t in soup.findAll(class_ = "main clearfix pl3 ml3"):
        comment = str(t.findAll('p'))
        comments.append(comment)
        #if(delivered_regex.findall(comment)):
            #From the comment object we find the date tag by matching a dictionary, then returnt he raw date value.
            #Example: <data class="Comment5751663" data-format="distance_date" data-value='"2014-01-27T12:15:13-05:00"' itemprop="Comment[created_at]">
        date_raw = str(t.find(attrs = {'itemprop': "Comment[created_at]"})['data-value'])
        date = date_raw[1:11]
        dates.append(date)
  
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
        reward_date = scrape_comments(comment_dates,comments,project_url)
    
        #If the project doesn't return a valid return date, then we are not interested.
        if reward_date is '':
            continue
        
        #cdf = cdf.append({'id':row.id,'reward_date':reward_date,'comment_dates':comment_dates,'comments':comments}, ignore_index=True)
        clst.append([row.id,reward_date,comment_dates,comments])
        
    #return cdf
    return clst
        

if __name__ == '__main__':
    ksdf = load_a_csv(path)
    #ksdf = ksdf[ksdf.id == 1630512510] #This line is for if you want to scrape a specific page
    #ksdf = ksdf[ksdf.id == 1320115942] #This line is for if you want to scrape a specific page
    #Only want to scrape projects that will deliver before 2017.
    #We need further data processing to figure out reward dates, but use deadline for now.
    ksdf = ksdf[ksdf.deadline <= end_2016]
    ksdf = ksdf[ksdf.usd_pledged > 100000]
    
    all_comment_dates = []
    all_comments = []
    all_reward_dates = []
    
    #cmdf = scrape_all_comments(ksdf)
    cmlst = scrape_all_comments(ksdf)
    cmdf = pd.DataFrame(cmlst,columns = ['id','reward_date','comment_dates','comments'])
    
    ksdf.to_pickle("all_kickstarters")
    cmdf.to_pickle("all_comments")


#project_url = 'https://www.kickstarter.com/projects/weaponshop/elixer-unique-suspended-painting/comments'
#project_url = 'https://www.kickstarter.com/projects/mcmatz/the-amanda-palmer-tarot/comments'
#project_url = 'https://www.kickstarter.com/projects/teplin/big-canal'
#project_url = 'https://www.kickstarter.com/projects/mcmatz/the-amanda-palmer-tarot'
#reward_date = scrape_comments(dates,comments,delivered_regex,project_url)

'''

large_success = ksdf.loc[( 0 < ksdf.deadline) & (ksdf.deadline < end_2016) & (ksdf.pledged >= 0)]

url_regex = re.compile('(?<={\"web\":{\"project\":\")(.*?)(?=\?)')
#delivered_regex = re.compile("(?<!not\s)(?<!hasen't\s)(?<!haven't\s)(?<!ever\s)(?<!yet\s)(recieved|received|arrived)", re.IGNORECASE)

all_comment_dates = []
all_comments = []
all_reward_dates = []
for index, row in large_success.iterrows():

    #print("ENTERING LOOP")
    project_url_raw =  row['urls']
    project_url = url_regex.search(project_url_raw).group(0)

    comment_dates = []
    comments = []
    reward_date = scrape_comments(comment_dates,comments,project_url)

    #print("AFTER REWARD DATE, BEFORE APPENDING")
    all_comment_dates.append(comment_dates)
    all_comments.append(comments)
    all_reward_dates.append(reward_date)
    #print("EXITING LOOP")

se_d_d = pd.Series(all_comment_dates)
se_c = pd.Series(all_comments)
se_r_d = pd.Series(all_reward_dates)

large_success['comment_dates'] = se_d_d.values
large_success['comments'] = se_c.values
large_success['reward_dates'] = se_r_d.values

#large_success = large_success.loc[large_success.reward_dates < current_date]

large_success.to_pickle("all_kickstarters")
'''
