from data_email_client import mailer
import os
import pickle

from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename


title = "nrgpy | Data Email Client"
config_file = ".data_mail_client.conf"


class imap_auto():
    
    def __init__(self, first=True, *args, **kwargs):
        
#         Tk.__init__(self, *args, **kwargs)
        self.root = Tk()
        self.root.title(title)
#         root.withdraw()
        
#         self.mainframe = ttk.Frame(root, padding="20 20 20 20")
#         self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
#         self.title = title
        
        self.root.columnconfigure(0, minsize=100, pad=10, weight=1)
        self.root.columnconfigure(1, minsize=100, pad=10, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        try:
            if first:
                self.imap = False
                self.first = False
        except:
            pass
        
        myImage = PhotoImage(file='data_email_client/nrg.png')
            
        self.server = StringVar()
        self.server_entry = ttk.Entry(self.root, width=35, textvariable=self.server)
        self.server_entry.grid(column=2, row=1, sticky=(W, E))

        self.username = StringVar()
        self.username_entry = ttk.Entry(self.root, width=25, textvariable=self.username)
        self.username_entry.grid(column=2, row=2, sticky=(W, E))

        self.password = StringVar()
        self.password_entry = ttk.Entry(self.root, width=25, textvariable=self.password)
        self.password_entry.grid(column=2, row=3, sticky=(W, E))
        self.password_entry.config(show="*")

        self.search_term = StringVar()
        self.search_term_entry = ttk.Entry(self.root, width=25, textvariable=self.search_term)
        self.search_term_entry.grid(column=2, row=4, pady=20, sticky=(W, E))

        self.download_folder_term = StringVar()
        self.download_folder_entry = ttk.Entry(self.root, width=25, textvariable=self.download_folder_term)
        self.download_folder_entry.grid(column=2, row=5, pady=20, sticky=(W, E))

        self.mail_folder_term = StringVar()
        self.mail_folder_entry = ttk.Entry(self.root, width=25, textvariable=self.mail_folder_term)
        self.mail_folder_entry.grid(column=2, row=6, pady=20, sticky=(W, E))
        
        self.ext_term = StringVar()
        self.ext_entry = ttk.Entry(self.root, width=25, textvariable=self.ext_term)
        self.ext_entry.grid(column=2, row=7, pady=20, sticky=(W, E))
        
        self.delete_term = IntVar()
        self.delete_check = ttk.Checkbutton(self.root, text='Delete emails', variable=self.delete_term)
        self.delete_check.grid(column=2, row=8, pady=20, sticky=(W, E))

        self.store_password = IntVar()
        self.password_check = ttk.Checkbutton(self.root, text='Store password?', variable=self.store_password)
        self.password_check.grid(column=3, row=12, pady=20, sticky=(W, E))
        
        if self.imap:
            
            self.console = ttk.Text(root, height=50, width=100)
            self.console.grid(column=[2, 3], row=11)
            
            try:
                for m in self.imap.mailboxes:
                    self.console.insert(END, f"{m}\n")

            except:
                import traceback
                print(traceback.format_exc())
                pass
            

        ttk.Button(self.root, text="Connect", command=lambda: self.connect()).grid(column=1, row=9, sticky=W)
        ttk.Button(self.root, text="Disconnect", command=lambda: self.disconnect()).grid(column=2, row=9, sticky=W)
        ttk.Button(self.root, text="Download attachments", command=lambda: self.download_attachments()).grid(column=1, row=10, sticky=W)
        ttk.Button(self.root, text="Load settings", command=lambda: self.load_settings()).grid(column=1, row=12, sticky=W)
        ttk.Button(self.root, text="Save settings", command=lambda: self.save_settings()).grid(column=2, row=12, sticky=W)
        
        ttk.Label(self.root, text="server address").grid(column=1, row=1, sticky=W)
        ttk.Label(self.root, text="username").grid(column=1, row=2, sticky=W)
        ttk.Label(self.root, text="password").grid(column=1, row=3, sticky=W)
        ttk.Label(self.root, text="search text").grid(column=1, row=4, sticky=W)
        ttk.Label(self.root, text="download folder").grid(column=1, row=5, sticky=W)
        ttk.Label(self.root, text="mail folder").grid(column=1, row=6, sticky=W)
        ttk.Label(self.root, text="file extension").grid(column=1, row=7, sticky=W)

        # status
        self.status = ttk.Label(self.root, text='').grid(column=4, row=1)


        for child in self.root.winfo_children(): 
            child.grid_configure(padx=5, pady=5)

        self.server_entry.focus()        
        self.root.mainloop()

    def connect(self):

        self.imap = mailer(server=self.server_entry.get(), username=self.username_entry.get(), password=self.password_entry.get(), gui=True)
        self.imap.connect()
        self.imap.list_mailboxes()
        print(self.imap.mailboxes)
        self.status.text = self.imap.mailboxes

        
    def disconnect(self):
        self.imap.disconnect()
        
    def download_attachments(self):
        
        if self.delete_check.instate(['selected']):
            delete = True
        else:
            delete = False
        
        self.imap.search_for_messages(text= self.search_term_entry.get(), area='body', folder=self.mail_folder_entry.get())
        self.imap.download_attachments(
            out_dir=self.download_folder_entry.get(), 
            extension=self.ext_entry.get(), 
            delete=delete, 
    #         archive_folder='INBOX/Archive'
        )

    def load_settings(self):
        """Open a file for editing."""
        
        try:
            with open(config_file, 'rb') as f:
                file_dict = pickle.load(f)
            
            print(file_dict)
            
            self.server_entry.delete(0, END)
            self.username_entry.delete(0, END)
            self.password_entry.delete(0, END)
            self.search_term_entry.delete(0, END)
            self.download_folder_entry.delete(0, END)
            self.mail_folder_entry.delete(0, END)
            self.ext_entry.delete(0, END)

            self.server_entry.insert(END, file_dict['server'])
            self.username_entry.insert(END, file_dict['username'])
            self.password_entry.insert(END, file_dict['password'])
            self.search_term_entry.insert(END, file_dict['search_term'])
            self.download_folder_entry.insert(END, file_dict['download_folder_term'])
            self.mail_folder_entry.insert(END, file_dict['mail_folder_term'])
            self.ext_entry.insert(END, file_dict['ext_term'])
            
            if file_dict['delete_term']:
                self.delete_check.state(['selected'])
            else:
                self.delete_check.state(['!selected'])

        except:
            import traceback
            print("EXCEPTION!")
            print(traceback.format_exc())

        pass

    def save_settings(self):
        """Save the current file as a new file."""
        
        file_dict = {
            "server": self.server_entry.get(),
            "username": self.username_entry.get(),
            "password": "",
            "search_term": self.search_term_entry.get(), 
            "download_folder_term": self.download_folder_entry.get(), 
            "mail_folder_term": self.mail_folder_entry.get(),
            "ext_term": self.ext_entry.get(), 
            "delete_term": self.delete_check.state()
        }
        
        if self.store_password.get():
            file_dict['password'] = self.password_entry.get()

        with open(config_file, 'wb') as f:
            pickle.dump(file_dict, f)

            
if __name__ == "__main__":
    app = imap_auto()