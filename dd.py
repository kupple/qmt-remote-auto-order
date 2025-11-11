import pywencai

res = pywencai.get(query='退市股票', sort_key='退市@退市日期', sort_order='asc', cookie='xxx')
print(res)