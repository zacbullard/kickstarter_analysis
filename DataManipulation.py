import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn' #Supresses warning
import glob as glob
import scipy.stats as stats
import matplotlib.pyplot as plt
import re
from bs4 import BeautifulSoup
import requests 
import time
import datetime
import plotly.plotly as py
from plotly.graph_objs import *
import plotly.graph_objs as go
import plotly.tools as tls
import cufflinks as cf

end_2013 = 1388534400
end_2014 = 1420070400
end_2015 = 1451606400
end_2016 = 1483228800

#Thanks for the download link
#work fine
#I actually got shipped
# I've had mine since I can't even remember when


def print_basic_stats(df):
    #print('TOTAL # OF PROJECTS',len(df.index))
    print('COMMENTS STATS:\n',df.comment_count.describe())
    print('SUCCESSFUL FUNDING RATIO',len(df[df.state == 'successful'].index)/len(df.index))
    print('TOTAL FUNDS RAISED, MILLIONS', df[df.state == 'successful'].usd_pledged.sum()/1000000.0)
    

def find_delays(df):
    #Preliminary clean-up of projects without a significant number of comments.
    comment_cutoff = 50
    df = df[df.comment_count >= comment_cutoff]
    
    delivered_regex = re.compile("(?<!not\s)(?<!hasen't\s)(?<!hasn't\s)(?<!haven't\sI\s)(?<!haven't\s)(?<!ever\s)(?<!never\s)(?<!yet\s)(recieved|received|arrived)", re.IGNORECASE)

    all_delivered_comments = []
    all_delivered_dates = []
    for i in range(len(df.comments)):
        delivered_comments = []
        delivered_dates = []
        for j in range(len(df.comments.iloc[i])):
            if delivered_regex.findall(df.comments.iloc[i][j]):
                delivered_comments.append(df.comments.iloc[i][j]) #A more efficient way to do this would be instead of making a copy of the comments with delivery, to record the index in the corrosponding comment list instead.
                delivered_dates.append(df.comment_dates.iloc[i][j])
                #print(df.comments.iloc[i][j],df.comment_dates.iloc[i][j])
                #time.sleep(500.5) 
        all_delivered_comments.append(delivered_comments)
        all_delivered_dates.append(delivered_dates)
    df['delivered_comments'] = all_delivered_comments
    df['delivered_comment_count'] = df.delivered_comments.apply(lambda x: len(x))
    df['delivered_dates'] = all_delivered_dates 
    #df['delivered_datetimes'] = df.delivered_dates.apply(lambda x:pd.to_datetime(pd.Series(x),unit='s'))
    #Only sampling kickstarters with at least a given number of samples. 
    #Scipy requires at least 20, but 50 is generally the minimum for normal_test.
    df = df[df.delivered_comment_count >= comment_cutoff]
    
    #From scipy: This function tests the null hypothesis that a sample comes from a normal distribution. It is based on D’Agostino and Pearson’s [R292], [R293] test that combines skew and kurtosis to produce an omnibus test of normality. 
    df['norm_test_pvalue'] = df.delivered_dates.apply(lambda x:stats.normaltest(x)[1])
    
    #plot_date_distribution(df.delivered_dates.iloc[0])
    #If p > 0.05, not enough of a normal distribution for us.
    df = df[df.norm_test_pvalue <= 0.05]
 
    reward_delays = []
    for index, row in df.iterrows():
        dates_se = pd.to_datetime(pd.Series(row['delivered_dates']),unit='s')
        
        #Delay is measured from the per-month mode of delivery confirmed comments
        mode_month = dates_se.groupby([dates_se.dt.year,dates_se.dt.month]).count().argmax()
        mode_month_string = str(mode_month[0])  + '-' + str(mode_month[1]) + '-15' #Assume the exact date is in the middle of the month
        mode_month_unix = time.mktime(datetime.datetime.strptime(mode_month_string, "%Y-%m-%d").timetuple())
        delivery_gap = (mode_month_unix - row['reward_date'])/60/60/24/30.44 #convert to months
    
        reward_delays.append(delivery_gap)
    df['reward_delay'] = reward_delays

    print('TOTAL NUMBER OF ACCEPTED PROJECTS:',len(df.index))

    return df

#Input is a list of linux dates
def plot_date_distribution(dates_se):
    
    dates_se = pd.to_datetime(pd.Series(dates_se),unit='s')
    
    hp = dates_se.groupby([dates_se.dt.year,dates_se.dt.month]).count().plot(fontsize=7,kind="bar", rot=80).get_figure()
   
    #plt.figure( dpi = 120)
    #plt.axvline(x = 11,linewidth=2, color = 'r')
    plt.title('Delivery Confirmations')
    plt.suptitle('')
    plt.ylabel('Number of Delivery Comments')
    #plt.xlabel('Date')
    #hp.savefig('comment_date.eps', figsize=(6,6),format='eps', dpi=1000)
    #plt.cla()
       


if __name__ == '__main__':
    
    print("Starting program...")

    #Import dirty dataframes    
    ksdf = pd.read_pickle("all_kickstarters_test")
    cmdf = pd.read_pickle("all_comments_test")
    
    #Let's clean up the basic info, while the data frame is relatively small
    ksdf = ksdf.drop(['slug','disable_communication','currency_trailing_code','currency_symbol','state_changed_at','profile','source_url','friends','created_at','is_starred','is_backing','permissions'],axis=1)
    ksdf['duration'] = (ksdf.deadline-ksdf.launched_at)/60.0/60/24
    ksdf.category = ksdf.category.str.partition('"slug":"')[2].str.partition('/')[0]

    #Clean our comments by removing xml tags, newlines, and stripping brackets
    carrot_match = re.compile('<[^>]*>')    
    cmdf.comments = cmdf.comments.map(lambda x:[carrot_match.sub('',y.lstrip('[').rstrip(']').replace('\n', '')) for y in x])
    cmdf['comment_count'] = cmdf.comments.map(lambda x: len(x))
    cmdf['comment_dates'] = [[time.mktime(datetime.datetime.strptime(date, "%Y-%m-%d").timetuple()) for date in dates] for dates in cmdf.comment_dates]

    
    mdf = pd.merge(cmdf,ksdf, on='id',how = 'inner' )
    
    #Eliminate projects whose reward dates are after 2016 
    mdf = mdf[mdf.reward_date <= end_2016]

    print_basic_stats(mdf)
    
    mdf = find_delays(mdf)
    
    

    
    
    