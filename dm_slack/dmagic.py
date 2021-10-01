#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #########################################################################
# Copyright (c) 2015, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2015. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

"""
Module containing an example on how to use DMagic to access the APS scheduling
system information.

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

def get_current_proposal_id():
    """
    Get the proposal id for the current proposal.

    Returns
    ---------
    proposal ID as an int
    """
    proposal = get_current_proposal()
    if not proposal:
        log.warning("No current valid proposal")
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
    # time_now = dt.datetime.now(pytz.utc)
    time_now = dt.datetime(2021, 7, 3, 8, 15, 12, 0, pytz.UTC)
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
            name='c4564656'
        )
        # Log the result which includes information like the ID of the conversation
        print(result)

    except SlackApiError as e:
        print("Error creating conversation: {}".format(e))

def main():

    # proposal_id = get_current_proposal_id()
    # print(proposal_id)
    slack()

if __name__ == '__main__':
    main()
