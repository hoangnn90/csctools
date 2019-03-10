## Install python 3.6
- Link: <https://www.python.org/ftp/python/3.6.6/python-3.6.6-amd64.exe>

>NOTE:
- Select <b>`Add Python 3.6 to PATH`</b>
- Choose <b>`Customize installation`</b>
- Select <b>`Install for all user`</b>
- Install to <b>`C:\Python36`</b> directory, <u><b>NOT</u></b> `C:\Program Files\Python36`

## Setup client workspace
In case of getting error 'Client `CLIENT_NAME` unknow', enter following cmds:
```cmd
p4 client -o CLIENT_NAME | p4 client -i
set P4CLIENT=
p4 set P4CLIENT=CLIENT_NAME
p4 info
```