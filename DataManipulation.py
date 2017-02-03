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



if __name__ == '__main__':
    
    ksdf = pd.read_pickle("all_kickstarters")
    cmdf = pd.read_pickle("all_comments")


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