import os
import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch, helpers, NotFoundError
from Logger import Logger


class Ingestor:
    def __init__(self, logger):
        self.logger = logger
        self.ygoprodeck_endpoint = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
        self.fandom_endpoint = "https://yugioh.fandom.com/wiki"
        self.es_endpoint = os.getenv("ELASTICSEARCH_ENDPOINT")
        self.es = Elasticsearch(self.es_endpoint)
        self.index = "yugioh_cards"

    def get_cards(self):
        try:
            r = requests.get(self.ygoprodeck_endpoint)
            result = r.json()["data"]

            self.logger.info("get_cards", "Successfully fetch data from YGOPRODECK")
            return result
        except Exception as err:
            self.logger.error("get_cards", err)
            return {}

    def get_japanese_name(self, name):
        formatted_name = name.replace(" ", "_")
        url = self.fandom_endpoint + "/" + formatted_name

        try:
            while True:
                page = requests.get(url)
                if page.status_code != 200 and page.status_code != 404:
                    continue

                soup = BeautifulSoup(page.content, "html.parser")

                span = soup.find("table", {"class": "cardtable"})
                span = span.find("span", {"lang": "ja"})
                jp_name = span.text

                self.logger.info("get_japanese_name", "Successfully retrieve japanese name for {0}".format(name))
                return jp_name
        except Exception as err:
            self.logger.error("get_japanese_name", "Unable to retrieve japanese name for {0} due to {1}".format(name, err))
            return ""

    def initial_cards_in_es(self, cards):
        try:
            for card in cards:
                try:
                    resp = self.es.search(
                        index=self.index,
                        query={
                                "term": {
                                    "id": card["id"]
                                }
                            }
                    )

                    if len(resp['hits']['hits']) > 0:
                        continue
                except NotFoundError as err:
                    pass

                self.es.index(
                    index=self.index,
                    document={
                        "id": card["id"],
                        "name": card["name"]
                    }
                )
                
            self.logger.info("initial_cards_in_es", "Initially add data to ES from YGOPRODECK successfully")

        except Exception as err:
            self.logger.error("initial_cards_in_es", err)

    def update_japanese_name_in_es(self, cards):
        try:
            for card in cards:
                resp = self.es.search(
                    index=self.index,
                    query={
                            "term": {
                                "id": card["id"]
                            }
                        }
                )
                
                card_es_id = resp["hits"]["hits"][0]["_id"]
                card_jp_name = resp["hits"]["hits"][0].get("jp_name")

                if card_jp_name is None or card_jp_name == "":
                    jp_name = self.get_japanese_name(card["name"])

                    self.es.update(
                        index=self.index,
                        id=card_es_id,
                        doc={
                            "jp_name": jp_name
                        }
                    )

            self.logger.info("update_japanese_name_in_es", "Add japanese names successfully")

        except Exception as err:
            self.logger.error("update_japanese_name_in_es", err)

    def process(self):
        cards = self.get_cards()
        self.initial_cards_in_es(cards)
        self.update_japanese_name_in_es(cards)
