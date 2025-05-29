import os
import uuid
import pathlib 
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

GOOGLE_TOKEN = os.path.join(str(pathlib.Path.home()), 'tokens', 'google_token.json')


class DriveSnippets(object):
    def __init__(self, service, credentials):
        self.service = service
        self.credentials = credentials

    def upload_file(self, drive_service, filepath, mimetype, drive_filename, parent_folder_id=None):
        file_metadata = {'name': drive_filename}
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]

        media = MediaFileUpload(filepath, mimetype=mimetype)
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print('File uploaded. File ID:', file.get('id'))
        
    def find_file_id(self, drive_service, filename, parent_folder_id=None):
        query = f"name='{filename}'"
        if parent_folder_id:
            query += f" and '{parent_folder_id}' in parents"
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            pageSize=1
        ).execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
        return None

    def upload_or_update_file(self, drive_service, filepath, mimetype, drive_filename, parent_folder_id=None):
        file_id = self.find_file_id(drive_service, drive_filename, parent_folder_id)
        media = MediaFileUpload(filepath, mimetype=mimetype)

        if file_id:
            print(f"File '{drive_filename}' exists (ID: {file_id}), updating...")
            updated_file = drive_service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            print('File updated:', updated_file.get('id'))
            return updated_file.get('id')
        else:
            print(f"File '{drive_filename}' does not exist, creating...")
            file_metadata = {'name': drive_filename}
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            created_file = drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print('File created:', created_file.get('id'))
            return created_file.get('id')


class SlidesSnippets(object):
    def __init__(self, service, credentials):
        self.service = service
        self.credentials = credentials

    def create_slide(self, presentation_id, page_id):
        slides_service = self.service
        # take the current number of slides
        presentation = slides_service.presentations().get(
            presentationId=presentation_id).execute()
        nslides = len(presentation.get('slides'))
        # insert a slide at the end
        requests = [
            {
                'createSlide': {
                    'objectId': page_id,
                    'insertionIndex': nslides,#-1tmp for Julie
                    'slideLayoutReference': {
                        'predefinedLayout': 'BLANK'
                    }
                }
            }
        ]
        # Execute the request.
        body = {
            'requests': requests
        }
        response = slides_service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()
        create_slide_response = response.get('replies')[0].get('createSlide')
        print('Created slide with ID: {0}'.format(
            create_slide_response.get('objectId')))
        return response
    
    def create_textbox_with_text(self, presentation_id, page_id, text, magnitude_width, magnitude_height, posx, posy, fontsize, fontcolor):
        slides_service = self.service
        # [START slides_create_textbox_with_text]
        # Create a new square textbox, using the supplied element ID.
        element_id = str(uuid.uuid4())
        requests = [
            {
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': page_id,
                        'size': {
                            'height': {'magnitude': magnitude_height, 'unit': 'PT'},
                            'width': {'magnitude': magnitude_width, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': posx,
                            'translateY': posy,
                            'unit': 'PT'
                        }
                    }
                }
            },

            # Insert text into the box, using the supplied element ID.
            {
                'insertText': {
                    'objectId': element_id,
                    'insertionIndex': 0,
                    'text': text
                }
            },
            
            {
                'updateTextStyle': {
                    'objectId': element_id,
                    'style': {
                        'fontFamily': 'Times New Roman',
                        'fontSize': {
                            'magnitude': fontsize,
                            'unit': 'PT'
                        },
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': {
                                    'blue': 0.0,
                                    'green': 0.0,
                                    'red': fontcolor
                                }
                            }
                        }                        
                    },
                    'fields': 'fontSize'
                }
            }            
        ]

        # Execute the request.
        body = {
            'requests': requests
        }
        response = slides_service.presentations() \
            .batchUpdate(presentationId=presentation_id, body=body).execute()
        create_shape_response = response.get('replies')[0].get('createShape')
        print('Created textbox with ID: {0}'.format(
            create_shape_response.get('objectId')))
        # [END slides_create_textbox_with_text]
        return response    

    def create_textbox_with_bullets(self, presentation_id, page_id, text, magnitude_width, magnitude_height, posx, posy, fontsize, fontcolor):
        slides_service = self.service
        # [START slides_create_textbox_with_text]
        # Create a new square textbox, using the supplied element ID.
        if text=="":
            return
        element_id = str(uuid.uuid4())
        requests = [
            {
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': page_id,
                        'size': {
                            'height': {'magnitude': magnitude_height, 'unit': 'PT'},
                            'width': {'magnitude': magnitude_width, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': posx,
                            'translateY': posy,
                            'unit': 'PT'
                        }
                    }
                }
            },

            # Insert text into the box, using the supplied element ID.
            {
                'insertText': {
                    'objectId': element_id,
                    'insertionIndex': 0,
                    'text': text
                }
            },
            
            {
                'updateTextStyle': {
                    'objectId': element_id,
                    'style': {
                        'fontFamily': 'Times New Roman',
                        'fontSize': {
                            'magnitude': fontsize,
                            'unit': 'PT'
                        },
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': {
                                    'blue': 0.0,
                                    'green': 0.0,
                                    'red': fontcolor
                                }
                            }
                        }
                    },
                    'fields': 'foregroundColor,fontSize'
                }
            },
            {
                'createParagraphBullets': {
                    'objectId': element_id,
                    'textRange': {
                        'type': 'ALL'
                    },
                    'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                }
            }
        ]

        # Execute the request.
        body = {
            'requests': requests
        }
        response = slides_service.presentations() \
            .batchUpdate(presentationId=presentation_id, body=body).execute()
        create_shape_response = response.get('replies')[0].get('createShape')
        print('Created textbox bullets with ID: {0}'.format(
            create_shape_response.get('objectId')))
        return response            
    
    def create_image(self, presentation_id, page_id, IMAGE_URL, magnitude_width, magnitude_height, posx, posy):
        slides_service = self.service
        # [START slides_create_image]
        # Create a new image, using the supplied object ID,
        # with content downloaded from IMAGE_URL.
        requests = []
        image_id = str(uuid.uuid4())
        requests.append({
            'createImage': {
                'objectId': image_id,
                'url': IMAGE_URL,
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': magnitude_height, 'unit': 'PT'},
                        'width': {'magnitude': magnitude_width, 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': posx,
                        'translateY': posy,
                        'unit': 'PT'
                    }
                }
            }
        })

        # Execute the request.
        body = {
            'requests': requests
        }
        response = slides_service.presentations() \
            .batchUpdate(presentationId=presentation_id, body=body).execute()
        create_image_response = response.get('replies')[0].get('createImage')
        print('Created image with ID: {0}'.format(
        create_image_response.get('objectId')))        
        return response

