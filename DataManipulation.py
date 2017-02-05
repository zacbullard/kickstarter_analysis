import pandas as pd
import glob as glob
import scipy.stats as sp
import matplotlib.pyplot as plt
import re
from bs4 import BeautifulSoup
import requests # <div class="main clearfix pl3 ml3">
import time
import datetime
#from lxml import etree

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
    
    ksdf = pd.read_pickle("all_kickstarters_test")
    cmdf = pd.read_pickle("all_comments_test")
    
    #Let's clean up the basic info, while the data frame is relatively small
    ksdf = ksdf.drop(['slug','disable_communication','currency_trailing_code','currency_symbol','state_changed_at','profile','source_url','friends','is_starred','is_backing','permissions'],axis=1)
    ksdf['duration'] = (ksdf.deadline-ksdf.launched_at)/60.0/60/24
    ksdf['prep_time'] = (ksdf.launched_at-ksdf.created_at)/60.0/60/24

    #Clean our comments by removing xml tags, newlines, and stripping brackets
    carrot_match = re.compile('<[^>]*>')    
    cmdf.comments = cmdf.comments.map(lambda x:[carrot_match.sub('',y.lstrip('[').rstrip(']').replace('\n', '')) for y in x])
    
    mdf = pd.merge(cmdf,ksdf, on='id',how = 'inner' )
    
    #Eliminate projects whose reward dates are after 2016 
    #cmdf = cmdf[cmdf.reward_date <= end_2016]
    #ksdf = ksdf[cmdf.reward_date <= end_2016]
    mdf = mdf[mdf.reward_date <= end_2016]
    

    