"""Design the Song 11 sunrise app end card (1080 × 1920)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import subprocess

ROOT = Path(__file__).resolve().parents[2]
P = ROOT / 'projects/thai-1000-song-11-mai-mi-khrai-ru-tua-rao'
font_path = subprocess.check_output(['fc-match', '-f', '%{file}', 'PingFang SC'], text=True)
font = lambda size: ImageFont.truetype(font_path, size)
W, H = 1080, 1920
navy = (9, 32, 39)
gold = '#EBC283'
cream = '#FFF7E8'

photo = Image.open(P / 'assets/images/dawn.png').convert('RGB')
scale = max(W / photo.width, H / photo.height)
photo = photo.resize((round(photo.width * scale), round(photo.height * scale)), Image.Resampling.LANCZOS)
left = (photo.width - W) // 2
im = photo.crop((left, 0, left + W, H)).convert('RGBA')
veil = Image.new('RGBA', (W, H), (0, 0, 0, 0))
pix = veil.load()
for y in range(H):
    if y < 500:
        alpha = round(105 - 35 * y / 500)
    elif y < 1030:
        alpha = round(70 + 75 * (y - 500) / 530)
    else:
        alpha = 0
    for x in range(W):
        pix[x, y] = (3, 20, 27, alpha)
im = Image.alpha_composite(im, veil)
d = ImageDraw.Draw(im)
d.rounded_rectangle((54, 64, 345, 124), radius=30, fill=(5, 30, 39, 195), outline=(235, 194, 131, 140), width=2)
d.text((82, 78), '泰语千词 · 歌曲课', font=font(27), fill=gold)
d.text((70, 218), '从一首歌开始，', font=font(70), fill=cream, stroke_width=1, stroke_fill='#10262b')
d.text((70, 320), '把泰语学进生活。', font=font(70), fill=cream, stroke_width=1, stroke_fill='#10262b')

# Editorial brand panel: the photo ends just above the logo, so the sunlit sky stays visible.
panel = Image.new('RGBA', (W, H), (0, 0, 0, 0))
pd = ImageDraw.Draw(panel)
pd.rounded_rectangle((0, 1015, W, 1990), radius=66, fill=(*navy, 253))
pd.rectangle((0, 1082, W, H), fill=(*navy, 253))
pd.line((72, 1110, 1008, 1110), fill=(235, 194, 131, 135), width=2)
im = Image.alpha_composite(im, panel)
d = ImageDraw.Draw(im)

icon = Image.open(P / 'composition/public/app/app_icon.png').convert('RGBA').resize((188, 188), Image.Resampling.LANCZOS)
shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
shadow.paste((0, 0, 0, 150), (74, 953, 266, 1145))
shadow = shadow.filter(ImageFilter.GaussianBlur(24))
im = Image.alpha_composite(im, shadow)
im.alpha_composite(icon, (78, 944))
d = ImageDraw.Draw(im)
d.text((306, 953), '泰语千词', font=font(84), fill=cream)
d.text((312, 1050), '听歌学泰语 · 每天学一点', font=font(32), fill=gold)

# Three compact promises use the space below the brand, with no button-like fake UI.
labels = [('听原唱', '一句一句听懂'), ('学发音', '跟着标准泰语读'), ('记表达', '用在真实生活里')]
for i, (title, sub) in enumerate(labels):
    x = 72 + i * 315
    d.rounded_rectangle((x, 1210, x + 290, 1415), radius=24, fill=(25, 58, 65, 255), outline=(91, 126, 126, 150), width=2)
    d.text((x + 22, 1247), title, font=font(48), fill=cream)
    d.text((x + 22, 1336), sub, font=font(27), fill='#B9CCCA')

d.line((72, 1518, 1008, 1518), fill=(235, 194, 131, 120), width=2)
d.text((72, 1577), '想听懂更多泰语歌？', font=font(53), fill=cream)
d.text((72, 1662), '跟着泰语千词，继续学。', font=font(48), fill=gold)
d.text((W // 2, 1835), '在泰国生活，够用了', anchor='mm', font=font(43), fill=cream)

out = P / 'renders/promo-card-v4.png'
im.convert('RGB').save(out, optimize=True)
print(out)
