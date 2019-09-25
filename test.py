import gspread
from oauth2client.service_account import ServiceAccountCredentials


# googleスプレッドシートとpythonを連携
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('<jsonファイル>.json', scope)
gc = gspread.authorize(credentials)
# 自分が設定したシートの値を抽出
sh_x = gc.open('E-H_distribution__with_arror').worksheet("Electric_x_vector").get_all_values()[1:]
sh_y = gc.open('E-H_distribution__with_arror').worksheet("Electric_y_vector").get_all_values()[1:]
sh_ab = gc.open('E-H_distribution__with_arror').worksheet("Electric_posision").get_all_values()[1:]
setting = gc.open('E-H_distribution__with_arror').worksheet("Setting").get_all_values()


# --------------------------------以下から矢印分布を作成する----------------------------------------------
# ｘ、ｚ方向を何分割にするか(ハイパーパラメータ)
# 分割したデータのみを矢印分布にする
x_div = int(setting[8][1])
z_div = int(setting[8][2])

import math
# ベクトルx座標を抜き取る
x_num =(-float(sh_ab[0][0]) * 2)/(float(sh_ab[1][0]) - float(sh_ab[0][0])) + 1
x_num_list =[int(math.floor((x_num/x_div)*(i+1))) for i in range(x_div)] 
x_list =[sh_ab[i-1][0] for i in x_num_list]
#x_list = [x for x in x_list if x]
#x_num_list = x_num_list[:len(x_list)]

import pandas as pd
pd.DataFrame(sh_ab)[1].values.max()
z_num = ((pd.DataFrame(sh_ab)[1].apply(lambda x:float(x)).max() - float(sh_ab[0][1]))/(float(sh_ab[1][1]) - float(sh_ab[0][1]))) + 1
z_num_list = [int(math.floor((z_num/z_div)*(i+1))) for i in range(z_div)]
z_list =[sh_ab[i-1][1] for i in z_num_list]
#z_list = [x for x in z_list if x]

# 選択された行列のデータを取得する
all_x = [list(pd.DataFrame(sh_x)[x].values) for x in range(len(sh_x[0]))]
all_y = [list(pd.DataFrame(sh_y)[y].values) for y in range(len(sh_y[0]))]

from matplotlib import pyplot
fig = pyplot.figure(figsize=(20,20),dpi=300)
ax = fig.add_subplot(111)
ax.tick_params(labelbottom="off",bottom="off") # x軸の削除
ax.tick_params(labelleft="off",left="off") # y軸の削除
ax.set_xlim([float(sh_ab[0][0]), -float(sh_ab[0][0])])
ax.set_ylim([pd.DataFrame(sh_ab)[1].apply(lambda x:float(x)).min(), pd.DataFrame(sh_ab)[1].apply(lambda x:float(x)).max()])

from pylab import *
#box("off")#枠組みを削除

arror_size = int(setting[8][5])
setcolor1 = str(setting[8][3])
setcolor2 = str(setting[8][4])
zz = 0
for z_number in z_num_list:
    xx = 0
    for x_number in x_num_list:
        x_va = float(all_x[z_number-1][x_number-1])
        z_va = float(all_y[z_number-1][x_number-1])
        
        sin0 = z_va/np.sqrt(z_va**2 + x_va**2)
        cos0 = x_va/np.sqrt(z_va**2 + x_va**2)

        # 矢印を大きくしたければ"end"の係数を変える
        point = {
            'start': [float(x_list[xx]), float(z_list[zz])],
            'end': [float(x_list[xx])+130*cos0,float(z_list[zz])+130*sin0]
        }
        #矢印を出したいときは"gray"に変える
        ax.annotate('', xy=point['end'], xytext=point['start'],
                    arrowprops=dict(shrink=0, width=4, headwidth=15, 
                                    headlength=20, connectionstyle='arc3',
                                    facecolor=setcolor1, edgecolor=setcolor2)
                   )
        xx+=1
    zz+=1
pyplot.tick_params(bottom=False,left=False,right=False,top=False)
#pyplot.show()
fig.savefig("E-矢印", transparent=True)


# --------------------------------以下からヒートマップ作成を作成する----------------------------------------------
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
plt.figure(figsize=(20, 20),dpi=300)
x_array = pd.DataFrame(sh_ab)[pd.DataFrame(sh_ab)[0]!=""][0].values
y_array = pd.DataFrame(sh_ab)[pd.DataFrame(sh_ab)[1]!=""][1].values
heat = pd.DataFrame(gc.open('E-H_distribution__with_arror').worksheet("Electric_intensity").get_all_values()[1:]).astype(float)
heat.columns = y_array
heat.index = x_array
order = y_array
heat = heat[order]
ax = sns.heatmap(heat.T,cbar=False,xticklabels=False,yticklabels=False)
ax.invert_yaxis()
plt.savefig("E-ヒートマップ", transparent=True)

# --------------------------------作成したヒートマップと矢印マップを重ねる----------------------------------------------
from PIL import Image
background = Image.open("E-ヒートマップ.png")
foreground = Image.open("E-矢印.png")

background.paste(foreground, (0, 0), foreground)
#background.show()
background.save("E-heatmap-with-arror.png")