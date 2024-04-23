import json
import requests

if __name__ == "__main__":

    headers = {
      "accept": "*/*",
      "authorization": "Basic enter-token-here"
    }

    res = requests.get('enter-url-here/sched-api/sched-api/beamline/findAllBeamlines', headers=headers)
    res_json = res.json()
    
    # print(res_json[0]['beamlineId'])
    # print(res.status_code)
   
    # beamlines = [item['beamlineId'] for item in res_json]
    # print(beamlines)

    # beamlines = [item for item in res_json if item['beamlineId'] == '2-BM-A,B'] # '2-BM-A,B', '7-BM-B', '32-ID-B,C'
    # print(beamlines)

    # current credetials are not authorized to see 2-BM-A,B
    res = requests.get('enter-url-here/sched-api/sched-api/beamtimeRequests/findBeamtimeRequestsByRunAndBeamline/2023-1/2-BM-A%2CB', headers=headers)
    res_json = res.json()
    print(res_json)