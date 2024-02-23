import re
import log

G_SPAT = re.compile(
    "^\w+\.(cc|com|net|me|club|jp|tv|xyz|biz|wiki|info|tw|us|de)@|^22-sht\.me|"
    "^(fhd|hd|sd|1080p|720p|4K)(-|_)|"
    "(-|_)(fhd|hd|sd|1080p|720p|4K|x264|x265|uncensored|hack|leak)",
    re.IGNORECASE)

# 按javdb数据源的命名规范提取number
G_TAKE_NUM_RULES = {
    'tokyo.*hot': lambda x: str(re.search(r'(cz|gedo|k|n|red-|se)\d{2,4}', x, re.I).group()),
    'carib': lambda x: str(re.search(r'\d{6}(-|_)\d{3}', x, re.I).group()).replace('_', '-'),
    '1pon|mura|paco': lambda x: str(re.search(r'\d{6}(-|_)\d{3}', x, re.I).group()).replace('-', '_'),
    '10mu': lambda x: str(re.search(r'\d{6}(-|_)\d{2}', x, re.I).group()).replace('-', '_'),
    'x-art': lambda x: str(re.search(r'x-art\.\d{2}\.\d{2}\.\d{2}', x, re.I).group()),
    'xxx-av': lambda x: ''.join(['xxx-av-', re.findall(r'xxx-av[^\d]*(\d{3,5})[^\d]*', x, re.I)[0]]),
    'heydouga': lambda x: 'heydouga-' + '-'.join(re.findall(r'(\d{4})[\-_](\d{3,4})[^\d]*', x, re.I)[0]),
    'heyzo': lambda x: 'HEYZO-' + re.findall(r'heyzo[^\d]*(\d{4})', x, re.I)[0],
    'mdbk': lambda x: str(re.search(r'mdbk(-|_)(\d{4})', x, re.I).group()),
    'mdtm': lambda x: str(re.search(r'mdtm(-|_)(\d{4})', x, re.I).group()),
    'caribpr': lambda x: str(re.search(r'\d{6}(-|_)\d{3}', x, re.I).group()).replace('_', '-'),
    'fc2': lambda x: "FC2-" + str(re.search(r'(fc2)(-|_){0,1}(ppv){0,1}(-|_){0,1}(\d{7})(?=\D)', x, re.I).group(5)),
}


def get_number(filename: str) -> str:
    """
    从文件名提取番号
    """
    filename = G_SPAT.sub("", filename)
    try:
        try:
            for k, v in G_TAKE_NUM_RULES.items():
                if re.search(k, filename, re.I):
                    return v(filename)
        except Exception as e:
            log.error(f"get_number with G_TAKE_NUM_RULES from [{filename}] error. [{e}]")
            # print(f"get_number with G_TAKE_NUM_RULES from [{filename}] error. [{e}]")

        result = re.search(r'([a-zA-Z]{2,6})(-|_{1,})(\d{2,5})', filename)
        if result is None:
            result = re.search(r'([a-zA-Z]{2,6})(-|_{0,1})(\d{2,5})', filename)
        if result is None:
            return None

        return "-".join(result.group(1, 3))
    except Exception as e:
        log.error(f'Number Parser exception: {e} [{filename}]')
        # print(f'Number Parser exception: {e} [{file_path}]')
        return None
