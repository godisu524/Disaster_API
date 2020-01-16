import csv
import requests
import datetime
import calendar
import time
import pymysql


def get_new_msg():
    #시간, 하루전
    now = datetime.datetime.now()
    #하루전시간
    yesterday = datetime.date.today() - datetime.timedelta(days=1) ##뺄 날자 
    yesterday=str(yesterday)+" 09:00:00"
    #print(yesterday)

    yesterday = datetime.datetime.strptime(yesterday, "%Y-%m-%d %H:%M:%S")

    








    #일단 메시지 담가놓을 배열
    Disaster_Msg=[]
    with open("DisasterMsg.csv",'r',encoding='utf-8',newline="")as file:
        reader = csv.reader(file)
        for row in reader:
            Disaster_Msg.append(row[0])
    #도시이름 다른것들 체크용
    cities=[]
    with open("city.csv",'r',encoding='utf-8',newline="")as file:
        reader = csv.reader(file)
        for row in reader:
            cities.append(row)

    #사용자(어르신) 정보가져오기
    #db 연결 
    con = pymysql.connect(host='35.201.169.147', user='root', password='1thefull!',db='silverCare',charset='utf8')
    #쿼리문통해 가져옴
    with con: 
        ELDERS=[]
        cur = con.cursor()
        cur.execute("SELECT ELDERLY_NAME,ELDERLY_ADDRESS1,ELDERLY_NO FROM silverCare.ELDERLY_INFO where CHAR_LENGTH(ELDERLY_ADDRESS1) > 1 ;")

        rows = cur.fetchall()

        for row in rows:
            ELDERS.append(row) #이름, 주소

    #API 발송!
    URL= "http://apis.data.go.kr/1741000/DisasterMsg2/getDisasterMsgList?ServiceKey=JCdCeC4ndtabahEXc%2BQFaXpfYNlnb5qGLlG87NZuchzyB72UAzlRHDEbTBuhTvqSibuNj3QVizylRgAzEbmSgA%3D%3D&type=json&pageNo=1&numOfRows=10"

    PARAMS={'ServiceKey':"JCdCeC4ndtabahEXc%2BQFaXpfYNlnb5qGLlG87NZuchzyB72UAzlRHDEbTBuhTvqSibuNj3QVizylRgAzEbmSgA%3D%3D",
            'type':'json',
            'pageNo':'1',
            'numOfRows':'10',
            'flag':'Y'}

    r = requests.get(url = URL)



    #가지고온 제이슨가지고 분석 전처리
    for d_message in (r.text.split('\"row\":[')[1]).split('},'):
        
            
        word="\"create_date\":"
        timeindex=d_message.index(word) +len(word)

        timestr=""
        for token in d_message[timeindex:]:
            if token ==",":
                break
            if token !='\"':
                timestr+=token
        #재난문자 발송시간
        Disaster_time = datetime.datetime.strptime(timestr, "%Y/%m/%d %H:%M:%S")

        #문자 발송 시간과 어제 갱신 시간비교 해서 갱신시간보다 뒤에 온 문자면 
        if Disaster_time>yesterday:
            d_message=d_message+"}"
            if d_message not in Disaster_Msg:
                with open("DisasterMsg.csv",'a',encoding='utf-8',newline="")as file:
                    writer= csv.writer(file)
                    writer.writerow([d_message])
        else:
            break
        #다솜이 사용자에게 발송 부분
        location_word="\"location_name\":"
        msg_word="\"msg\":"
        
        
        full_location=""
        msg_str=""
        msg_index=d_message.index(msg_word) +len(msg_word)
        
        location_index=d_message.index(location_word) +len(location_word)
       
        #지역 정보가져오기
        for token in d_message[location_index+1:]:
            if token =="\"":
                break
            else:
                full_location+=token
        
        #문자 정보가져오기
        for token in d_message[msg_index+1:]:
            if token =="\"":
                break

            else:
                msg_str+=token
            msg_str.replace("\n"," ")
            msg_str.replace("  "," ")
        


       
        #full_location = 경기도 김포시
        #seperate_location = 경기도
        #city = [경기도,경기 ...]
        #ELDERS=[이름,주소,고유식별번호] 우선.
        
        #날린 문자갯수
        count=1
        for seperate_location in full_location.split(','):

            for city in cities:
                
                if city[0] ==seperate_location.split(' ')[0]:
                    for olds in ELDERS:
                        #도시 확인
                        if olds[1].split(' ')[0] in city:
                            #시/군/구 확인 
                            #전체면 모두 발싸
                            if seperate_location.split(' ')[1] == "전체":
                                print(str(olds) +" 문자내용 :" +msg_str)
                                count+=1
                            #전체가 아니면 시/군/구 확인후 발사
                            elif seperate_location.split(' ')[1] == olds[1].split(' ')[1]:
                                print(str(olds) +" 문자내용 :" +msg_str)
                                count+=1
                            #해당사항없으면 발사 안함
                            else:
                                break
        
        print(str(count) + "번 만큼의 사람들에게 재난 문자를 보내야합니다.")
            


            

get_new_msg()