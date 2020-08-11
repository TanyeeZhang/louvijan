# coding=utf-8
from pd2ml import Loader
import sqlalchemy
engine = sqlalchemy.create_engine('mysql+pymysql://root:123456@localhost:3306/learn?charset=utf8&local_infile=1')
df = Loader(engine).load_from('stock')
print(df)