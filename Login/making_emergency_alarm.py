from flask import Flask, render_template, jsonify, request
import json
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import save_emercency_csv


def check_DisasterMsg():
    save_emercency_csv.get_new_msg()
    print("실행완료")
sched = BackgroundScheduler(daemon=False)
#hour= api 모듈 사용 시간 설정(0~23)
sched.add_job(check_DisasterMsg,'cron',hour='9') 

sched.start()



app = Flask(__name__)

@app.route('/')
def index():
  return jsonify({'data': "none"})

def response_json(return_json):
  return json.dumps(return_json, ensure_ascii=False)


  

if __name__ =="__main__":
    #use_reloader -> 두번 되는거방지
    app.run(debug=True, host='0.0.0.0',port=5001,use_reloader=False)




