import os

import pandas as pd
import numpy as np
import requests
from credentials import *
from twitterAPIFactory import *

import plotly.graph_objs as go
import plotly.offline as offline

from flask import Flask, jsonify, render_template

app = Flask(__name__)

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate(r"C:\Users\abooth\Documents\Python Scripts\SentimentAnalysisApp\sentiment-twitter-app-firebase-adminsdk.json")
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': FB_URL
})

@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")


@app.route("/tag/<tag>/<limit>")
def tags(tag, limit):
    """Return a list of sample names."""

    #Get data from database
    tweetsDB = "tweets.json"
    r = requests.get(FB_URL + tweetsDB)
    r = r.json()
    style_in_html = ""
    data_in_html = ""
    if r:
        data = [r[i] for i in r]
        df = pd.DataFrame.from_dict(data, orient='columns')
        dfSub = df[df.Tag.str.lower() == tag.lower()]
        dfSub = dfSub.drop(columns=['CreatedAt', 'CreatedAtLocal'])
        dfSub = dfSub.tail(int(limit)) #get last limit amount of rows

        # Return a list of the column names (sample names)
        pd.set_option('display.max_colwidth', -1) #don't truncate columns
        data_in_html = dfSub.to_html(index=False)
        total_id = 'totalID'
        header_id = 'headerID'
        style_in_html = """<style>
            table#{total_table} {{color:black;font-size:13px; text-align:center; border:0.2px solid black;
                                border-collapse:collapse; table-layout:fixed; height:250px; text-align:center }}
            thead#{header_table} {{background-color: #4D4D4D; color:#ffffff}}
            </style>""".format(total_table=total_id, header_table=header_id)
        data_in_html = re.sub(r'<table', r'<table id=%s ' % total_id, data_in_html)
        data_in_html = re.sub(r'<thead', r'<thead id=%s ' % header_id, data_in_html)
    return jsonify(style_in_html + data_in_html)

@app.route("/dowork/<tag>/<limit>")
def doWork(tag, limit):
    """Return a list of sample names."""

    #Get data from database
    final = DoWork(tag, limit)

    # Return a list of the column names (sample names)
    return jsonify(final)

@app.route("/doworkforuser/<username>/<count>")
def DoWorkForUser(username, count):
    """Return a list of sample names."""

    #Get data from database
    final = DoWorkForUserTwitter(username, count)

    # Return a list of the column names (sample names)
    return jsonify(final)

@app.route("/tagplot/<tag>/<limit>")
def tagplots(tag, limit):
    #Get data from database
    tweetsDB = "tweets.json"
    r = requests.get(FB_URL + tweetsDB)
    r = r.json()
    rtnString = ""
    if r:
        data = [r[i] for i in r]
        df = pd.DataFrame.from_dict(data, orient='columns')
        dfSub = df[df.Tag.str.lower() == tag.lower()]
        dfSub = GetRollingMeans(dfSub, vader=True)
        dfSub = dfSub.tail(int(limit)) #get last limit amount of rows

        dataToPlot = dfSub
        dataToPlot = dataToPlot[["Clean_Date", "Less_Clean_Text", "Tweet_Link", "Sentiment_VADER", "rolling_mean", "rolling_mean2"]]

        plotTitle = tag + " Sentiment Tweets"
        yLabel = 'Sentiment'
        yStart = -1.05
        yEnd = 1.05
        hoverFormat = '.2f'

        x = dataToPlot.index.values
        data = []
        trace = go.Scatter(
                x=x,
                y=dataToPlot["Sentiment_VADER"],
                text = [row.Less_Clean_Text[0:100] + "..." for index, row in dataToPlot.iterrows()],
                mode='lines+markers',
                name = "Sentiment_VADER",
                line = dict(
                        color = 'rgb(6, 174, 213)',
                        width = 4,
                        shape='linear'))

        data.append(trace)
        plotAnnotes = []
        for index, row in dataToPlot.iterrows():
            plotAnnotes.append(dict(x=index,
                                    y=row.Sentiment_VADER,
                                    text="<a href='" + row.Tweet_Link + "'> </a>".format("Text"),
                                    showarrow=False,
                                    xanchor='center',
                                    yanchor='middle',
                                    ))
        trace = go.Scatter(
                x=x,
                y=dataToPlot["rolling_mean"],
                mode='lines+markers',
                name = "20 MA",
                line = dict(
                        color = 'rgb(255,165,0)',
                        width = 4,
                        shape='linear'))

        data.append(trace)
        trace = go.Scatter(
                x=x,
                y=dataToPlot["rolling_mean2"],
                mode='lines+markers',
                name = "50 MA",
                line = dict(
                        color = 'rgb(255,0,255)',
                        width = 4,
                        shape='linear'))

        data.append(trace)
        layout = go.Layout(
            title = plotTitle,
            annotations=plotAnnotes,
            yaxis = dict(title = yLabel,
                        range = [yStart, yEnd],
                        hoverformat = hoverFormat),
            xaxis = go.layout.XAxis(
                tickmode = 'array',
                tickvals = dataToPlot.index.values[0::10],
                ticktext = dataToPlot.Clean_Date[0::10]
            )
        )

        fig = go.Figure(data = data, layout = layout)
        rtnString = offline.plot(fig, include_plotlyjs=False, output_type='div')
    return jsonify(rtnString)

if __name__ == "__main__":
    app.run(debug=True)
