TODO
- TTP翻译 XXXXX
- APT组织分类  XXXXX
- docker-cucko X


BUG
- 400 Error Cuckoo  
- net::ERR:CONNECTIONABORT 

# 项目结构

📦app

 ┣ 📂api 
 ┃ ┣ 📂v1
 ┃ ┣ 📂v2 # 所有API接口
 ┃ ┃ ┣ 📜__init__.py
 ┃ ┃ ┣ 📜feature.py # 主要是用于给前端显示的接口
 ┃ ┃ ┗ 📜task.py # 主要是用于处理上传样本的接口
 ┃ ┗ 📜__init__.py
 ┣ 📂auth
 ┣ 📂config # 配置文件
 ┃ ┣ 📜__init__.py
 ┃ ┣ 📜basicConfig.py
 ┃ ┣ 📜developmentConfig.py
 ┃ ┗ 📜productionConfig.py
 ┣ 📂extensions # 不用管
 ┃ ┣ 📜__init__.py
 ┃ ┗ 📜neo4j.py 
 ┣ 📂main # 属于前端，不用管
 ┃ ┣ 📜__init__.py
 ┃ ┗ 📜routes.py
 ┣ 📂mock # 不用管
 ┃ ┗ 📜report.json
 ┣ 📂models # 数据库模型，不用管
 ┃ ┣ 📜__init__.py
 ┃ ┗ 📜feature.py
 ┣ 📂services # 服务, 介于API和Model之间的抽象, 之所以有这个是因为最好不要让API直接访问数据库以及处理异步任务必须
 ┃ ┣ 📜__init__.py
 ┃ ┣ 📜feature_service.py # 主要返回前端显示的数据
 ┃ ┗ 📜task_executor.py # 处理上传样本
 ┣ 📂templates # 前端，不用管
 ┃ ┗ 📜index.html
 ┣ 📂utils # 包含模型文件，预处理样本的工具等
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


