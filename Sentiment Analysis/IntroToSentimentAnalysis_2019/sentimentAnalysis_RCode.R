
# Author: Alexander Booth
# Date: January 25, 2018

# Intro to Sentiment Analysis in R

#References:
#https://www.tidytextmining.com/sentiment.html
#https://cran.r-project.org/web/packages/SentimentAnalysis/SentimentAnalysis.pdf

#Packages to Install
#install.packages("tidytext")
#install.packages("ggplot2")
#install.packages("gridExtra")
#install.packages("lattice")
#install.packages("hash")
#install.packages("wordcloud")
#install.packages("tm")

setwd('C:\\Users\\abooth\\source\\repos\\Other-Projects\\Sentiment Analysis\\IntroToSentimentAnalysis_2019')

# Load external libraries for visualizations and data manipulation
# ensure that these have been installed prior to calls
library(lattice) 
library(ggplot2)
library(scales)
library(grid)
library(RColorBrewer)
library(gridExtra)
library(hash)
library(reshape2)
source("fte_theme.R")

# Libraries for Text Analysis
library(tidytext)
library(dplyr)
library(stringr)
library(wordcloud)
library(tm)
library(tidyr)

# Get Data
library(janeaustenr)

#########################################################################
#Chapter 1: Get Lexicons and Data

#Get Lexicons
#Scores
get_sentiments("afinn")
#Binary
get_sentiments("bing")
#Also emotions
get_sentiments("nrc")

head(get_sentiments("afinn"), 20)
head(get_sentiments("bing"), 20)
head(get_sentiments("nrc"), 20)

# Prep Data
tidy_books <- austen_books() %>%
  group_by(book) %>%
  mutate(linenumber = row_number(),
         chapter = cumsum(str_detect(text, regex("^chapter [\\divxlc]", 
                                                 ignore_case = TRUE)))) %>%
  ungroup() %>%
  #Organize one word per row
  unnest_tokens(word, text)

View(tidy_books)

# It is a truth universally known...
View(tidy_books %>%
  filter(book == "Pride & Prejudice" & chapter == 1 & linenumber < 12))

##############################################################################
# Chapter 2: Intro to Lexicons

#Get NRC Positive Words
nrcpos <- get_sentiments("nrc") %>% 
  filter(sentiment == "positive")

#Get BING positive words
bingpos <- get_sentiments("bing") %>% 
  filter(sentiment == "positive")

#Get BING negative words
bingneg <- get_sentiments("bing") %>% 
  filter(sentiment == "negative")

#Get NRC Joy words
nrcjoy <- get_sentiments("nrc") %>% 
  filter(sentiment == "joy")

#Compare Positive words in Pride & Prejudice
tidy_books %>%
  filter(book == "Pride & Prejudice") %>%
  inner_join(nrcpos) %>%
  count(word, sort = TRUE)

tidy_books %>%
  filter(book == "Pride & Prejudice") %>%
  inner_join(bingpos) %>%
  count(word, sort = TRUE)

#Get Joyous words in Emma
tidy_books %>%
  filter(book == "Emma") %>%
  inner_join(nrcjoy) %>%
  count(word, sort = TRUE)

# Get Counts of Positive and Negative words in NRC and BING
get_sentiments("nrc") %>% 
  filter(sentiment %in% c("positive", 
                          "negative")) %>% 
  count(sentiment)

get_sentiments("bing") %>% 
  count(sentiment)

############################################################################
# Chapter 3: Comparison of various Lexicon sentiments on Pride and Prejudice

pride_prejudice <- tidy_books %>% 
  filter(book == "Pride & Prejudice")

# AFINN
afinn <- pride_prejudice %>% 
  inner_join(get_sentiments("afinn")) %>% 
  group_by(index = linenumber %/% 80) %>% 
  summarise(sentiment = sum(index)) %>% 
  mutate(method = "AFINN")

# Bing and NRC
bing_and_nrc <- bind_rows(pride_prejudice %>% 
                            inner_join(get_sentiments("bing")) %>%
                            mutate(method = "Bing et al."),
                          pride_prejudice %>% 
                            inner_join(get_sentiments("nrc") %>% 
                                         filter(sentiment %in% c("positive", 
                                                                 "negative"))) %>%
                            mutate(method = "NRC")) %>%
  count(method, index = linenumber %/% 80, sentiment) %>%
  spread(sentiment, n, fill = 0) %>%
  mutate(sentiment = positive - negative)

# Plot
bind_rows(afinn, 
          bing_and_nrc) %>%
  ggplot(aes(index, sentiment, fill = method)) +
  fte_theme() +
  geom_col(show.legend = FALSE) +
  facet_wrap(~method, ncol = 1, scales = "free_y")

############################################################
# Chapter 4: Are the Sentimental words being treated properly? Stop Words.

