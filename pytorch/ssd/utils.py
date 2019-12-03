from itertools import  product
import torch 

import math
from math import  sqrt
import numpy as np
 
 def generate_prior_box():

    fmap_dims = {"conv4_3": 38,
                "conv7": 19,
                "conv8_2": 10,
                "conv9_2": 5,
                "conv10_2": 3,
                "conv11_2": 1}  # feature maps size
    obj_scales = {"conv4_3": 0.1,
                "conv7": 0.2,
                "conv8_2": 0.375,
                "conv9_2": 0.55,
                "conv10_2": 0.725,
                "conv11_2": 0.9}  # scale
    aspect_ratios = {"conv4_3": [1.,2.,0.5],
                    "conv7": [1.,2.,3.,0.5,0.333],
                    "conv8_2": [1.,2.,3.,0.5,0.333],
                    "conv9_2": [1.,2.,3.,0.5,0.333],
                    "conv10_2": [1.,2.,0.5],
                    "conv11_2": [1.,2.,0.5]}  # ratios

    fmaps = list(fmap_dims.keys())

    prior_boxes = []

    for k, fmap in enumerate(fmaps):
        for i in range(fmap_dims[fmap]):
            for j in range(fmap_dims[fmap]):

                cx = (j + 0.5) / fmap_dims[fmap]
                cy = (i + 0.5) / fmap_dims[fmap] # 中心点

                for ratio in aspect_ratios[fmap]:

                    prior_boxes.append([cx, cy, obj_scales[fmap] * sqrt(ratio), obj_scales[fmap] / sqrt(ratio)])
                    
                    # ratio = 1.0的情况下，添加一个额外的prior box
                    if ratio == 1.0:
                        try:
                            additional_scale = sqrt(obj_scales[fmap] * obj_scales[fmaps[k + 1]])
                        except IndexError:
                            additional_scale = 1.0  # 最后一个scale 
                        prior_boxes.append([cx, cy, additional_scale, additional_scale])
                        
    # prior_boxes = torch.FloatTensor(prior_boxes)  # (8732,4)
    # prior_boxes.clamp_(0,1) # 裁剪

    prior_boxes = np.clip(prior_boxes,0,1)

    return prior_boxes

print(prior_boxes.shape)

print(prior_boxes[0:4])

min_dim = 300   #######维度
# conv4_3 ==> 38 x 38
# fc7 ==> 19 x 19
# conv6_2 ==> 10 x 10
# conv7_2 ==> 5 x 5
# conv8_2 ==> 3 x 3
# conv9_2 ==> 1 x 1
mbox_source_layers = ['conv4_3', 'fc7', 'conv6_2', 'conv7_2', 'conv8_2', 'conv9_2'] #####prior_box来源层，可以更改。很多改进都是基于此处的调整。
# in percent %
min_ratio = 20 ####这里即是论文中所说的Smin=0.2，Smax=0.9的初始值，经过下面的运算即可得到min_sizes，max_sizes。具体如何计算以及两者代表什么，请关注我的博客SSD详解。这里产生很多改进。
max_ratio = 90
####math.floor()函数表示：求一个最接近它的整数，它的值小于或等于这个浮点数。
step = int(math.floor((max_ratio - min_ratio) / (len(mbox_source_layers) - 2)))####取一个间距步长，即在下面for循环给ratio取值时起一个间距作用。可以用一个具体的数值代替，这里等于17。
min_sizes = []  ###经过以下运算得到min_sizes和max_sizes。
max_sizes = []
for ratio in range(min_ratio, max_ratio + 1, step):  ####从min_ratio至max_ratio+1每隔step=17取一个值赋值给ratio。注意xrange函数的作用。
########min_sizes.append（）函数即把括号内部每次得到的值依次给了min_sizes。
  min_sizes.append(min_dim * ratio / 100.)
  # print(min_sizes)
  max_sizes.append(min_dim * (ratio + step) / 100.)
min_sizes = [min_dim * 10 / 100.] + min_sizes
max_sizes = [min_dim * 20 / 100.] + max_sizes
steps = [8, 16, 32, 64, 100, 300]  ###这一步要仔细理解，即计算卷积层产生的prior_box距离原图的步长，先验框中心点的坐标会乘以step，相当于从feature map位置映射回原图位置，比如conv4_3输出特征图大小为38*38，而输入的图片为300*300，所以38*8约等于300，所以映射步长为8。这是针对300*300的训练图片。
aspect_ratios = [[2], [2, 3], [2, 3], [2, 3], [2], [2]]
 
print(min_sizes)




    