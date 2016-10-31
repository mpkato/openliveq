# -*- coding: utf-8 -*-
import requests
import json

class Chiebukuro(object):

    BASEURL = 'http://chiebukuro.yahooapis.jp/Chiebukuro/V1/'

    def __init__(self, apikey):
        self.apikey = apikey

    def detail_search(self, question_id,
        sort="-postdate", answer_id=None, start=1, results=0,
        use_title=80, image_type=0):
        '''
        質問詳細
        http://developer.yahoo.co.jp/webapi/chiebukuro/chiebukuro/v1/detailsearch.html
        '''
        params = {"question_id": question_id, "sort": sort, "start": start,
            "results": results, "use_title": use_title,
            "image_type": image_type}
        if answer_id is not None:
            params["answer_id"] = answer_id
        result = self._get_json_data("detailSearch", params)
        return result

    def _get_json_data(self, method, params):
        params = dict(params)
        url = self.BASEURL + method
        params["appid"] = self.apikey
        params["output"] = "json"
        response = requests.get(url, params)
        res = json.loads(response.text)
        if "Error" in res:
            raise ChiebukuroException(res["Error"])
        return res

class ChiebukuroException(Exception):
    pass
