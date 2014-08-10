from PIL import Image
# get dominant color


def get_domi_color(name):
    file_path = u"img_" + name + u".jpg"
    img = Image.open(file_path)
    color = img.resize((1, 1), Image.ANTIALIAS).getpixel((0, 0))
    if type(color) is tuple:
        color_hex = '#%02x%02x%02x' % color
    else:
        color_hex = "#cccccc"
    return color_hex
