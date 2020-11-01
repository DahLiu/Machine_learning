def cal_iv(df, feature, target):
  lst = []
  cols = ['Variable', 'Interval', 'All', 'Bad']
  for val in df[feature].unique():
    temp1 = df[df[feature]==val].count()[feature]
    temp2 = df[(df[feature]==val) & (df[target]==1)].count()[feature]
    lst.append([feature, val, temp1, temp2])
  data = pd.DataFrame(lst, columns=cols)
  data = data[data['Bad']>0]
  data['Share'] = data['All'] / data['All'].sum()
  data['Bad Rate'] = data['Bad'] / data['All'].sum()
  data['Distribution Bad'] = data['Bad'] / data['Bad'].sum()
  data['Distribution Good'] = (data['All'] - data['Bad']) / (data['All'] - data['Bad']).sum()
  data['WOE'] = np.log(data['Distribution Bad'] / data['Distribution Good'])
  data['IV'] = ((data['Distribution Bad'] - data['Distribution Good']) * data['WOE'])
  data = data.sort_values(by=['Variable', 'Interval'], ascending=True)
  # print(data)
  return data['IV'].sum()

# for col in bin_cols:
#   print('The IV of ' + col + ':')
#   print(cal_iv(df, col, 'SeriousDlqin2yrs'))
