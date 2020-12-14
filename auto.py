from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from easylog import log
import time as _time
import json
import re
import os
import sys

STATIC_PATH = "./static/"
DATA_PATH = "./data/"
DRIVER_PATH = "./static/chromedriver.exe"

class RepProcesser:
    """
    A twitter processer for getting reply.
    """
    def __init__(self, webdriver):
        self.driver = webdriver
        self.count = 0
        self.data = []

    def open(self, url):
        """
        Open a tweet from `url` by webdriver. 
        The `url` is like `https://twitter.com/KaguraMea_VoV/status/1332606260282212353/`.
        """
        self.driver.get(url)
        self.id = str(re.search("status/([0-9]*)", url).group(1))
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article')))

    def modify(self):
        """
        Modifying the web page.
        """
        self.driver.set_window_size(640, 2000)
        self.driver.execute_script('''
            function clear(node){
                for(let e of node.parentElement.children) {if(e !== node) e.remove()};
                if(node.id !== "react-root") clear(node.parentElement);
            }
            document.querySelector("div[data-testid=primaryColumn]").style.maxWidth="640px";
            document.querySelector("div[data-testid=primaryColumn]").style.border="0";
            clear(document.querySelector('section[aria-labelledby=accessible-list-0]'));
        ''')


    def process(self):
        """
        Start to process the tweet.
        """
        self.data_path = f'{DATA_PATH}/{self.id}/'
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)
        self.modify()

        interact = []
        while True:
            tweets= self.driver.find_elements_by_css_selector("main section>div>div>div")
            if len(tweets) == 0:
                with open(f'{self.data_path}/data.json', "w", encoding="utf-8") as f:
                    f.write(json.dumps(self.data))
                break

            try:
                for tweet in tweets:
                    self.driver.execute_script('''
                        try {
                            document.querySelectorAll("section div[role=button] div[dir=auto]").forEach(o=>o.click());
                            document.querySelectorAll("article div[role=group]").forEach(o=>o.remove());
                        } catch {}
                    ''')
                    tweet.find_element_by_tag_name("article")  # raise a error when no element be found.
                    interact.append(tweet)
            except:
                if len(interact) >= 2 or (                    # have interact each other.
                self.count == 0 and len(interact) == 1):      # the main tweet.
                    self.count = self.count + 1
                    self.get_data(interact)
                for _ in range(len(interact) + 1):  #  remove the node after got it.
                    self.driver.execute_script('''
                        document.querySelector("main section>div>div>div").remove();
                    ''')
                interact = []
                continue
        return self.data

    def get_data(self, elements):
        """
        Getting data from web page and get screenshots of tweet.

        elements : A list of webdriver element.
        """
        for index, element in enumerate(elements):
            info = self.driver.execute_script('''
                var article = document.body.querySelectorAll("article")[%d];
                if (article.querySelector("a div[dir=ltr]")) {
                    var user = article.querySelector("a div[dir=ltr]").innerText;
                } else {
                    var user = "";
                }
                if (article.querySelector("a time")) {
                    var datetime = article.querySelector("a time").getAttribute("datetime");
                } else {
                    var datetime = "";
                }
                if (article.querySelector("[lang]")) {
                    var text = article.querySelector("[lang]").innerText;
                } else {
                    var text = "";
                }
                return {"user": user, "datetime": datetime, "text": text};
            '''%(index))
            if info["user"] == "":
                break
            if len(elements) == 1:  # the main tweet.
                self.driver.execute_script('''
                    var article = document.querySelectorAll("article>div>div>div>div")[2];
                    article.children[3].remove();
                ''')
                sc_name = "main" + info["user"]
            else:
                t = info["datetime"]
                sc_name = t[:13] + t[14:16] + t[17:19] + info["user"]  # remove the char ":" .
            sc_path = self.data_path + f'/{sc_name}.png'
            info["img"] = sc_path
            info["index"] = str(self.count) + "-" + str(index+1)
            self.data.append(info)
            if not os.path.exists(sc_path):
                _time.sleep(0.2)  # maybe be misplaced if too fast.
                element.screenshot(sc_path)
        print("[推文获取]已保存 {} 条回复.".format(self.count))

def execute(url):
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")
    option.add_argument('--disable-gpu')
    option.add_experimental_option('excludeSwitches', ['enable-logging'])
    with webdriver.Chrome(DRIVER_PATH, options=option) as driver:
        processer = RepProcesser(driver)
        print("[推文获取]获取页面中...")
        processer.open(url)
        print("[推文获取]下载图片中...")
        data = processer.process()
        print("[推文获取]完成！")
        return data

if __name__ == "__main__":
    url = sys.argv[1]
    execute(url)