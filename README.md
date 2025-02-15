# ![NRGPy](https://www.gravatar.com/avatar/6282094b092c756acc9f7552b164edfe?s=24) data_email_client 

**data_email_client** is a Python package for downloading data files from emails using the imap protocol (SSL-compatible)

## installation

```pip install data_email_client```

## examples

_see script docstrings for more usage info._

### symphonie data emails

``` python
...
>>> body_text = 'SymphoniePRO Logger data attached.'  # 'Wind Data attached.' for older logger types
>>> imap = mailer(server=server, username=username, password=password)
>>> data_boxes = [m for m in imap.mailboxes if 'data' in m]
>>> imap.search_for_messages(text=body_text, area='body', folder=data_boxes)
>>> imap.download_attachments(
        out_dir='/path/to/data/', 
        extension='rld', 
        delete=False, 
        archive_folder='INBOX/Archive'
    )
```