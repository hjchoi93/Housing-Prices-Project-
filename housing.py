# -*- coding: utf-8 -*-
"""Housing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KerdlrCA43hiweAxy7x3TyVUjYhiTDRK

    Predicting Housing Prices based on 79 features that describe almost every aspect of a residential home. More information about the data can be found at: https://www.kaggle.com/c/house-prices-advanced-regression-techniques

Base Imports
"""

# data analysis and wrangling
import pandas as pd
import numpy as np
import random as rnd
import sys 

# visualization
import seaborn as sns
import matplotlib.pyplot as plt
# %matplotlib inline 

import warnings
warnings.filterwarnings('ignore')

# machine learning
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier

"""Load in data and create a combined table for easy data clean up.  Will apply same mappings to each DF independently of combined; using combined to see any correlation on various stats tests."""

train_url = 'https://raw.githubusercontent.com/timchoh585/kaggle-data/master/house%20prices/train.csv'
test_url = 'https://raw.githubusercontent.com/timchoh585/kaggle-data/master/house%20prices/test.csv'

train_df = pd.read_csv(train_url)
test_df = pd.read_csv(test_url)
combine = pd.concat([train_df, test_df])

# print(train_df.columns.values)
# train_df.head()
# train_df.tail()
# train_df.info()
# print('_'*40)
# test_df.info()
# print('_'*40)
# combine.describe()

combine_null = new_combine[new_combine['SalePrice'].isnull()]
combine_null['SalePrice']
train_df['SalePrice'].isna().any()

"""check for null values"""

combine.columns[combine.isna().any()].tolist()

def plot_missing(df, showplot = True):
    
    # Get dataframe with percentage of missing values
    missing = pd.DataFrame(df.isnull().sum(), columns = ['perc_missing'])
    missing = missing.loc[missing['perc_missing'] > 0]
    missing = (missing/len(df))*100
    
    # Plot resulting dataframe
    missing = missing.sort_values('perc_missing')
    if(showplot):
        ax = missing.plot(
            kind = 'barh',
            figsize=(10,8),
            title = 'Percentage of Missing Values in Dataset by Feature',
            legend = None,
            color = 'coral'
        )

        for i in ax.patches:
            ax.text(
                i.get_width()+.3, i.get_y(),
                str(round(i.get_width(), 2)), 
                fontsize=12,
                color='blue'
            )

        plt.style.use('ggplot')
        plt.show()
    
    return missing

plot_missing(train_df)
plot_missing(test_df)

#Writing a function to handle NA values
def handle_na(train, test, cols_to_clean, cols_to_drop):
    if(cols_to_drop):
        train.drop(cols_to_drop, axis = 1, inplace = True)
        test.drop(cols_to_drop, axis = 1, inplace = True)
    
    if(cols_to_clean):
        for col in cols_to_clean:
            train[col+'_is_na'] = train[col].isnull()
            test[col+'_is_na'] = test[col].isnull()
        
    for col in test.columns:
        # If numeric, fill with median
        if np.issubdtype(train[col].dtype, np.number):
            train.loc[train[col].isnull() == True, col] = train[col].median()
            test.loc[test[col].isnull() == True, col] = train[col].median()

        # If object, fill with mode
        if (train[col].dtype == 'O'): 
            train.loc[train[col].isnull() == True, col] = train[col].mode().iloc[0]
            test.loc[test[col].isnull() == True, col] = train[col].mode().iloc[0]
            
    print(f'Shape of Train Set: {train.shape}')
    print(f'Shape of Test Set : {test.shape}')

    return train, test

cols_to_drop = []
cols_to_clean = []
new_train = train_df.copy()
new_test = test_df.copy()

new_train, new_test = handle_na(new_train, new_test, cols_to_clean, cols_to_drop)



new_combine = pd.concat([new_train, new_test])
new_combine.head(10)
corr = combine.corr()
corr.style.background_gradient(cmap='coolwarm').set_precision(2)

#turn correlations into absolute values for fair comparison 
new_corr = corr.abs()

#Calculating the correlation for each variable with the target variable 
corr_input = combine[combine.columns[1:]].corr()['SalePrice'][:].abs()
type(corr_input)
corr_input.sort_values(ascending=False)

new_combine.BsmtQual = new_combine.BsmtQual.astype('float64')

#I am going to implement a simple linear regression model 
#Input features will be the top 10 variables with the highest correlation 
#features that are highly correlated with the target variable. This may be more accurate in predicting housing prices


#new_combine['SalePrice'].replace(new_combine['SalePrice'] == 0, new_combine['SalePrice'].mean())

#checking to make sure the Y variable has no zeros 
new_combine[new_combine['SalePrice'] == 0].sum()
#Replacing all NA values in dependent variable with zeros
new_combine['SalePrice'].fillna(0, inplace=True)

#removing outliers using z-scores 
from scipy import stats
z = np.abs(stats.zscore(new_combine))
print(z)
threshold = 3 #Setting the Z-score to 3 because the majority of values should be within 3 standard deviations of the mean
print(np.where(z>3)) #Hence, any Z-score greater than 3 (any value greater than 3 standard deviations of the mean) will be counted as an outlier
np.set_printoptions(threshold=sys.maxsize)
print(z[1][7])
new_combine_1 = new_combine[(z < 3).all(axis=1)] #This ensures all columns satisfy the constraints and removes the outliers
new_combine_1.shape #Gets rid of 870 rows

