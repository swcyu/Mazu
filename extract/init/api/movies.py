import requests
import json

serviceKey = 'MHD81YQ678I2F0KLGRZ3'
# (1) 2020~현재 (2) 2010~2019 (3) 2000~2009
url = f'http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2&detail=N&ServiceKey={serviceKey}&listCount=500&startCount=0&releaseDts=20000101&releaseDte=20220913'
response = requests.get(url)
contents = response.text
#print(contents)
rjson = response.json()
#13305 -> 26 * 500 = 13,000
totalCount = rjson['TotalCount']
print(totalCount)


for i in range(0, int(totalCount/500)+1):
    startCount = 500 * i
    print(startCount)
    url = f'http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2&detail=N&ServiceKey={serviceKey}&listCount=500&startCount={startCount}&releaseDts=20000101&releaseDte=20220913'
    response = requests.get(url)
    r_json = json.loads(response.text, strict=False)

    data = r_json['Data'][0]['Result']
    dict = {"movie": data}
    print(data[0])
    with open('movie'+str(i)+'.json', 'w', encoding='utf-8') as f:
        json.dump(dict, f, ensure_ascii=False, indent=4)
