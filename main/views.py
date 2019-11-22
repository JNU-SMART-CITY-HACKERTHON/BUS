from django.shortcuts import render
from .models import Day, Hour, Line
import json
import urllib.request
from urllib.parse import urlencode
import ssl
import random
import time

wday = ['월', '화', '수', '목', '금', '토', '일']
tm_wday = time.localtime().tm_wday

def getPlace(name):
    place = urllib.parse.quote(name)
    context = ssl._create_unverified_context()
    url = "http://dapi.kakao.com/v2/local/search/keyword.json?y=33.478779&x=126.531613&radius=20000&query="+place
    headers = {'Authorization': 'KakaoAK dd957b22980535947df249d89b3d62f1'}
    req = urllib.request.Request(url, headers=headers, unverifiable=True)
    page = urllib.request.urlopen(req, context=context).read()
    if len(json.loads(page)['documents']) > 0:
        return json.loads(page)['documents'][0]
    else:
        return []


def convertWGS2WCONG(x, y):
    context = ssl._create_unverified_context()
    url = "https://dapi.kakao.com/v2/local/geo/transcoord.json?x="+x+"&y="+y+"&input_coord=WGS84&output_coord=WCONGNAMUL"
    headers = {'Authorization': 'KakaoAK dd957b22980535947df249d89b3d62f1'}
    req = urllib.request.Request(url, headers=headers, unverifiable=True)
    page = urllib.request.urlopen(req, context=context).read()
    if len(json.loads(page)['documents']) > 0:
        return (str(json.loads(page)['documents'][0]['x']), str(json.loads(page)['documents'][0]['y']))
    else:
        return ('0','0')

def convertWCONG2WGS(x, y):
    context = ssl._create_unverified_context()
    url = "https://dapi.kakao.com/v2/local/geo/transcoord.json?x="+x+"&y="+y+"&input_coord=WCONGNAMUL&output_coord=WGS84"
    headers = {'Authorization': 'KakaoAK dd957b22980535947df249d89b3d62f1'}
    req = urllib.request.Request(url, headers=headers, unverifiable=True)
    page = urllib.request.urlopen(req, context=context).read()
    if len(json.loads(page)['documents']) > 0:
        return (str(json.loads(page)['documents'][0]['x']), str(json.loads(page)['documents'][0]['y']))
    else:
        return ('0','0')
    

def getRoute(startStation, endStation, hour):
    if startStation == [] or endStation == []:
        return []

    start = urllib.parse.quote(startStation['place_name'])
    end = urllib.parse.quote(endStation['place_name'])
    context = ssl._create_unverified_context()

    startStation['x'], startStation['y'] = convertWGS2WCONG(startStation['x'], startStation['y'])
    endStation['x'], endStation['y'] = convertWGS2WCONG(endStation['x'], endStation['y'])

    url = "https://map.kakao.com/route/pubtrans.json?inputCoordSystem=WCONGNAMUL&outputCoordSystem=WCONGNAMUL&service=map.daum.net&sX="+startStation['x']+"&sY="+startStation['y']+"&sName="+start+"&sid="+startStation['id']+"&eX="+endStation['x']+"&eY="+endStation['y']+"&eName="+end+"&eid="+endStation['id']
    page = urllib.request.urlopen(url, context=context).read()
    data = json.loads(page)
    busdata = []

    count = 0
    for line_data in data["in_local"]["routes"]:
        busdata.append([])
        busdata[count].append(line_data["distance"]["text"])#거리
        busdata[count].append(line_data["fare"]["text"]) #가격
        busdata[count].append(line_data["time"]["text"]) #시간
        busdata[count].append([])
        for step in line_data["steps"]: #step에서 처음과 끝은 그냥 출발이므로 데이터 필요 ㄴㄴ
            if step["action"] != "MOVE" and step["action"] != "GETON":
                continue

            arr = []
            arr.append(step["actionName"])  # 액션 상태
            arr.append(step["distance"]["text"])  # 이동거리
            arr.append(step["information"])  # 현재 스탭 정보
            arr.append(step["polyline"]) # 이동라인
            arr.append(step["time"]["text"])  # 이동시간

            if step["action"] == "GETON":
                linenumber = random.choice(step["vehicles"])["name1"]
                arr.append(linenumber) # 노선


                try:
                    day = Day.objects.get(day=wday[tm_wday])
                    hour1 = Hour.objects.get(hour=hour)
                    line = Line.objects.filter(line__startswith=linenumber)[0]

                    rate = int(day.rate * hour1.rate * line.rate * 100)
                except:
                    rate = 0
                # rate = (max(min(day.rate * hour1.rate * line.rate, 0.6), 0.4) - 0.4)*5

                arr.append(rate)

            busdata[count][len(busdata[count])-1].append(arr)
        
        count = count + 1

    return busdata


def index(request):
    return render(request, 'main/index.html')

def show(request):
    start = getPlace(request.GET['start'])
    end = getPlace(request.GET['end'])
    hour = int(request.GET['hour'].split(":")[0])

    print(hour)

    route = getRoute(start, end, hour)
    
    return render(request, 'main/show.html', {'route': route})
