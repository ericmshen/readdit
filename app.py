from flask import Flask, render_template, request, redirect
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

import requests
from bs4 import BeautifulSoup
import urllib

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template(
        "index.html",
        displayresults = False
    )

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        if not request.form.get('subreddit'):
            return render_template(
            "index.html",
            displayresults = False
        )
        
        timechoices = {
            'top posts right now': 'hour',
            'top posts today': 'day',
            'top posts this week': 'week',
            'top posts this month': 'month',
            'top posts this year': 'year',
            'top posts of all time': 'all'
        }

        timechoice = request.form.get('timeperiod')

        subentry = request.form.get('subreddit')
        sub = urllib.parse.quote_plus(subentry.lower())

        url = 'https://old.reddit.com/r/' + sub + "/top/?t=" + timechoices[timechoice]
        headers = {'User-Agent': 'Mozilla/5.0'}

        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        page_head = soup.find('head')
        subname = page_head.find('title').text.split()[-1]

        posts = []

        site_table = soup.find(id = "siteTable")
        entries = site_table.find_all(class_ = "thing")
        promoted_entries = site_table.find_all(class_ = "promoted")
        not_promoted_entries = []

        for entry in entries:
            if entry not in promoted_entries:
                not_promoted_entries.append(entry)

        for i in range(len(not_promoted_entries)):
            post = {}
            user_post = not_promoted_entries[i]
            top_matter = user_post.find(class_ = "top-matter")
            
            title = top_matter.find(class_ = "title")
            headline = title.find('a')
            post["title"] = headline.get_text()
            
            link_section = top_matter.find(class_ = "first")
            link_material = link_section.find('a')
            link = link_material.get('href')
            post["link"] = link

            posts.append(post)
        
        return render_template(
            "index.html",
            displayresults = True,
            timetext = timechoice,
            subname = subname,
            posts = posts,
        )
    else:
        return render_template(
            "index.html",
            displayresults = False
        )
        