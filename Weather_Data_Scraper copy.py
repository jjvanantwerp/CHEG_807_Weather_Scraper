#Written by James VanAntwerp - UDEL CHEME - vanantj@udel.edu - for the CHEG 807 project

# importing the library
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
from csv import writer

# get current datetime
dt = datetime.now()
dt_yesterday=datetime.now()-timedelta(1)
dt_before_yesterday=dt_yesterday-timedelta(1)
dt_tomorrow = datetime.now()+timedelta(1)
dt_after_tomorrow = dt_tomorrow+timedelta(1)


Months_dict={'1':"January",
             '2':"Febuary",
             '3':"March",
             '4':"April",
             '5':"May",
             '6':"June",
             '7':"July",
             '8':"August",
             '9':"September",
             '10':"October",
             '11':"November",
             '12':"December",}

# get day of week
Days_dict={0:"Monday",
      1:"Tuesday",
      2:"Wednesday",
      3:"Thursday",
      4:"Friday",
      5:"Saturday",
      6:"Sunday",}


suffix={'1':'st','2':'nd','3':'rd','4':'th','5':'th','6':'th','7':'th','8':'th','9':'th','0':'th'}

##Get formatting for the day before yesterday, yesterday, today, tomorrow, and the day after tomorrow
if ((str(dt).split("-")[2]).split()[0])[0]=='0':
    TODAY=Days_dict[dt.weekday()]+", "+Months_dict[str(dt).split("-")[1]]+" "+(str(dt).split("-")[2]).split()[0][1]
else:
    TODAY=Days_dict[dt.weekday()]+", "+Months_dict[str(dt).split("-")[1]]+" "+(str(dt).split("-")[2]).split()[0]
if ((str(dt_tomorrow).split("-")[2]).split()[0])[0]=='0':
    TOMORROW=Days_dict[dt_tomorrow.weekday()]+", "+Months_dict[str(dt_tomorrow).split("-")[1]]+" "+(str(dt_tomorrow).split("-")[2]).split()[0][1]
else:
    TOMORROW=Days_dict[dt_tomorrow.weekday()]+", "+Months_dict[str(dt_tomorrow).split("-")[1]]+" "+(str(dt_tomorrow).split("-")[2]).split()[0]
if ((str(dt_after_tomorrow).split("-")[2]).split()[0])[0]=='0':
    DAY_AFTER_TOMORROW=Days_dict[dt_after_tomorrow.weekday()]+", "+Months_dict[str(dt_after_tomorrow).split("-")[1]]+" "+(str(dt_after_tomorrow).split("-")[2]).split()[0][1]
else:
    DAY_AFTER_TOMORROW=Days_dict[dt_after_tomorrow.weekday()]+", "+Months_dict[str(dt_after_tomorrow).split("-")[1]]+" "+(str(dt_after_tomorrow).split("-")[2]).split()[0]

if ((str(dt_yesterday).split("-")[2]).split()[0])[0]=='0':
    YESTERDAY=Days_dict[dt_yesterday.weekday()][0:3]+", "+Months_dict[str(dt_yesterday).split("-")[1]][0:3]+" "+(str(dt_yesterday).split("-")[2]).split()[0][1]+suffix[(str(dt_yesterday).split("-")[2]).split()[0][-1]]+" 2023"
else:
    YESTERDAY=Days_dict[dt_yesterday.weekday()][0:3]+", "+Months_dict[str(dt_yesterday).split("-")[1]][0:3]+" "+(str(dt_yesterday).split("-")[2]).split()[0]+suffix[(str(dt_yesterday).split("-")[2]).split()[0][-1]]+" 2023"

if ((str(dt_before_yesterday).split("-")[2]).split()[0])[0]=='0':
    DAY_BEFORE_YESTERDAY=Days_dict[dt_before_yesterday.weekday()][0:3]+", "+Months_dict[str(dt_before_yesterday).split("-")[1]][0:3]+" "+(str(dt_before_yesterday).split("-")[2]).split()[0][1]+suffix[(str(dt_before_yesterday).split("-")[2]).split()[0][-1]]+" 2023"
