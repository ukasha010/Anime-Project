from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
# Function to authenticate and get a Google Drive service instance
def get_google_drive_service():
    credentials = service_account.Credentials.from_service_account_file(
        'E:\\programming\\Django\\anime_project\\anime-397811-7a713f44ac67.json',
        scopes = ['https://www.googleapis.com/auth/drive'])
    return build('drive', 'v3', credentials=credentials)

def upload_file_to_google_drive(uploaded_file, file_name, project_folder_id):
    drive_service = get_google_drive_service()
    
    file_metadata = {
        'name': file_name,
        'parents': [project_folder_id],  # Associate the file with the project folder
    }

    # Read the content of the TemporaryUploadedFile
    file_content = uploaded_file.read()

    # Create a BytesIO object and write the file content to it
    file_stream = BytesIO()
    file_stream.write(file_content)
    file_stream.seek(0)

    media = MediaIoBaseUpload(file_stream, mimetype='application/octet-stream', resumable=True)

    uploaded_drive_file = drive_service.files().create(
        body=file_metadata,
        media_body=media
    ).execute()

    # Share the file with anyone with the link (public access)
    drive_service.permissions().create(
        fileId=uploaded_drive_file['id'],
        body={
            'type': 'anyone',
            'role': 'reader',
        }
    ).execute()

    return uploaded_drive_file['id']



# Retrieve a file from Google Drive by specifying file_name
def retrieve_file_from_google_drive_by_name(user_name, project_name, file_name):
    drive_service = get_google_drive_service()
    try:
        # Get the user folder ID based on the user_name
        user_folder_id = get_folder_id_by_name(user_name)

        if user_folder_id:
            # Get the project folder ID based on the project_name within the user's folder
            project_folder_id = get_folder_id_by_name(project_name)

            if project_folder_id:
                # Query to retrieve the file by name within the project folder and get its webContentLink
                results = drive_service.files().list(
                    q=f"name = '{file_name}' and '{project_folder_id}' in parents and trashed=false",
                    fields="files(id, webContentLink)").execute()

                files = results.get('files', [])
                if not files:
                    return None  # File not found
                else:
                    return files[0]['webContentLink']
        
        # If user or project folder doesn't exist, or the file is not found, return None
        return None
    except Exception as e:
        print(f"An error occurred while retrieving the file '{file_name}' in project '{project_name}' for user '{user_name}': {e}")
        return None

def get_file_id_by_name(user_name, project_name, file_name):
    drive_service = get_google_drive_service()
    
    # Get the user folder ID based on the user_name
    user_folder_id = get_folder_id_by_name(drive_service, user_name)

    if user_folder_id:
        # Get the project folder ID based on the project_name within the user's folder
        project_folder_id = get_folder_id_by_name(drive_service, project_name, parent_folder_id=user_folder_id)

        if project_folder_id:
            # Query to search for the file by name within the project folder
            results = drive_service.files().list(
                q=f"name = '{file_name}' and '{project_folder_id}' in parents and trashed=false",
                fields="files(id)").execute()
            
            files = results.get('files', [])
            
            if not files:
                return None  # File not found
            else:
                return files[0]['id']
    
    # If user, project folder, or file is not found, return None
    return None
            
            
def delete_file_from_google_drive(user_name, project_name, file_id):
    drive_service = get_google_drive_service()

    # Get the user folder ID based on the user_name
    user_folder_id = get_folder_id_by_name(user_name)

    if user_folder_id:
        # Get the project folder ID based on the project_name within the user's folder
        project_folder_id = get_folder_id_by_name(project_name, parent_folder_id=user_folder_id)

        if project_folder_id:
            try:
                drive_service.files().delete(fileId=file_id).execute()
                print(f"File with ID {file_id} has been deleted from project '{project_name}' for user '{user_name}'.")
            except Exception as e:
                print(f"An error occurred while deleting the file with ID {file_id} from project '{project_name}' for user '{user_name}': {e}")
    else:
        print(f"User folder for user '{user_name}' not found.")
        
        
def get_file_name_by_id(user_name, project_name, file_id):
    drive_service = get_google_drive_service()
    
    # Get the user folder ID based on the user_name
    user_folder_id = get_folder_id_by_name(drive_service, user_name)

    if user_folder_id:
        # Get the project folder ID based on the project_name within the user's folder
        project_folder_id = get_folder_id_by_name(drive_service, project_name, parent_folder_id=user_folder_id)

        if project_folder_id:
            try:
                # Query to retrieve the file by file_id and get its name
                results = drive_service.files().get(fileId=file_id, fields="name").execute()
                return results.get('name')
            except Exception as e:
                print(f"An error occurred while getting the file name for ID {file_id}: {e}")
                return None
    return None
    
def create_folder(parent_folder_id, folder_name):
    drive_service = get_google_drive_service()
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_folder_id],
    }

    folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')

def get_user_folder_id(user_id):
    # Check if the user folder already exists
    user_folder_id = get_folder_id_by_name(user_id)

    if not user_folder_id:
        # User folder doesn't exist, create it
        user_folder_id = create_folder(None, user_id)  # No parent folder, create at root

    return user_folder_id

def get_folder_id_by_name(folder_name):
    drive_service = get_google_drive_service()
    try:
        # Query to search for the folder by name
        results = drive_service.files().list(
            q=f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed=false",
            fields="files(id)").execute()

        files = results.get('files', [])

        if not files:
            return None  # Folder not found
        else:
            return files[0]['id']
    except Exception as e:
        print(f"An error occurred while getting the folder ID for name '{folder_name}': {e}")
        return None
def list_all_files_in_google_drive():
    drive_service = get_google_drive_service()
    results = drive_service.files().list(
        fields="files(id, name)",
        pageSize=1000  # Adjust as needed to retrieve all files
    ).execute()
    files = results.get('files', [])
    return files
def delete_all_files_from_google_drive():
    drive_service = get_google_drive_service()

    # Retrieve a list of all files in Google Drive
    files = list_all_files_in_google_drive()

    if not files:
        print("No files found in Google Drive.")
        return

    # Iterate through the list of files and delete each one
    for file in files:
        file_id = file['id']
        try:
            drive_service.files().delete(fileId=file_id).execute()
            print(f"File with ID {file_id} has been deleted.")
        except Exception as e:
            print(f"An error occurred while deleting the file with ID {file_id}: {e}")

# Call the function to delete all files from Google Drive

