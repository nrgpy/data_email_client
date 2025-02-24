from pydantic import BaseModel


class EmailSettings(BaseModel):
    server: str | None = None
    username: str | None = None
    password: str | None = None
    search_term: str | None = None
    download_folder_path: str | None = None
    mail_folder: str | None = None
    file_ext: str | None = None
    is_delete_enabled: bool | None = None