#Get all sentimental words
bing_word_counts <- tidy_books %>%
  inner_join(get_sentiments("bing")) %>%
  count(word, sentiment, sort = TRUE) %>%
  ungroup()

#Get top words in Jane Austen's canon with sentiment
bing_word_counts %>%
  group_by(sentiment) %>%
  top_n(10) %>%
  ungroup() %>%
  mutate(word = reorder(word, n)) %>%
  ggplot(aes(word, n, fill = sentiment)) +
  fte_theme() +
  geom_col(show.legend = FALSE) +
  facet_wrap(~sentiment, scales = "free_y") +
  labs(y = "Contribution to sentiment",
       x = NULL) +
  coord_flip()

#Get Wordcloud 1
tidy_books %>%
  anti_join(stop_words) %>%
  inner_join(get_sentiments("bing")) %>%
  count(word, sentiment, sort = TRUE) %>%
  acast(word ~ sentiment, value.var = "n", fill = 0) %>%
  comparison.cloud(colors = c("#F8766D", "#00BFC4"),
                   random.order=FALSE,
                   title.size=1.5,
                   max.words = 250)

# Add Miss to stop words
custom_stop_words <- bind_rows(data_frame(word = c("miss"), 
                                          lexicon = c("custom")), 
                               stop_words)
#clean again
tidy_books_clean <- tidy_books %>%
  anti_join(custom_stop_words)

#create new wordcloud 2
tidy_books_clean %>%
  inner_join(get_sentiments("bing")) %>%
  count(word, sentiment, sort = TRUE) %>%
  acast(word ~ sentiment, value.var = "n", fill = 0) %>%
  comparison.cloud(colors = c("#F8766D", "#00BFC4"),
                   random.order=FALSE,
                   title.size=1.5,
                   max.words = 250)

#############################################################
# Chapter 5: Sentiment Analysis throughout Jane Austen's Canon

#Get sentiment estimates for book chunks
janeaustensentiment <- tidy_books_clean %>%
  inner_join(get_sentiments("bing")) %>%
  count(book, index = linenumber %/% 80, sentiment) %>%
  spread(sentiment, n, fill = 0) %>%
  mutate(sentiment = positive - negative)

head(janeaustensentiment)

#Sentiment Plot across books
gg <- ggplot(janeaustensentiment, aes(index, sentiment, fill = book)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~book, ncol = 2, scales = "free_x") + 
  fte_theme()

gg

#############################################################
# Chapter 6: What are the most emotional chapters in each of Jane Austen's novels?

#Get Chapters
austen_chapters <- austen_books() %>%
  group_by(book) %>%
  unnest_tokens(chapter, text, token = "regex", 
                pattern = "Chapter|CHAPTER [\\dIVXLC]") %>%
  ungroup()

#Count Chapters per book
austen_chapters %>% 
  group_by(book) %>% 
  summarise(chapters = n())

#Get sad words
nrcsad <- get_sentiments("nrc") %>% 
  filter(sentiment == "sadness")

#Get all words
wordcounts <- tidy_books %>%
  group_by(book, chapter) %>%
  summarize(words = n())

#Get Saddest Chapters
tidy_books_clean %>%
  semi_join(nrcsad) %>%
  group_by(book, chapter) %>%
  summarize(sadwords = n()) %>%
  left_join(wordcounts, by = c("book", "chapter")) %>%
  mutate(ratio = sadwords/words) %>%
  filter(chapter != 0) %>%
  top_n(1) %>%
  ungroup()

#Get most negative chapters
tidy_books_clean %>%
  semi_join(bingneg) %>%
  group_by(book, chapter) %>%
  summarize(negativewords = n()) %>%
  left_join(wordcounts, by = c("book", "chapter")) %>%
  mutate(ratio = negativewords/words) %>%
  filter(chapter != 0) %>%
  top_n(1) %>%
  ungroup()

#get most positive chapters
tidy_books_clean %>%
  semi_join(bingpos) %>%
  group_by(book, chapter) %>%
  summarize(positivewords = n()) %>%
  left_join(wordcounts, by = c("book", "chapter")) %>%
  mutate(ratio = positivewords/words) %>%
  filter(chapter != 0) %>%
  top_n(1) %>%
  ungroup()

###############################################################
#Chapter 7: Term Frequencies

#Get most common words per book
book_words <- austen_books() %>%
  unnest_tokens(word, text) %>%
  count(book, word, sort = TRUE) %>%
  ungroup()
total_words <- book_words %>% 
  group_by(book) %>% 
  summarize(total = sum(n))
book_words <- left_join(book_words, total_words)
book_words

#Plot
ggplot(book_words, aes(n/total, fill = book)) +
  geom_histogram(show.legend = FALSE) +
  xlim(NA, 0.0009) +
  facet_wrap(~book, ncol = 2, scales = "free_y") +
  fte_theme()

