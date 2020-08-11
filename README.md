<div align="center">
 <div>
   <img src="https://user-images.githubusercontent.com/32212649/89178083-72d12380-d5bf-11ea-8b14-56ed824b28bf.png">
  </div>
</div>

## louvijan
**louvijan** is a tool to control the script pipeline (not limited to Python scripts), which means that scripts can be executed in a specified order. In addition, it is recommended because it is lightweight, fast and easy to use.

## Installation
You can install `louvijan` with `pip`:

```sh
pip install louvijan
```

## Examples
In one word, easy to use! After reading, please show your thumb.
If you have a series of scripts that need to be executed in a certain order, as shown in the figure:

<div align="center">
 <div>
   <img src="https://user-images.githubusercontent.com/32212649/89850126-86324f00-dbbc-11ea-8905-2cb6c71af757.png">
  </div>
</div>


In the figure, A to G represent scripts respectively. First execute A, then execute B, C, D at the same time, then execute E, F at the same time, and finally execute G.

Let's describe it with louvijan:
```python
from louvijan import PipeLine
PipeLine('A', ['B', 'C', 'D'], ['E', 'F'], 'G')()
```

If you want to execute B, C, D on a remote server, you can create a new configuration file `remote.conf`:

```sh
[remote]
ip = 127.0.0.1
port = 22
username = root
password = 123456
```

This is the case with louvijan:

```python
PipeLine('A', Python(['B', 'C', 'D'], config='remote.conf'), ['E', 'F'], 'G')()
```


It is able to also send you an email after the script execution succeeds or fails or regardless of success or failure, by adding options in the configuration file like this:

```sh
[email]
host = smtp.qq.com
username = 12345
port = 25
authcode = ************
sender = tanyee@qq.com
receivers = one@qq.com, two@qq.com, three@qq.com
send_mail_flag = always
```

You can execute the following statement to generate a configuration file template:

```python
from louvijan import Config
Config().template()
```

By setting the configuration file and multiple nested PipeLine, you can construct a variety of complex pipeline projects.

For more details, see `example.py`.
