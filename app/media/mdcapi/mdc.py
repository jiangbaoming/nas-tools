import json
import log


class MDC(object):
    all_sources = ['javlibrary', 'javdb', 'javbus', 'airav', 'fanza', 'xcity', 'jav321',
                   'mgstage', 'fc2', 'avsox', 'dlsite', 'carib', 'madou', 'msin',
                   'getchu', 'gcolle', 'javday', 'pissplay', 'javmenu', 'pcolle', 'caribpr'
                   ]
    proxies = None
    verify = None
    specifiedSource = None
    specifiedUrl = None

    dbcookies = None
    dbsite = None
    # 使用storyline方法进一步获取故事情节
    morestoryline = False

    def __init__(self):
        pass

    def search(self, name):
        return self.search_adult(name, self.all_sources)

    def search_adult(self, number, sources):
        if self.specifiedSource:
            sources = [self.specifiedSource]
        elif type(sources) is list:
            pass
        else:
            sources = self.checkAdultSources(sources, number)
        json_data = {}
        for source in sources:
            try:
                data = {}
                if data == 404:
                    continue
                json_data = json.loads(data)
                if self.get_data_state(json_data):
                    log.info(f"[+]Find movie [{number}] metadata on website '{source}'")
                break
            except Exception as e:
                continue
        # javdb的封面有水印，如果可以用其他源的封面来替换javdb的封面
        if 'source' in json_data and json_data['source'] == 'javdb':
            try:
                other_sources = sources[sources.index('javdb') + 1:]
                other_json_data = self.search_adult(number, other_sources)
                if other_json_data is not None and 'cover' in other_json_data and other_json_data['cover'] != '':
                    json_data['cover'] = other_json_data['cover']
                    log.info(f"[+]Find movie [{number}] cover on website '{other_json_data['cover']}'")
            except Exception:
                pass
        if not json_data or json_data['title'] == "":
            return None
        if not json_data['actor']:
            json_data['actor'] = "佚名"
        return json_data
