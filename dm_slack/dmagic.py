#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module containing an example on how to use DMagic and Slack to create a channel named GUP-# 
retrieving the information from the scheduling system

running under python 3.8 

and bash including:

export DM_ROOT_DIR=/home/dm_bm/production
export DM_DS_WEB_SERVICE_URL=https://xraydtn02.xray.aps.anl.gov:22236
export DM_DAQ_WEB_SERVICE_URL=https://s2bmdm.xray.aps.anl.gov:33336
export DM_CAT_WEB_SERVICE_URL=https://s2bmdm.xray.aps.anl.gov:44436
export DM_PROC_WEB_SERVICE_URL=https://s2bmdm.xray.aps.anl.gov:55536
export DM_APS_DB_WEB_SERVICE_URL=https://xraydtn02.xray.aps.anl.gov:11236
export DM_STATION_NAME=2BM
export DM_ALLOWED_EXPERIMENT_TYPES=2BM,TEST

export DM_LOGIN_FILE=/home/dm_bm/etc/.user2bm.system.login
export DM_BEAMLINE_NAME=2-BM-A,B
export DM_ESAF_SECTOR=02
export DM_STATION_GUI_USE_ESAF_DB=
export DM_BEAMLINE_MANAGERS=d49734
export DM_DATA_DIRECTORY_MAP=

"""
import os
import sys
import time
import datetime
import argparse
import pathlib
import datetime as dt
import pytz 

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dm import BssApsDbApi

dm_api = BssApsDbApi()

def get_current_emails(exclude_pi=True):
    """
    Find user's emails currently running at beamline
     
    Parameters
    ----------
    users : dictionary-like object containing user information
    
    
    Returns
    -------
    List of user emails (default: all but PI)       
    """
    emails = []
    
    users = get_current_users()
    if not users:
        return None

    for u in users:
        if exclude_pi and 'piFlag' in u.keys() and u['piFlag'] == 'Y':
            continue
        if 'email' in u.keys() and u['email'] != None:
            emails.append(str(u['email']).lower())
            print('Added {0:s} to the e-mail list.'.format(emails[-1]))
        else:            
            print("    Missing e-mail for badge {0:6d}, {1:s} {2:s}, institution {3:s}"
                    .format(u['badge'], u['firstName'], u['lastName'], u['institution']))
    return emails

def get_current_users():
    """
    Get users running at beamline currently
    
    Returns
    -------
    users : dictionary-like object containing user information      
    """
    proposal = get_current_proposal()
    if not proposal:
        log.warning("No current valid proposal")
        return None
    return proposal['experimenters']

def get_current_proposal_id():
    """
    Get the proposal id for the current proposal.

    Returns
    ---------
    proposal ID as an int
    """
    proposal = get_current_proposal()
    # print(proposal)
    if not proposal:
        print("No current valid proposal")
        return None
    return str(get_current_proposal()['id'])

def get_current_proposal():
    """
    Get a dictionary-like object with current proposal information.
    If no proposal is active, return None
    
    Returns
    -------------
    dict-like object with information for current proposal
    """
    proposals = dm_api.listProposals()
    # print(proposals)
    # time_now = dt.datetime.now(pytz.utc)
    time_now = dt.datetime(2021, 11, 6, 8, 15, 12, 0, pytz.UTC)
    for prop in proposals:
        for i in range(len(prop['activities'])):
            prop_start = dt.datetime.fromisoformat(prop['activities'][i]['startTime'])
            prop_end = dt.datetime.fromisoformat(prop['activities'][i]['endTime'])
            if prop_start <= time_now and prop_end >= time_now:
                return prop
    return None

def slack():
    # Set bot tokens as environment values
    env_path = os.path.join(str(pathlib.Path.home()), '.slackenv')
    load_dotenv(dotenv_path=env_path)

    bot_token = os.environ.get("BOT_TOKEN")

    client = WebClient(token=bot_token)
    try:
        # Call the conversations.create method using the WebClient
        # conversations_create requires the channels:manage bot scope
        result = client.conversations_create(
            # The name of the conversation
            name='d4564656'
        )
        # Log the result which includes information like the ID of the conversation
        print(result)

    except SlackApiError as e:
        print("Error creating conversation: {}".format(e))

def main():

    proposal_id = get_current_proposal_id()
    print(proposal_id)
    print(get_current_emails())
    # slack()

if __name__ == '__main__':
    main()


    #     users = scheduling.get_current_users(args)
    #     emails = scheduling.get_current_emails(users, exclude_pi=False)
    #     emails.append(args.primary_beamline_contact_email)
    #     emails.append(args.secondary_beamline_contact_email)
    #     for email in emails:
    #         args.pi_email = email
    #         log.warning('Sharing %s%s with %s' % (args.globus_server_top_dir, new_dir, args.pi_email))
    #         globus.share_globus_dir(args, ac, tc)
    # else:
    #     log.error("%s is not a supported globus server" % args.globus_server_name)

    # def yes_or_no(question):
    # answer = str(input(question + " (Y/N): ")).lower().strip()
    # while not(answer == "y" or answer == "yes" or answer == "n" or answer == "no"):
    #     log.warning("Input yes or no")
    #     answer = str(input(question + "(Y/N): ")).lower().strip()
    # if answer[0] == "y":
    #     return True
    # else:
    #     return False
