from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

def authenticate_drive() -> GoogleDrive:
    gauth = GoogleAuth()

    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()  # Will prompt in browser on first run
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("mycreds.txt")
    return GoogleDrive(gauth)

def upload_to_drive(content, filename: str = "file.txt", binary: bool = True) -> str:
    try:
        drive = authenticate_drive()
        file = drive.CreateFile({'title': filename})
        if binary:
            file.SetContentString(content.decode("utf-8", errors="ignore")) if isinstance(content, bytes) else file.SetContentString(content)
        else:
            file.SetContentBinary(content)
        file.Upload()
        file.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })
        return f"https://drive.google.com/file/d/{file['id']}/view"
    except Exception as e:
        print(f"Drive upload failed: {e}")
        return "ERROR"
