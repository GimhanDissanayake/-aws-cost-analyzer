import os
import json  
import boto3
from datetime import date, timedelta


# global variables
LINKED_ACCOUNT = os.environ.get('LINKED_ACCOUNT')


date_today = date.today()
date_1_day_ago = str(date_today - timedelta(days=1))
date_2_day_ago  = str(date_today - timedelta(days=2))
cost_filter = f'{{ "And": [ {{"Dimensions": {{ "Key": "LINKED_ACCOUNT", "Values": [ "{LINKED_ACCOUNT}" ] }} }}, {{"Not": {{"Dimensions": {{ "Key": "RECORD_TYPE", "Values": ["Credit"] }} }} }} ] }}'


ce_client = boto3.client('ce')


def lambda_handler(event, context):
    print(date_today)
    print(date_1_day_ago)
    print(date_2_day_ago)
    print('*************')
    
    get_cost_diff()
    
    
def get_cost_diff():
    # calculate yesterday
    yesterday_cost = get_cost(date_1_day_ago,str(date_today))[0]['Total']['UnblendedCost']['Amount']
    print(f'yesterday_cost: {yesterday_cost} USD')
    
    # calculate day before yesterday cost
    day_before_yesterday_cost = get_cost(date_2_day_ago,date_1_day_ago)[0]['Total']['UnblendedCost']['Amount']
    print(f'day_before_yesterday_cost: {day_before_yesterday_cost} USD')
    
    # cost diff
    cost_diff = float(yesterday_cost) - float(day_before_yesterday_cost)
    print(f'cost_diff: {cost_diff}')
    
    # generate message
    if cost_diff > 0:
        diff_message = f'Your daily cost has increased by {cost_diff} USD on {date_1_day_ago} compared to {date_2_day_ago}'
    else:
        diff_message = f'Your daily cost has decreased by {-1 * cost_diff} USD on {date_1_day_ago} compared to {date_2_day_ago}'
    
    message = f'AWS Account ID: {LINKED_ACCOUNT} \n{diff_message}'    
    print(message)
    
def get_cost(startdate,enddate):
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': startdate,
            'End': enddate
        },
        Granularity='DAILY',
        #Filter=json.loads(cost_filter),
        Filter=json.loads(cost_filter),
        Metrics=[
            'UnblendedCost'
        ]
    )    
    
    return response['ResultsByTime']