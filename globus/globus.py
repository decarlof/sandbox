
import os
import pathlib
import time
import globus_sdk
import numpy as np

import log



def refresh_globus_token(globus_app_uuid):
    """
    Create and save a globus token. The token is valid for 48h.

    Parameters
    ----------
    globus_app_uuid : App UUID 
      
    """

    globus_token_file=os.path.join(str(pathlib.Path.home()), 'token.npy')

    try:
        token_response = np.load(globus_token_file, allow_pickle='TRUE').item()
    except FileNotFoundError:
        log.error('Globus token is missing. Creating one')
        # Creating new token
        # --------------------------------------------
        client = globus_sdk.NativeAppAuthClient(globus_app_uuid)
        client.oauth2_start_flow(refresh_tokens=True)

        log.warning('Please go to this URL and login: {0}'.format(client.oauth2_get_authorize_url()))

        get_input = getattr(__builtins__, 'raw_input', input)
        auth_code = get_input('Please enter the code you get after login here: ').strip() # pythn 3
        # auth_code = raw_input('Please enter the code you get after login here: ').strip() # python 2.7
        token_response = client.oauth2_exchange_code_for_tokens(auth_code)
        # --------------------------------------------
        np.save(globus_token_file, token_response) 

    # let's get stuff for the Globus Transfer service
    globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']
    # the refresh token and access token, often abbr. as RT and AT
    transfer_rt = globus_transfer_data['refresh_token']
    transfer_at = globus_transfer_data['access_token']
    expires_at_s = globus_transfer_data['expires_at_seconds']

    globus_token_life = expires_at_s - time.time()
    if (globus_token_life < 0):
        # Creating new token
        # --------------------------------------------
        globus_app_id = globus_app_uuid
        client = globus_sdk.NativeAppAuthClient(globus_app_id)
        client.oauth2_start_flow(refresh_tokens=True)

        log.warning('Please go to this URL and login: {0}'.format(client.oauth2_get_authorize_url()))

        get_input = getattr(__builtins__, 'raw_input', input)
        auth_code = get_input('Please enter the code you get after login here: ').strip() # pythn 3
        # auth_code = raw_input('Please enter the code you get after login here: ').strip() # python 2.7
        token_response = client.oauth2_exchange_code_for_tokens(auth_code)
        # --------------------------------------------
        np.save(globus_token_file, token_response) 

    return token_response


def create_dir(directory,       # Subdirectory name under top to be created
               ep_uuid,         # Endpoint UUID
               tc):             # Transfer client

    dir_path = '/~/' + directory + '/'
    try:
        response = tc.operation_mkdir(ep_uuid, path=dir_path)
        log.info('*** Created folder: %s' % dir_path)
        return True
    except globus_sdk.TransferAPIError as e:
        log.error(f"Transfer API Error: {e.code} - {e.message}")
        # log.error(f"Details: {e.raw_text}")
    except:
        log.warning('*** Path %s already exists' % dir_path)
        return False


def share_dir(user_email,
              directory,       # Subdirectory name under top to be created
              ep_uuid,         # Endpoint UUID
              ac,              # Access client
              tc):             # Transfer client

    """
    Share an existing globus directory with a globus user. The user receives an email with the link to the folder.
    To add a custom message to the email edit the "notify message" field below
 
    Parameters
    ----------
    user_email  : email address of the user you want to share the globus directory with
    directory   : directory name to be shared
    ep_uuid     : end point UUID
    ac          : Access client
    tc          : Transfer client

    """

    # This part is to handle the case a user does not have yet a globus ID, it is not working yet.
    # # Query to Auth Client to verify if a globus user ID is associated to the user email address, if not one is generated
    # response = ac.get("/v2/api/identities?usernames="+user_email)

    # Get user id from user email
    r = ac.get_identities(usernames=user_email)
    user_id = r['identities'][0]['id']
    # print(r, user_id)

    dir_path = '/~/' + directory + '/'
    # Set access control and notify user
    rule_data = {
      'DATA_TYPE': 'access',
      'principal_type': 'identity',
      'principal': user_id,
      'path': dir_path,
      'permissions': 'r',
      'notify_email': user_email,
      'notify_message': "add here a custom meassage"
    }

    try: 
        response = tc.add_endpoint_acl_rule(ep_uuid, rule_data)
        log.info('*** Path %s has been shared with %s' % (dir_path, user_email))
        return True
    except globus_sdk.TransferAPIError as e:
        log.error(f"Transfer API Error: {e.code} - {e.message}")
        return False
    except:
        log.warning('*** Path %s is already shared with %s' % (dir_path, user_email))
        return False


