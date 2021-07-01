import json
import os
import re
import py2neo
from py2neo import Graph, Node, Relationship, NodeMatcher

def to_neo4j(g, res_json, filename):
    """
    g: the Graph object
    res_json: json string 
    filename: malware name
    """
    def string_duplicate_4(s):
        new_s = []
        for x in s:
            if x not in new_s:
                new_s.append(x)
        return new_s

    """
    构建正则表达式以提取字段
    """
    mailre = re.compile(r"(\w+@\w+\.\w+)")  # 获取邮件的正则表达式
    ipre = re.compile(
        r'(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)')
    urlre = re.compile(
        r'((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?')

    # 定义存放提取字段的列表
    dll_list = []  # 存放dll
    ip_list = []  # 存放ip
    url_list = []  # 存放域名
    mail_list = []  # 存放的邮箱


    # 按行提取字段
    lines = res_json.split('\n')
    for line in lines:
        if '.dll' in line:  # 导入dll
            dll_un_line = line.strip().split(":")  # 分割dll数据
            for dll_line in dll_un_line:
                if '.dll' in dll_line:
                    if '\\' in dll_line:  # 去除前缀
                        temp_dll = dll_line.split('\\')
                        for dll_new in temp_dll:
                            if '.dll' in dll_new:
                                dll_list.append(dll_new.replace('"', '').replace(',', '').strip())
                    else:
                        dll_list.append(dll_line.strip().replace('"', '').replace(',', '').strip())

        if ipre.findall(line) and 'src' not in line and '192.168.56.101' not in line:  # 导入目的地址
            for ipa in ipre.findall(line):
                ww = ''
                ww = '.'.join(ipa)
                ip_list.append(ww)

        if urlre.findall(line):  # 导入url
            for urla in urlre.findall(line):
                ww = ''
                for tup in urla:
                    ww = ww + tup
                    aa = ww.split('\\')
                    ww = aa[0]
                    url_list.append(ww)

        if mailre.findall(line):  # 导入邮箱
            for mail in mailre.findall(line):
                mail_list.append(mail)

    # 删除列表中重复的元素
    dll_list = string_duplicate_4(dll_list)
    ip_list = string_duplicate_4(ip_list)
    url_list = string_duplicate_4(url_list)
    mail_list = string_duplicate_4(mail_list)

    # 导入结果到Neo4
    start_node = Node("Malware", name=filename)
    g.merge(start_node, 'Malware', "name")

    for dll_item in dll_list:  # 创建dll
        dll_node = Node("DLL", name=dll_item)
        dll_relation = Relationship(start_node,'DLL',dll_node)
        g.merge(dll_node, "DLL", "name")
        g.merge(dll_relation, "DLL", "name")

    for ip_item in ip_list:  # 创建ip
        ip_node = Node("IP", name=ip_item)
        ip_relation = Relationship(start_node,'IP',ip_node )
        g.merge(ip_node, "IP", "name")
        g.merge(ip_relation, "IP", "name")

    for url_item in ip_list:  # 创建url
        url_node = Node("URL", name=url_item)
        url_relation = Relationship(start_node,'URL',url_node )
        g.merge(url_node, "URL", "name")
        g.merge(url_relation, "URL", "name")

    for mail_item in mail_list:  # 创建mail
        mail_node = Node("Mail", name=mail_item)
        mail_relation = Relationship(start_node,'Mail',mail_node )
        g.merge(mail_node, "Mail", "name")
        g.merge(mail_relation, "Mail", "name")

