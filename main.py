from json.tool import main
import os
import re
import time
from tokenize import Name
from turtle import heading
from typing import Pattern
import requests
from bs4 import BeautifulSoup
import numpy as np
import json
import pandas as pd
import spacy
from medialist import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


nlp = spacy.load('el_core_news_lg')  # loading greek core

list_media = []
data_titles = []
data_csv_list = []

list_of_left_imparticles = []


class MediaScrapped:
    def __init__(self, media_name):
        self.article_titles = get_news(media_name)
        self.media_name = media_name


class ImpArticle:
    main_header_attached = ""
    article_title = []
    media_name = []
    link = []

    def __str__(self):
        str = ("Printing Object ImpArticle: Main Header: %s \n" %
               self.main_header_attached)
        for i in range(len(self.article_title)):
            str += ("Article_Attached : %s \n Link: %s Media: %s\n" %
                    (self.article_title[i], self.link[i], self.media_name[i]))

        return (str)


def get_news(a_media):

    news_contents = []
    list_links = []
    list_titles = []

    if (a_media['Dynamic'] == True):
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()))
        driver.get(a_media['Url'])
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

    else:
        response = requests.get(a_media['Url'])
        response.status_code
        coverpage = response.content
        soup = BeautifulSoup(coverpage, 'html.parser')

    def f_all_params(tag):

        if tag.name == 'article':  # some cms uses this header for articles
            return True

        if tag.has_attr('class'):
            for class_name in tag['class']:
                if re.match(".*article.*", class_name) or re.match("art-container", class_name) or re.match("single-post-container", class_name):
                    return(True)

    # Important call - Choose the correct classname

    coverpage_news = soup.find_all(f_all_params)

    print("Number of class resolved with regex pattern in " +
          str(a_media['Name']) + " is :" + str(len(coverpage_news)) + '\n')

    # Empty lists for content, links and titles
    news_contents = []
    list_links = []
    list_titles = []

    for n in np.arange(0, len(coverpage_news)):

        # Getting the link of the article
        if coverpage_news[n].has_attr('href'):
            link = coverpage_news[n]['href']
            if link.startswith("javascript:"):
                # this happens only in media Ethnos, because they use href = "javascript:..."
                print("I found a bug \n")
                continue

        else:

            if (not coverpage_news[n].find('a')):
                # continuing because there is no href children
                continue

            link = coverpage_news[n].find('a')['href']
            if link.startswith("javascript:"):
                print("I found a bug \n")
                continue
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
        # some articles does not have h1 as a header tag
        elif soup_article.has_attr('h1'):
            title = soup_article.find('h1').getText()
        elif soup_article.has_attr('h2'):
            title = soup_article.find('h2').getText()
        else:
            title = ''

        title = title.replace('\n', ' ')  # remove whitespace trailing
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


def readall():
    for media in media_list:
        readnews(media['Name'])
    match_leftwing_media()


def readnews(media_name):
    path = os.path.dirname(os.path.dirname(__file__))
    outdir = path
    outname = str(media_name) + '.csv'

    fullname = os.path.join(outdir, "reports/" + outname)

    data_csv = pd.read_csv(fullname)
    data_csv_list.append(data_csv)
    data_titles.append(data_csv['Article Title'])

# print(data_titles)


def HeadingSimilarity(tokens1, tokens2):
    counter = 0
    for token in tokens1:
        if (not token.is_stop and not token.is_punct):
            for token2 in tokens2:
                similarity_value = token.similarity(token2)
                if similarity_value > 0.7:
                    #print(token, token2)
                    counter += 1
                    break  # in order to avoid multiple matchings, but this has pros and cons
                if counter >= 2:
                    return(True)


# Familiar media lookup
def match_leftwing_media():
    for i in range(0, 3):
        for j in range(i+1, 3):
            for title_m in data_csv_list[i]["Article Title"]:
                index = 0
                for title in data_csv_list[j]["Article Title"]:
                    index += 1
                    tokens1 = nlp(title_m)
                    tokens2 = nlp(title)
                    if(HeadingSimilarity(tokens1, tokens2)):
                        #print("Titles matching with similarity are: Efsyn: %s - Avgi: %s" %(title_m, title))
                        # CreateThread()  # this function will create an important topic targeted by other media
                        #input(" press enter to continue")
                        p = ImpArticle()
                        p.main_header_attached = title_m
                        p.article_title .append(
                            str(title).replace('\t', '').replace('\n', ''))
                        p.media_name.append(
                            data_csv_list[j].at[1, 'Newspaper'])
                        p.link.append(
                            data_csv_list[j].loc[index-1, 'Article Link'])
                        list_of_left_imparticles.append(p)
                        break

    for imparticle in list_of_left_imparticles:
        print(imparticle.__str__())


menu_options = {
    1: 'Scrapp All',
    2: 'Read csvs and Match leftwing',
    3: 'Read csvs and Match rightwing',
    4: 'Exit',
}


def print_menu():
    for key in menu_options.keys():
        print(key, '--', menu_options[key])


def option3():
    print("not yet accomplished \n")


def main():
    if __name__ == '__main__':
        while(True):
            print_menu()
            option = ''
            try:
                option = int(input('Enter your choice: '))
            except:
                print('Wrong input. Please enter a number ...')
            # Check what choice was entered and act accordingly
            if option == 1:
                scrapp_all()
            elif option == 2:
                readall()
            elif option == 3:
                option3()
            elif option == 4:
                print('Thanks message before exiting')
                exit()
            else:
                print('Invalid option. Please enter a number between 1 and 4.')


get_news(media_list[4])


"""
#TESTS

tokens1 = nlp("«Κάτι σαράβαλες καρδιές»*")
tokens2 = nlp("Κορωνοϊός / Διαρρέουν χαλάρωση μέτρων παρά την επέλαση της «Όμικρον»")
print(tokens1.similarity(tokens2))

if(HeadingSimilarity(tokens1, tokens2)):
    print("Matched")
"""
