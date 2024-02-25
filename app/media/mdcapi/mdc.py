import log
import requests

from app.media.mdcapi.api import search


class MDC(object):
    proxies = None
    watermark = False
    watermark_type = 1
    dbcookies = None
    dbsite = None
    # 使用storyline方法进一步获取故事情节
    morestoryline = True
    image_naming_with_number = False
    number_uppercase = True
    is_translate = True
    translate_values = 'title,outline,tag'
    is_extrafanart = False

    def __init__(self):
        pass

    def search(self, media_info):
        file_number = media_info.get_name()
        return self._search(file_number)

    def _search(self, file_number):
        media_data = search(file_number, **self.__dict__)
        return self._handler_data(media_data, file_number)

    def _handler_data(self, json_data, file_number):
        if not json_data:
            log.info('[-]Movie Number not found!')
            return None
        # 增加number严格判断，避免提交任何number，总是返回"本橋実来 ADZ335"，这种返回number不一致的数据源故障
        # 目前选用number命名规则是javdb.com Domain Creation Date: 2013-06-19T18:34:27Z
        # 然而也可以跟进关注其它命名规则例如airav.wiki Domain Creation Date: 2019-08-28T07:18:42.0Z
        # 如果将来javdb.com命名规则下不同Studio出现同名碰撞导致无法区分，可考虑更换规则，更新相应的number分析和抓取代码。
        if str(json_data.get('number')).upper() != file_number.upper():
            try:
                if json_data.get('allow_number_change'):
                    pass
            except:
                log.info('[-]Movie number has changed! [{}]->[{}]'.format(file_number, str(json_data.get('number'))))
                return None

        # ================================================网站规则添加结束================================================
        if json_data.get('title') == '':
            log.info('[-]Movie Number or Title not found!')
            return None
        title = json_data.get('title')
        actor_list = str(json_data.get('actor')).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
        actor_list = [actor.strip() for actor in actor_list]  # 去除空白
        director = json_data.get('director')
        release = json_data.get('release')
        number = json_data.get('number')
        studio = json_data.get('studio')
        outline = json_data.get('outline')
        label = json_data.get('label')
        series = json_data.get('series')
        year = json_data.get('year')

        if json_data.get('cover_small'):
            cover_small = json_data.get('cover_small')
        else:
            cover_small = ''

        if json_data.get('trailer'):
            trailer = json_data.get('trailer')
        else:
            trailer = ''

        if json_data.get('extrafanart'):
            extrafanart = json_data.get('extrafanart')
        else:
            extrafanart = ''

        tag = str(json_data.get('tag')).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
        while 'XXXX' in tag:
            tag.remove('XXXX')
        while 'xxx' in tag:
            tag.remove('xxx')
        if json_data['source'] == 'pissplay':  # pissplay actor为英文名，不用去除空格
            actor = str(actor_list).strip("[ ]").replace("'", '')
        else:
            actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')

        # ====================处理异常字符====================== #\/:*?"<>|
        actor = special_characters_replacement(actor)
        actor_list = [special_characters_replacement(a) for a in actor_list]
        title = special_characters_replacement(title)
        label = special_characters_replacement(label)
        outline = special_characters_replacement(outline)
        series = special_characters_replacement(series)
        studio = special_characters_replacement(studio)
        director = special_characters_replacement(director)
        tag = [special_characters_replacement(t) for t in tag]
        release = release.replace('/', '-')
        tmpArr = cover_small.split(',')
        if len(tmpArr) > 0:
            cover_small = tmpArr[0].strip('\"').strip('\'')
        # 处理大写
        if self.number_uppercase:
            json_data['number'] = number.upper()

        # 返回处理后的json_data
        json_data['title'] = title
        json_data['name'] = file_number
        json_data['first_air_date'] = year
        json_data['original_title'] = title
        json_data['actor'] = actor
        json_data['release'] = release
        json_data['cover_small'] = cover_small
        json_data['tag'] = tag
        json_data['year'] = year
        json_data['actor_list'] = actor_list
        json_data['trailer'] = trailer
        json_data['extrafanart'] = extrafanart
        json_data['label'] = label
        json_data['outline'] = outline
        json_data['series'] = series
        json_data['studio'] = studio
        json_data['director'] = director
        json_data['id'] = file_number
        json_data['media_type'] = 'AV'
        if self.is_translate:
            if self.translate_values:
                translate_values = self.translate_values.split(",")
                for translate_value in translate_values:
                    if json_data[translate_value] == "":
                        continue
                    if len(json_data[translate_value]):
                        if type(json_data[translate_value]) == str:
                            json_data[translate_value] = special_characters_replacement(json_data[translate_value])
                            json_data[translate_value] = translate(json_data[translate_value])
                        else:
                            for i in range(len(json_data[translate_value])):
                                json_data[translate_value][i] = special_characters_replacement(
                                    json_data[translate_value][i])
                            list_in_str = ",".join(json_data[translate_value])
                            json_data[translate_value] = translate(list_in_str).split(',')
        return json_data


