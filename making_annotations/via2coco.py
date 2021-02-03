# _*_ coding:utf-8 _*_
# Editor: ly
# Time: 2021/1/8上午10:43
# Filename: AIR_jsoner.py
# IDE: PyCharm

import json
import tqdm

# 源文件
path_json = '/home/ly/Dataset/AIR/annotations/train_ori/pro_version_train.json'
path_coco = '/home/ly/Dataset/AIR/annotations/train_ori/coco_version_train.json'
save = 'train_v1.json'

# 打开源文件
file_pro = open(path_json, 'r')
file_coco = open(path_coco, 'r')

'''对关键点信息 KPT 的处理'''
pro_all = json.load(file_pro)

# 获取图像数量：
sample_list_size = len(pro_all['_via_img_metadata'])

# 获取图像名字：
sample_name = list(pro_all['_via_img_metadata'].keys())

# 获取关键点标签字典
# （剔除了其中的mask和box标签）
sample_cat = pro_all['_via_attributes']['region']['plane']['options']
# cat_table = list(sample_cat.keys())[:-2]
cat_table = list(sample_cat.keys())[:-1]

'''关键点信息与关键点表的映射关系'''
# 一幅图片 i 中的关键点 j 位于： ['meta'][i]['regions'][j],
# 具体信息位于： ['regions'][j]['shape_attr']['cx/cy']
# 对应标签位于： ['regions'][j]['region_attr']['plane']
'''由于信息中有mask 和 box信息， 需要经过cat_table表来剔除'''
# 或者直接将['region_attr']['plane']转为整型？

# samp_id: 图片名在 metadata 列表中的序号

# 建立关键点存储数组
JOINT_NUM = 9
sample_KPT = [0] * sample_list_size
for samp_id in range(sample_list_size):
    sample_KPT[samp_id] = {}
    sample_KPT[samp_id]['kpt'] = [0] * (JOINT_NUM * 3)
    sample_KPT[samp_id]['num'] = 0

# 遍历via_pro中各图片, 生成kpt字典
for samp_id in range(sample_list_size):
    # if samp_id == 174 or samp_id == 410 or samp_id == 414 or samp_id == 545 or samp_id == 588 or samp_id == 821:
    #     continue
    # 从名字中分离出id， 其中，图片id = 标签id = 名字的整型
    img_name_id = int(sample_name[samp_id][:12])

    # 获得图中关键点标注信息{一个列表}
    ori_kpt_list = pro_all['_via_img_metadata'][sample_name[samp_id]]['regions']
    cnt = 0
    # print("空点debug...:")
    # print(img_name_id)
    # print("\n")
    # 遍历各点
    for i in range(len(ori_kpt_list)):
        # 获得第i个关键点的种类编号， 为了删除原始资料中的 MASK 和 BOX 信息
        cati = ori_kpt_list[i]['region_attributes']['plane']

        # 遍历关键点种类表： 查找第i个点的种类
        tmp = [j for j in cat_table if j in cati]
        if len(tmp) == 1:
            kpt_id = int(cati)

            sample_KPT[img_name_id]['kpt'][kpt_id * 3] = ori_kpt_list[i]['shape_attributes']['cx']
            sample_KPT[img_name_id]['kpt'][kpt_id * 3 + 1] = ori_kpt_list[i]['shape_attributes']['cy']
            sample_KPT[img_name_id]['kpt'][kpt_id * 3 + 2] = 2
            cnt = cnt + 1

    # 保存图片中关键点数量
    sample_KPT[img_name_id]['num'] = cnt

'''至此， kpt 与 num_kpt 部分提取完毕'''

'''对 掩膜， box 和 area信息的处理'''
json_coco = json.load(file_coco)
coco_WH = json_coco['images']
coco_SAB = json_coco['annotations']

# sample_SAB = [0] * (len(coco_SAB) // 2)
# for samp_id in range(len(coco_SAB) // 2):
sample_SAB = [0] * (len(coco_SAB))
for samp_id in range(len(coco_SAB)):
    sample_SAB[samp_id] = {}
    sample_SAB[samp_id]['seg'] = []
    sample_SAB[samp_id]['area'] = 0
    sample_SAB[samp_id]['bbox'] = 0
