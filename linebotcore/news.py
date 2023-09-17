import requests
from bs4 import BeautifulSoup
from linebot.models import *
from .models import StockWatchList, HistoricalRecord

news_url = "https://tw.news.yahoo.com/stock/"


class NewsHandler:
    def __init__(self, message_text='', key=None, user_id=None):
        self.key = key
        self.message_text = message_text
        self.messages = []
        self.user_id = user_id
        self.articles = []
        self.columns = []
        self.code_type = 'News'

    def setup_message_text(self, message_text):
        self.message_text = message_text

    def limit_columns_quantity(self):
        self.columns = self.columns[:10]
        # print(self.columns)

    def command(self, type='stock'):
        if type == 'stock':
            self.crawl_stock_news()
        elif type == 'default':
            self.crawl_default_news()
        elif type == 'world':
            self.crawl_international_news()

        for article in self.articles:
            self.generate_news_columns(
                article["title"][:30]+'...',
                article["summary"][:30]+'...',
                article["source"][:30],
                article["url"]
            )
        self.limit_columns_quantity()
        self.generate_news_carousel()

    def detect(self):
        if self.key == '關注':
            if StockWatchList.objects.filter(user_id=self.user_id, code=self.message_text, code_type=self.code_type).exists():
                self.messages.append(
                    TextSendMessage(text='{} ({}) 已經存在你的關注清單內了!'.format(self.message_text, self.code_type))
                )
            else:
                StockWatchList.objects.create(user_id=self.user_id, code=self.message_text, code_type=self.code_type)
                self.messages.append(
                    TextSendMessage(text='已新增至專注清單: {} ({})'.format(self.message_text, self.code_type))
                )
                HistoricalRecord.objects.create(user_id=self.user_id, message=self.message_text, action='關注新聞關鍵字', remark=self.code_type)
        elif self.key == '取消':
            if StockWatchList.objects.filter(user_id=self.user_id, code=self.message_text, code_type=self.code_type).exists():
                StockWatchList.objects.filter(user_id=self.user_id, code=self.message_text, code_type=self.code_type).delete()
                self.messages.append(
                    TextSendMessage(text='成功從關注清單移除 {} ({}) !'.format(self.message_text, self.code_type))
                )
                HistoricalRecord.objects.create(user_id=self.user_id, message=self.message_text, action='取消關注新聞關鍵字', remark=self.code_type)

            else:
                self.messages.append(
                    TextSendMessage(text='{} ({}) 不再你的關注清單內!'.format(self.message_text, self.code_type))
                )
        self.crawl_search_news()
        for article in self.articles:
            if self.message_text.strip() in article["title"]:
                self.generate_news_columns(
                    article["title"][:15],
                    article["summary"][:15] + '...',
                    article["source"],
                    article["url"]
                )


        titles = [article['title'] for article in self.articles]
        # print(titles)
        self.limit_columns_quantity()
        self.generate_news_carousel()
    
    def crawl_search_news(self, start=0, limit=999999):
        response = requests.get('https://tw.news.yahoo.com/search?p={}'.format(self.message_text))
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all("li", class_='StreamMegaItem')[start:limit]
            # print(len(articles))


            for article in articles:
                title = article.find("h3").text.strip()
                # print(title)
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

    def crawl_default_news(self, start=0, limit=999999):
        response = requests.get('https://tw.news.yahoo.com/archive')
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all("li", class_='StreamMegaItem')[start:limit]
            # print(len(articles))


            for article in articles:
                title = article.find("h3").text.strip()
                # print(title)
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

    def crawl_international_news(self):
        r = requests.get('https://edition.cnn.com/business')
        html_response = r.text
        soup = BeautifulSoup(html_response,'html.parser')
        left_articles = soup.find_all('div', class_='container__field-links container_lead-plus-headlines-with-images__field-links')
        articles = left_articles[0].find_all('div', class_='card container__item container__item--type-section container_lead-plus-headlines-with-images__item container_lead-plus-headlines-with-images__item--type-section')
        for article in articles:
            context = article.find_all('a')
            title = context[1].text.strip()
            url = 'https://edition.cnn.com' + context[1]['href'].strip()
            self.articles.append({
                    "title": title,
                    "summary": 'Click the button below to see the article.',
                    "source": 'CNN',
                    "url": url
                })

    def crawl_stock_news(self, start=0, limit=999999):
        response = requests.get(news_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all("li", class_="js-stream-content Pos(r)")[start:limit]
            for article in articles:
                title = article.find("h3").text.strip()
                # print(title)
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


