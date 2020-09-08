from flask import Flask, render_template, jsonify, request
from flask_restful import Resource, Api
from flask_restful import reqparse
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyperclip
import time

from pymongo import MongoClient

app = Flask(__name__)
# Scss(app)

client = MongoClient('localhost', 27017)
db = client.dbsparta

#
# # 1.크롬 웹 드라이버 경로 설정
# driver = webdriver.Chrome('C:/Users/Windows10/Downloads/chromedriver/chromedriver.exe')
#
# # 2. 크롬 웹 드라이버로 url 접속
# url = 'localhost:5000'
# driver.get(url)

# # 3. 네이버 로그인 창에 아이디와 비밀번호 입력
# login = {
#     'id':'jd06280',
#     'pw':'dmswn12!!'
# }
# time.sleep(0.5)
# # driver.find_element_by_name('id').send_keys('아이디') # "아이디라는 값을 보내준다"
#
# def clipboard_input(user_xpath, user_input):
#     temp_user_input = pyperclip.paste()  # 사용자 클립보드를 따로 저장
#
#     pyperclip.copy(user_input)
#     driver.find_element_by_xpath(user_xpath).click()
#     ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
#
#     pyperclip.copy(temp_user_input)  # 사용자 클립보드에 저장 된 내용을 다시 가져 옴
#     time.sleep(1)
#
# clipboard_input('//*[@id="id"]',login.get('id'))
# clipboard_input('//*[@id="pw"]',login.get('pw'))
#
# # 4. 네이버 로그인 버튼 클릭
# driver.find_element_by_xpath('//*[@id="log.login"]').click()

SECRET_KEY = 'hi'

import jwt
import datetime
import hashlib

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/calendar')
def calendar():
    return render_template('fullcalendar.html')

@app.route('/graph')
def graph():
    return render_template('index2.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nick_receive = request.form['nick_give']

    id_already = db.info.find_one({'id': id_receive})
    nick_already = db.info.find_one({'nick':nick_receive})

    if id_already is not None: #id가 있으면
        return jsonify({'result': 'fail_id', 'msg': '이미 있는 아이디입니다'})
    elif nick_already is not None: #닉네임이 있으면
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

    if person is not None: #person이 있으면
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1000)
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
    print(count_receive)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        if count_receive == '0':
            return jsonify({'result':'None'})
        else:
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

@app.route('/api/inputEvent',methods=['POST'])
def api_inputEvent():
    token_receive = request.headers['token_give']
    title_receive = request.form['title']
    year_receive = request.form['year']
    month_receive = request.form['month']
    day_receive = request.form['day']

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user = db.info.find_one({'id': payload['id']}) #이 아이디 값을 가지는 첫번째 애
        event = {
            'id': user['id'],
            'title': title_receive,
            'year': year_receive,
            'month': month_receive,
            'day': day_receive
        }
        db.event.insert_one(event)
        return jsonify({'result': 'success'})
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail time'})

@app.route('/api/reviseEvent',methods=['POST'])
def api_reviseEvent():
    token_receive = request.headers['token_give']

    title_receive = request.form['title']
    new_title_receive = request.form['new_title']
    year_receive = request.form['year']
    month_receive = request.form['month']
    day_receive = request.form['day']

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        db.event.update_one({'id': payload['id'], 'title': title_receive, 'year': year_receive, 'month': month_receive,
                             'day': day_receive}, {'$set': {'title': new_title_receive}})

        if new_title_receive != '':
            return jsonify({'result':'success'})
        elif new_title_receive == '':
            db.event.delete_one({'title': new_title_receive,'year': year_receive,'month': month_receive,'day': day_receive})
            db.time.delete_one({'id': payload['id'], 'year': year_receive, 'month': month_receive, 'day': day_receive})
            return jsonify({'result': 'success'})

    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail time'})

@app.route('/api/postEvent', methods=['GET'])
def api_postEvent():
    token_receive = request.headers['token_give']

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        events = list(db.event.find({'id': payload['id']}, {'_id': 0}))
        return jsonify({'result': 'success', 'events': events})

    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail time'})

