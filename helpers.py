import csv
import datetime
# import pytz
import requests
import subprocess
import urllib
import uuid

import io
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

def feed_figure(feeds):
    df = pd.DataFrame(feeds)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    daily_feeding_data = df.groupby([df['timestamp'].dt.date, 'type'])[['duration_minutes', 'quantity_ml']].sum().unstack(fill_value=0)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    width = 0.2
    daily_feeding_data["duration_minutes"].plot(kind='bar', ax=ax1, color='skyblue', position=1, width=width, legend=None)
    daily_feeding_data["quantity_ml"].plot(kind='bar', ax=ax2, color='coral', position=0, width=width, legend=None)
    plt.title("Daily Feed Totals by Type")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Breast: Total Time (mins)", color='skyblue')
    ax1.tick_params(axis='y', labelcolor='skyblue')
    ax2.set_ylabel("Bottle: Total Quantity (ml)", color='coral')
    ax2.tick_params(axis='y', labelcolor='coral')
    plt.tight_layout()

    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return output.getvalue(), 'image/png'

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