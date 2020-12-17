import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv
import datetime as dt
load_dotenv()
dirname = os.path.dirname(__file__)


class DF_Cache:
    def __init__(self, name=None, refresh=True, index_col=None, datetimeIndex = False):
        if name is None:
            raise ValueError('name must be supplied')
        path = os.path.join(os.path.dirname(__file__),name)
        self.script_path = f'{path}.sql'
        self.csv_path = f'{path}.csv'
        self.name = name
        self.refresh = refresh
        self.query_string = None
        self.index_col = index_col
        self.datetimeIndex = datetimeIndex
        host = os.getenv('SQL_HOST')
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
                self.df = pd.read_sql(self.query_string, cnxn, index_col = self.index_col, parse_dates = [self.index_col])
                self.df.to_csv(self.csv_path)
        else:
            print(f'Loading {self.name} data from csv...')
            if self.datetimeIndex:
                self.df = pd.read_csv(self.csv_path, index_col=self.index_col, parse_dates = [self.index_col])
            else:
                self.df = pd.read_csv(self.csv_path, index_col=self.index_col)
        return self.df

# pullInvoices = DF_Cache(name='pull-invoices')
Invoices = DF_Cache(name='invoices', index_col='proc_date', datetimeIndex = True)
Accounts = DF_Cache(name='accounts')
