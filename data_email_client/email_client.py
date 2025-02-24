from typing import Tuple
from data_email_client.common.log import log
import email
import getpass
import imaplib
import os
import sys


class Mailer:
    """IMAP client for mail servers

    optionally create a credentials.py file containing definitions for username and password

    Parameters
    ----------
    server : str
        imap server name or ip address
    username : str
        email address of client
    password : str
    port : int
        (993) port to connect to imap server

    Examples
    --------
    connect to email account
    >>> server = 'imap.myemail.com'
    >>> username = 'the-big-data-catcher@myemail.com'
    >>> password = '1234567890'
    >>> imap = Mailer(server=server, username=username, password=password)
    >>> imap.connect()
    >>> imap.list_mailboxes()
    >>> imap.search_for_messages(text='data', area='SUBJECT', folder="INBOX")
    >>> imap.download_attachments(out_dir='data_files/', delete=True, archive_folder="INBOX")

    """

    def __init__(
        self,
        server: str = "",
        username: str = "",
        password: str = "",
        gui: bool = False,
        port: int = 993,
    ):
        self.server = server
        self.username = username
        self.password = password
        self.gui = gui
        self.port = port

        if not self.username and not self.password and not self.server and not self.gui:

            try:
                from credentials import USERNAME, PASSWORD, IMAP_SERVER  # type: ignore

                self.username = USERNAME
                self.password = PASSWORD
                self.server = IMAP_SERVER
            except ImportError:
                self.username = getpass.getuser()
                self.password = getpass.getpass()

            self.connect()
            self.list_mailboxes()

    def connect(self, timeout_seconds: int = 10) -> None:
        try:
            self.imap4 = imaplib.IMAP4_SSL(
                host=self.server,
                port=self.port,
                timeout=timeout_seconds,
            )
            self.imap4.login(self.username, self.password)
            self.imap4.select()
        except TimeoutError:
            log.error(
                f"connection to {self.server} timed out after {timeout_seconds} seconds"
            )
        except Exception as e:
            if "authenticationfailed" in str(e).lower():
                log.error(f"authentication failed for {self.username}")
            else:
                log.exception(f"connection failed to {self.server}")

    def disconnect(self) -> None:
        self.imap4.logout()

    def list_mailboxes(self) -> None:
        """return a list of all mailboxes in the account

        new object is self.mailboxes
        """
        self.result, self.b_mailboxes = self.imap4.list()
        self.mailboxes = []

        for f in self.b_mailboxes:
            try:
                self.mailboxes.append(f.decode().split(' "/" ')[1])
            except Exception:
                pass

    def search_for_messages(
        self, text: str = "", area: str = "", folder: str = "", echo: bool = True
    ) -> None:
        """find messages that match text

        Parameters
        ----------
        text : str
            text to search for
        area : str
            part of message to search. options are SUBJECT, FROM, TO, BODY
        folder : str
            folder to search. if not given, searches the whole inbox.
        echo : bool
            (True) show results as searching through folders

        Returns
        -------
        None
            this creates and populates the self.results list of [folder, [messages-as-list]]

        Examples
        --------
        >>> username = 'me@mymail.mo'
        >>> password = '1234567890'
        >>> server = 'imap.mymail.mo'
        >>> imap = mailer(username=username, password=password, server=server)
        >>> imap.list_mailboxes()
        >>> imap.search_for_messages(text='data', area='SUBJECT', folder=imap.mailboxes[0])
        """

        self.echo = echo
        self.results = []

        search_term = f'({area} "{text}")'

        if folder and isinstance(folder, str):
            folder = [folder]
        else:
            self.list_mailboxes()
            folder = self.mailboxes

        if echo:
            log.info(f"Searching {len(folder)} folders for {text}\n")

        for i, f in enumerate(folder):
            if echo:
                sys.stdout.write("\r")
            if echo:
                sys.stdout.write(
                    f"{i+1} SEARCHING ... {f}                                   "
                )

            self.imap4.select(f)
            typ, msg = self.imap4.search(None, search_term)
            if msg[0]:
                self.results.append([f, msg[0].split()])
            sys.stdout.flush()

    def download_attachments(
        self,
        extension: Tuple[str, str] = ("rld", "rwd"),
        out_dir: str = "",
        delete: bool = False,
        archive_folder: str = "",
    ) -> None:
        """download email attachments to folder and optionally archive/delete emails

        requires that the search_for_messages function be called first, and uses the self.results message list as a queue.

        Parameters
        ----------
        extension : str
            ('rld','rwd') filter for attachments; other messages will be passed over.
            if set to '', all attachments in the self.results list will be saved.
        out_dir : str
            path to store downloaded attachments at
        delete : bool
            (False) delete messages
        archive_folder : str
            (optional) folder to move files to (must be existing)

        Examples
        --------
        >>> imap.download_attachments(out_dir='data_files/', delete=True, archive_folder=imap.mailboxes[13])

        """

        cnt = 0

        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        for i, _ in enumerate(self.results):
            msgs = self.results[i][1]
            for emailid in msgs:
                cnt = self._process_email(
                    emailid, extension, out_dir, delete, archive_folder, cnt
                )

        if self.echo:
            sys.stdout.write("\r")
            sys.stdout.write(
                f"downloaded {cnt} attachments to {out_dir}                                "
            )

        self.imap4.expunge()

    def _process_email(
        self,
        emailid: str,
        extension: Tuple[str, str],
        out_dir: str,
        delete: bool,
        archive_folder: str,
        cnt: int,
    ) -> int:
        _, data = self.imap4.fetch(emailid, "(RFC822)")
        email_body = data[0][1]
        m = email.message_from_bytes(email_body)

        if m.get_content_maintype() != "multipart":
            return cnt

        for part in m.walk():
            cnt = self._process_part(part, extension, out_dir, cnt)

        if self._should_process(part, extension):
            if archive_folder:
                self.imap4.copy(emailid, archive_folder)
            if delete:
                self.imap4.store(emailid, "FLAGS", "\\Deleted")

        return cnt

    def _process_part(
        self,
        part: object,  # email.message.Message,
        extension: Tuple[str, str],
        out_dir: str,
        cnt: int,
    ) -> int:
        if part.get_content_maintype() == "multipart":
            return cnt
        if part.get("Content-Disposition") is None:
            return cnt

        filename = part.get_filename()

        if self.echo:
            sys.stdout.write("\r")
            sys.stdout.write(
                f"{cnt} ... checking attachment ... {filename}                               "
            )

        if (filename is not None) and (filename.lower().endswith(extension)):
            cnt += 1
            self._download_attachment(part, filename, out_dir, cnt)

        return cnt

    def _download_attachment(
        self,
        part: object,  # email.message.Message,
        filename: str,
        out_dir: str,
        cnt: int,
    ) -> None:
        if self.echo:
            sys.stdout.write("\r")
            sys.stdout.write(
                f"{cnt} ... downloading ... {filename}                               "
            )

        save_path = os.path.join(out_dir, filename)

        if not os.path.isfile(save_path):
            with open(save_path, "wb") as fp:
                fp.write(part.get_payload(decode=True))

        if self.echo:
            sys.stdout.write("\r")
            sys.stdout.write(
                f"{cnt} ... downloading ... {filename}                     [OK]      "
            )

    def _should_process(
        self, part: object, extension: Tuple[str, str]  # email.message.Message,
    ) -> bool:
        filename = part.get_filename()
        return (filename is not None) and (filename.lower().endswith(extension))
