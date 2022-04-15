import subprocess
from os import listdir
from os.path import expanduser, isfile, join
from subprocess import PIPE


class Mail:
    is_mailbox = False
    is_qmail = False
    account_name = ''
    qmail = ''
    qmail_file = ''
    to_mailboxes = []
    from_mails = []

    def __init__(self, account_name=''):
        self.account_name = account_name
        self.to_mailboxes = []
        self.from_mails = []

    def state_html(self):
        if self.is_mailbox:
            state = '<b>Mailbox:&nbsp;yes</b><br />'
        else:
            state = 'Mailbox:&nbsp;no<br />'

        if self.is_qmail:
            state += '<b>qmail: yes</b>'
        else:
            state += 'qmail: no'

        return state

    def __str__(self):
        return '| %s%s%s | %s | %s |' % ('**' if self.is_mailbox else '',
                                         self.account_name,
                                         '**' if self.is_mailbox else '',
                                         ';'.join(self.to_mailboxes),
                                         ';'.join(self.from_mails))

    def account_name_html(self):
        if self.is_mailbox:
            return '<b>%s</b>' % self.account_name

        if self.is_qmail:
            return '%s<br /><i>%s</i>' % (self.account_name, self.qmail_file)

        return self.account_name

    def get_class(self):
        if self.is_mailbox:
            return 'mailbox'

        if self.is_qmail:
            return 'qmail'

        return 'other'

    def to_row(self):
        return '<tr class="%s"><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % \
               (self.get_class(), self.account_name_html(), '<br>'.join(self.to_mailboxes), '<br />'.join(self.from_mails), '<br />'.join(self.qmail))


def read_qmail(accounts, username):
    # read mails in homedir
    home = expanduser("~")
    qmail_files = [f for f in listdir(home) if
                   isfile(join(home, f)) and f.startswith('.qmail')]

    for qmail_file in qmail_files:
        with open(join(home, qmail_file), 'r') as qmail:
            qmail_data = qmail.readlines()

        account = username
        if len(qmail_file) > 7:
            account = qmail_file[7:]

        if account not in accounts:
            accounts[account] = Mail(account)
            accounts[account].is_qmail = True
            accounts[account].qmail_file = qmail_file

        accounts[account].qmail = qmail_data

        for qmail_target in qmail_data:
            target = qmail_target.strip()

            if len(target) < 2:
                continue

            if target != username:
                if target.startswith(username):
                    target = target[len(username) + 1:]

                if target.startswith('&'):
                    target = target[1:]

                if '@' in target:
                    target = target[:target.find('@')]

                if target.startswith('./users/'):
                    target = target[8:]
                    target = target[:target.find('/')]

            if target.startswith('|') or target.startswith('#'):
                # commands or commments are not considered "on the other side"
                continue

            accounts[account].to_mailboxes.append(target)

            if target not in accounts:
                accounts[target] = Mail(qmail_target)
                accounts[target].is_qmail = '@' not in qmail_target

            accounts[target].from_mails.append(account)


def read_uberspace_mail():
    user_list = subprocess.run(['uberspace','mail','user','list'], stdout=PIPE)
    stdout = user_list.stdout

    mails = {}
    accounts = stdout.strip().split(b'\n')
    for account in accounts:
        account_name = account.decode('utf-8')
        mails[account_name] = Mail(account_name)
        mails[account_name].is_mailbox = True
        mails[account_name].to_mailboxes.append(account_name)

    return mails


def get_username():
    username = subprocess.run(['whoami'], cwd=expanduser("~"), stdout=PIPE)
    return username.stdout.strip().decode('utf-8')


def mail_overview():
    username = get_username()
    print("Get configured mails for " + username)

    mails = read_uberspace_mail()
    print("Got %d configured mailboxes, now reading .qmail files" % len(mails))
    read_qmail(mails, username)


    with open('mails.html', 'w+') as file:
        print('<html><head><meta charset="utf-8"><style>table, td, th, tr{border:1px solid grey; border-collapse: collapse;}.hidden{display:none;}</style>', file=file)

        print('<script>let state = {\'mailbox\': true,\'qmail\': true,\'other\': true}\n\
                function updateState(type) {\nstate[type] = !state[type];\nlet table = document.getElementById(\'accounts\');\n\
                rows = table.getElementsByClassName(type); for (let i = 0; i < rows.length; ++i) {        if (state[type]) {        rows[i].classList.remove(\'hidden\');        } else {        rows[i].classList.add(\'hidden\');        }        }        }        </script>', file=file)
        print('</head>\n<body>        <h3>Übersicht Accounts</h3>\
              <input type="checkbox" checked="checked" onchange="updateState(\'mailbox\');"> Mailbox<br />\n\
              <input type="checkbox" checked="checked" onchange="updateState(\'qmail\');"> qmail<br />\n\
              <input type="checkbox" checked="checked" onchange="updateState(\'other\');"> Other\n<table id="accounts">', file=file)
        print('<tr><th>Account</th><th>to Mailboxes</th><th>from Mails</th><th>qmail-Content</th></tr>', file=file)

        for mail in sorted(mails):
            print(mails[mail].to_row(), file=file)

        print('</table></body></html>', file=file)
    print("Created mails.html")


if __name__ == '__main__':
    mail_overview()
