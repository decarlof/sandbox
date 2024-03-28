import json
import pathlib
import requests

from requests.auth import HTTPBasicAuth


def read_credentials(filename):
    credentials = []
    with open(filename, 'r') as file:
        for line in file:
            url, username, password = line.strip().split('|')  # Assuming | separated values: url|user|pwd
            credentials.append((url, username, password))
    return credentials


def beamtime_request(scheduling_period, beamline_id="2-BM-A,B", credential_filename='.scheduling_credentials'):
    credentials = read_credentials(pathlib.PurePath(pathlib.Path.home(), credential_filename))
    # print(credentials[0])

    url               = credentials[0][0]
    username          = credentials[0][1]
    password          = credentials[0][2]
    end_point         = "sched-api/beamtimeRequests/findBeamtimeRequestsByRunAndBeamline"
    api_url = url + "/" + end_point + "/" + scheduling_period + "/" + beamline_id

    response = requests.get(api_url, auth = HTTPBasicAuth(username, password))

    return response

def main():

    response = beamtime_request("2020-1")  
    print(response.json())
    print(response.status_code)

if __name__ == '__main__':
    main()