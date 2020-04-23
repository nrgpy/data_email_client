# ![NRGPy](https://www.gravatar.com/avatar/6282094b092c756acc9f7552b164edfe?s=24) data_email_client 

**data_email_client** is a Python package for downloading data files from emails. 

## installation

```pip install data_email_client```

## examples

__see script docstrings for more usage info.__

### spidar data files:

``` python

>>> from data_email_client import mailer
>>> import getpass
>>> server = 'outlook.office365.com'
>>> username = 'data-email@my-domain.com'
>>> password = getpass.getpass()
...
>>> imap = mailer(server=server, username=username, password=password)
>>> imap.list_mailboxes()
>>> data_boxes = [m for m in imap.mailboxes if 'data' in m]
>>> imap.search_for_messages(text='spidardatanotification@nrgsystems.com', area='FROM', folder=data_boxes)
>>> imap.download_attachments(out_dir='/path/to/data/', delete=False)
```

### symphonie data emails

``` python
...
>>> body_text = 'SymphoniePRO Logger data attached.' # 'Wind Data attached.' for older logger types
>>> imap = mailer(server=server, username=username, password=password)
>>> imap.list_mailboxes()
>>> data_boxes = [m for m in imap.mailboxes if 'data' in m]
>>> imap.search_for_messages(text=body_text, area='BODY', folder=data_boxes)
>>> imap.download_attachments(out_dir='/path/to/data/', delete=False)
```