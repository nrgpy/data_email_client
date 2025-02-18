from data_email_client.email_client import Mailer
from data_email_client.common.log import log
from data_email_client.common.models import EmailSettings
from data_email_client.common.utils import store_settings, load_settings
import sys
from tkinter import (
    BooleanVar,
    E,
    END,
    PhotoImage,
    StringVar,
    ttk,
    Tk,
    W,
)


title = "nrgpy | Data Email Client"


class ImapAuto:

    class IORedirector:
        """A general class for redirecting I/O to this Text widget."""

        def __init__(self, text_area: str):
            self.text_area = text_area

    class StdoutRedirector(IORedirector):
        """A class for redirecting stdout to this Text widget."""

        def write(self, string: str) -> None:
            self.text_area.set(string[:75])

        def flush(self) -> None:
            pass

    def __init__(self, first: bool = True, *args, **kwargs):

        self.root = Tk()
        self.root.title(title)
        self.root.wm_title(title)

        self.root.columnconfigure(0, minsize=100, pad=10, weight=1)
        self.root.columnconfigure(1, minsize=100, pad=10, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.icon = PhotoImage(file="data_email_client/nrg.png")
        self.root.iconphoto(False, self.icon)

        self.server_var = StringVar()
        self.server_entry = ttk.Entry(self.root, width=45, textvariable=self.server_var)
        self.server_entry.grid(column=2, row=1, sticky=(W, E))

        self.username_var = StringVar()
        self.username_entry = ttk.Entry(
            self.root, width=25, textvariable=self.username_var
        )
        self.username_entry.grid(column=2, row=2, sticky=(W, E))

        self.password_var = StringVar()
        self.password_entry = ttk.Entry(
            self.root, width=25, textvariable=self.password_var
        )
        self.password_entry.grid(column=2, row=3, sticky=(W, E))
        self.password_entry.config(show="*")

        self.search_term_var = StringVar()
        self.search_term_entry = ttk.Entry(
            self.root, width=25, textvariable=self.search_term_var
        )
        self.search_term_entry.grid(column=2, row=4, pady=20, sticky=(W, E))

        self.mail_folder_var = StringVar()
        self.mail_folder_entry = ttk.Entry(
            self.root, width=25, textvariable=self.mail_folder_var
        )
        self.mail_folder_entry.grid(column=2, row=5, pady=20, sticky=(W, E))

        self.file_ext_var = StringVar()
        self.file_ext_entry = ttk.Entry(
            self.root, width=25, textvariable=self.file_ext_var
        )
        self.file_ext_entry.grid(column=2, row=6, pady=20, sticky=(W, E))

        self.download_folder_var = StringVar()
        self.download_folder_entry = ttk.Entry(
            self.root, width=25, textvariable=self.download_folder_var
        )
        self.download_folder_entry.grid(column=2, row=7, pady=20, sticky=(W, E))

        self.delete_check_var = BooleanVar()
        self.delete_check = ttk.Checkbutton(
            self.root, text="Delete emails", variable=self.delete_check_var
        )
        self.delete_check.grid(column=2, row=8, pady=20, sticky=(W, E))

        self.store_password_var = BooleanVar()
        self.store_password = ttk.Checkbutton(
            self.root, text="Store password?", variable=self.store_password_var
        )
        self.store_password.grid(column=3, row=12, pady=20, sticky=(W, E))

        self.mailboxes = StringVar()

        sys.stdout = self.StdoutRedirector(self.mailboxes)

        # load settings from file if it exists
        self.populate_from_saved_settings()

        ttk.Button(self.root, text="Connect", command=lambda: self.connect()).grid(
            column=1, row=9, sticky=W
        )
        ttk.Button(
            self.root, text="Disconnect", command=lambda: self.disconnect()
        ).grid(column=2, row=9, sticky=W)
        ttk.Button(
            self.root,
            text="Download attachments",
            command=lambda: self.download_attachments(),
        ).grid(column=1, row=10, sticky=W)
        # ttk.Button(
        #     self.root, text="Load settings", command=lambda: self.load_settings()
        # ).grid(column=1, row=12, sticky=W
        ttk.Button(
            self.root, text="Save settings", command=lambda: self.save_settings()
        ).grid(column=1, row=12, sticky=W)

        ttk.Label(self.root, text="server address").grid(column=1, row=1, sticky=W)
        ttk.Label(self.root, text="username").grid(column=1, row=2, sticky=W)
        ttk.Label(self.root, text="password").grid(column=1, row=3, sticky=W)
        ttk.Label(self.root, text="search text").grid(column=1, row=4, sticky=W)
        ttk.Label(self.root, text="mail folder").grid(column=1, row=5, sticky=W)
        ttk.Label(self.root, text="file extension").grid(column=1, row=6, sticky=W)
        ttk.Label(self.root, text="download folder").grid(column=1, row=7, sticky=W)
        self.status = ttk.Label(self.root, textvariable=self.mailboxes)
        self.status.grid(column=1, columnspan=3, row=13, sticky=W)

        for child in self.root.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.server_entry.focus()
        self.root.mainloop()

    def connect(self) -> None:

        try:
            self.imap = Mailer(
                server=self.server_entry.get(),
                username=self.username_entry.get(),
                password=self.password_entry.get(),
                gui=True,
            )
            self.imap.connect()
            self.imap.list_mailboxes()
            log.info("mailboxes: {}".format("\n".join(self.imap.mailboxes)))
            print(self.imap.mailboxes)
            log.info(f"connected to {self.server_entry.get()}")

        except Exception as e:
            log.error("login failed")
            log.debug(e)

    def disconnect(self) -> None:
        self.imap.disconnect()
        log.info(f"disconnected from {self.server_entry.get()}")

    def download_attachments(self) -> None:

        if self.delete_check.instate(["selected"]):
            log.debug("delete email option selected")
            delete = True
        else:
            delete = False

        log.info(f"searching for messages in {self.mail_folder_entry.get()}")
        self.imap.search_for_messages(
            text=self.search_term_entry.get(),
            area="body",
            folder=self.mail_folder_entry.get(),
        )
        log.info(f"found {len(self.imap.results)} messages")
        print(self.imap.results)

        log.info(f"downloading attachments from {self.server_entry.get()}")

        self.imap.download_attachments(
            out_dir=self.download_folder_entry.get(),
            extension=self.file_ext_entry.get(),
            delete=delete,
        )

    def populate_from_saved_settings(self) -> None:
        """Open a file for editing."""

        try:
            email_settings = load_settings()

            self.server_entry.delete(0, END)
            self.server_entry.insert(0, email_settings.server)

            self.username_entry.delete(0, END)
            self.username_entry.insert(0, email_settings.username)

            self.password_entry.delete(0, END)
            self.password_entry.insert(0, email_settings.password)

            self.search_term_entry.delete(0, END)
            self.search_term_entry.insert(0, email_settings.search_term)

            self.download_folder_entry.delete(0, END)
            self.download_folder_entry.insert(0, email_settings.download_folder_path)

            self.mail_folder_entry.delete(0, END)
            self.mail_folder_entry.insert(0, email_settings.mail_folder)

            self.file_ext_entry.delete(0, END)
            self.file_ext_entry.insert(0, email_settings.file_ext)

            self.delete_check_var.set(False)

            if email_settings.is_delete_enabled:
                self.delete_check.state(["selected"])
            else:
                self.delete_check.state(["!selected"])

            log.info("loaded saved settings")

        except Exception:

            log.exception("failed to load settings")

    def save_settings(self) -> None:
        """Save the current file as a new file."""
        email_settings = EmailSettings(
            server=self.server_entry.get(),
            username=self.username_entry.get(),
            password="",
            search_term=self.search_term_entry.get(),
            download_folder_path=self.download_folder_entry.get(),
            mail_folder=self.mail_folder_entry.get(),
            file_ext=self.file_ext_entry.get(),
            is_delete_enabled=self.delete_check_var.get(),
        )

        if self.store_password_var.get():
            email_settings.password = self.password_entry.get()

        store_settings(email_settings, self.store_password_var)

        log.info("saved settings")


if __name__ == "__main__":
    app = ImapAuto()
