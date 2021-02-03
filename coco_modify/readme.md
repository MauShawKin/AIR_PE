由于飞机姿态关键点数据集是按coco的标准设计的，而样本关键点类型，关键点聚类以及关键点分布指数均不同，于是需要修改coco工具包中的cocoeval.py文件，具体路径大致如下：

`.../anaconda3/envs/HRNet/lib/python3.7/site-packages/pycocotools-2.0-py3.7-linux-x86_64.egg/pycocotools`

即位于所安装coco的anaconda环境目录下。