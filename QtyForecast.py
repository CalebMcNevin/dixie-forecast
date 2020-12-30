"""
Forecast for dixie sales
---

Forecast A:
Forecast Net Exchange per customer, per month,
with a forecast horrizon of 12 months

Forecast B:
Forecast Net Qty per Functional Category, Build type, and month,
with a forecast horizon of 12 months
"""
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
from sklearn import linear_model
from statsmodels.tsa.forecasting.theta import ThetaModel

import matplotlib
matplotlib.use('TkAgg')

import datetime as dt
from dotenv import load_dotenv
load_dotenv()

# Import scripts after loading evnironment to check for refresh flag
import scripts

# Get data
invoices = scripts.Invoices.load(refresh=True)
accounts = scripts.Accounts.load(refresh=True)
bins_df = pd.DataFrame({
    'FunctionalCategory': ['Alternators', 'Starters', 'Other Finished Goods'],
    'OrderType': ['Sales', 'Intercompany']
})

# prepare to get results
result_dfs = []
results_df = pd.DataFrame()

for i, functionalCategory in enumerate(
        bins_df.FunctionalCategory):
    print(f'Forecasting {functionalCategory}...', end='', flush=True)

    # Filter invoices for current Functional Category, and resample on monthly basis
    raw_sales_df = invoices[invoices.account_number == functionalCategory]
    end_clamp = pd.Series(
        [account, 'clamp', 0, 0],
        name=dt.datetime.today(),
        index=['account_number', 'part_number', 'NetQty', 'NetExchange'])
    clamped_sales_df = raw_sales_df.append(end_clamp)
    clamped_sales_df.index = pd.to_datetime(clamped_sales_df.index)
    sales_df = clamped_sales_df.resample('M').sum().filter(['NetExchange'])

    if sales_df.NetExchange.sum() <= 0:
        print('No Data; forecast aborted')
        continue

    # Run example forecast
    # forecast_test(sales_df, account)

    # Prepare data for forecast
    endog = sales_df.NetExchange

    # Create and fit model, and forecast for 12 months
    mod = ThetaModel(endog, deseasonalize=(len(endog) >= 24))
    res = mod.fit(disp=0)
    fcast = res.forecast(15)

    # Plot forecast data
    try:
        res.plot_predict(
            15,
            alpha=0.2,
            in_sample=True,
        )
        plt.hlines(y=0,
                   xmin=dt.datetime.strptime('2010-01-01', '%Y-%M-%d'),
                   xmax=dt.datetime.strptime('2022-04-01', '%Y-%M-%d'))
        # endog['2016-01-01':].plot()
        plt.xlim((dt.datetime.strptime('2016-01-01', '%Y-%M-%d'),
                  dt.datetime.strptime('2022-04-01', '%Y-%M-%d')))
        plt.title(account)
        plt.xlabel('Date')
        plt.ylabel('Net Exchange')

        plt.savefig(f'./figures/{account}.png')
        plt.close()
    except:
        print(f'Failed to plot for account {account}.')

    # Save forecast data to results
    fcast.index = pd.to_datetime(fcast.index)
    fcast.name = account

    result_dfs.append(fcast)

    print('\r', ' ' * 80, end='\r')

results_df = results_df.append(result_dfs)
results_df.index.name = 'Account'
results_df = results_df.append(accounts[['ExchangeTotal']])
print(results_df.to_string())
results_df.to_csv('results.csv')
