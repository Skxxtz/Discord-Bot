#imports
import discord
from discord.ext import commands, tasks
import os
from keep_alive import keep_alive
from discord.ext import tasks 
from bs4 import BeautifulSoup
import requests

id=****************
client = discord.Client()
bot = commands.Bot(command_prefix='$')

sports = ["Werder", "Bremen"]
politics = ["Russ","Ukrain","Putin","Militär","nato","Corona"]
keywords = []
for element in sports:
  keywords.append(element)
for element in politics:
  keywords.append(element)

print("Looking for keywords: {}".format(keywords))
  
#sources
welt_url = "https://www.welt.de/newsticker/"
filtered_news= []
new_news = []
identifier = ["c-grid__item c-grid__item--is-full c-grid__item--has-no-gap","ExpandableList.Item Stage.Teaser"]  

def clear():
  '''
  This function clears the old data.
  '''
  r = requests.get(welt_url)
  soup = BeautifulSoup(r.text, "html.parser")
  samples = soup.find_all("li")
  for i in range(len(samples)):
      if identifier[0] and identifier[1] in str(samples[i]):
          element = samples[i].findAll("a").pop()
          article = {"title" : element["title"],
                     "time": element.find("span").get_text(),
                     "link": "https://www.welt.de{}".format(element.get("href"))}
          if article not in filtered_news:
              filtered_news.append(article)
clear()

#user  interaction
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("$channel"): #returns the channel ID 
        await message.channel.send(message.channel)
    if message.content.startswith("$keywords"): #returns a list of keywords
        await message.channel.send(keywords)
    
     
@tasks.loop(minutes=2) #web scraping loop, running every 2 minutes
async def news(): 
  print("new iteration. cache = {}".format(len(filtered_news)))
  if len(filtered_news)>100:
    clear()
  new_news = []
  r = requests.get(welt_url)
  soup = BeautifulSoup(r.text, "html.parser")
  samples = soup.find_all("li")
  for i in range(len(samples)):
      if identifier[0] and identifier[1] in str(samples[i]):
          element = samples[i].findAll("a").pop()
          article = {"title" : element["title"],
                     "time": element.find("span").get_text(),
                     "link": "https://www.welt.de{}".format(element.get("href"))}
          for element in keywords:
            if article not in filtered_news and article not in new_news:
              if element.lower() in article["title"].lower(): 
                  filtered_news.append(article)
                  new_news.append(article)

#sending data to user as a discord embed
  channel = client.get_channel(953352776266706985)
  for element in new_news:
    #await channel.send("{}\n{}".format(element["title"],element["link"]))
    r = requests.get(element["link"])
    soup = BeautifulSoup(r.text, "html.parser")
    desc = "" 
    try:
      desc = soup.find("div", class_="c-summary__intro").get_text()
    except:
      pass
    print(desc)
    embed_thumbnail_url = str(soup.find("img").get("src"))
    if desc == "":
      embed=discord.Embed(title=element["title"], url=element["link"], color=0x383E42)
    else:
      embed=discord.Embed(title=element["title"],description = desc, url=element["link"], color=0x383E42)
      
    embed.set_thumbnail(url = embed_thumbnail_url)
    await channel.send(embed=embed)
    
    print(element["title"],"\n",element["link"],"\n",desc,"\n\n")
  new_news = []
@client.event
async def on_ready():
  news.start()
  print("Online as {0.user}".format(client))
  

  
token = os.environ['TOKEN']
keep_alive()
client.run(token)
