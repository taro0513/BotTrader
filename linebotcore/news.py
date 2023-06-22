import requests
from bs4 import BeautifulSoup
from linebot.models import *

news_url = "https://tw.news.yahoo.com/stock/"


class NewsHandler:
    def __init__(self, message_text):
        self.message_text = message_text
        self.messages = []
        self.articles = []
        self.columns = []
        self.detect()

    def detect(self):
        self.crawl_stock_news()
        for article in self.articles:
            if self.message_text.strip() in article["title"]:
                self.generate_news_columns(
                    article["title"],
                    article["summary"][:45] + '...',
                    article["source"],
                    article["url"]
                )
        self.generate_news_carousel()

    def crawl_stock_news(self, start=0, limit=999999):
        response = requests.get(news_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all("li", class_="js-stream-content Pos(r)")[start:limit]
            print("Number of articles:", len(articles))
            for article in articles:
                title = article.find("h3").text.strip()
                summary = article.find("p").text.strip()
                source = article.find("div", class_="C(#959595)").text
                url = 'https://tw.news.yahoo.com' + article.find("a")["href"]
                self.articles.append({
                    "title": title,
                    "summary": summary,
                    "source": source,
                    "url": url
                })
        else:
            return

    def generate_news_columns(self, title, summary, source, url):
        self.columns.append(
            CarouselColumn(
                # thumbnail_image_url="https://i.imgur.com/7GdYzja.png",
                title=title,
                text="({}) {}".format(source, summary),
                actions=[
                    URITemplateAction(
                        label="原文連結",
                        uri=url
                    )
                ]
            )
        )

    def generate_news_carousel(self):
        if self.columns:
            self.messages.append(
                TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(
                        columns=self.columns
                    )
                )
            )
