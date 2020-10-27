# -*- coding: utf-8 -*-
"""第六课：预测全家桶.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1g_W9txkZBrDPnojGdO23fbE7hoJUMOoY
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

"""## 1.载入数据"""

df = pd.read_csv('/content/drive/My Drive/核心课/6第六课：预测全家桶/L6-code核心/code/voice/voice.csv')
df.head()

"""## 2.数据预处理和探索"""

df['label'] = df['label'].map(lambda x:1 if x=='male' else 0)
df.head()

df.isnull().sum()

df.info()

df['label'].value_counts()

df_corr = df.corr()

plt.figure(figsize=(20,12))
sns.heatmap(df_corr, cmap='coolwarm', annot=True)
plt.show()

## based on the heatmap, we delete the co-linear features: centroid, dfrange
df_processed = df.drop(['centroid', 'dfrange'],axis=1)
plt.figure(figsize=(20,12))
sns.heatmap(df_processed.corr(), cmap='coolwarm', annot=True)
plt.show()

"""## 3.准备训练数据及归一化"""

X = df_processed.iloc[:, :-1]
y = df_processed.iloc[:, -1]

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X = scaler.fit_transform(X)

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

"""## 4.训练模型"""

from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import xgboost as xgb

## lr &　svm
lr_model = LogisticRegression()
svm_model = SVC()

lr_model.fit(X_train, y_train)
svm_model.fit(X_train, y_train)

## XGB


xgb_model = xgb.XGBClassifier()
xgb_model.fit(X_train, y_train, eval_metric='auc', eval_set=[(X_train, y_train),(X_test,y_test)],
              verbose=False, early_stopping_rounds=10)

param = {'boosting_type':'gbdt',
                         'objective' : 'binary:logistic', #任务目标
                         'eval_metric' : 'auc', #评估指标
                         'eta' : 0.01, #学习率
                         'max_depth' : 15, #树最大深度
                         'colsample_bytree':0.8, #设置在每次迭代中使用特征的比例
                         'subsample': 0.9, #样本采样比例
                         'subsample_freq': 8, #bagging的次数
                         'alpha': 0.6, #L1正则
                         'lambda': 0, #L2正则
        }

# 读取数据
train_data = xgb.DMatrix(X_train, label=y_train)
# dtrain = xgb.DMatrix('demo/data/agaricus.txt.train')# 读取svm数据
test_data = xgb.DMatrix(X_test, label=y_test)

xgb_model_2 = xgb.train(
    param,
    train_data,
    evals=[(train_data,'train'), (test_data,'test')],
    num_boost_round=10000,
    early_stopping_rounds=200,
    verbose_eval=False
)

## lightGBM
param = {'boosting_type':'gbdt',
      'objective' : 'binary', #任务类型
      'metric' : 'auc', #评估指标
      'learning_rate' : 0.01, #学习率
      'max_depth' : 15, #树的最大深度
      'feature_fraction':0.8, #设置在每次迭代中使用特征的比例
      'bagging_fraction': 0.9, #样本采样比例
      'bagging_freq': 8, #bagging的次数
      'lambda_l1': 0.6, #L1正则
      'lambda_l2': 0, #L2正则
}

#数据加载
import lightgbm as lgb
train_data_lgb = lgb.Dataset(X_train, label=y_train)
test_data_lgb = lgb.Dataset(X_test, label=y_test)

# 模型训练
model_lgb = lgb.train(param, train_data_lgb,
            valid_sets=[train_data_lgb, test_data_lgb],
            num_boost_round=10000,
            early_stopping_rounds=200,
            verbose_eval=False)
#                       categorical_feature=attr)

"""## 5.模型选择及预测"""

def evaluate_model(model, test_x, test_y, is_bi=True):
  if is_bi:
    pred = model.predict(test_x)
    acc = accuracy_score(test_y, pred)
    f1 = f1_score(test_y, pred)
    cm = confusion_matrix(test_y, pred)
    print('Model {} evaluation: \n'.format(str(model)))
    print('Accuracy Score: {}'.format(acc))
    print('f1 Score: {}'.format(f1))
    print('Confusion Matrix: \n{}'.format(cm))
  else:
    pred = pd.Series(model.predict(test_x)).map(lambda x:1 if x>0.5 else 0)
    acc = accuracy_score(test_y, pred)
    f1 = f1_score(test_y, pred)
    cm = confusion_matrix(test_y, pred)
    print('Model {} evaluation: \n'.format(str(model)))
    print('Accuracy Score: {}'.format(acc))
    print('f1 Score: {}'.format(f1))
    print('Confusion Matrix: \n{}'.format(cm))

evaluate_model(lr_model, X_test, y_test)

evaluate_model(svm_model, X_test, y_test)

evaluate_model(xgb_model, X_test, y_test)

evaluate_model(xgb_model_2, test_data, y_test, False)

evaluate_model(model_lgb, X_test, y_test, False)
