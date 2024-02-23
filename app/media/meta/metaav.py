import re

import zhconv

import anitopy
from app.media.meta._base import MetaBase
from app.media.meta.release_groups import ReleaseGroupsMatcher
from app.media.meta.customization import CustomizationMatcher
from app.utils import StringUtils, ExceptionUtils
from app.utils.types import MediaType
from app.utils.number_parser_util import get_number


class MetaAv(MetaBase):
    """
    识别AV
    """
    def __init__(self,
                 title,
                 subtitle=None,
                 fileflag=False,
                 filePath=None,
                 media_type=None,
                 cn_name=None,
                 en_name=None,
                 tmdb_id=None,
                 imdb_id=None):
        super().__init__(title,
                         subtitle,
                         fileflag,
                         filePath,
                         media_type,
                         cn_name,
                         en_name,
                         tmdb_id,
                         imdb_id)
        if not title:
            return
        av_number = get_number(title)
        self.title = av_number
        self.type = MediaType.AV
        self.cn_name = av_number
        self.en_name = av_number
        self.tmdb_id = av_number
        self.year = 1997
        self.actor = '佚名'