removing outliers using IQR
Q1 = new_combine.quantile(0.25)
Q3 = new_combine.quantile(0.75)
IQR = Q3 - Q1
print(IQR)
print(new_combine < (Q1 - 1.5 * IQR)) |(new_combine > (Q3 + 1.5 * IQR))

#Chose top 10 highest correlated variable with Sale Price as the input features 
X = new_combine_1[['OverallQual','GrLivArea','GarageCars','GarageArea','TotalBsmtSF','FullBath','FullBath','TotRmsAbvGrd',
               'YearBuilt','YearRemodAdd']]
y = new_combine_1['SalePrice']

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=101)

#creating and training the model
from sklearn.linear_model import LinearRegression 
lm = LinearRegression()
lm.fit(X_train, y_train)

#predicting the model
predictions = lm.predict(X_test)
plt.scatter(y_test,predictions)
sns.distplot((y_test-predictions),bins=50);

#evaluating Metrics
from sklearn import metrics

print('MAE:', metrics.mean_absolute_error(y_test, predictions))
print('MSE:', metrics.mean_squared_error(y_test, predictions))
print('RMSE:', np.sqrt(metrics.mean_squared_error(y_test, predictions)))



#######
#Alternative methods to map string variables to integers
#########

# train_df[['Alley', 'SalePrice']].groupby(['Alley'], as_index = False).mean()
# train_df['Alley'].head(10)

alley_map = {'Grvl': 1, 'Pave': 2}

combine['Alley'].unique()
combine.
for dataset in combine:
    print(dataset)

# title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5}
# for dataset in combine:
#     dataset['Title'] = dataset['Title'].map(title_mapping)
#     dataset['Title'] = dataset['Title'].fillna(0)

#Hojoon Edits
# train_df['Alley'].unique()
# train_df.Alley[train_df.Alley == 'Grvl'] = 1
# train_df.Alley[train_df.Alley == 'Pave'] = 2
# train_df['Alley'].fillna(0, inplace=True)
# train_df['Alley'].isnull().values.any()


# train_df['BsmtCond'].unique()
# train_df.BsmtCond[train_df.BsmtCond == 'TA'] = 1
# train_df.BsmtCond[train_df.BsmtCond == 'Gd'] = 2
# train_df.BsmtCond[train_df.BsmtCond == 'Fa'] = 3
# train_df.BsmtCond[train_df.BsmtCond == 'Po'] = 4
# train_df['BsmtCond'].fillna(0, inplace=True)


# train_df['BsmtExposure'].unique()
# train_df.BsmtExposure[train_df.BsmtExposure == 'No'] = 1
# train_df.BsmtExposure[train_df.BsmtExposure == 'Gd'] = 2
# train_df.BsmtExposure[train_df.BsmtExposure == 'Mn'] = 3
# train_df.BsmtExposure[train_df.BsmtExposure == 'Av'] = 4
# train_df['BsmtExposure'].fillna(0, inplace=True)

# train_df['BsmtFinType1'].unique()
# train_df.BsmtFinType1[train_df.BsmtFinType1 == 'GLQ'] = 1
# train_df.BsmtFinType1[train_df.BsmtFinType1 == 'ALQ'] = 2
# train_df.BsmtFinType1[train_df.BsmtFinType1 == 'Unf'] = 3
# train_df.BsmtFinType1[train_df.BsmtFinType1 == 'Rec'] = 4
# train_df.BsmtFinType1[train_df.BsmtFinType1 == 'BLQ'] = 5
# train_df.BsmtFinType1[train_df.BsmtFinType1 == 'LwQ'] = 6
# train_df['BsmtFinType1'].fillna(0, inplace=True)

# train_df['BsmtFinType2'].unique()
# train_df.BsmtFinType2[train_df.BsmtFinType2 == 'GLQ'] = 1
# train_df.BsmtFinType2[train_df.BsmtFinType2 == 'ALQ'] = 2
# train_df.BsmtFinType2[train_df.BsmtFinType2 == 'Unf'] = 3
# train_df.BsmtFinType2[train_df.BsmtFinType2 == 'Rec'] = 4
# train_df.BsmtFinType2[train_df.BsmtFinType2 == 'BLQ'] = 5
# train_df.BsmtFinType2[train_df.BsmtFinType2 == 'LwQ'] = 6
# train_df['BsmtFinType2'].fillna(0, inplace=True)

# train_df['BsmtQual'].unique()
# train_df.BsmtQual[train_df.BsmtQual == 'Gd'] = 1
# train_df.BsmtQual[train_df.BsmtQual == 'TA'] = 2
# train_df.BsmtQual[train_df.BsmtQual == 'Ex'] = 3
# train_df.BsmtQual[train_df.BsmtQual == 'Fa'] = 4
# train_df['BsmtQual'].fillna(0, inplace=True)


# #Some of the listed variables don't have any missing values. Hence, no need to drop them

# #These represent the square footage of each finished basement
# train_df['BsmtFinSF1'].isna().sum() #0 missing values
# train_df['BsmtFinSF2'].isna().sum()
# #number of full baths
# train_df['BsmtFullBath'].isna().sum()
# train_df['BsmtHalfBath'].isna().sum()

# train_df['BsmtQual'].unique()

X.shape

"""create integer mappings for all NULL columns first

Show Correlation map to see which features are "most" important
"""

corr = combine.corr()
corr.style.background_gradient(cmap='coolwarm').set_precision(2)

"""Need to create a mapping off of this data for all other values that was not covered from the NULL pass through"""

new_combine