def show_endpoints(tc):
    """
    Show all end points

    Parameters
    ----------
    tc : Transfer client

    """

    log.info('Show all endpoints shared and owned by my globus user credentials')
    log.info("*** Endpoints shared with me:")
    for ep in tc.endpoint_search(filter_scope="shared-with-me"):
        log.info("*** *** [{}] {}".format(ep["id"], ep["display_name"]))
    log.info("*** Endpoints owned with me::")
    for ep in tc.endpoint_search(filter_scope="my-endpoints"):
        log.info("*** *** [{}] {}".format(ep["id"], ep["display_name"]))


def create_clients(globus_app_uuid):
    """
    Create authorize and transfer clients

    Parameters
    ----------
    globus_app_id : App UUID 

    Returns
    -------
    ac : Authorize client
    tc : Transfer client
      
    """

    globus_token_file=os.path.join(str(pathlib.Path.home()), 'token.npy')
    token_response = refresh_globus_token(globus_app_uuid)
    # let's get stuff for the Globus Transfer service
    globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']
    # the refresh token and access token, often abbr. as RT and AT
    transfer_rt = globus_transfer_data['refresh_token']
    transfer_at = globus_transfer_data['access_token']
    expires_at_s = globus_transfer_data['expires_at_seconds']

    globus_token_life = expires_at_s - time.time()
    log.warning("Globus access token will expire in %2.2f hours", (globus_token_life/3600))
    globus_app_id = globus_app_uuid
    client = globus_sdk.NativeAppAuthClient(globus_app_id)
    client.oauth2_start_flow(refresh_tokens=True)
    # Now we've got the data we need, but what do we do?
    # That "GlobusAuthorizer" from before is about to come to the rescue
    authorizer = globus_sdk.RefreshTokenAuthorizer(transfer_rt, client, access_token=transfer_at, expires_at=expires_at_s)
    # and try using `tc` to make TransferClient calls. Everything should just
    # work -- for days and days, months and months, even years
    ac = globus_sdk.AuthClient(authorizer=authorizer)
    tc = globus_sdk.TransferClient(authorizer=authorizer)

    return ac, tc


def main():

    # this is just to print nice logger messages
    log.setup_custom_logger()

    # Create a client or "app" definition registered with Globus and get its uuid 
    # see https://globus-sdk-python.readthedocs.io/en/stable/tutorial.html#tutorial-step1
    globus_app_uuid = '2f1fd715-ee09-43f9-9b48-1f06810bcc70'
    # Set the Globus server UUID. To find the UUID of alcf#dtn_eagle go to Globus and open
    # the server overview page at https://app.globus.org/file-manager/collections/05d2c76a-e867-4f67-aa57-76edeb0beda0/overview
    # The UUID of alcf#dtn_eagle is 05d2c76a-e867-4f67-aa57-76edeb0beda0
    alcf_eagle_globus_server_uuid = '05d2c76a-e867-4f67-aa57-76edeb0beda0'
    # Create a client
    ac, tc = create_clients(globus_app_uuid)
    # Ask the Globus server to show all end points it has access to
    show_endpoints(tc)
    # Select one end points e.g. 2-BM tomography data = [635c3ecb-f073-42ef-8278-471ed99bfd6e]
    ep_uuid = '635c3ecb-f073-42ef-8278-471ed99bfd6e'
    # create a new directory on the selected end point
    directory = "test"
    create_dir(directory, ep_uuid, tc)
    # share the directory with the Globus user associated to an email address
    share_dir("decarlof@gmail.com", directory, ep_uuid, ac, tc)


if __name__ == '__main__':
    main()