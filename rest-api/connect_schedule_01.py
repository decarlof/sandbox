import json
import pathlib
import pprint
import requests

import datetime as dt

from requests.auth import HTTPBasicAuth

url = 'https://mis7.aps.anl.gov:7004'
offset = -1500     # offset : float +/- number of days from the current date. (test: -1500, -600, -700, -7000)

def fix_iso(s):
    """
    This is a temporary fix until timezone is returned as -05:00 instead of -0500
    """
    pos = len("2022-07-31T01:51:05-0400") - 2 # take off end "00"
    if len(s) == pos:                 # missing minutes completely
        s += ":00"
    elif s[pos:pos+1] != ':':         # missing UTC offset colon
        s = f"{s[:pos]}:{s[pos:]}"
    return s

def read_credentials(filename):
    """
    Read username and password from filename.
    Must create filename in the user home directory with | separated values: user|pwd
    """
    credentials = []
    with open(filename, 'r') as file:
        for line in file:
            username, password = line.strip().split('|')  
            credentials.append((username, password))
    return credentials

def authorize(filename='.scheduling_credentials'):
    """
    Get authorization using username and password contained in filename.
    """
    credentials = read_credentials(pathlib.PurePath(pathlib.Path.home(), filename))

    username          = credentials[0][0]
    password          = credentials[0][1]
    auth = HTTPBasicAuth(username, password)

    return auth

def current_run(auth):
    """
    Determine the current run

    Parameters
    ----------
    auth : Basic http authorization object
        Basic http authorization.


    Returns
    -------
    run : string
        Run name 2024-1.
    """
    end_point         = "beamline-scheduling/sched-api/run/getAllRuns"
    api_url = url + "/" + end_point 
    print(api_url)

    reply = requests.get(api_url, auth=auth)

    start_times = [item['startTime'] for item in reply.json()]
    end_times   = [item['endTime']   for item in reply.json()]
    runs        = [item['runName']   for item in reply.json()]
    
    time_now = dt.datetime.now().astimezone() + dt.timedelta(offset) + dt.timedelta(offset)

    for i in range(len(start_times)):
        prop_start = dt.datetime.fromisoformat(fix_iso(start_times[i]))
        prop_end   = dt.datetime.fromisoformat(fix_iso(end_times[i]))
        if prop_start <= time_now and prop_end >= time_now:
            return runs[i]
    return None

def beamtime_requests(run, auth, beamline_id="2-BM-A,B"):
    """
    Get a dictionary-like object with all proposals that have a beamtime request scheduled during the run.
    If no proposal is active or auth does not have permission for beamline_id, return None.
    
    Parameters
    ----------
    run : string
        Run name e.g. '2024-1'
    auth : Basic http authorization object
        Basic http authorization.
    beamline_id : string
        beamline ID as stored in the APS scheduling system, e.g. 2-BM-A,B or 7-BM-B or 32-ID-B,C

    Returns
    -------
    proposals : list
        dict-like object with proposals that have a beamtime request scheduled during the run.
        Returns None if there are no proposals or if auth does not have permission for beamline_id.
    """
    if not run:
        return None
    else:
        end_point="beamline-scheduling/sched-api/activity/findByRunNameAndBeamlineId"
        api_url = url + "/" + end_point + "/" + run + "/" + beamline_id
        reply = requests.get(api_url, auth=auth)

        return reply.json()

def get_current_proposal(proposals):
    """
    Get a dictionary-like object with currently active proposal information.
    If no proposal is active, return None
    
    Returns
    -------
    dict-like object with information for currently active proposal
    """
    time_now = dt.datetime.now().astimezone() + dt.timedelta(offset)
    for prop in proposals:
        prop_start = dt.datetime.fromisoformat(fix_iso(prop['startTime']))
        prop_end = dt.datetime.fromisoformat(fix_iso(prop['endTime']))
        if prop_start <= time_now and prop_end >= time_now:
            # pprint.pprint(prop, compact=True)
            return prop
    return None
 