else:
    DAY_BEFORE_YESTERDAY=Days_dict[dt_before_yesterday.weekday()][0:3]+", "+Months_dict[str(dt_before_yesterday).split("-")[1]][0:3]+" "+(str(dt_before_yesterday).split("-")[2]).split()[0]+suffix[(str(dt_before_yesterday).split("-")[2]).split()[0][-1]]+" 2023"


'''
PUT YOUR CITY URL and NAME HERE:
    the city URL is the url on weather.com, hour by hour. It should have the form "https://weather.com/weather/hourbyhour...."
    the name of the city is what weather.com calls the city on the website (exactly). This is important for getting the right data.
ALSO PUT IN THE WEBPAGE FOR PAST RAIN
    get your city's url from localconditions.com. It should have the form "https://www.localconditions.com/{city name}/{zip code}/past.php"
'''
#Info for weather prediction
City_URL=''
City_Name=''
#Info for past rain data
City_Observed=''


# requests instance
forecast_html = requests.get(City_URL).content
 
# getting raw data
Forecast_SOUP = BeautifulSoup(forecast_html, 'html.parser')
Forecast = Forecast_SOUP.find('div', attrs={'class': 'HourlyForecast--DisclosureList--MQWP6'}).text

#Parsing out the hourly forecasts
blocks = {}
for heading in Forecast_SOUP.find_all("h2"):  # find separators, in this case h2 nodes
    values = []
    for sibling in heading.find_next_siblings():
        if sibling.name == "h2":  # iterate through siblings until separator is encoutnered
            break
        values.append(sibling)
    blocks[heading.text] = values

#Set up parsing (below)
Today_Forecast_Tags=blocks[TODAY]
Tomorrow_Forecast_Tags=blocks[TOMORROW]
Today_Rain_Forecast={}
Tomorrow_Rain_Forecast={}

#Get the current forecast (should be run at midnight)
Today_Rain_Forecast['12 am']=(int((Forecast_SOUP.text.split(City_Name)[-1]).split('°')[1].split("%")[0][4:]))/100

#Parse out the hourly rain forecasts for the rest of today
for hour_tag in Today_Forecast_Tags:
    if "Advertisement" not in hour_tag.text:
        Time=''.join(hour_tag.text.split('m')[0])+"m"
        if '°' in hour_tag.text and '%' in hour_tag.text.split("°")[1]: 
            Percipition_Chance=(hour_tag.text.split("°")[1]).split("%")[0][4:]
            Today_Rain_Forecast[Time]=(int(Percipition_Chance)/100)

#print(Today_Rain_Forecast)

#Parse out the hourly rain forecasts for tomorrow
for hour_tag in Tomorrow_Forecast_Tags:
    if "Advertisement" not in hour_tag.text:
        Time=''.join(hour_tag.text.split('m')[0])+"m"
        if '°' in hour_tag.text and '%' in hour_tag.text.split("°")[1]: 
            Percipition_Chance=(hour_tag.text.split("°")[1]).split("%")[0][4:]
            Tomorrow_Rain_Forecast[Time]=(int(Percipition_Chance)/100)

#print(Tomorrow_Rain_Forecast)
# requests instance
observed_html = requests.get(City_Observed).content
 
#Pull all recordings of percipition
Observed_SOUP = BeautifulSoup(observed_html, 'html.parser')
yesterday_observed_data=((Observed_SOUP.text.split(DAY_BEFORE_YESTERDAY)[0]).split(YESTERDAY)[-1]).split('Depth')[1]
Records=yesterday_observed_data.split('\n')


#Parse from mess above into a new mess of types
All_Records = []
last_hour = '11'
med = "PM"

for entry in Records:
    if entry: #Empty strings evaluate to False
        hour=entry.split(':')[0]
        if hour != last_hour: #If we have gone through all the entries for the previous hour,
            All_Records.append(((last_hour+med),False)) #Record that there was no rain in the previous hour
            last_hour=hour #Update
        med=entry.split(' ')[1][0:2]
        #Check for rain in this entry
        rec_rain=entry[-2]
        if rec_rain != '-': #If there is rain,
            All_Records.append(((hour+med),True)) #Record that there IS rain in this hour

