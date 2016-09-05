# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch
import elasticsearch

class Elastic:
    def __init__(self, _host='localhost', _port=9200):
        self.host = _host
        self.port = _port
        self.es = Elasticsearch([{'host': self.host, 'port': self.port }])

    def save2elk(self, _index, _doc_type, _id=None, _body=None):
        try:
            res = self.es.index(index=_index, doc_type=_doc_type, id=_id, body=_body)
            print ("Save to ELK: %r" % res['created'])
        except elasticsearch.ElasticsearchException as e:
            print (e)
            print ('Failed to save to ELK')

    def update2elk(self, _index, _doc_type, _id=None, _body=None):
        try:
            res = self.es.update(index=_index, doc_type=_doc_type, id=_id, body=_body)
            print (res)
            print ("Update to ELK")
        except elasticsearch.ElasticsearchException as e:
            print (e)
            print ('Failed to update to ELK')