def special_characters_replacement(text) -> str:
    if not isinstance(text, str):
        return text
    return (text.replace('\\', '∖').  # U+2216 SET MINUS @ Basic Multilingual Plane
            replace('/', '∕').  # U+2215 DIVISION SLASH @ Basic Multilingual Plane
            replace(':', '꞉').  # U+A789 MODIFIER LETTER COLON @ Latin Extended-D
            replace('*', '∗').  # U+2217 ASTERISK OPERATOR @ Basic Multilingual Plane
            replace('?', '？').  # U+FF1F FULLWIDTH QUESTION MARK @ Basic Multilingual Plane
            replace('"', '＂').  # U+FF02 FULLWIDTH QUOTATION MARK @ Basic Multilingual Plane
            replace('<', 'ᐸ').  # U+1438 CANADIAN SYLLABICS PA @ Basic Multilingual Plane
            replace('>', 'ᐳ').  # U+1433 CANADIAN SYLLABICS PO @ Basic Multilingual Plane
            replace('|', 'ǀ').  # U+01C0 LATIN LETTER DENTAL CLICK @ Basic Multilingual Plane
            replace('&lsquo;', '‘').  # U+02018 LEFT SINGLE QUOTATION MARK
            replace('&rsquo;', '’').  # U+02019 RIGHT SINGLE QUOTATION MARK
            replace('&hellip;', '…').
            replace('&amp;', '＆').
            replace("&", '＆')
            )


def translate(keywords, target_language='zh_cn'):
    trans_result = ""
    gsite = 'translate.google.com'
    url = (
        f"https://{gsite}/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl=auto&tl={target_language}&q={keywords}"
    )
    result = get_html(url=url, return_type="object")
    if not result.ok:
        log.info('[-]Google-free translate web API calling failed.')
        return keywords
    translate_list = [i["trans"] for i in result.json()["sentences"]]
    trans_result = trans_result.join(translate_list)
    return trans_result


G_USER_AGENT = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.133 Safari/537.36'


def get_html(url, cookies: dict = None, ua: str = None, return_type: str = None, encoding: str = None, json_headers=None, verify=None, proxies=None, timeout=20, retry=3):
    """
    网页请求核心函数
    """
    errors = ""
    headers = {"User-Agent": ua or G_USER_AGENT}
    if json_headers is not None:
        headers.update(json_headers)
    for i in range(retry):
        try:
            if proxies:
                result = requests.get(str(url), headers=headers, timeout=timeout, proxies=proxies,
                                      verify=verify,
                                      cookies=cookies)
            else:
                result = requests.get(str(url), headers=headers, timeout=timeout, cookies=cookies)

            if return_type == "object":
                return result
            elif return_type == "content":
                return result.content
            else:
                result.encoding = encoding or result.apparent_encoding
                return result.text
        except Exception as e:
            log.info("[-]Connect retry {}/{}".format(i + 1, retry))
            errors = str(e)
    if "getaddrinfo failed" in errors:
        log.info("[-]Connect Failed! Please Check your proxy config")
    else:
        log.info("[-]" + errors)
        log.info('[-]Connect Failed! Please check your Proxy or Network!')
    raise Exception('Connect Failed')


if __name__ == '__main__':
    mdc = MDC()
    data = mdc._search("ssni-865")
    # cover = data['cover']
    log.info(data)
    # log.info(mdc.image_ext(cover))
