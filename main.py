import os
import re
from pprint import pp
from pprint import pprint
from turtle import heading
from typing import Pattern
from webbrowser import get
import requests
from bs4 import BeautifulSoup
import numpy as np
import json
import pandas as pd
import spacy
from medialist import *


nlp = spacy.load('el_core_news_lg')  # loading greek core

list_media = []
data_titles = []


class MediaScrapped:
    def __init__(self, media_name):
        self.article_titles = get_news(media_name)
        self.media_name = media_name


def get_news(a_media):

    news_contents = []
    list_links = []
    list_titles = []

    response = requests.get(a_media['Url'])
    response.status_code

    coverpage = response.content

    # def f_all_params(tag):

    #     if tag.has_attr('class'):
    #         if ('full-link' in tag['class']) or ('article' in tag['class']):  # efsyn cms
    #             print("Ok this is a good sign")
    #             return(True)

    #     for child in tag.descendants: # this is usefull recersive for all the childern of a tag
    #         if child.name == 'h2' or child.name == 'article':
    #             return(True)

    #     return tag.has_attr('h2') or tag.has_attr('article')

    def f_all_params(tag):

        if tag.name == 'article':  # some cms uses this header for articles
            return True

        if tag.has_attr('class'):
            #    if ('full-link' in tag['class']) or ('article' in tag['class']):  # efsyn cms
            #         print("Ok this is a good sign")
            #         return(True)

            for class_name in tag['class']:
                if re.match(".*article.*", class_name) or re.match("art-container", class_name) or re.match("single-post-container", class_name):
                    return(True)

    #     for child in tag.descendants: # this is usefull recersive for all the childern of a tag
    #         if child.name == 'h2' or child.name == 'article':
    #             return(True)

    soup1 = BeautifulSoup(coverpage, 'html.parser')

    # Important call - Choose the correct classname
    # ['h2', 'article'], 'primary-content__article')  # h2 for kathimerini
    coverpage_news = soup1.find_all(f_all_params)

    #coverpage_news = soup1.select('a[href^="https://www.kathimerini.gr/"]')

    #coverpage_news = soup1.select('div[class^="article"]')

    """ 
    #write to file processed.
        with open('coverpage_news.txt','w') as f:
            f.write(str(coverpage_news))
    """

   # with open('coverpage_news.txt', 'w') as f:
    # f.write(soup1.b.prettify())

    print("Number of class resolved with regex pattern in " +
          str(a_media['Name']) + " is :" + str(len(coverpage_news)) + '\n')
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
        if coverpage_news[n].has_attr('href'):
            link = coverpage_news[n]['href']
        else:

            if (not coverpage_news[n].find('a')):
                # continuing because there is no href children
                continue

            link = coverpage_news[n].find('a')['href']
            # if not ("https" in link):

        if link in list_links:
            continue
        list_links.append(link)

        # Getting the title

        # Gettin

        # Reading the content (it is divided in paragraphs)
        linkresolved = requests.compat.urljoin(a_media['Url'], link)
        article = requests.get(linkresolved)
        article_content = article.content
        #print("Type of article is:" + str(type(article)))
        soup_article = BeautifulSoup(article_content, 'html.parser')

        # find title by h1 header. I don't like this syntax explicit for one media to type h2
        if (a_media['Name'] == 'Leftgr'):
            title = soup_article.find_all('h2')[1].getText()
        else:
            title = soup_article.find('h1').getText()

        list_titles.append(title)

        body = soup_article.find_all('div')  # class_='entry-content'
        #print("Type of body is:" + str(type(body)) +'\n')
        if (len(body) > 0):
            x = body[0].find_all('p')
            if len(x) == 0:
                #print("Continue because there is no 'p' elements \n")
                continue
        else:
            print("Continue because there is no 'div' elements \n")
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

    outname = a_media['Name'] + '.csv'

    path = os.path.dirname(os.path.dirname(__file__))

    outdir = path

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # watch out os backslash character, in windows // chars has different path
    fullname = os.path.join(outdir, "reports/" + outname)

    df_show_info.to_csv(fullname)

    return (df_show_info)  # function can also returned df_features


def scrapp_all():
    for media in media_list:
        list_media.append(MediaScrapped(media))


# ### READ KATHIMERINI ###
# path = os.path.dirname(os.path.dirname(__file__))
# outdir = path
# outname = 'Kathimerini' + '.csv'

# fullname = os.path.join(outdir, "reports/" + outname)

# data_csv = pd.read_csv(fullname)
# data_titles = data_csv["ArticleTitle"]

# #### READ TA NEA ######
# path = os.path.dirname(os.path.dirname(__file__))
# outdir = path
# outname = 'TaNea' + '.csv'

# fullname = os.path.join(outdir, "reports/" + outname)

# data_csv_tanea = pd.read_csv(fullname)
# data_titles_tanea = data_csv["ArticleTitle"]

def readnews(media_name):
    path = os.path.dirname(os.path.dirname(__file__))
    outdir = path
    outname = str(media_name) + '.csv'

    fullname = os.path.join(outdir, "reports/" + outname)

    data_csv = pd.read_csv(fullname)
    data_titles.append(data_csv['Article Title'])

for media in media_list:
    readnews(media['Name'])

print(data_titles)


def HeadingSimilarity(tokens1, tokens2):
    counter = 0
    for token in tokens1:
        if (not token.is_stop):
            for token2 in tokens2:
                similarity_value = token.similarity(token2)
                if similarity_value > 0.7:
                    counter += 1
                    break  # in order to avoid multiple matchings, but this has pros and cons
                if counter >= 2:
                    return(True)


                   
for title_m in data_titles[1]:
    for title in data_titles[4]:
        tokens1 = nlp(title_m)
        tokens2 = nlp(title)
        if(HeadingSimilarity(tokens1, tokens2)):
            print("Titles matching with similarity are: Efsyn: %s - Avgi: %s" %
                  (title_m, title))
            #CreateThread()  # this function will create an important topic targeted by other media
            input(" press enter to continue")
            break



'''
tokens1 = nlp("Ανοιξε το βιβλίο προσφορών για το δεκαετές ομόλογο")
tokens2 = nlp("Daily Telegraph: Πάτμος και Αθήνα στις καλύτερες κρουαζιέρες του κόσμου για το 2022")
print(tokens1.similarity(tokens2))

if(HeadingSimilarity(tokens1, tokens2)):
    print("Matched")
'''
