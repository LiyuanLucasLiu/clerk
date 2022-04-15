import gspread
import logging
import argparse
import time

from .clerk import init_clerk_logger
from .utils import *

logger = logging.getLogger(__name__)

def get_args_add_subparser(name, parser):
    subparser = parser.add_parser(name, description="get train args as argparser format from the spreadsheet", help='get train args as argparser format from the spreadsheet')
    subparser.add_argument('fields', nargs=argparse.REMAINDER, help='fields of interest')
    subparser.add_argument('-ss', '--spreadsheet-entry', required=False, type=str, default="", help='subspace entry')
    subparser.add_argument('-ws', '--worksheet-name', required=False, type=str, default="", help='worksheet name')
    subparser.add_argument('-w', '--worker-name', required=False, type=str, help='worker name')
    subparser.add_argument('-c', '--credential-path', required=False, type=str, default='/home/lucliu/.clerk/clerk.json', help='bot app key credential')
    subparser.set_defaults(func=get_args)

def get_args(args):
    clerk_config = args_to_clerk_config(args)
    clerk = init_clerk_logger(**clerk_config)

    exp_config = clerk.get_log_columns( args.fields )
    argstr = []
    for k, v in exp_config.items():
        argstr.append('--{} {}'.format(k, v))
    print(' ' + ' '.join(argstr) + ' ')

def add_log_add_subparser(name, parser):
    subparser = parser.add_parser(name, description="add log to the current run", help='add log to the current run')
    subparser.add_argument('log', nargs=argparse.REMAINDER, help='define of the search space, format is "acc=0.9 lr=0.01"')
    subparser.add_argument('-ss', '--spreadsheet-entry', required=False, type=str, default="", help='subspace entry')
    subparser.add_argument('-ws', '--worksheet-name', required=False, type=str, default="", help='worksheet name')
    subparser.add_argument('-w', '--worker-name', required=False, type=str, help='worker name')
    subparser.add_argument('-c', '--credential-path', required=False, type=str, default='/home/lucliu/.clerk/clerk.json', help='bot app key credential')
    subparser.set_defaults(func=add_log)

def add_log(args):
    clerk_config = args_to_clerk_config(args)
    init_clerk_logger(**clerk_config)
    logger.info('[clerk] {}'.format(';'.join(args.log)))
    
def new_run_add_subparser(name, parser):
    subparser = parser.add_parser(name, description="conclude a run for a worker", help='conclude a run for a worker')
    subparser.add_argument('-ss', '--spreadsheet-entry', required=False, type=str, default="", help='subspace entry')
    subparser.add_argument('-ws', '--worksheet-name', required=False, type=str, default="", help='worksheet name')
    subparser.add_argument('-w', '--worker-name', required=False, type=str, help='worker name')
    subparser.add_argument('-c', '--credential-path', required=False, type=str, default='/home/lucliu/.clerk/clerk.json', help='bot app key credential')
    subparser.set_defaults(func=new_run)

def new_run(args):
    clerk_config = args_to_clerk_config(args)
    clerk = init_clerk_logger(**clerk_config)
    if not clerk._new_row_added:
        logger.info('[clerk] worker {} finished one run!'.format(updated_clerk_config['worker_name']))
        logger.info("[clerk] worker_name='{}_finished'".format(updated_clerk_config['worker_name']))

def clerk_config_add_subparser(name, parser):
    subparser = parser.add_parser(name, description="add clerk config to ENV", help='add clerk config to ENV')
    subparser.add_argument('-ss', '--spreadsheet-entry', required=True, type=str, help='subspace entry')
    subparser.add_argument('-ws', '--worksheet-name', required=True, type=str, help='worksheet name')
    subparser.add_argument('-w', '--worker-name', required=True, type=str, help='worker name')
    subparser.add_argument('-c', '--credential-path', required=False, type=str, default='/home/lucliu/.clerk/clerk.json', help='bot app key credential')
    subparser.set_defaults(func=clerk_config_write_args)
    return subparser

