from flask import Flask, render_template, jsonify, request
from flask_restful import Resource, Api
from flask_restful import reqparse
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta

SECRET_KEY = 'hi'

import jwt
import datetime
import hashlib

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nick_receive = request.form['nick_give']

    id_already = db.info.find_one({'id': id_receive})
    nick_already = db.info.find_one({'nick':nick_receive})

    if id_already is not None:
        return jsonify({'result': 'fail_id', 'msg': '이미 있는 아이디입니다'})
    elif nick_already is not None:
        return jsonify({'result': 'fail_nick', 'msg': '이미 있는 닉네임입니다'})
    else:
        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        db.info.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nick_receive})
        return jsonify({'result': 'success'})


@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    person = db.info.find_one({'id': id_receive, 'pw': pw_hash})

    if person is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/api/nickname', methods=['GET'])
def api_valid():
    token_receive = request.headers['token_give']

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        user = db.info.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result':'success','nickname': user['nick']})

    except jwt.ExpiredSignatureError:
        return jsonify({'result':'fail'})

@app.route('/api/study', methods=['GET'])
def api_advice():
    advices = [
      {'advice': '실패란 넘어지는 것이 아니라,넘어진 자리에 머무는 것이다'},
      {'advice': '같은 실수를 두려워하되 새로운 실수를 두려워하지 마라. 실수는 곧 경험이다'},
      {'advice': '어떤 것이 당신의 계획대로 되지 않는다고해서 그것이 불필요한 것은 아니다.'},
      {'advice': '내 자신에 대한 자신감을 잃으면 온 세상이 나의 적이 된다.'},
      {'advice': '실패하는 게 두려운 게 아니라 노력하지 않는 게 두렵다.'},
    ]
    return jsonify({'advices':advices, 'response':'success'})

@app.route('/api/timeRecord', methods=['POST'])
def api_time():
    time_receive = request.form['timeSet_give']
    count_receive = request.form['count_give']
    token_receive = request.headers['token_give']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        if count_receive == 0:
            print('카운트')
            return jsonify({'result':'None'})
        else:
            print(count_receive)
            if time_receive >= '0':
                user = db.time.find_one({'id': payload['id']})
                if user is not None:  #id가 있으면 덮어쓰기
                    time = user['timeSet']
                    db.time.update_one({'timeSet': time}, {'$set': {'timeSet': time_receive}})
                    return jsonify({'result': 'success'})
                else:  #id가 없으면
                    db.time.insert_one({'timeSet': time_receive, 'id': payload['id']})
                    return jsonify({'result': 'success'})
            else:
                return jsonify({'result': 'fail <0' })
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail time'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)