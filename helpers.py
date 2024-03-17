# import csv
# import datetime
# import pytz
# import requests
# import subprocess
# import urllib
# import uuid

# import io
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import plotly
import plotly.express as px
import json

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def baby_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("babies") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

def sort_babies(babies, baby_id):
    baby_index = [i for i, baby in enumerate(babies) if baby.get("baby_id") == baby_id][0]
    this_baby = babies.pop(baby_index)
    babies.insert(0, this_baby)
    return babies


def feed_fig_px(feeds):
    df = pd.DataFrame(feeds)
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    df["quantity_ml"]= df["quantity_ml"].fillna(0)
    df["quantity_ml"]= df["quantity_ml"].replace('', 0)
    df["duration_minutes"]= df["duration_minutes"].fillna(0)
    df["duration_minutes"]= df["duration_minutes"].replace('', 0)

    daily_data = df.groupby("date")[["duration_minutes", "quantity_ml"]].sum()

    daily_data_indexed = daily_data.reset_index()
    daily_data_indexed.rename(columns={"duration_minutes": "Breast (minutes)", "quantity_ml": "Bottle (ml)"}, inplace=True)

    labels = {"date": "Date", "value": "Total Time (mins)/Volume (ml)", "variable": "Feed Type"}
    fig = px.bar(daily_data_indexed, x='date', y=['Breast (minutes)', 'Bottle (ml)'], barmode='group', title='Sum of Feeds by Day', labels=labels)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def sleep_fig_px(sleeps): 
    df = pd.DataFrame(sleeps)
    df["start_time"] = pd.to_datetime(df["start_time"])
    df["end_time"] = pd.to_datetime(df["end_time"])
    df["start_date"] = df["start_time"].dt.date
    df["begin_hour"] = df["start_time"].dt.hour
    df["overnight"] = (df["begin_hour"] >= 18) | (df["begin_hour"] < 6)
    df["start_date"] = df["start_date"].where(df["begin_hour"] > 6, (df["start_time"] - pd.Timedelta(days=1)).dt.date)
    df = df.groupby(["start_date", "overnight"])["duration_minutes"].sum()
    df = df.reset_index()
    df["hours"] = (df["duration_minutes"] / 60).round(1)
    df["overnight"] = df["overnight"].apply(lambda x: "Night" if x else "Day")
    df.rename(columns = {"overnight": "Night/Day", "start_date": "Date"}, inplace=True)
    df.sort_values("Night/Day", inplace=True, ascending=False)
    
    labels = {"hours": "Hours of Sleep"}
    colors = {"Night": "#04658F", "Day": "#FF8C00"}
    
    fig = px.bar(df, x='Date', y='hours', color='Night/Day', labels=labels, title="Total Sleep by Day", color_discrete_map=colors)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON

def nappy_fig_px(nappies):
    df = pd.DataFrame(nappies)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    df["both"] = (df["wet"] & df["dirty"])
    df["wet"] = df["wet"].where(df["both"] == 0, 0)
    df["dirty"] = df["dirty"].where(df["both"] == 0, 0)
    df = df.groupby(["date"])[["wet", "dirty", "both"]].sum()
    df = df.reset_index()
    df.rename(columns={"wet": "Wet", "dirty": "Dirty", "both": "Both"}, inplace=True)
    
    labels = {"value": "Number of Nappies", "variable": "Nappy Contents", "date": "Date"}
    colors = {"Wet": "#FFCC00", "Dirty": "#9E5E05", "Both": "#9E7F05"}
    fig = px.bar(df, x='date', y=['Wet', 'Dirty', 'Both'], labels=labels, color_discrete_map=colors)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON
    