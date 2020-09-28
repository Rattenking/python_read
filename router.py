
from flask import Flask, request, render_template
import requests
import json
from lxml import etree
import booksource
import re

app = Flask(__name__)

def withDataCode(r):
  encode_content = r.text
  if r.encoding == 'ISO-8859-1':
    encodings = requests.utils.get_encodings_from_content(r.text) 
    if encodings:
      encoding = encodings[0]
    else:
      encoding = r.apparent_encoding
    encode_content = r.content.decode(encoding, 'replace') 
  return encode_content

def getEtreeHtml(url):
  req = requests.get(url)
  encode_content = withDataCode(req)
  html = etree.HTML(encode_content)
  return html

def getSearchList(request):
  if request.method == 'POST':
    result = request.form
    bookname = result["bookname"]
    booksources = booksource.bookRule
    lst = []
    for item in booksources:
      html = getEtreeHtml(item["ruleSearchUrl"] + bookname)
      # 书本列表
      book_names = html.xpath(item["ruleSearchListName"])
      book_urls = html.xpath(item["ruleSearchListUrl"])
      
      for idx,book in enumerate(book_names):
        url = re.sub(r'^https://www.kuxiaoshuo.com', "", book_urls[idx])
        lst.append({
          'bookName': book,
          'bookUrl': url,
          'bookId': item["bookSourceId"]
        })
    return lst

def getChapterList(bookSourceId,bookId):
  curBookSource = {}
  booksources = booksource.bookRule
  for item in booksources:
    if item["bookSourceId"] == bookSourceId:
      curBookSource = item

  # 查找当前书源下当前书本的章节列表
  html = getEtreeHtml(curBookSource["bookSourceUrl"] + "/" + bookId + "/")
  chapter_names = html.xpath(curBookSource["ruleChapterName"])
  chapter_urls = html.xpath(curBookSource["ruleChapterUrl"])

  lst = []
  for idx,item in enumerate(chapter_names):
    url = re.sub(r'^https://www.kuxiaoshuo.com', "", chapter_urls[idx])
    url = re.sub(r'\.html$',"",url)
    lst.append({
      "chapter_name": item,
      "chapter_url": "/" + curBookSource["bookSourceId"] + url
    })
  return lst

def getChapterDetail(bookSourceId,bookId,chapterId):
  curBookSource = {}
  chapter = {}
  booksources = booksource.bookRule
  for item in booksources:
    if item["bookSourceId"] == bookSourceId:
      curBookSource = item
  
  # 查找章节详情
  html = getEtreeHtml(curBookSource["bookSourceUrl"] + "/" + bookId + "/" + chapterId + ".html")
  
  chapter_details = html.xpath(curBookSource["ruleChapterContent"])
  chapter_prev = html.xpath(curBookSource["ruleChapterPrev"])
  chapter_list = html.xpath(curBookSource["ruleChapterList"])
  chapter_next = html.xpath(curBookSource["ruleChapterNext"])
  chapter_prev = re.sub(r'^https://www.kuxiaoshuo.com', "", chapter_prev[0])
  chapter_prev = re.sub(r'\.html$',"",chapter_prev)
  chapter_list = re.sub(r'^https://www.kuxiaoshuo.com', "", chapter_list[0])
  chapter_list = re.sub(r'\.html$',"",chapter_list)
  chapter_next = re.sub(r'^https://www.kuxiaoshuo.com', "", chapter_next[0])
  chapter_next = re.sub(r'\.html$',"",chapter_next)
  # 上下章节数据重构
  chapter_prev_list_next = [
    {"title": "上一章", "url": "/" + curBookSource["bookSourceId"] + chapter_prev},
    {"title": "目录", "url": "/" + curBookSource["bookSourceId"] + chapter_list},
    {"title": "下一章", "url": "/" + curBookSource["bookSourceId"] + chapter_next}
  ]
  print(chapter_details)
  print(chapter_prev_list_next)
  chapter = {
    "chapter_details": chapter_details,
    "chapter_btns": chapter_prev_list_next
  }
  return chapter