def search_setup_add_subparser(name, parser):
    subparser = parser.add_parser(name, description="setup the search space", help='setup the grid search space on spreadsheet')
    subparser.add_argument('columns', nargs=argparse.REMAINDER, help='define of the search space, format is "a=[\'a\',2] b=[\'b\',3]"')
    subparser.add_argument('--clean-worksheet', action='store_true', help='clean the worksheet before search, could be dangeous')
    subparser.add_argument('-ss', '--spreadsheet-entry', required=False, type=str, default='', help='subspace entry')
    subparser.add_argument('-ws', '--worksheet-name', required=False, type=str, default='', help='worksheet name')
    subparser.add_argument('-c', '--credential-path', required=False, type=str, default='/home/lucliu/.clerk/clerk.json', help='bot app key credential')
    subparser.set_defaults(func=search_setup)
    return subparser

def search_setup(args):
    clerk_config_args_update(args)

    space = args.columns
    idx_to_name = list()
    idx_to_limit = list()
    idx_to_values = list()
    for si in space:
        si = si.split('=')
        assert len(si) == 2
        si[1] = eval(si[1])
        idx_to_name.append(si[0])
        idx_to_limit.append(len(si[1]))
        idx_to_values.append(si[1])

    gspread_succeed = False
    while not gspread_succeed:
        try:
            if isinstance(args.credential_path, str):
                gc = gspread.service_account(filename=args.credential_path)
            else:
                assert isinstance(args.credential_path, dict)
                gc = gspread.service_account_from_dict(args.credential_path)

            if args.spreadsheet_entry.startswith('https'):
                sh = gc.open_by_url(args.spreadsheet_entry)
            else:
                sh = gc.open(args.spreadsheet_entry)
        except gspread.exceptions.APIError as e:
            logger.error('gspread error: 429 RESOURCE_EXHAUSTED! wait 20s')
            time.sleep(20)
        else:
            gspread_succeed = True

    ws_list = [wsi.title for wsi in sh.worksheets()]

    gspread_succeed = False
    while not gspread_succeed:
        try:
            if args.worksheet_name in ws_list:
                if args.clean_worksheet:
                    sh.del_worksheet(sh.worksheet(args.worksheet_name))
                    ws = sh.add_worksheet(title=args.worksheet_name, rows=100, cols=20)
                    update_cell(ws, 1, 1, 'worker_name')
                    line_idx = 2
                else:
                    ws = sh.worksheet(args.worksheet_name)
                    line_idx = ws.row_count + 1
            else:
                ws = sh.add_worksheet(title=args.worksheet_name, rows=100, cols=20)
                update_cell(ws, 1, 1, 'worker_name')
                line_idx = 2
        except gspread.exceptions.APIError as e:
            logger.error('gspread error: 429 RESOURCE_EXHAUSTED! wait 20s')
            time.sleep(20)
        else:
            gspread_succeed = True
    
    first_column = row_values(ws, 1)
    column_range = len(first_column)

    cells = wsrange(ws, 1, column_range + 1, 1, column_range + len(idx_to_name))
    for i, n in enumerate(idx_to_name):
        cells[i].value = n 
    update_cells(ws, cells)

    idx_list = [0 for _ in range(len(idx_to_name))]
    finished = False
    
    while not finished:
        cells = wsrange(ws, line_idx, column_range + 1, line_idx, column_range + len(idx_to_name))
        for i, vi in enumerate(idx_to_values):
            if len(vi) > 0:
                cells[i].value = vi[idx_list[i]]
        update_cells(ws, cells)
        line_idx += 1
        finished, idx_list = update_idx_list(idx_list, idx_to_limit)

def update_idx_list(idx_list, idx_to_limit):
    idx = len(idx_list) - 1

    while idx >= 0:
        if idx_to_limit[idx] > 0:
            idx_list[idx] += 1
            if idx_to_limit[idx] == idx_list[idx]:
                idx_list[idx] = 0
            else:
                return False, idx_list
        idx -= 1
    return True, idx_list

def run():
    logging.basicConfig(
        format="%(asctime)s | clerk | %(message)s",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Commands', metavar='')

    subcommands = {
            "clerk-config": clerk_config_add_subparser,
            "search-setup": search_setup_add_subparser,
            "new-run": new_run_add_subparser,
            "add-log": add_log_add_subparser,
            "get-args": get_args_add_subparser,
    }

    for name, subcommand in subcommands.items():
        subparser = subcommand(name, subparsers)

    args = parser.parse_args()

    # If a subparser is triggered, it adds its work as `args.func`.
    # So if no such attribute has been added, no subparser was triggered,
    # so give the user some help.
    if 'func' in dir(args):
        args.func(args)
    else:
        parser.print_help()