def get_current_proposal_title(proposal):
    """
    Get the title of the currently active proposal.
    
    Returns
    -------
    str: title of the currently active proposal
    """
    if not proposal:
        print("No current valid proposal")
        return None
    return proposal['beamtime']['proposal']['proposalTitle']

def get_current_proposal_id(proposal):
    """
    Get the proposal id for the currently active proposal.

    Returns
    -------
    currently active proposal ID as an int
    """
    if not proposal:
        print("No current valid proposal")
        return None
    return proposal['beamtime']['proposal']['gupId']

def get_current_users(proposal):
    """
    Get users listed in the currently active proposal.
    
    Returns
    -------
    users : dictionary-like object containing user information      
    """
    if not proposal:
        print("No current valid proposal")
        return None
    return proposal['beamtime']['proposal']['experimenters']

def get_current_pi(proposal):
    """
    Get information about the currently active proposal PI.
    
    Returns
    -------
    dictionary-like object containing PI information
    """
    users = get_current_users(proposal)
    for u in users:
        if 'piFlag' in u.keys():
            if u['piFlag'] == 'Y':
                return u
    # If we are here, nothing was listed as PI.  Use first user
    return users[0]

def get_current_emails(proposal, exclude_pi=True):
    """
    Find user's emails listed in the currently active proposal
     
    Parameters
    ----------
    users : dictionary-like object containing user information
    
    Returns
    -------
    List of user emails (default: all but PI)       
    """
    emails = []
    
    users = get_current_users(proposal)

    if not users:
        return None

    for u in users:
        if exclude_pi and 'piFlag' in u.keys() and u['piFlag'] == 'Y':
            continue
        if 'email' in u.keys() and u['email'] != None:
            emails.append(str(u['email']).lower())
            # print('Added {0:s} to the e-mail list.'.format(emails[-1]))
        else:            
            print("    Missing e-mail for badge {0:6d}, {1:s} {2:s}, institution {3:s}"
                    .format(u['badge'], u['firstName'], u['lastName'], u['institution']))
    return emails

def print_current_experiment_info():
    """
    Print the currently active proposal info running at beamline
     
    Returns
    -------
    Print experiment information        
    """
    auth = authorize()
    run = current_run(auth)
    proposals = beamtime_requests(run, auth)
    # pprint.pprint(proposals, compact=True)
    if not proposals:
        print('No valid current experiment')
        return None
    try:
        log.error(proposals['message'])
        return None
    except:
        pass

    proposal = get_current_proposal(proposals)
    if proposal != None:
        proposal_pi          = get_current_pi(proposal)
        user_name            = proposal_pi['firstName']
        user_last_name       = proposal_pi['lastName']   
        user_affiliation     = proposal_pi['institution']
        user_email           = proposal_pi['email']
        user_badge           = proposal_pi['badge']

        proposal_gup         = get_current_proposal_id(proposal)
        proposal_title       = get_current_proposal_title(proposal)
        proposal_user_emails = get_current_emails(proposal, False)
        proposal_start       = dt.datetime.fromisoformat(fix_iso(proposal['startTime']))
        proposal_end         = dt.datetime.fromisoformat(fix_iso(proposal['endTime']))
       
        print("\tRun: {0:s}".format(run))
        print("\tPI Name: {0:s} {1:s}".format(user_name, user_last_name))
        print("\tPI affiliation: ", user_affiliation)
        print("\tPI e-mail: ", user_email)
        print("\tPI badge: ", user_badge)   
        print("\tProposal GUP: {0:d}".format(proposal_gup))
        print("\tProposal Title: {0:s}".format(proposal_title))
        print("\tStart time: ", proposal_start)
        print("\tEnd Time: ", proposal_end)
        print("\tUser email address: ")
        for ue in proposal_user_emails:
            print("\t\t{:s}".format(ue))
    else:
        time_now = dt.datetime.now().astimezone() + dt.timedelta(offset)

        print('No proposal run on %s during %s' % (time_now, run))

def main():
    print_current_experiment_info()

if __name__ == '__main__':
    main()