
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

#  默认首页
@app.route('/')
def index():
  return render_template('find.html')

#搜索书列表
@app.route('/findlist',methods=['POST','GET'])
def findlist():
  if request.method == 'POST':
    result = request.form
    bookname = result["bookname"]
    booksources = booksource.bookRule
    lst = []
    for item in booksources:
      print(item)
      req = requests.get(item["ruleSearchUrl"] + bookname)
      print(item["ruleSearchUrl"])
      encode_content = withDataCode(req)
      print(encode_content)
      html = etree.HTML(encode_content)
      print(html)
      # 书本列表
      book_names = html.xpath(item["ruleSearchListName"])
      book_urls = html.xpath(item["ruleSearchListUrl"])
      print(item["ruleSearchListName"])
      print(item["ruleSearchListUrl"])
      print(book_names)
      print(book_urls)
      
      for idx,book in enumerate(book_names):
        url = re.sub(r'^https://www.kuxiaoshuo.com', "", book_urls[idx])
        lst.append({
          'bookName': book,
          'bookUrl': url,
          'bookId': item["bookSourceId"]
        })
      print(lst)
        
    return render_template("findlist.html",result = lst)

#书章节列表
@app.route('/<bookSourceId>/<bookId>/',methods=['POST','GET'])
def chapterList(bookSourceId,bookId):
  curBookSource = {}
  booksources = booksource.bookRule
  for item in booksources:
    if item["bookSourceId"] == bookSourceId:
      curBookSource = item

  # 查找当前书源下当前书本的章节列表
  req = requests.get(curBookSource["bookSourceUrl"] + "/" + bookId + "/")
  encode_content = withDataCode(req)
  html = etree.HTML(encode_content)
  print(encode_content)
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

  return render_template('chapterList.html' ,result = lst)

#章节详情
@app.route('/<bookSourceId>/<bookId>/<chapterId>',methods=['POST','GET'])
def chapterDetail(bookSourceId,bookId,chapterId):
  curBookSource = {}
  booksources = booksource.bookRule
  for item in booksources:
    if item["bookSourceId"] == bookSourceId:
      curBookSource = item
  
  # 查找章节详情
  req = requests.get(curBookSource["bookSourceUrl"] + "/" + bookId + "/" + chapterId + ".html")
  encode_content = withDataCode(req)
  html = etree.HTML(encode_content)
  print(encode_content)
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

  return render_template('chapterDetail.html', result = chapter_details, chapter_btns = chapter_prev_list_next)


if __name__ == '__main__':
  app.run(debug=True)