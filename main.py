import pandas as pd
import os
import openpyxl
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.stattools import adfuller, kpss, zivot_andrews
from arch.unitroot import PhillipsPerron
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from tabulate import tabulate
from arch.unitroot import PhillipsPerron

#import and basic cleaning
file_path=os.path.join(os.getcwd(), 'MVE_Assignment_DataSet.xlsx')
columns = ['Unnamed: 0',
           #'EN.ATM.METH.AG.KT.CE',
           #'EN.ATM.NOXE.AG.KT.CE',
           #'AG.PRD.CROP.XD',
           #'EN.ATM.CO2E.KT',
           'mean+tmp',
           'mean_pre',
           'SP.POP.TOTL',
           'NV.AGR.TOTL.KD']

data = pd.read_excel(file_path, header=1, usecols=columns)

data.rename(columns={'Unnamed: 0': 'year',
                     #'EN.ATM.METH.AG.KT.CE' : 'methane' ,
                     #'EN.ATM.NOXE.AG.KT.CE' :  'nox' ,
                     #'AG.PRD.CROP.XD' :  'crop_production' ,
                     #'EN.ATM.CO2E.KT' :  'co2',
                     'mean+tmp' :  'mean_temp',
                     'mean_pre': 'mean_rainfall',
                     'SP.POP.TOTL' : 'population',
                     'NV.AGR.TOTL.KD' :  'agricultural_GDP'     
                     }, inplace=True)
data.set_index('year', inplace=True)

data=data[['mean_temp','mean_rainfall','population','agricultural_GDP']]

for col in data.columns:
    fig, axs = plt.subplots(3, 1, figsize=(12, 15)) 
    axs[0].plot(data.index, data[col], label=col)
    axs[0].set_xlabel('Year')
    axs[0].set_ylabel('Level')
    axs[0].legend()
  
    axs[1].plot(data.index, np.log(data[col]), label=col)
    axs[1].set_xlabel('Year')
    axs[1].set_ylabel('Log(Level)')
    axs[1].legend()

    axs[2].plot(data.index, data[col].diff(), label=col)
    axs[2].set_xlabel('Year')
    axs[2].set_ylabel('First Difference')
    axs[2].legend()

    output_directory = 'graphs'
    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, f'{col}.png')
    plt.savefig(output_file_path)

    plt.show()


for col in data.columns:
    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(18, 8))
    # Original Series
    axes[0, 0].plot(data[col])
    axes[0, 0].set_title(f'Original - {col}')
    plot_acf(data[col], lags=8, ax=axes[0, 1], title=f'ACF - {col} (Original)')
    plot_pacf(data[col], lags=8, ax=axes[0, 2], title=f'PACF - {col} (Original)')

    # First Difference
    first_diff = np.diff(data[col])
    axes[1, 0].plot(first_diff)
    axes[1, 0].set_title(f'First Diff - {col}')
    plot_acf(first_diff, lags=8, ax=axes[1, 1], title=f'ACF - {col} (First Diff)')
    plot_pacf(first_diff, lags=8, ax=axes[1, 2], title=f'PACF - {col} (First Diff)')

    # Second Difference
    second_diff = np.diff(data[col], n=2)
    axes[2, 0].plot(second_diff)
    axes[2, 0].set_title(f'Second Diff - {col}')
    plot_acf(second_diff, lags=8, ax=axes[2, 1], title=f'ACF - {col} (Second Diff)')
    plot_pacf(second_diff, lags=8, ax=axes[2, 2], title=f'PACF - {col} (Second Diff)')

    output_file_path = os.path.join(output_directory, f'{col}_p_acf.png')
    plt.tight_layout()
    plt.savefig(output_file_path)
    plt.close()
    

#Part 3
# Check for serial correlation of residuals
for column_name in data.columns:
    print(f'The results of {column_name}:')
    timeseries = np.asarray(data[column_name])
    y = timeseries[1:]
    y_lag = timeseries[:-1]
    model = sm.OLS(y, y_lag)
    results = model.fit()
    
    plot_acf(results.resid, lags=10,title=f'ACF - {column_name} (Residuals)')
    output_directory = 'graphs'
    os.makedirs(output_directory, exist_ok=True)
    output_file_path = os.path.join(output_directory, f'{column_name}_residuals_acf.png')
    plt.savefig(output_file_path)

    # Calculate and print Durbin-Watson statistic
    dw_statistic = durbin_watson(results.resid)
    print(f"\nDurbin-Watson Statistic: {dw_statistic}")

    # Interpret Durbin-Watson statistic
    if dw_statistic < 1.5:
        print("Positive autocorrelation may be present.")
    elif dw_statistic > 2.5:
        print("Negative autocorrelation may be present.")
    else:
        print("No significant autocorrelation detected.")
    print()
    print()


### Testing 
df_results = pd.DataFrame(columns=['Variable', 'Deterministic Component', 'DF', 'ADF', 'PP', 'KPSS', 'Zivot Andrews'])

