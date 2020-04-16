from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

@app.route("/")
def index():
    mars_news = mongo.db.mars_news.find_one()
    return render_template("index.html", mars_news=mars_news)


@app.route("/scrape")
def scraper():
    mars_news = mongo.db.mars_news
    mars_news_data = scrape_mars.scrape_nasa()
    mars_news.update({}, mars_news_data, upsert=True)
    return redirect("/", code=302)

@app.route("/mars_facts")
def mars_facts():
    raw_html = ''
    with open('mars_facts.html', 'r') as file:
        raw_html = file.read()
    return raw_html


if __name__ == "__main__":
    app.run(debug=True, port=5003)
    #make different port