#Caluclate tf*idf
book_words <- book_words %>%
  bind_tf_idf(word, book, n)
book_words

book_words %>%
  select(-total) %>%
  arrange(desc(tf_idf))

#Plot
book_words %>%
  arrange(desc(tf_idf)) %>%
  mutate(word = factor(word, levels = rev(unique(word)))) %>% 
  group_by(book) %>% 
  top_n(15) %>% 
  ungroup %>%
  ggplot(aes(word, tf_idf, fill = book)) +
  geom_col(show.legend = FALSE) +
  labs(x = NULL, y = "tf-idf") +
  facet_wrap(~book, ncol = 2, scales = "free") +
  coord_flip() +
  fte_theme()
###############################################################
#Chapter 8: Bigrams

#Get bigrams
austen_bigrams <- austen_books() %>%
  unnest_tokens(bigram, text, token = "ngrams", n = 2)
austen_bigrams %>%
  count(bigram, sort = TRUE)

#want to keep bigrams with mr and mrs
custom_stop_words2 <- stop_words[!(stop_words$word %in% c("mr", "mrs")),]

#Separate and Filter
bigrams_separated <- austen_bigrams %>%
  separate(bigram, c("word1", "word2"), sep = " ")
bigrams_filtered <- bigrams_separated %>%
  filter(!word1 %in% custom_stop_words2$word) %>%
  filter(!word2 %in% custom_stop_words2$word)

#new bigram counts
bigram_counts <- bigrams_filtered %>% 
  count(word1, word2, sort = TRUE)
bigram_counts

#Recombine
bigrams_united <- bigrams_filtered %>%
  unite(bigram, word1, word2, sep = " ")
bigrams_united

#Get most popular streets mentioned
bigrams_filtered %>%
  filter(word2 == "street") %>%
  count(book, word1, sort = TRUE)

#Get tf*idf score
bigram_tf_idf <- bigrams_united %>%
  count(book, bigram) %>%
  bind_tf_idf(bigram, book, n) %>%
  arrange(desc(tf_idf))
bigram_tf_idf

#Plot
bigram_tf_idf %>%
  arrange(desc(tf_idf)) %>%
  mutate(bigram = factor(bigram, levels = rev(unique(bigram)))) %>% 
  group_by(book) %>% 
  top_n(15) %>% 
  ungroup %>%
  ggplot(aes(bigram, tf_idf, fill = book)) +
  geom_col(show.legend = FALSE) +
  labs(x = NULL, y = "tf-idf") +
  facet_wrap(~book, ncol = 2, scales = "free") +
  coord_flip() +
  fte_theme()

#Get Not Bigrams
#Not is a stopword, so do not use filtered bigrams
bigrams_separated %>%
  filter(word1 == "not") %>%
  count(word1, word2, sort = TRUE)

#get sentiments with scores
AFINN <- get_sentiments("afinn")
AFINN

#Show most common sentiment-associated word to follow "not" 
not_words <- bigrams_separated %>%
  filter(word1 == "not") %>%
  inner_join(AFINN, by = c(word2 = "word")) %>%
  count(word2, value, sort = TRUE) %>%
  ungroup()
not_words

#Plot
not_words %>%
  mutate(contribution = n * value) %>%
  arrange(desc(abs(contribution))) %>%
  head(20) %>%
  mutate(word2 = reorder(word2, contribution)) %>%
  ggplot(aes(word2, n * value, fill = n * value > 0)) +
  geom_col(show.legend = FALSE) +
  xlab("Words preceded by \"not\"") +
  ylab("Sentiment score * number of occurrences") +
  coord_flip() +
  fte_theme()

###############################################################
# Chapter 9: Bee Movie, less code

#install.packages("SentimentAnalysis")
library(SentimentAnalysis)
library(qdapDictionaries)

beeMovie <- readLines("beeMovieScript.txt")

#Get chunks of 20 lines and their sentiments
#This takes a while to Run
beeSentiments = c()
i = 1
while(i < 1360){
  chunk <- paste(beeMovie[i:(i+19)], collapse = " ")
  sentiment <- analyzeSentiment(chunk, language = "english", removeStopwords = TRUE)
  beeSentiments <- append(beeSentiments, sentiment$SentimentQDAP)
  i = i + 20
}

#Create DataFrame
beeIndx <- seq(0, 1359, 20)
beeSentiments <- beeSentiments * 100
beeDf <- data.frame(beeIndx, beeSentiments)

#Plot
gg <- ggplot(beeDf, aes(beeIndx, beeSentiments, fill = beeSentiments)) +
  geom_col(show.legend = FALSE) +
  fte_theme() +
  theme(plot.title = element_text(face = "bold", size = (15))) +
  labs(title="Bee Movie Sentiment")
gg

#Get negative indices
beeDf[beeDf$beeSentiments < 0,]