for col in data.columns:
    # 1. c
    df_df= adfuller(data[col],autolag=None,maxlag=0)
    df_adf = adfuller(data[col], autolag='AIC', regression='c')
    p_value_pp = PhillipsPerron(data[col], trend="n").pvalue
    df_kpss = kpss(data[col], regression='c')
    #df_za = zivot_andrews(data[col], regression='c')
    df_results = pd.concat([df_results, pd.DataFrame({'Variable': [col],
                                                       'Deterministic Component': ['c'],
                                                       'DF': [df_df[1]],
                                                       'ADF': [df_adf[1]],
                                                       'PP': [p_value_pp],
                                                       'KPSS': ["--"],
                                                       'Zivot Andrews': "--"#[df_za[1]]
                                                       })
                            ], ignore_index=True)

    # 2. ct
    df_df= adfuller(data[col],autolag=None,maxlag=0)
    df_adf = adfuller(data[col], autolag='AIC', regression='ct')
    p_value_pp = PhillipsPerron(data[col], trend="ct").pvalue
    df_kpss = kpss(data[col], regression='ct')
    #df_za = zivot_andrews(data[col], regression='ct')
    df_results = pd.concat([df_results, pd.DataFrame({'Variable': [col],
                                                       'Deterministic Component': ['ct'],
                                                       'DF': [df_df[1]],
                                                       'ADF': [df_adf[1]],
                                                       'PP': [p_value_pp],
                                                       'KPSS': ["--"],
                                                       'Zivot Andrews':"--" #[df_za[1]]
                                                       })], ignore_index=True)

    # 3. n
    df_df= adfuller(data[col],autolag=None,maxlag=0)
    df_adf = adfuller(data[col], autolag='AIC', regression='n')
    p_value_pp = PhillipsPerron(data[col], trend="n").pvalue
    df_results = pd.concat([df_results, pd.DataFrame({'Variable': [col],
                                                       'Deterministic Component': ['n'],
                                                       'DF': [df_df[1]],
                                                       'ADF': [df_adf[1]],
                                                       'PP': [p_value_pp],
                                                       'KPSS': ["--"],
                                                       'Zivot Andrews': ["--"]})], ignore_index=True)

#Part 4
# Assuming the data is I(1), then in the first part we are performing Engle-Granger, ADF and Philip-Ouliaris tests:

results = []

# Engle-Granger Cointegration Test
for col1 in data.columns:
    for col2 in data.columns:
        if col1 != col2:
            eg_test_stat, eg_p_value, _ = coint(data[col1], data[col2], trend='c')
            results.append((f"Engle-Granger Test ({col1}, {col2})", eg_test_stat, eg_p_value))

# Johansen Cointegration Test
johansen_results = coint_johansen(data.values, det_order=1, k_ar_diff=1)
trace_statistic = johansen_results.lr1
max_eig_statistic = johansen_results.lr2
trace_critical_values = johansen_results.cvm[:, 1]
max_eig_critical_values = johansen_results.cvm[:, 0]
results.append(("Johansen Trace Test", trace_statistic, "N/A"))
results.append(("Johansen Max Eigenvalue Test", max_eig_statistic, "N/A"))

# Phillips-Ouliaris Cointegration Test 
for col1 in data.columns:
    for col2 in data.columns:
        if col1 != col2:
            diff_series = data[col1] - data[col2]
            lags = 1  # You can adjust the number of lags as needed
            lagged_diff = diff_series.shift(1).dropna()
            lagged_levels = data[col1].shift(1).dropna(), data[col2].shift(1).dropna()

            # Regression
            model = PhillipsPerron(lagged_diff, trend='c', lags=lags)
            po_test_stat = model.stat
            po_p_value = model.pvalue

            results.append((f"Phillips-Ouliaris Test ({col1}, {col2})", po_test_stat, po_p_value))

# ADF Cointegration Test
for col1 in data.columns:
    for col2 in data.columns:
        if col1 != col2:
            adf_test_result = adfuller(data[col1] - data[col2], autolag='AIC')
            adf_test_stat = adf_test_result[0]
            adf_p_value = adf_test_result[1]
            critical_values = adf_test_result[4]
            results.append((f"ADF Test ({col1}, {col2})", adf_test_stat, adf_p_value, critical_values))

# Results
columns = ["Test", "Test Statistic", "P-Value", "Critical Values"]
df_results = pd.DataFrame(results, columns=columns)

print(tabulate(df_results, headers='keys', tablefmt='fancy_grid'))

# In the second part, we perform Maximum Likelihood based tests based on Johansen Trace and Maximum Eigenvalue tests:
results = []

# Johansen Cointegration Test
johansen_results = coint_johansen(data.values, det_order=1, k_ar_diff=1)

# Trace Statistic and Critical Values
trace_statistic = johansen_results.lr1
trace_critical_values = johansen_results.cvt[:, 2]  # Adjust the index based on your number of variables

# Maximum Eigenvalue Statistic and Critical Values
max_eig_statistic = johansen_results.lr2
max_eig_critical_values = johansen_results.cvm[:, 2]  # Adjust the index based on your number of variables

# Eigenvalues
eigenvalues = johansen_results.eig

results.append(("Johansen Trace Test", trace_statistic, trace_critical_values))
results.append(("Johansen Max Eigenvalue Test", max_eig_statistic, max_eig_critical_values))

# Results
columns = ["Test", "Test Statistic", "Critical Values"]
df_results = pd.DataFrame(results, columns=columns)

print(tabulate(df_results, headers='keys', tablefmt='fancy_grid'))
