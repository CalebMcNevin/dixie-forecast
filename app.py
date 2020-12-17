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
from statsmodels.tsa.arima.model import ARIMA

from pandas.plotting import autocorrelation_plot

import datetime as dt
from dotenv import load_dotenv
load_dotenv()

# Import scripts after loading evnironment to check for refresh flag
import scripts

# invoices.info()

invoices = scripts.Invoices.load(refresh=False)
accounts = scripts.Accounts.load(refresh=False)

# print(invoices.info())

# invoices_resamp = invoices.resample('w').sum().filter(['NetQty'])
# df = invoices_resamp.copy()

i = 0
for account in accounts.account_number:
    i += 1
    account_sales = invoices[invoices.account_number == account]
    account_sales = account_sales.resample('BM').sum().filter(['NetExchange'])
    # account_sales['EWMA_24'] = account_sales.NetQty.ewm(span=52).mean()
    # account_sales['error'] = (account_sales.NetQty - account_sales.EWMA_24)**2
    # account_sales.filter(['NetQty','EWMA_24']).plot()
    # plt.title(f'{account} (MSE:{account_sales.error.mean()})')
    # plt.show(block=False)

    # Calculate split point and split data
    split_index = int(len(account_sales) * 0.9)
    df_train, df_test = account_sales[:split_index], account_sales[
        split_index:]
    X_train = df_train.index.map(dt.datetime.toordinal).values.reshape(-1, 1)
    y_train = df_train.NetExchange.values.reshape(-1, 1)
    X_test = df_test.index.map(dt.datetime.toordinal).values.reshape(-1, 1)
    y_test = df_test.NetExchange.values.reshape(-1, 1)

    #* Fit a linear model using sklearn
    lin_mdl = linear_model.LinearRegression()
    lin_mdl.fit(X_train, y_train)
    y_guess = lin_mdl.predict(X_test)

    #* Fit an ARIMA model using sklearn
    # autocorrelation_plot(account_sales.NetExchange)
    arima_mdl = ARIMA(df_train, order=(1, 1, 1))
    arima_mdl_fit = arima_mdl.fit()
    print(arima_mdl_fit.summary())
    residuals = pd.DataFrame(arima_mdl_fit.resid)
    # residuals.plot()
    # plt.title(f'{account} residuals')
    # plt.show()
    # residuals.plot(kind='kde')
    # plt.title(f'{account} residual kde')
    # plt.show()
    print(residuals.describe())

    # ind = pd.DatetimeIndex(
    #     list(map(dt.datetime.fromordinal, np.append(X_train, X_test))))
    df = pd.DataFrame(
        {
            'NetExchange':
            np.append(y_train, y_test),
            'prediction':
            np.append(np.full((len(X_train), 1), None), y_guess),
            'arima':
            arima_mdl_fit.forecast(
                dt.datetime.strptime('2022-01-01', '%Y-%m-%d'))
        },
        index=account_sales.index)
    df['error'] = (df.prediction - df.NetExchange)**2
    # fig, ax = plt.subplots()
    # ax.plot(X_test, mdl.predict(X_test), linewidth=2, color='blue')
    # ax.plot(X_train, y_train, c='red')
    # ax.plot(X_test, y_test, c='red')
    # ax.set_title(account)
    df.filter(['NetExchange', 'prediction', 'arima']).plot()
    plt.title(f'{account} (MSE:{df.error.mean()})')
    # plt.show(block=False)

    plt.show(block=False)

    # input('Press Enter to finish...')
    # exit()

    if i >= 10:
        input('Press Enter to finish...')
        quit()
quit()

# df['EWMA0.5'] = df.NetQty.ewm(alpha=0.5).mean()
# df['EWMA0.25'] = df.NetQty.ewm(alpha=0.25).mean()
# df['EWMA0.1'] = df.NetQty.ewm(alpha=0.1).mean()
df['EWMA_6'] = df.NetQty.ewm(span=6).mean()
df['EWMA_13'] = df.NetQty.ewm(span=13).mean()
df['EWMA_26'] = df.NetQty.ewm(span=26).mean()
df['EWMA_52'] = df.NetQty.ewm(span=52).mean()
df.plot()
plt.show()

# for i in range(1, 13):
#     invoices_resamp[f"lag_{i}"] = invoices_resamp.NetQty.shift(i)
# df_train = invoices_resamp[~np.isnan(invoices_resamp.lag_11)]
# print(df_train)

print(df)

# X = df_train.index.map(dt.datetime.toordinal)
# y = df_train.NetQty

# model_1 = sm.OLS(y, X).fit()
# predictions_1 = model_1.predict(X)
# print(model_1.summary())

# tscv = TimeSeriesSplit(n_splits=2)
# for train_index, test_index in tscv.split(X):
#     print(f'TRAIN:{y[train_index]}\tTEST:{y[test_index]}')
# X_train, X_test, y_train, y_test = tscv
# model_2 = sm.tsa.arima.ARIMA(y, X, freq='M').fit()
# predictions_2 = model_2.predict(X[0],X[-1])
# print(model_2.summary())

# sns.lineplot(x=df_train.index, y=df_train.NetQty)
# sns.lineplot(x=invoices_resamp.index, y=invoices_resamp.NetQty.rolling(window=12, center=False).mean())
# plt.show()

# time = pd.date_range('2020-01-01','2020-12-15', freq='1d')
# data = np.cumsum(invoices.NetQty)
# np.polyfit()
exit()