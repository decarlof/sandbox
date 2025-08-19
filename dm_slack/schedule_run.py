import os
import pytz 
import pathlib
import requests
import datetime as dt

from requests.auth import HTTPBasicAuth

__author__ = "Francesco De Carlo"
__copyright__ = "Copyright (c) 2025, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['basic',
          'read_credentials', ]

debug = False

CREDENTIALS_FILE_NAME = os.path.join(str(pathlib.Path.home()), '.scheduling_credentials')

def read_credentials(filename):
    """
    Read username and password from filename.
    """
    credentials = []
    with open(filename, 'r') as file:
        for line in file:
            username, password = line.strip().split('|')  
            credentials.append((username, password))
    return credentials

def fix_iso(s):
    """
    This is a temporary fix until timezone is returned as -05:00 instead of -0500

    Parameters
    ----------
    s : string
        Like "2022-07-31T01:51:05-0400"

    Returns
    -------
    s : string
        Like "2022-07-31T01:51:05-04:00"

    """
    pos = len("2022-07-31T01:51:05-0400") - 2 # take off end "00"
    if len(s) == pos:                 # missing minutes completely
        s += ":00"
    elif s[pos:pos+1] != ':':         # missing UTC offset colon
        s = f"{s[:pos]}:{s[pos:]}"
    return s


def authorize(filename):
    """
    Get authorization using username and password contained in filename in the format of USERNAME|PASSWORD
    """
    credentials = read_credentials(filename)

    username          = credentials[0][0]
    password          = credentials[0][1]
    auth = HTTPBasicAuth(username, password)

    return auth

def get_current_run(time, auth):

    url = "https://beam-api.aps.anl.gov"
    end_point         = "beamline-scheduling/sched-api/run/getAllRuns"
    api_url = url + "/" + end_point 

    reply = requests.get(api_url, auth=auth)

    if reply.status_code != 404:
        start_times = [item['startTime'] for item in reply.json()]
        end_times   = [item['endTime']   for item in reply.json()]
        runs        = [item['runName']   for item in reply.json()]
        
        for i in range(len(start_times)):
            prop_start = dt.datetime.fromisoformat(fix_iso(start_times[i]))
            prop_end   = dt.datetime.fromisoformat(fix_iso(end_times[i]))
            if prop_start <= time and prop_end >= time:
                return runs[i]
    else:
        log.error("No response from the restAPI. Error: %s" % reply.status_code)    
    return None


def main():

    auth      = authorize(CREDENTIALS_FILE_NAME)

    time_now = dt.datetime.now(pytz.timezone('America/Chicago')) #+ dt.timedelta(args.set)
    current_run = get_current_run(time_now, auth)
    print(current_run)

if __name__ == '__main__':
    main()
