import email
import imaplib
import os
import sys

class mailer(object):
    """ imap client for mail servers
    
    optionally create a danger.py file containing definitions for username and password
    
    Parameters
    ----------
    server : str
        imap server name or ip address
    username : str
        email address of client
    password : str
    
    Returns
    -------
    obj
        object for handling emails
    
    Examples
    --------
    connect to email account
    >>> server = 'outlook.office365.com' # for gmail use 'imap.gmail.com'
    >>> username = 'the-big-data-catcher@mycompany.com'
    >>> password = '1234567890'
    >>> imap = mailer(server=server, username=username, password=password)

    """
    
    def __init__(self, server='', username='', password=''):
        self.server = server
        self.username = username
        self.password = password
    
        if self.username == '' and self.password == '':

            try:
                from danger import username, password
                self.username = username
                self.password = password
            except:
                self.username = getpass.getuser()
                self.password = getpass.getpass()
                
        self.connect()
        
                
    def connect(self):
        self.imap4 = imaplib.IMAP4_SSL(self.server)
        self.imap4.login(self.username, self.password)
        self.imap4.select()
        
        
    def disconnect(self):
        self.imap4.logout()
    
    
    def list_mailboxes(self):
        """ return a list of all mailboxes in the account
        
        new object is self.mailboxes
        """
        self.result, self.b_mailboxes = self.imap4.list()
        self.mailboxes = []
        
        for f in self.b_mailboxes:
            try:
                self.mailboxes.append(f.decode().split(' "/" ')[1])
            except:
                pass
        
        
    def search_for_messages(self, text="", area='', folder='', echo=True):
        """ find messages that match text
        
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
        
        self.results = []
        
        search_term = f'({area} "{text}")'
        
        if folder:
            folder = [folder]
        else:
            self.list_mailboxes()
            folder = self.mailboxes
        
        if echo: print(f"Searching {len(folder)} folders for {text}\n")
        
        for i, f in enumerate(folder):
            if echo: sys.stdout.write("\r")
            if echo: sys.stdout.write(f"{i+1} SEARCHING ... {f}                                   ")
            
            self.imap4.select(f)
            
            typ, msg = self.imap4.search(None, search_term)
            
            if msg[0]:
                self.results.append([f, msg[0].split()])

                
            sys.stdout.flush()
            
            
    def download_attachments(self, out_dir='', delete=False, archive_folder=''):
        """ download email attachments to folder and optionally archive/delete emails
        
        Parameters
        ----------
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
        if out_dir: self.affirm_directory(out_dir)
        
        for i, result in enumerate(self.results):
            
            message_folder = self.results[i][0]
            msgs = self.results[i][1]
            
            for emailid in msgs:

                resp, data = self.imap4.fetch(emailid, "(RFC822)")
                email_body = data[0][1]
                
                m = email.message_from_bytes(email_body)

                if m.get_content_maintype() != 'multipart':
                    continue

                for part in m.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    filename = part.get_filename()
                    
                    if filename is not None:
                        save_path = os.path.join(out_dir, filename)
                        
                        if not os.path.isfile(save_path):
                            fp = open(save_path, 'wb')
                            fp.write(part.get_payload(decode=True))
                            fp.close()
                            
                if archive_folder: self.imap4.copy(emailid, archive_folder)
                    
                if delete: self.imap4.store(emailid, 'FLAGS', '\\Deleted')
            
        self.imap4.expunge()
            
            
    def affirm_directory(self, directory):
        """ ensure a directory exists """
        try:
            os.mkdir(directory)
        except:
            pass
                            
                            
