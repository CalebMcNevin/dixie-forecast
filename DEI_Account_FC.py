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


def forecast_test(df, account):
    # Calculate split point and split data
    split_index = '2019-12-01'
    df_train, df_test = sales_df[sales_df.index < split_index], sales_df[
        sales_df.index >= split_index]
    X_train = df_train.index.map(dt.datetime.toordinal).values.reshape(-1, 1)
    y_train = df_train.NetExchange.values.reshape(-1, 1)
    X_test = df_test.index.map(dt.datetime.toordinal).values.reshape(-1, 1)
    y_test = df_test.NetExchange.values.reshape(-1, 1)
    endog = df_train.NetExchange
    exog = df_test.NetExchange

    # Create and fit model, and forecast 12 months
    mod = ThetaModel(endog, deseasonalize=(len(endog) >= 24))
    res = mod.fit(disp=0)
    fcast = res.forecast(12)

    # Create plot for test forecast
    fig, ax = plt.subplots()
    ax.set_title(account)
    ax.set_xlabel('Date')
    ax.set_ylabel('Net Exchange')

    # plot forecast, and actual sales history
    fcast.plot(ax=ax)
    endog.loc['2010':].plot(ax=ax)
    exog.plot(ax=ax)
    plt.legend()

    # Save figure for reference
    plt.savefig(f'./figures_us/{account}.png')
    plt.close(fig)


# Get data
invoices = scripts.DEI_Invoices.load(refresh=True)
accounts = scripts.DEI_Accounts.load(refresh=True)

# total_df = invoices.resample('Y').sum().filter(['NetExchange'])
# mod = ThetaModel(total_df)
# res = mod.fit(disp=0)
# fcast = res.forecast()
# res.plot_predict(2, in_sample=True)
# plt.show()
# exit()

# prepare to get results
result_dfs = []
results_df = pd.DataFrame()

for i, account in enumerate(accounts.account_number):
    print(f'Forecasting {account}...', end='', flush=True)

    # Filter invoices for current account, and resample on monthly basis
    raw_sales_df = invoices[invoices.account_number == account]
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
    # try:
    #     res.plot_predict(
    #         15,
    #         alpha=0.2,
    #         in_sample=True,
    #     )
    #     plt.hlines(y=0,
    #                xmin=dt.datetime.strptime('2010-01-01', '%Y-%M-%d'),
    #                xmax=dt.datetime.strptime('2022-04-01', '%Y-%M-%d'))
    #     # endog['2016-01-01':].plot()
    #     plt.xlim((dt.datetime.strptime('2016-01-01', '%Y-%M-%d'),
    #               dt.datetime.strptime('2022-04-01', '%Y-%M-%d')))
    #     plt.title(account)
    #     plt.xlabel('Date')
    #     plt.ylabel('Net Exchange')

    #     plt.savefig(f'./figures_us/{account}.png')
    #     plt.close()
    # except:
    #     print(f'Failed to plot for account {account}.')

    # Save forecast data to results
    fcast.index = pd.to_datetime(fcast.index).strftime('%Y-%m-%d')
    fcast.name = account

    result_dfs.append(fcast)

    print('\r', end='', flush=True)
print(' ' * 20, end='\r')
results_df = results_df.append(result_dfs)
accounts = accounts.set_index('account_number')
results_df = pd.concat([results_df, accounts[['TwelveMonthSales']]], axis=1)
results_df.index.name = 'Account'
# print(results_df.to_string())
results_df.to_csv('DEI_Account_FC.csv')
