# DrAdvice
parse the doctor's advice

# data structor

## paients_source
```python

{
    '_id': 'xxx',
    'd': {
        'info':['', ''],
        'doctor_advice':[
            ["", "", "2015-09-25 15:30", "临", "其他", "丽洁胃管包(有盖胃管) 1包", "", "", "name", "", "", "", "", "", "", "已核对", "已执行", "name" ],
            []
            ]
    }
}
```
## paients_splited
```python

{
    '_id': 'xxx',
    'info':['', ''],
    'wt':[{'t': '2017-01-01', 'v': 2.0}, {}]
    'nu':[
        {'en': False, 't': '2015-05-04', 'v': 100.0, 't': '葡萄糖', 'wt':0.25},
        {}
    ]
}
```
## paients_merged
```python

{
    '_id': 'xxx',
    'info':['', ''],
    'wt':[{'t': '2017-01-01', v: 2.0}, {}]
    'nu':[
        {'en': False, 't': '2015-05-04', 'v': 100.0, 't': '葡萄糖', 'wt':0.25},
        {}
    ]
}
```