def google_drive(token_fname):
    print('Establishing connection to google drive')
    try:
        creds = service_account.Credentials.from_service_account_file(token_fname).with_scopes(['https://www.googleapis.com/auth/presentations']).with_scopes(['https://www.googleapis.com/auth/drive'])  # FULL DRIVE SCOPE
        drive = build('drive', 'v3', credentials=creds)
        snippets_drive = DriveSnippets(drive, creds)
        print('Connection to google drive: OK')
        return snippets_drive, drive
    except Exception as e:
        print('Failed to connect to Google Drive:', e)
        return None

def google_slide(token_fname):
    print('Establishing connection to google slide')
    try:
        creds = service_account.Credentials.from_service_account_file(token_fname).with_scopes(['https://www.googleapis.com/auth/presentations'])
        slides = build('slides', 'v1', credentials=creds)
        snippets_slide = SlidesSnippets(slides, creds)
        print('Connection to google slide: OK')
        return snippets_slide
    except FileNotFoundError:
        print('Google slide token file not found at %s' % token_fname)
        exit()

def init_slide(google, presentation_url, file_name):
    # create a slide and publish file name
    file_name = os.path.basename(file_name)
    try:
        presentation_id = presentation_url.split('/')[-2]
    except AttributeError:
        print("Set --presentation-url to point to a valid Google slide location")
        exit()
    # Create a new Google slide
    page_id = str(uuid.uuid4())
    google.create_slide(presentation_id, page_id)
    google.create_textbox_with_text(presentation_id, page_id, os.path.basename(file_name)[:-3], 400, 50, 0, 0, 13, 1)
    
    return presentation_id, page_id


def main():

    snippets_slide = google_slide(GOOGLE_TOKEN)

    presentation_url = 'https://docs.google.com/presentation/d/1gEtlkj5fYbQ5rJh1wgTmf6bh_FjqMP7aD5ZrF1_ZvTA/edit?usp=sharing'
    file_name = 'test.hdf'
    presentation_id, page_id = init_slide(snippets_slide, presentation_url, file_name)
    descr = "test text box with bullet"
    snippets_slide.create_textbox_with_bullets(presentation_id, page_id, descr, 240, 120, 0, 18, 8, 0)
    
    snippets_drive, drive_service = google_drive(GOOGLE_TOKEN)
    if snippets_drive:
        # Example: Upload image
        folder_id = '1aVGsEXgxM1IPO9ZdSGUl4jkl6yGB-llT'
        file_id = snippets_drive.upload_or_update_file(
            drive_service=drive_service,
            filepath='AD_02.png',
            # mimetype='text/plain',
            mimetype='image/png',
            drive_filename='uploaded_image.png',
            parent_folder_id=folder_id
        )
    
    image_url = f"https://drive.google.com/uc?export=view&id={file_id}"
    print("File URL:", image_url)
    snippets_slide.create_image(presentation_id, page_id, image_url, 300, 300, 0, 0)

if __name__ == '__main__':
    main()