#This mess deals with the mess I made again.
Daily_Hours=['11PM','10PM','9PM','8PM','7PM','6PM','5PM','4PM','3PM','2PM','1PM','12PM','11AM','10AM','9AM','8AM','7AM','6AM','5AM','4AM','3AM','2AM','1AM','12AM']
Daily_Hours.reverse()
Daily_Hours_lower_case=['11 pm','10 pm','9 pm','8 pm','7 pm','6 pm','5 pm','4 pm','3 pm','2 pm','1 pm','12 pm','11 am','10 am','9 am','8 am','7 am','6 am','5 am','4 am','3 am','2 am','1 am','12 am']
Daily_Hours_lower_case.reverse()

Yesterday_Rain_Records=[]
for hour in Daily_Hours:
    rain=any([i[1] for i in All_Records if i[0]==hour]) #If any records for the hour record rain, record True
    Yesterday_Rain_Records.append(rain)


#Okay, now we've gotten all our data so we can write out to a file.
daily_predictions_file="Today_Forecast.csv"
tomorrow_predictions_file="Tomorrow_Forecast.csv"
observed_rain_file="Observed_Rain.csv"
Header=''.join([i+','for i in Daily_Hours])

#Create/set up files if they don't exist already
if not os.path.isfile(daily_predictions_file):
    with open(daily_predictions_file,'w+') as fout:
        fout.write("DATE:,")
        fout.write(Header)
        fout.write('\n')
        fout.close()  
if not os.path.isfile(tomorrow_predictions_file):
    with open(tomorrow_predictions_file,'w+') as fout:
        fout.write("DATE:,")
        fout.write(Header)
        fout.write('\n')
if not os.path.isfile(observed_rain_file):
    with open(observed_rain_file,'w+') as fout:
        fout.write("DATE:,")
        fout.write(Header)
        fout.write('\n')
        fout.close()

# Open our existing CSV files in append mode
with open(observed_rain_file, 'a') as fout:
    writer_object = writer(fout)
    fout.write(YESTERDAY.replace(',','')+",")
    writer_object.writerow(Yesterday_Rain_Records)
    fout.close()
with open(tomorrow_predictions_file, 'a') as fout:
    writer_object = writer(fout)
    fout.write(TOMORROW.replace(',','')+",")
    for i in Daily_Hours_lower_case:
        if i in Tomorrow_Rain_Forecast.keys():
            fout.write(str(Tomorrow_Rain_Forecast[i])+',')
        else:
            fout.write('no data,')
    #writer_object.writerow([Tomorrow_Rain_Forecast[i] for i in Daily_Hours_lower_case if i in Tomorrow_Rain_Forecast.keys() else 'no data'])
    fout.write('\n')
    fout.close()
with open(daily_predictions_file, 'a') as fout:
    writer_object = writer(fout)
    fout.write(TODAY.replace(',','')+",")
    for i in Daily_Hours_lower_case:
        if i in Today_Rain_Forecast.keys():
            fout.write(str(Today_Rain_Forecast[i])+',')
        else:
            fout.write('no data,')
    #writer_object.writerow([Today_Rain_Forecast[i] for i in Daily_Hours_lower_case if i in Today_Rain_Forecast.keys() else 'no data'])
    fout.write('\n')
    fout.close()

print("You can do this!")
#Print("Berris can't keep you down! You have nothing to lose but your chains! This history of graduate education The history of all hitherto existing society is the history of class struggles. Freeman and slave, patrician and plebeian, lord and serf, guild-master and journeyman, in a word, Professor and Grad Student.... Working students of all labs, UNITE! ")

if not os.path.isfile('log.txt'):
    with open('log.txt','w+') as fout:
        fout.write("LOG OF DATES WITH COLLECTED DATA:")

with open('log.txt', 'a+') as fout:
    fout.write("Recorded Data For: "+TODAY+'\n')
    fout.close()
