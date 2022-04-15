import os
import json
import time
import gspread
import logging

logger = logging.getLogger(__name__)

_config_path = '.clerkconfig'

def args_to_clerk_config(args):
    return {
        "spreadsheet_entry": args.spreadsheet_entry,
        "worksheet_name": args.worksheet_name,
        "worker_name": args.worker_name,
        "credential_path": args.credential_path,
    }

def clerk_config_write_args(args):

    if os.path.exists(_config_path):
        with open(_config_path, 'r') as fin:
            previous_config = json.load(fin)
    else:
        previous_config = {}
    if os.path.exists(args.credential_path):
        with open(args.credential_path, 'r') as fin:
            credential = json.load(fin)
        previous_config['credential_path'] = credential
    if len(args.spreadsheet_entry) > 0:
        previous_config['spreadsheet_entry'] = args.spreadsheet_entry
    if len(args.worksheet_name) > 0:
        previous_config['worksheet_name'] = args.worksheet_name
    if len(args.worker_name) > 0:
        previous_config['worker_name'] = args.worker_name
    with open(_config_path, 'w') as fout:
        json.dump(previous_config, fount)

def clerk_config_read():
    assert os.path.exists(_config_path)
    with open(_config_path, 'r') as fin:
        clerk_config = json.load(fin)
    assert 'spreadsheet_entry' in clerk_config, 'clerk error: spreadsheet not set up properly, missing `spreadsheet_entry` in {}'.format(_config_path)
    assert 'worksheet_name' in clerk_config, 'clerk error: spreadsheet not set up properly, missing `worksheet_name` in {}'.format(_config_path)
    assert 'worker_name' in clerk_config, 'clerk error: spreadsheet not set up properly, missing `worker_name` in {}'.format(_config_path)
    assert 'credential_path' in clerk_config, 'clerk error: spreadsheet not set up properly, missing `credential_path` in {}'.format(_config_path)
    return clerk_config

def clerk_config_args_update(args):
    if hasattr(args,'spreadsheet_entry') and len(args.spreadsheet_entry) > 0 \
        and hasattr(args,'worksheet_name') and len(args.worksheet_name) > 0 \
        and hasattr(args, 'worker_name') and len(args.worker_name) > 0 \
        and hasattr(args,'credential_path') and os.path.exists(args.credential_path) > 0:
        clerk_config_write_args(args)
    else:
        config_dict = clerk_config_read()
        args.spreadsheet_entry = config_dict['spreadsheet_entry']
        args.worksheet_name = config_dict['worksheet_name']
        args.worker_name = config_dict['worker_name']
        args.credential_path = config_dict['credential_path']

def clerk_config_update(
    spreadsheet_entry="", 
    worksheet_name="", 
    worker_name="", 
    credential_path="/home/lucliu/.clerk/clerk.json"
):
    if len(spreadsheet_entry) > 0 and \
        len(worksheet_name) > 0 and \
        len(worker_name) > 0 and \
        os.path.exists(credential_path):
        with open(credential_path, 'r') as fin:
            credential = json.load(fin)
        config_dict = {
            'spreadsheet_entry': spreadsheet_entry,
            'worksheet_name': worksheet_name,
            'worker_name': worker_name,
            'credential_path': credential,
        }
        with open(_config_path, 'w') as fout:
            json.dump(config_dict, fout)
    else:
        config_dict = clerk_config_read()
    return config_dict


def update_cells(ws, cell_list):
    succeed = False
    while not succeed:
        try:
            results = ws.update_cells(cell_list)
        except gspread.exceptions.APIError as e:
            logger.error('[clerk] gspread error: 429 RESOURCE_EXHAUSTED! wait 20s')
            time.sleep(20)
        else:
            succeed = True
    return results

def wsrange(ws, first_row, first_col, last_row, last_col):
    succeed = False
    while not succeed:
        try:
            results = ws.range(first_row, first_col, last_row, last_col)
        except gspread.exceptions.APIError as e:
            logger.error('[clerk] gspread error: 429 RESOURCE_EXHAUSTED! wait 20s')
            time.sleep(20)
        else:
            succeed = True
    return results

def row_values(ws, row_id):
    succeed = False
    while not succeed:
        try:
            results = ws.row_values(row_id)
        except gspread.exceptions.APIError as e:
            logger.error('[clerk] gspread error: 429 RESOURCE_EXHAUSTED! wait 20s')
            time.sleep(20)
        else:
            succeed = True
    return results

def col_values(ws, col_id):
    succeed = False
    while not succeed:
        try:
            results = ws.col_values(col_id)
        except gspread.exceptions.APIError as e:
            logger.error('[clerk] gspread error: 429 RESOURCE_EXHAUSTED! wait 20s')
            time.sleep(20)
        else:
            succeed = True
    return results
    
def update_cell(ws, row_id, col_id, value):
    succeed = False
    while not succeed:
        try:
            results = ws.update_cell(row_id, col_id, value)
        except gspread.exceptions.APIError as e:
            logger.error('[clerk] gspread error: 429 RESOURCE_EXHAUSTED! wait 20s')
            time.sleep(20)
        else:
            succeed = True
    return results

def get_nonempty_row_ct(ws):
    succeed = False
    while not succeed:
        try:
            results = len(ws.get_all_values())
        except gspread.exceptions.APIError as e:
            logger.error('[clerk] gspread error: 429 RESOURCE_EXHAUSTED! wait 20s')
            time.sleep(20)
        else:
            succeed = True
    return results