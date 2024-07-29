from elasticsearch import Elasticsearch
import datetime
import re
import logging
from essential_tokens import ELASTIC_DOMAIN


searchBody = {
    "track_total_hits": True,
    "size" : 10000,
    "query": {
        "bool": {
            "must": [],
                "filter": [
                    {
                        "range": {
                            "@timestamp": {
                                "gte": "now-1m",
                                "lte": "now",
                                "time_zone" : "Asia/Taipei"
                            }
                        }
                    },
                    {
                        "match_phrase": {
                            "log.file.path": "/var/opt/mssql/log/sqlagent.out"
                        }
                    },
                    { 
                        "exists": {
                            "field": "error.message"
                        }
                    }                
                ],
                "should": [],
                "must_not": [
                    {
                        "match_phrase": {
                            "input.type": "filestream"
                        }
                    }
                ]
        }
    }
}


class ElasticGetter :
    def __init__(self):
       self.es = Elasticsearch(f"http://{ELASTIC_DOMAIN}:9200")

    def getlog(self):
        logging.info('🫑  Start Qureying Elastic !')
        result = []
        resultcount = 0
        currYear = str(self.__getYear())
        currMonth = str(self.__getMonth())
        currDay = str(self.__getDay())
        yesterday = str(self.__getDay()-1)
        if len(currMonth) == 1 :
            currMonth = "0" + currMonth
        if len(currDay) == 1 :
            currDay = "0" + currDay
        if len(yesterday) == 1 :
            yesterday = "0" + yesterday

        index=f".ds-filebeat-*-{currYear}.{currMonth}.{currDay}-*"
        indexYesterday = f".ds-filebeat-*-{currYear}.{currMonth}.{yesterday}-*"
        #print(index)
        #print(indexYesterday)
        resp = self.es.search(
            # dynamic date
            index=index,
            body=searchBody,
        )
        respYesterday = self.es.search(
            # dynamic date
            index=indexYesterday,
            body=searchBody,
        )
        hits = resp.body["hits"]["hits"]
        logging.info(f"🫑  hits today count = {len(hits)}")
        hitsYesterday = respYesterday.body["hits"]["hits"]
        logging.info(f"🫑  hits Yesterday count = {len(hitsYesterday)}")
        for hit in hits :
            isMatch = re.match(".*fail.*", hit['_source']['error']['message'][0], re.I)
            if isMatch != None :
                result.append(hit['_source'])
                resultcount += 1

        for hit in hitsYesterday :
            isMatch = re.match(".*fail.*", hit['_source']['error']['message'][0], re.I)
            if isMatch != None :
                result.append(hit['_source'])
                resultcount += 1

        return result, resultcount


    def __getDay(self):
        now = datetime.datetime.now()
        return now.day

    def __getMonth(self):
        now = datetime.datetime.now()
        return now.month

    def __getYear(self):
        now = datetime.datetime.now()
        return now.year
    
    def __del__(self) :
        self.es.transport.close()


if __name__ == "__main__" :
    es = ElasticGetter()
    i, j = es.getlog()
    print(i)
    es.__del__()