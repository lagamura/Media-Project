import os
from typing import Pattern
import requests
from bs4 import BeautifulSoup
import numpy as np
import json
import pandas as pd

media_list = [
    {
    "Name":"Kathimerini",
    "Url": 'https://www.kathimerini.gr/',
    "Political_view":"central-right"
    },
    {
        "Name": "Efsyn",
        "Url": 'https://www.efsyn.gr/',
        "Political_view": "central-left"
    }
]

kathimerini = 'https://www.kathimerini.gr/'
efsyn = 'https://www.efsyn.gr/'



def get_news(a_media):

 
    news_contents = []
    list_links = []
    list_titles = []

    response = requests.get(a_media['Url'])
    response.status_code

    coverpage = response.content

    soup1 = BeautifulSoup(coverpage, 'html.parser')
    # Important call - Choose the correct classname
    coverpage_news = soup1.find_all(['h2','article']) # h2 for kathimerini
    print("Number of h2 headers in " + str(a_media['Name']) + " is :" + str(len(coverpage_news)) + '\n')
    # We have to delete elements such as albums and other things
    # den kserw ti kanei
    # coverpage_news = [x for x in coverpage_news if "inenglish" in str(x)]

    #number_of_articles = 5

    # Empty lists for content, links and titles
    news_contents = []
    list_links = []
    list_titles = []

    for n in np.arange(0, len(coverpage_news)): 

        # Getting the link of the article
        if (not coverpage_news[n].find('a')):
            continue

        link = coverpage_news[n].find('a')['href']
        #if not ("https" in link):

        list_links.append(link)

        # Getting the title
        title = coverpage_news[n].find('a').get_text()
        list_titles.append(title)

        # Reading the content (it is divided in paragraphs)
        linkresolved = requests.compat.urljoin(a_media['Url'],link)
        article = requests.get(linkresolved)
        article_content = article.content
        #print("Type of article is:" + str(type(article)))
        soup_article = BeautifulSoup(article_content, 'html.parser')
        body = soup_article.find_all('div')  # class_='entry-content'
        #print("Type of body is:" + str(type(body)) +'\n')
        if (len(body)>0):
            x = body[0].find_all('p')
            if len(x) == 0: continue
        else:
            continue

        # Unifying the paragraphs
        list_paragraphs = []
        for p in np.arange(0, len(x)):
            paragraph = x[p].get_text()
            list_paragraphs.append(paragraph)
            final_article = " ".join(list_paragraphs)

        news_contents.append(final_article)
        

    df_features = pd.DataFrame(
        {'Content': news_contents
        })

    # df_show_info
    df_show_info = pd.DataFrame(
        {'Article Title': list_titles,
        'Article Link': list_links,
        'Newspaper': a_media['Name']})


    outname = a_media['Name'] +'.csv'

    path = os.path.dirname(os.path.dirname(__file__))

    outdir = path

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    #watch out os backslash character, in windows // chars has different path
    fullname = os.path.join(outdir,"reports/" + outname) 

    df_show_info.to_csv(fullname)

    return (df_features, df_show_info)


# for media in media_list:
#     print(get_news(media))
print(get_news(media_list[1]))

