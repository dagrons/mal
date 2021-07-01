# Todo List
TODO
- cfg
- asm2vec, 频繁子图
- 知识图谱

# 项目结构
📦app

 ┣ 📂api 
 ┃ ┣ 📂v1
 ┃ ┣ 📂v2 # 所有API接口
 ┃ ┃ ┣ 📜__init__.py
 ┃ ┃ ┣ 📜feature.py
 ┃ ┃ ┗ 📜task.py
 ┃ ┗ 📜__init__.py
 ┣ 📂auth
 ┣ 📂config # 配置文件
 ┃ ┣ 📜__init__.py
 ┃ ┣ 📜basicConfig.py
 ┃ ┣ 📜developmentConfig.py
 ┃ ┗ 📜productionConfig.py
 ┣ 📂extensions
 ┃ ┣ 📜__init__.py
 ┃ ┗ 📜neo4j.py
 ┣ 📂main # 属于前端
 ┃ ┣ 📜__init__.py
 ┃ ┗ 📜routes.py
 ┣ 📂mock # 不用管
 ┃ ┗ 📜report.json
 ┣ 📂models # 数据库模型
 ┃ ┣ 📜__init__.py
 ┃ ┗ 📜feature.py
 ┣ 📂services # 服务, 介于API和Model之间的抽象, 之所以有这个是因为最好不要让API直接访问数据库以及处理异步任务必须
 ┃ ┣ 📜__init__.py
 ┃ ┣ 📜feature_service.py 
 ┃ ┗ 📜task_executor.py # cuckoo异步任务执行
 ┣ 📂templates
 ┃ ┗ 📜index.html
 ┣ 📂utils
 ┃ ┣ 📂malware_classification # 家族分类模型
 ┃ ┃ ┣ 📂scripts
 ┃ ┃ ┃ ┗ 📜transform.py
 ┃ ┃ ┣ 📂trained_models
 ┃ ┃ ┃ ┗ 📜malware_classification%resnet34%best.pt
 ┃ ┃ ┣ 📜predict.py
 ┃ ┃ ┗ 📜resnet.py
 ┃ ┣ 📂malware_sim # doc2vec模型
 ┃ ┃ ┣ 📂scripts
 ┃ ┃ ┃ ┗ 📜transform.py
 ┃ ┃ ┣ 📂trained_models
 ┃ ┃ ┃ ┗ 📜malware_sim%doc2vec.pth
 ┃ ┃ ┗ 📜predict.py
 ┃ ┣ 📜compute_md5.py # 计算文件哈希
 ┃ ┣ 📜is_pe.py # 判断是否为PE文件
 ┃ ┣ 📜log.py # 增强日志效果, 不用管
 ┃ ┣ 📜to_neo4j.py # 保存到neo4j数据库
 ┃ ┗ 📜transform.py # pe, bmp, asm, bytes文件之间的转化
 ┗ 📜__init__.py


# FAQ
## CUCKOO
- 401 ERROR
> token不正确或者文件上传格式不正确
- 400 ERROR
> 被cuckoo识别为重复文件, 详细原因不知