for i in range(len(coco_SAB)):
    real_img_id = int(coco_SAB[i]['image_id'])
    if coco_SAB[i]['category_id'] == 10:
        sample_SAB[real_img_id]['seg'].append(coco_SAB[i]['segmentation'])
        sample_SAB[real_img_id]['area'] += coco_SAB[i]['area']
        sample_SAB[real_img_id]['bbox'] = coco_SAB[i]['bbox']

'''对 宽高 的处理'''
sample_WH = [0] * (len(coco_WH))
for samp_id in range(len(coco_WH)):
    sample_WH[samp_id] = {}
    sample_WH[samp_id]['width'] = 0
    sample_WH[samp_id]['height'] = 0
for img in coco_WH:
    sample_WH[img['id']]['width'] = img['width']
    sample_WH[img['id']]['height'] = img['height']

'''coco.json文件生成'''
# sample_SAB
# sample_KPT
# 列表id 即为：
print("writting...\n")
info = '{"info":{"year":2020,"version":"1","description":"Airplane Dataset(imitated COCO2017)","contributor":"Annotation tools: VIA, Resource web: VJshi, Scholiast: IOE_lab5_ly","url":"https://github.com/Maushawkin/","date_created":"Wed Dec 25 2020 00:00:01 GMT+0800"},"images":['
z = open(save, 'a+')
z.write(info)
z.close()

'''writing images'''
for i in tqdm.tqdm(range(sample_list_size)):
    '''require two parameters:[id, name, width, height]'''
    temp_id = int(sample_name[i][0:12])
    img_par = [temp_id, sample_name[i][0:16], sample_WH[temp_id]['width'], sample_WH[temp_id]['height']]
    buff_img = '{{"id":{0[0]},"width":{0[2]},"height":{0[3]},"file_name":"{0[1]}","license":0,"date_captured":"2020-12-25 00:00:00"}},' \
        .format(img_par)
    if i == sample_list_size - 1:
        buff_img = '{{"id":{0[0]},"width":{0[2]},"height":{0[3]},"file_name":"{0[1]}","license":0,"date_captured":"2020-12-25 00:00:00"}}],"annotations":[' \
            .format(img_par)
    z = open(save, 'a+')
    z.write(buff_img)
    z.close()
    # core = {"current": i, "total": sample_list_size}
    # print('{current}/{total}'.format(**core))

'''writing annotations'''
for i in tqdm.tqdm(range(sample_list_size)):
    seg = sample_SAB[i]['seg']
    area = sample_SAB[i]['area']
    bbox = sample_SAB[i]['bbox']
    kpt = sample_KPT[i]['kpt']
    num_kpt = sample_KPT[i]['num']
    ann_par = [seg, num_kpt, area, kpt, i, bbox, i]
    buff_ann = '{{"segmentation":{0[0]},"num_keypoints":{0[1]},"area":{0[2]},"iscrowd":0,"keypoints":{0[3]},"image_id":{0[4]},"bbox":{0[5]},"category_id":1,"id":{0[6]}}},' \
        .format(ann_par)
    if i == sample_list_size - 1:
        buff_ann = '{{"segmentation":{0[0]},"num_keypoints":{0[1]},"area":{0[2]},"iscrowd":0,"keypoints":{0[3]},"image_id":{0[4]},"bbox":{0[5]},"category_id":1,"id":{0[6]}}}],' \
            .format(ann_par)
    z = open(save, 'a+')
    z.write(buff_ann)
    z.close()

'''writing others'''
others = '"licenses":[{"id":0,"name":"Vjshi","url":"https://www.vjshi.com/"}],"categories":[{"id":1,"name":"plane","supercategory":"plane","keypoints":["head","lshdr","rshdr","lwing","rwing","tail","uptail","ltail","rtail"],"skeleton":[[0,1],[0,2],[0,5],[1,2],[1,3],[2,4],[5,6],[5,7],[5,8],[7,8]]}]}'
z = open(save, 'a+')
z.write(others)
z.close()
print('done\n')
