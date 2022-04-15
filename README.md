## Uberspace Mail Overview
Provides an html overview of your mail addresses configured on your Uberspace.
It shows which emails are defined by mailboxes and .qmail-files, shows the content of the .qmail-files
and where these redirect to.    

- [Example](example.html) of the output

### Usage
Get the mail-overview.py and execute it using python. Afterwards open the mails.html.
```shell
wget https://raw.githubusercontent.com/ebroda/uberspace-mail-overview/main/mail-overview.py
python3.9 mail-overview.py
mv mails.html ~/html/
```
Open your-username.uber.space/mails.html.


### Known limitations
- It does not consider redirects defined by 'uberspace mail user forward'.
