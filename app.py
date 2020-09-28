
from flask import Flask, request, render_template
import requests
import json
from lxml import etree
import booksource
import router
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
@app.route('/',methods=['POST','GET'])
def index():
  lst = []
  if request.method == 'POST':
    lst = router.getSearchList(request)
  return render_template('find.html', result = lst)

#搜索书列表
@app.route('/findlist',methods=['POST','GET'])
def findlist():
  lst = []
  if request.method == 'POST':
    lst = router.getSearchList(request)
  return render_template("findlist.html",result = lst)

#书章节列表
@app.route('/<bookSourceId>/<bookId>/',methods=['POST','GET'])
def chapterList(bookSourceId,bookId):
  lst = router.getChapterList(bookSourceId,bookId)
  return render_template('chapterList.html' ,result = lst)

#章节详情
@app.route('/<bookSourceId>/<bookId>/<chapterId>',methods=['POST','GET'])
def chapterDetail(bookSourceId,bookId,chapterId):
  lst = router.getChapterDetail(bookSourceId,bookId,chapterId)
  return render_template('chapterDetail.html', result = lst)


if __name__ == '__main__':
  app.run(debug=True)