@app.route('/api/compareTime', methods=['POST'])
def api_compareTime():
    token_receive = request.headers['token_give']

    year_receive = request.form['year']
    month_receive = request.form['month']
    day_receive = request.form['day']

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        events = db.event.find({'id': payload['id'], 'year': year_receive, 'month': month_receive, 'day': day_receive})
        hour = 0
        minute = 0
        sec = 0
        if events is not None: #들어올 때 마다 그 날짜에 해당하는 #다음에 오는 시간을 모두 체크함
            for event in events:
                if event['title'][0:1] == '#':  # 이벤트 title 첫글자가 #이면
                    hour += int(event['title'][3:4])
                    minute += int(event['title'][5:7])
                    sec += int(event['title'][8:10])

            if sec >= 60:
                minute += 1
                sec -= 60
            if minute >= 60:
                hour += 1
                minute -= 60

        time = db.time.find_one({'id': payload['id'],'year':year_receive,'month':month_receive,'day':day_receive})

        if time is not None: # 이미 공부시간을 등록한게 있을 때
            db.time.update_one({'id': payload['id'],'year': year_receive, 'month': month_receive,
                                'day': day_receive},{'$set':{'hour':hour,'min':minute,'sec':sec}})
        else: #이미 등록한거 없이 새로 등록하는 경우

            time = {
                'id': payload['id'],
                'hour': hour,
                'min': minute,
                'sec': sec,
                'year': year_receive,
                'month': month_receive,
                'day': day_receive
            }
            db.time.insert_one(time)
        return jsonify({'result':'success'})

        # # weeks = soup.select('#calendar > div > div > table > tbody > tr')
        # # for week in weeks:
        # #     days = week.select('td.fc-day')
        # #     for day in days:
        # #         if day['data-date'] == (year_receive+'-'+month_receive+'-'+day_receive):
        # #             return jsonify({'result': 'True'});
        # #         else:
        # #             return jsonify({'result': 'False'});
        # for set in time_set:
        #     if set['timeSet'] is not None:  # timeSet 을 가지고 있는 애는,
        #         if hour >= int(set['timeSet']):
        #             return jsonify({'result': 'True'});
        #         else:
        #             return jsonify({'result': 'False'});

    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail time'})

# @app.route('/api/graph', methods=['GET'])
# def api_graph():
#     token_receive = request.headers['token_give']
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         events = list(db.event.find({'id': payload['id']},{'_id':0}))
#         # print('하이')
#         return jsonify({'result': 'success', 'event': events})
#     except jwt.ExpiredSignatureError:
#         return jsonify({'result': 'fail time'})

@app.route('/api/showGraph', methods=['GET'])
def api_graph():
    token_receive = request.headers['token_give']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        events = db.event.find({'id':payload['id']},{'_id':0})
        if events is None:
            return jsonify({'result':'공부 기록이 없습니다!'})
        else:
            com_sum = 0
            eng_sum = 0
            stock_sum = 0
            for event in events:
                if event['title'][0:2] == '#컴':
                    com_sum += int(event['title'][3:4])
                elif event['title'][0:2] == '#영':
                    eng_sum += int(event['title'][3:4])
                elif event['title'][0:2] == '#주':
                    stock_sum += int(event['title'][3:4])

            # print(com_sum)
            # print(eng_sum)
            # print(stock_sum)

        graphs = db.graph.find_one({'id': payload['id']},{'_id':0})
        if graphs is None:  #저장된 것이 없다면
            db.graph.insert_one({'id':payload['id'],'computer':com_sum,'english':eng_sum,'stock':stock_sum})
        else:
            db.graph.update_one({'id': payload['id']}, {'$set':{'computer': com_sum, 'english': eng_sum, 'stock':stock_sum}})

        info = list(db.graph.find({'id': payload['id']},{'_id':0}))
        return jsonify({'result': 'success', 'info': info})

    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail time'})

@app.route('/api/setPlan', methods=['POST'])
def api_setPlan():
    token_receive = request.headers['token_give']
    plan_receive = request.form['plan']

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        db.plan.insert_one({'id':payload['id'],'plan':plan_receive})
        plans = list(db.plan.find({'id':payload['id']},{'_id':0}))
        return jsonify({'result':'success','plan':plans})

    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail time'})

@app.route('/api/postPlan', methods=['GET'])
def api_postPlan():
    token_receive = request.headers['token_give']
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        plans = list(db.plan.find({'id':payload['id']},{'_id':0}))
        return jsonify({'result':'success','plan':plans})

    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail time'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)