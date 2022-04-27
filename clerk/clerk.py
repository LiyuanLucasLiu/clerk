
import gspread
import time
import logging
from .utils import *

logger = logging.getLogger(__name__)

def init_clerk_logger(**kwargs):
    if 'rank' not in kwargs or kwargs['rank'] is None:
        kwargs['rank'] = 0
    
    clerk = SpreadsheetClerk(**kwargs)
    if 0 == kwargs['rank']:
        handler = ClerkHandler(clerk)
        logging.getLogger().addHandler(handler)
    
    return clerk

def update_args_w_clerk(args, clerk):
    config = clerk.get_log_allcolumns()
    for k, v in config.items():
        if hasattr(args, k):
            v = type(getattr(args, k)) (v)
            logger.info('[clerk] updated args. {} to {}'.format(k, v))
            setattr(
                args,
                k, 
                v
            )

def find_row_ind(worker_list, worker_name):
    for i, wi in enumerate(worker_list):
        if len(wi) == 0 or wi.isspace():
            return True, i + 1
        elif not wi.endswith('_finished') and wi == worker_name:
            return False, i + 1
    return True, len(worker_list) + 1

class SpreadsheetClerk(object):
    def __init__(self, rank = None, **kwargs) -> None:
        kwargs = clerk_config_update(**kwargs)
        spreadsheet_entry, worksheet_name, worker_name, credential_path = \
            kwargs['spreadsheet_entry'], kwargs['worksheet_name'], kwargs['worker_name'], kwargs['credential_path']
        
        self._rank = rank

        gspread_succeed = False
        while not gspread_succeed:
            try:
                if isinstance(credential_path, str):
                    self._gc = gspread.service_account(filename=credential_path)
                else:
                    assert isinstance(credential_path, dict)
                    self._gc = gspread.service_account_from_dict(credential_path)

                if spreadsheet_entry.startswith('https'):
                    self._sh = self._gc.open_by_url(spreadsheet_entry)
                else:
                    self._sh = self._gc.open(spreadsheet_entry)
                self._ws = self._sh.worksheet(worksheet_name)
            except gspread.exceptions.APIError as e:
                logger.error('gspread error: 429 RESOURCE_EXHAUSTED! wait 20s')
                time.sleep(20)
            else:
                gspread_succeed = True
        
        self._worker_name = worker_name

        name_list = row_values(self._ws, 1)
        assert name_list[0] == 'worker_name' or ''
        self._name_to_id = {v: i+1 for i, v in enumerate(name_list) if len(v) > 0}
        self._id_to_name = {i: v for v, i in self._name_to_id.items()}
        self._max_col_id = len(name_list)

        rct = get_nonempty_row_ct(self._ws)
        self._worker_row_id = 0
        worker_list = col_values(self._ws, 1)
        while self._worker_row_id == 0:
            self._new_worker_record_added, worker_row_id = find_row_ind(worker_list, self._worker_name)
            if 0 == self._rank:
                update_cell(self._ws, worker_row_id, 1, self._worker_name)
            time.sleep(2)
            worker_list = col_values(self._ws, 1)
            if worker_list[worker_row_id - 1] == self._worker_name:
                self._worker_row_id = worker_row_id
                self._new_row_added = (worker_row_id > rct)

    def record(self, record):
        if 0 == self._rank and '=' in record:
            cell_list = wsrange(self._ws, self._worker_row_id, 1, self._worker_row_id, self._max_col_id)
            changed_cell_list = list()
            record = record.split(';')
            for ri in record:
                ri = ri.split('=')
                if len(ri) == 2:
                    key, value = ri
                    key = key.strip()
                    value = value.strip()
                    if key in self._name_to_id:
                        cell_list[self._name_to_id[key] - 1].value = eval(value)
                        changed_cell_list.append(cell_list[self._name_to_id[key] - 1])
            if len(changed_cell_list) > 0:
                update_cells(self._ws, changed_cell_list)
    
    def get_log_allcolumns(self):
        rows = row_values(self._ws, self._worker_row_id)
        return {self._id_to_name[i + 1]: vi for i, vi in enumerate(rows) if len(vi) > 0 and i < self._max_col_id}
        
    def get_log_columns(self, fields=[]):
        if len(fields) == 0:
            return self.get_log_allcolumns()
        rows = row_values(self._ws, self._worker_row_id)
        return {self._id_to_name[i + 1]: vi for i, vi in enumerate(rows) if len(vi) > 0 and i < self._max_col_id and self._id_to_name[i + 1] in fields}

class ClerkHandler(logging.Handler):

    def __init__(self, clerk):
        logging.Handler.__init__(self)
        self.clerk = clerk

    def emit(self, record):
        msg = record.msg
        if '[clerk]' in msg:
            msg = msg.split('[clerk]')
            if len(msg) == 2:
                self.clerk.record(msg[1])
