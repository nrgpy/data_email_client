from data_email_client import mailer
from data_email_client.log import log
import pickle
import sys


try:
    from tkinter import *
    from tkinter import ttk
    from tkinter.filedialog import askopenfilename, asksaveasfilename

except ModuleNotFoundError as e:
    print(e)
    print(
        "tkinter not installed.\n\ncheck here: https://duckduckgo.com/?t=canonical&q=install+tkinter&ia=web\n"
    )
    log.error(
        "tkinter not installed.\n\ncheck here: https://duckduckgo.com/?t=canonical&q=install+tkinter&ia=web\n"
    )

    raise ModuleNotFoundError

title = "nrgpy | Data Email Client"
config_file = ".data_mail_client.conf"


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

    def __init__(self, first: bool=True, *args, **kwargs):

        self.root = Tk()
        self.root.title(title)
        self.root.wm_title(title)

        self.root.columnconfigure(0, minsize=100, pad=10, weight=1)
        self.root.columnconfigure(1, minsize=100, pad=10, weight=1)
        self.root.rowconfigure(0, weight=1)

        # myImage = PhotoImage(file='data_email_client/nrg.png')

        self.server = StringVar()
        self.server_entry = ttk.Entry(self.root, width=45, textvariable=self.server)
        self.server_entry.grid(column=2, row=1, sticky=(W, E))

        self.username = StringVar()
        self.username_entry = ttk.Entry(self.root, width=25, textvariable=self.username)
        self.username_entry.grid(column=2, row=2, sticky=(W, E))

        self.password = StringVar()
        self.password_entry = ttk.Entry(self.root, width=25, textvariable=self.password)
        self.password_entry.grid(column=2, row=3, sticky=(W, E))
        self.password_entry.config(show="*")

        self.search_term = StringVar()
        self.search_term_entry = ttk.Entry(
            self.root, width=25, textvariable=self.search_term
        )
        self.search_term_entry.grid(column=2, row=4, pady=20, sticky=(W, E))

        self.mail_folder_term = StringVar()
        self.mail_folder_entry = ttk.Entry(
            self.root, width=25, textvariable=self.mail_folder_term
        )
        self.mail_folder_entry.grid(column=2, row=5, pady=20, sticky=(W, E))

        self.ext_term = StringVar()
        self.ext_entry = ttk.Entry(self.root, width=25, textvariable=self.ext_term)
        self.ext_entry.grid(column=2, row=6, pady=20, sticky=(W, E))

        self.download_folder_term = StringVar()
        self.download_folder_entry = ttk.Entry(
            self.root, width=25, textvariable=self.download_folder_term
        )
        self.download_folder_entry.grid(column=2, row=7, pady=20, sticky=(W, E))

        self.delete_term = IntVar()
        self.delete_check = ttk.Checkbutton(
            self.root, text="Delete emails", variable=self.delete_term
        )
        self.delete_check.grid(column=2, row=8, pady=20, sticky=(W, E))

        self.store_password = IntVar()
        self.password_check = ttk.Checkbutton(
            self.root, text="Store password?", variable=self.store_password
        )
        self.password_check.grid(column=3, row=12, pady=20, sticky=(W, E))

        self.mailboxes = StringVar()

        sys.stdout = self.StdoutRedirector(self.mailboxes)

        # try:
        #     # self.imap

        #     # self.console = ttk.Label(self.root, height=50, width=100)
        #     # self.console.grid(column=[2, 3], row=11)

        #     print("trying to write mailboxes...")
        #     _mailboxes = "\n".join(self.imap.mailboxes)
        #     self.mailboxes.set(_mailboxes)

        #         # for m in self.imap.mailboxes:
        #         #     self.console.(END, f"{m}\n")

        # except:
        #     import traceback
        #     print(traceback.format_exc())
        #     pass

        #     self.mailboxes.set("mailboxes...")

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
        ttk.Button(
            self.root, text="Load settings", command=lambda: self.load_settings()
        ).grid(column=1, row=12, sticky=W)
        ttk.Button(
            self.root, text="Save settings", command=lambda: self.save_settings()
        ).grid(column=2, row=12, sticky=W)

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
            self.imap = mailer(
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
            extension=self.ext_entry.get(),
            delete=delete,
            #         archive_folder='INBOX/Archive'
        )
        # sys.stdout = sys.__stdout__

    # def download_file(self):

    #     for i, result in enumerate(self.imap.results):

    #         message_folder = self.results[i][0]
    #         msgs = self.results[i][1]

    #         for emailid in msgs:

    #             resp, data = self.imap4.fetch(emailid, "(RFC822)")
    #             email_body = data[0][1]

    #             m = email.message_from_bytes(email_body)

    #             if m.get_content_maintype() != 'multipart':
    #                 continue

    #             for part in m.walk():
    #                 if part.get_content_maintype() == 'multipart':
    #                     continue
    #                 if part.get('Content-Disposition') is None:
    #                     continue

    #                 filename = part.get_filename()

    #                 if self.echo: sys.stdout.write('\r')
    #                 if self.echo: sys.stdout.write(f'{cnt} ... checking attachment ... {filename}                               ')

    #                 if (filename is not None) and (filename.lower().endswith(extension)):
    #                     cnt += 1
    #                     process = True

    #                     if self.echo: sys.stdout.write('\r')
    #                     if self.echo: sys.stdout.write(f'{cnt} ... downloading ... {filename}                               ')

    #                     save_path = os.path.join(out_dir, filename)

    #                     if not os.path.isfile(save_path):
    #                         fp = open(save_path, 'wb')
    #                         fp.write(part.get_payload(decode=True))
    #                         fp.close()

    #                     if self.echo: sys.stdout.write('\r')
    #                     if self.echo: sys.stdout.write(f'{cnt} ... downloading ... {filename}                     [OK]      ')

    #                 else:
    #                     process = False

    #             if process:

    #                 if archive_folder: self.imap4.copy(emailid, archive_folder)

    #                 if delete: self.imap4.store(emailid, 'FLAGS', '\\Deleted')

    #     if self.echo: sys.stdout.write('\r')
    #     if self.echo: sys.stdout.write(f'downloaded {cnt} attachments to {out_dir}                                ')

    #     self.imap4.expunge()

    def load_settings(self) -> None:
        """Open a file for editing."""

        try:
            with open(config_file, "rb") as f:
                file_dict = pickle.load(f)

            self.server_entry.delete(0, END)
            self.username_entry.delete(0, END)
            self.password_entry.delete(0, END)
            self.search_term_entry.delete(0, END)
            self.download_folder_entry.delete(0, END)
            self.mail_folder_entry.delete(0, END)
            self.ext_entry.delete(0, END)

            self.server_entry.insert(END, file_dict["server"])
            self.username_entry.insert(END, file_dict["username"])
            self.password_entry.insert(END, file_dict["password"])
            self.search_term_entry.insert(END, file_dict["search_term"])
            self.download_folder_entry.insert(END, file_dict["download_folder_term"])
            self.mail_folder_entry.insert(END, file_dict["mail_folder_term"])
            self.ext_entry.insert(END, file_dict["ext_term"])

            if file_dict["delete_term"]:
                self.delete_check.state(["selected"])
            else:
                self.delete_check.state(["!selected"])

            log.info(f"loaded settings from {config_file}")

        except Exception:

            log.exception()

    def save_settings(self) -> None:
        """Save the current file as a new file."""

        file_dict = {
            "server": self.server_entry.get(),
            "username": self.username_entry.get(),
            "password": "",
            "search_term": self.search_term_entry.get(),
            "download_folder_term": self.download_folder_entry.get(),
            "mail_folder_term": self.mail_folder_entry.get(),
            "ext_term": self.ext_entry.get(),
            "delete_term": self.delete_check.state(),
        }

        if self.store_password.get():
            file_dict["password"] = self.password_entry.get()

        with open(config_file, "wb") as f:
            pickle.dump(file_dict, f)

        log.info(f"saved settings to {config_file}")


if __name__ == "__main__":
    app = ImapAuto()
