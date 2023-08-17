#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023 06 23

IMPORTANT NOTICE
-----
Code here might be generated by ChatGPT
and might yet to be tested by human

NOTE ON PATHS
-----
Since we primarily use `pathlib`,
all backslackshes (`\`) in Windows paths MUST be sanitized
to forward slashes (`/`) to avoid issues within a string.

@author: Qiushi (Chris) Tian

Last edit: 2023 08 16
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime

# Define the directory where the FITS files are located
SRC_PATH = Path("D:/Images/Scheduler/Kyle McGregor")
# SRC_PATH = Path("D:/chris-tian/copy-folder-test")

# Define the path for the copied FITS files
DEST_PATH = Path("//tsclient/mountpoint/space-raw")
DEST_PATH = Path("D:/chris-tian/for-jj")
# DEST_PATH = Path("//tsclient/mountpoint/schcopy_test")

# TODO
LOG_ROOT = Path("D:/chris-tian/schcopy-log")

# size of single FITS file
FILE_SIZE = 8395200 # byte

def is_target(observed_object, target):
    '''
    '''
    if all(word.casefold() in observed_object.casefold() for word in target.split()):
        return True

# def shutil_copy(src, dest, *args, copytree_func=copyfile, bufsize=None):
#     pass

def robocopy(src, dest, mt=8):
    dest_parts = "-".join(dest.parts[-2:])
    # timestamp = datetime.now().isoformat()
    log_name = f'robocopy_{dest_parts}.log'#_{timestamp}.log' TODO too long

    robocmd = ['robocopy', str(src), str(dest),
               '/S', '/DCOPY:DX', '/COPY:DX',# '/XN', '/XO',
               f'/MT:{mt}', '/R:0', '/W:0', f'/LOG+:{LOG_ROOT / log_name}']
    roboproc = subprocess.run(robocmd, shell=True, stdout=subprocess.DEVNULL) # supress console printing
    # print(f'robocopy returns {roboproc.returncode}')
    # print(roboproc.stdout)
    # print(roboproc.stderr)

    # handling robocopy error
    if roboproc.returncode >= 8:
        print('\n********** robocopy error **********')
        # print(robocmd)
        # print(f'Return code = {roboproc.returncode}')
        # print(roboproc.stdout) # commented out because of stdout redirected to DEVNULL
        print(roboproc.stderr)
        print()
        raise subprocess.CalledProcessError(roboproc.returncode, robocmd)

    # no error, echo by returning
    return f'robocopy {roboproc.returncode} {src}'

def copy(src, dest, copyfunc=robocopy, *args, **kwargs):
    return copyfunc(src, dest, *args, **kwargs)

def copycalib(date):
    SRC = Path('D:/Images')
    # SRC = Path('D:/chris-tian/copy-folder-test/Images')

    DST = Path('//tsclient/mountpoint/space-raw/calib')
    DST = Path("D:/chris-tian/for-jj/calib")
    # DST = Path('//tsclient/mountpoint/schcopy_test/Calib')

    if (SRC / date).exists():
        # TODO if we want to figure out whether calib frames are copied or not,
        #      we need return values from `copy`
        # TODO NEW good option is to count how many files are copied,
        #          and return it. so now nfile would include calibs
        return 'calib ' + copy(SRC / date, DST / date)
        # TODO NEW NEW maybe pass a pointer of a dict of copied calib dates?
    else: # if date folder doesn't exist
        return 'calib NO ' + date

def read_log():
    pass

def write_log():
    pass

if __name__ == '__main__':
    today = int(datetime.now().strftime('%Y%m%d'))
    start = 0
    end = today - 2

    import sys
    if len(sys.argv) < 2 or sys.argv[1] in ['h', '/h', '-h', '--h', r'\h', 'help', '/help', '-help', '--help', r'\help']:
        print('Usage: python **/schcopy.py <target_name_separate_by_space_QUOTED> [<start_date_inclusive>] [<end_date_exclusive>]')
        sys.exit(0)
    input_target = sys.argv[1]
    target_san = input_target.replace('_', ' ').replace('-', ' ')
    if len(sys.argv) >= 3:
        start = int(sys.argv[2])
    if len(sys.argv) >= 4:
        end = int(sys.argv[3])

    dates = set()
    # TODO `calib_dates` is only a temporary implementation (see below)
    calib_dates = {'20230409', '20230319', '20230613', '20230530', '20230421', '20230329', '20230628', '20221213', '20230701', '20230326', '20230321', '20230118', '20230128', '20230218', '20230320', '20230705', '20230707', '20230427', '20230224', '20230629', '20230627', '20230330', '20230525', '20230117', '20221225', '20230425', '20230407', '20230220', '20230505', '20230419', '20230417', '20230324', '20221208', '20230410', '20221128', '20230610', '20221214', '20230131', '20230225', '20230531', '20230216', '20230318', '20230226', '20230213', '20230221', '20230524', '20221224', '20230402', '20230523', '20230316', '20230601', '20230423', '20230522', '20230426', '20230706', '20230328', '20230311', '20230315', '20230506'}
    calib_dates = set()
    nfile = 0

    # TODO read log and skip already copied
    # with read_log and write_log

    # create
    # what is that?

    # TODO os.scandir os.listdir Path.iterdir??
    excepted = None
    try:
        # loop through date-named subdirs
        for date_path in SRC_PATH.iterdir():
            # skip non-folders
            if not date_path.is_dir():
                continue

            # VARIBLE date string
            date = date_path.name

            # skip non-date folders
            if not date.startswith('20'):
                continue

            # date range
            datenum = int(date)
            if datenum < start or datenum >= end:
                continue

            # loop through targets of the day
            for target_path in date_path.iterdir():
                # skip non-folders
                if not target_path.is_dir():
                    continue

                target = target_path.name

                # skip non-targets folders
                if not is_target(target, input_target):
                    continue

                # record date of file being copied
                dates.add(date)

                # number of files
                n = len(list(target_path.iterdir()))
                if n < 1: # skip emplty dir
                    continue
                nfile += n

                # COPYING
                dest = DEST_PATH / target_san / date # TODO folder name should contain commentary info
                os.makedirs(dest, exist_ok=True)
                print(copy(target_path, dest))
                if date not in calib_dates:
                    print(copycalib(date), end='\n\n')
                    calib_dates.add(date)
                else:
                    print(f'calib DONE {date}', end='\n\n')
    except Exception as e:
        excepted = e

    if len(dates):
        # sort dates
        sorted_dates = sorted(dates)

        # TODO add creating file header

        # write file
        log_path = LOG_ROOT / datetime.now().isoformat().replace('.', '_').replace(':', '-')
        os.makedirs(log_path)
        with open(log_path / f'schcopy_{target_san}.log', mode='a') as f:
            f.writelines(date + '\n' for date in sorted_dates[:-1])
            f.write(f'{sorted_dates[-1]}\t{datetime.now().isoformat()}\t{nfile}\n')

        # get total size
        total_size = [nfile * FILE_SIZE / 1024 / 1024 / 1024, 'GB']
        if total_size[0] < 1:
            total_size[0] *= 1024
            total_size[1] = 'MB'

        # print result stat
        try:
            print('\n---------------- Run Concluded ----------------')
            print('Science copied:', sorted_dates)
            print('Calib copied:', calib_dates)
            print(f'{nfile} sicence file(s) copied, estimated to be {total_size}\n')
        except NameError:
            pass
    else:
        print('\n---------------- Run Concluded ----------------')
        print('NOTHING COPIED!!')

    if excepted:
        raise excepted
