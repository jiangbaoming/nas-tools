from app.media.meta._base import MetaBase
from app.utils.number_parser_util import get_number
from app.utils.types import MediaType


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
        self.media_type = MediaType.AV
        self.type = MediaType.AV
        self.cn_name = av_number
        self.en_name = av_number
        self.tmdb_id = av_number
        self.year = 1997
        self.actor = '佚名'
