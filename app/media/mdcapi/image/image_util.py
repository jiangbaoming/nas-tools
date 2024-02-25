import importlib
import os

from PIL import Image


def cut_image(imagecut, path, thumb_path, poster_path, aspect_ratio=2.12, locations_models='hog', skip_facerec=False):
    fullpath_fanart = os.path.join(path, thumb_path)
    fullpath_poster = os.path.join(path, poster_path)
    if not os.path.isfile(fullpath_poster) or os.path.getsize(fullpath_poster) == 0:
        return
    # imagecut为4时同时也是有码影片 也用人脸识别裁剪封面
    if imagecut == 1 or imagecut == 4:  # 剪裁大封面
        try:
            img = Image.open(fullpath_fanart)
            width, height = img.size
            if width / height > 2 / 3:  # 如果宽度大于2
                if imagecut == 4:
                    # 以人像为中心切取
                    img2 = img.crop(face_crop_width(fullpath_fanart, width, height, aspect_ratio, locations_models))
                elif skip_facerec:
                    # 有码封面默认靠右切
                    img2 = img.crop((width - int(height / 3) * aspect_ratio, 0, width, height))
                else:
                    # 以人像为中心切取
                    img2 = img.crop(face_crop_width(fullpath_fanart, width, height, aspect_ratio, locations_models))
            elif width / height < 2 / 3:  # 如果高度大于3
                # 从底部向上切割
                img2 = img.crop(face_crop_height(fullpath_fanart, width, height, locations_models))
            else:  # 如果等于2/3
                img2 = img
            img2.save(fullpath_poster)
            print(f"[+]Image Cutted!")
        except Exception as e:
            print(e)
            print('[-]Cover cut failed!')


def face_crop_width(filename, width, height, aspect_ratio, locations_models):
    # 新宽度是高度的2/3
    cropWidthHalf = int(height / 3)
    try:
        locations_model = locations_models.lower().split(',')
        locations_model = filter(lambda x: x, locations_model)
        for model in locations_model:
            center, top = face_center(filename, model)
            # 如果找到就跳出循环
            if center:
                cropLeft = center - cropWidthHalf
                cropRight = center + cropWidthHalf
                # 越界处理
                if cropLeft < 0:
                    cropLeft = 0
                    cropRight = cropWidthHalf * aspect_ratio
                elif cropRight > width:
                    cropLeft = width - cropWidthHalf * aspect_ratio
                    cropRight = width
                return (cropLeft, 0, cropRight, height)
    except:
        print('[-]Not found face!   ' + filename)
    # 默认靠右切
    return (width - cropWidthHalf * aspect_ratio, 0, width, height)


def face_crop_height(filename, width, height, locations_models):
    cropHeight = int(width * 3 / 2)
    try:
        locations_model = locations_models.lower().split(',')
        locations_model = filter(lambda x: x, locations_model)
        for model in locations_model:
            center, top = face_center(filename, model)
            # 如果找到就跳出循环
            if top:
                # 头部靠上
                cropTop = top
                cropBottom = cropHeight + top
                if cropBottom > height:
                    cropTop = 0
                    cropBottom = cropHeight
                return (0, cropTop, width, cropBottom)
    except:
        print('[-]Not found face!   ' + filename)
    # 默认从顶部向下切割
    return (0, 0, width, cropHeight)


def face_center(filename, model):
    try:
        mod = importlib.import_module('.' + model, 'process')
        return mod.face_center(filename, model)
    except Exception as e:
        print('[-]Model found face  ' + filename)
        return (0, 0)


def add_mark(watermark_type, pic_path, cn_sub, leak, uncensored, hack, _4k, iso):
    size = 9
    img_pic = Image.open(pic_path)
    # 获取自定义位置，取余配合pos达到顺时针添加的效果
    # 左上 0, 右上 1, 右下 2， 左下 3
    count = watermark_type
    if cn_sub and not leak and not hack:
        add_to_pic(pic_path, img_pic, size, count, 1)  # 添加
        count = (count + 1) % 4
    if leak:
        add_to_pic(pic_path, img_pic, size, count, 2)
        count = (count + 1) % 4
    if uncensored:
        add_to_pic(pic_path, img_pic, size, count, 3)
        count = (count + 1) % 4
    if hack:
        add_to_pic(pic_path, img_pic, size, count, 4)
        count = (count + 1) % 4
    if _4k:
        add_to_pic(pic_path, img_pic, size, count, 5)
        count = (count + 1) % 4
    if iso:
        add_to_pic(pic_path, img_pic, size, count, 6)
    img_pic.close()


def add_to_pic(pic_path, img_pic, size, count, mode):
    if mode == 1:
        pngpath = "Img/SUB.png"
    elif mode == 2:
        pngpath = "Img/LEAK.png"
    elif mode == 3:
        pngpath = "Img/UNCENSORED.png"
    elif mode == 4:
        pngpath = "Img/HACK.png"
    elif mode == 5:
        pngpath = "Img/4K.png"
    elif mode == 6:
        pngpath = "Img/ISO.png"
    else:
        print('[-]Error: watermark image param mode invalid!')
        return
    mark_pic_path = ''
    if os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), pngpath)):
        mark_pic_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), pngpath)
    if mark_pic_path:
        img_subt = Image.open(mark_pic_path)
        scroll_high = int(img_pic.height / size)
        scroll_wide = int(scroll_high * img_subt.width / img_subt.height)
        img_subt = img_subt.resize((scroll_wide, scroll_high), Image.ANTIALIAS)
        r, g, b, a = img_subt.split()  # 获取颜色通道，保持png的透明性
        # 封面四个角的位置
        pos = [
            {'x': 0, 'y': 0},
            {'x': img_pic.width - scroll_wide, 'y': 0},
            {'x': img_pic.width - scroll_wide, 'y': img_pic.height - scroll_high},
            {'x': 0, 'y': img_pic.height - scroll_high},
        ]
        img_pic.paste(img_subt, (pos[count]['x'], pos[count]['y']), mask=a)
        img_pic.save(pic_path, quality=95)
