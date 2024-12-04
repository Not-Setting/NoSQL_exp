import matplotlib.font_manager as fm
from matplotlib.font_manager import FontManager
# 获取系统中所有字体
font_paths = fm.findSystemFonts()

# 打印出包含中文字符的字体路径
for path in font_paths:
    font = fm.FontProperties(fname=path)
    if "SimHei" in font.get_name() or "Microsoft YaHei" in font.get_name():
        print(font.get_name(), path)



mpl_fonts = set(f.name for f in FontManager().ttflist)

print('all font list get from matplotlib.font_manager:')
for f in sorted(mpl_fonts):
    print('\t' + f)