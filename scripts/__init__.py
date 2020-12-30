import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv
import datetime as dt
load_dotenv()
dirname = os.path.dirname(__file__)


class DF_Cache:
    def __init__(self,
                 name=None,
                 refresh=True,
                 index_col=None,
                 datetimeIndex=False,
                 db=None):
        if name is None:
            raise ValueError('name must be supplied')
        self.script_path = os.path.join(os.path.dirname(__file__),
                                        f'{name}.sql')
        self.csv_path = os.path.join(os.path.dirname(__file__), 'cache',
                                     f'{name}.csv')
        self.name = name
        self.refresh = refresh
        self.query_string = None
        self.index_col = index_col
        self.datetimeIndex = datetimeIndex
        host = os.getenv('SQL_HOST')
        if db is None:
            db = os.getenv('SQL_DATABASE')
        usr = os.getenv('SQL_USERNAME')
        pwd = os.getenv('SQL_PASSWORD')
        self.__connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host};DATABASE={db};UID={usr};PWD={pwd};'

    def load(self, refresh=None):
        if refresh is None:
            refresh = self.refresh
        if self.query_string is None:
            with open(self.script_path) as f:
                self.query_string = f.read()
        if not os.path.exists(self.csv_path) or refresh:
            with pyodbc.connect(self.__connectionString) as cnxn:
                print(f'Loading {self.name} data from SQL...')
                self.df = pd.read_sql(self.query_string,
                                      cnxn,
                                      index_col=self.index_col,
                                      parse_dates=[self.index_col])
                self.df.to_csv(self.csv_path)
        else:
            print(f'Loading {self.name} data from csv...')
            if self.datetimeIndex:
                self.df = pd.read_csv(self.csv_path,
                                      index_col=self.index_col,
                                      parse_dates=[self.index_col])
            else:
                self.df = pd.read_csv(self.csv_path, index_col=self.index_col)
        return self.df


# pullInvoices = DF_Cache(name='pull-invoices')
DEL_Invoices = DF_Cache(name='DEL_Invoices',
                        index_col='proc_date',
                        datetimeIndex=True)
DEL_Accounts = DF_Cache(name='DEL_Accounts')
DEL_NetQty = DF_Cache(name='DEL_NetQty',
                      index_col='proc_date',
                      datetimeIndex=True)
DEI_Invoices = DF_Cache(name='DEI_Invoices',
                        index_col='proc_date',
                        datetimeIndex=True,
                        db='DIXIE_US')
DEI_Accounts = DF_Cache(name='DEI_Accounts', db='DIXIE_US')
DEI_NetQty = DF_Cache(name='DEI_NetQty',
                      index_col='proc_date',
                      datetimeIndex=True,
                      db='DIXIE_US')
