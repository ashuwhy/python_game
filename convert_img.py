from PIL import Image

def convert_to_bmp(filename):
    img = Image.open(filename + '.png')
    img = img.convert('RGBA')
    bg = Image.new('RGBA', img.size, (255, 0, 255, 255))
    bg.paste(img, (0, 0), img)
    bg = bg.convert('RGB')
    bg.save(filename + '.bmp')

convert_to_bmp('tile_set')
convert_to_bmp('item_objects')
