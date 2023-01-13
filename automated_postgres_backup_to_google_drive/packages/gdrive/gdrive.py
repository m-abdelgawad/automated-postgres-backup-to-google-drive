import io
import mimetypes
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import logging

# Import logger
log = logging.getLogger()


class GoogleDrive:
    """
    Integrate with Google Drive API version 3 and perform the following actions:
    > Download a file
    > Upload a file
    > Delete a file
    > Get a list of all available files and folders
    > Get the ID of a folder
    > Get the ID of a file
    """

    def __init__(self, key_file_location):
        """
        Initiate a new object

        :param key_file_location: The path of credentials' key file.
        """

        credentials = service_account.Credentials.from_service_account_file(
            key_file_location)

        scoped_credentials = credentials.with_scopes([
            'https://www.googleapis.com/auth/drive'
        ])

        # Build the service object.
        self.service = build('drive', 'v3', credentials=scoped_credentials)

    def get_list_items(self):
        """
        Get a list of all available files and folders in the drive

        :return: a list of all available files and folders
        """

        # Call the Drive v3 API
        results = self.service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        return items

    @staticmethod
    def print_items(items_list):
        """
        Print the files/folders along with their IDs.

        :param items_list: The list of the files and folders
        :return: None
        """

        if not items_list:
            print('No files found.')
            return
        print('Files:')
        for item in items_list:
            print(u'{0} ({1})'.format(item['name'], item['id']))

    def get_folder_id(self, folder_name):
        """
        Get the ID of a folder

        :param folder_name: The name of the folder that you want its ID.
        :return: A string of the folder ID.
        """

        results = self.service.files().list(
            q=f"mimeType='application/vnd.google-apps.folder' and name = '{folder_name}'",
            pageSize=10, fields="nextPageToken, files(id, name)").execute()

        if results['files']:
            return results['files'][0]['id']
        else:
            return None

    def get_file_id(self, file_name):
        """
        Get the ID of a file

        :param file_name: The name of the folder that you want its ID.
        :return: A string of the file ID.
        """

        results = self.service.files().list(
            q=f"name = '{file_name}'",
            pageSize=10,
            fields="nextPageToken, files(id, name)").execute()

        if results['files']:
            return results['files'][0]['id']
        else:
            return None

    def download_file(self, file_name, output_folder_path):
        """
        Download a file from the drive

        :param file_name: The name of the file to be downloaded.
        :param output_file_path: The complete path to write the file.
        :return: None
        """

        output_file_path = os.path.join(output_folder_path, file_name)

        # Get the ID of the file
        file_id = self.get_file_id(file_name=file_name)

        # Set the request to download the file
        request = self.service.files().get_media(fileId=file_id)

        # The path of the output file
        fh = io.FileIO(output_file_path, 'w')

        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

    def upload_file(self, file_name, folder_path, remote_folder_name):
        """
        Upload a file to the drive.

        :param file_name: The file name to be uploaded.
        :param folder_path: The path of the folder that contains the file.
        :param remote_folder_name: The name of the remote folder.
        :return: None
        """

        # Set the full path to the file
        file_path = os.path.join(folder_path, file_name)
        mime_type = mimetypes.guess_type(file_path)

        # Get the id of the folder
        folder_id = self.get_folder_id(folder_name=remote_folder_name)

        file_metadata = {'name': file_name}

        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path, mimetype=mime_type[0])

        self.service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()

        print(
            "The file {0} was uploaded successfully to the folder {1}. ".format(
                file_name, remote_folder_name
            )
        )

    def delete_file(self, file_name):
        """
        Delete a file from the drive

        :param file_name: The name of the file to be deleted
        :return: None
        """
        # Get the ID of the file
        file_id = self.get_file_id(file_name=file_name)

        if file_id:
            # Delete the file
            self.service.files().delete(fileId=file_id).execute()
            print("The file {0} was deleted successfully.".format(file_name))
        else:
            print("The file {0} wasn't found in drive.".format(file_name))
