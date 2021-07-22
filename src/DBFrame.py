from sqlalchemy import create_engine, func, exists, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from sqlalchemy.ext.declarative import declarative_base
from BackEnd.Spyder.Tables import *


class DBIF:
    '''
    mysql接入

    :param username
    
    :param passwd

    '''

    def __init__(self, username, passwd, address="47.109.26.240:3306/projdb"):
        # 准备连接
        self.engine = create_engine(
            f"mysql+pymysql://{username}:{passwd}@{address}?charset=utf8",
            echo=True)
        # 创建会话
        self.DbSession = sessionmaker(bind=self.engine)

    def cearte_tables(self):
        '''
        构建所有表
        '''
        try:
            Base.metadata.create_all(self.engine)  # 构建所有通过Base构建的表
        except:
            print("exist")

    def drop_tables(self):
        '''
        删除所有表
        '''
        Base.metadata.drop_all(self.engine)  # 删除所有通过Base构建的表

    def add(self, data):
        '''
        将数据加入数据库，插入时自动根据主键判断是否存在，存在则跳过
        主键必须有意义, 表示1对多的关系数据用add_relationship
        :param data: 一个表实例化的对象，相当于一条数据
        '''
        session = self.DbSession()  # 建立会话

        try:
            session.add(data)  # 添加到session:
            session.commit()  # 提交即保存到数据库:
            session.close()  # 关闭接口
        except Exception as e:
            print(e)
            session.close()  # 存在相同主键数据，关闭接口

    def update(self, data):
        '''
        更新表中的数据，插入时自动根据主键判断是否存在，存在则更新，不存在则插入
        主键必须有意义
        :param data: 一个表实例化的对象，相当于一条数据
        '''
        session = self.DbSession()
        try:
            session.add(data)  # 添加到session:
            session.commit()  # 提交即保存到数据库:
            session.close()  # 关闭接口
        except Exception as e:
            print(e)
            # 存在相同主键数据，准备更新数据
            session.rollback()
            i = DataTables.index(type(data))  # 判断本次插入关系属于哪张表
            Table = DataTables[i]  # 判断本次插入关系属于哪张表
            new = dict(data.__dict__)  # 获取插入数据字典
            try:
                del new["_sa_instance_state"]  # 删除非数据键
                del new["id"]  # 删除主键，不需要更新
            except:
                pass
            session.query(Table).filter(Table.id == data.id).update(new)
            session.commit()  # 提交即保存到数据库
            session.close()  # 关闭接口

    def add_relationship(self, relation):
        '''
        向关系表中添加一条关系，若关系存在则跳过
        主键无意义
        :param relation: 一个实例化的关系表对象
        '''
        session = self.DbSession()
        i = RelationTables.index(type(relation))  # 判断本次插入关系属于哪张表
        Table = RelationTables[i]  # 判断本次插入关系属于哪张表
        data = dict(relation.__dict__)  # 获取插入数据字典
        table = Table.__dict__  # 获取表模型成员字典
        try:
            del data["_sa_instance_state"]  # 删除非数据键
        except:
            pass
        ks = list(data.keys())
        if not len(session.query(RelationTables[i]).filter(table[ks[0]] == data[ks[0]], table[ks[1]] == data[ks[1]]).all()):
            session.add(relation)
            session.commit()
        else:
            print("relation existed")
        session.close()

    def add_updateALL(self, data):
        '''
        向数据表插入数据，存在则更新，主键id及对应数据表id
        主键有意义
        :param data:一个实例化的数据表对象或实例化对象列表
        '''
        if isinstance(data, list):
            for one in data:
                self.update(data)
        else:
            self.update(data)

    def add_jump_to_RelationTable(self, relation):
        '''
        向关系表插入数据，存在则更新，主键id与关系数据无关，按插入顺序随机生成
        主键无意义
        :param relation: 一个实例化的关系表对象或实例化对象列表
        '''
        if isinstance(relation, list):
            for one in relation:
                self.add_relationship(relation)
        else:
            self.add_relationship(relation)
