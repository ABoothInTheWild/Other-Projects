# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 23:58:26 2017

@author: Alexander
"""
#Thanks to https://stackoverflow.com/questions/4576077/python-split-text-on-sentences
import re

caps = "([A-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websitesSuff = "[.](com|net|org|io|gov)"
websitesPre = "(www)[.]"
digits = "([0-9])"

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websitesSuff,"<prd>\\1",text)
    text = re.sub(websitesPre,"\\1<prd>",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    if "e.g." in text: text = text.replace("e.g.","e<prd>g<prd>")
    if "i.e." in text: text = text.replace("i.e.","i<prd>e<prd>")
    text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
    text = re.sub(digits + "[.]" + digits," \\1<prd>\\2",text)
    if '"' in text: text = text.replace(".\"","\".")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

#testStr = "Mr. John Johnson Jr. was born in the U.S.A but earned his Ph.D. in Israel in 5.5 years before joining Nike Inc. as an engineer. He also worked at www.craigslist.org as a business analyst, e.g. or i.e. Data Science."
#ugh = "You may copy it, give it away or re-use it under the terms of the Project Gutenberg License included with this eBook or online at www.gutenberg.org Title: Alices Adventures in Wonderland Author: Lewis Carroll Posting Date: June 25, 2008 [EBook #11] Release Date: March, 1994 Last Updated: October 6, 2016 Language: English Character set encoding: UTF-8 *** START OF THIS PROJECT GUTENBERG EBOOK ALICES ADVENTURES IN WONDERLAND *** ALICES ADVENTURES IN WONDERLAND Lewis Carroll THE MILLENNIUM FULCRUM EDITION  3.0 CHAPTER I. Down the Rabbit-Hole Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do: once or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it, and what is the use of a book, thought Alice without pictures or conversations?'"
#test = split_into_sentences(testStr)
#ugh = 'sdfsd "sfsdfds?" sdfsdf.'
#split_into_sentences(ugh)


text = '"What is his name?" "Bingley." "Is he married or single?"'
split_into_sentences(text)
TextBlob(text).sentences

for grp in re.findall(r'"[^"]*\."|("[^"]*")*([^".]*\.)', text):
    print (grp)