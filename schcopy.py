#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023 06 23

NOTE ON PATHS
-----
Since we primarily use `pathlib`,
all backslackshes (`\`) in Windows paths MUST be sanitized
to forward slashes (`/`) to avoid issues within a string.

@author: Qiushi (Chris) Tian

Contact: qtian [at] wesleyan [dot] edu

Last edit: 2024 05 06
"""

import os
import subprocess
import shutil
import pyfastcopy  # optional
from pathlib import Path
from datetime import datetime

# Define the directory where the FITS files are located
SRC_PATH = Path('[REPLACE_VALUE]')

# Define the path for the copied FITS files
DEST_PATH = Path('[REPLACE_VALUE]')

# Define the directory where original date folders of calib files are located
CALIB_SRC = Path('[REPLACE_VALUE]')

# Define the path where teh copied calib files will go to
CALIB_DST = Path('[REPLACE_VALUE]')

# Define the directory to put log files
LOG_ROOT = Path('[REPLACE_VALUE]')

# size of single FITS file
FILE_SIZE = 8395200 # byte

# calib dates copied
calib_dates = set()

def is_target(observed_object, target):
    '''
    '''
    if all(word.casefold() in observed_object.casefold() for word in target.split()):
        return True

def shutil_copy(src, dest, *args, copytree_func=shutil.copyfile, bufsize=None):
    return str(shutil.copytree(src, dest, dirs_exist_ok=True))

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

def copy(src, dest, copyfunc=shutil_copy, *args, **kwargs):
    return copyfunc(src, dest, *args, **kwargs)

def copycalib(date):
    src_w_date = CALIB_SRC / date
    dest_w_date = CALIB_DST / date

    # skip if has date folder AND folder has file
    if dest_w_date.exists() and len(list(dest_w_date.rglob('*.*'))) > 0:
            return 'CALIB EXISTS for ' + date
        
    if src_w_date.exists() and len(list(src_w_date.rglob('*.*'))) > 0:
        # TODO if we want to figure out whether calib frames are copied or not,
        #      we need return values from `copy`
        # TODO NEW good option is to count how many files are copied,
        #          and return it. so now nfile would include calibs
        calib_dates.add(date)
        return 'CALIB COPIED to ' + copy(src_w_date, dest_w_date)
        # TODO NEW NEW maybe pass a pointer of a dict of copied calib dates?
    else: # if date folder doesn't exist
        return 'NO CALIB FOUND for ' + date

def read_log():
    pass

def write_log():
    pass

if __name__ == '__main__':
    today = int(datetime.now().strftime('%Y%m%d'))
    start = 0
    end = today - 2
    sorted_dates = 0
    total_size = 0

    import sys
    if len(sys.argv) < 2 or sys.argv[1] in ['h', '/h', '-h', '--h', r'\h', 'help', '/help', '-help', '--help', r'\help']:
        print('Usage: python **/schcopy.py <target name> [<start date (inclusive)>] [<end date (exclusive)>]')
        sys.exit(0)
    input_target = sys.argv[1]
    target_san = input_target.replace('_', ' ').replace('-', ' ')
    if len(sys.argv) >= 3:
        start = int(sys.argv[2])
    if len(sys.argv) >= 4:
        end = int(sys.argv[3])

    dates = set()

    nfile = 0

    # TODO read log and skip already copied
    # with read_log and write_log

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
            date = date.split('-')[0].split('_')[0]

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
                if not is_target(target, target_san): # was input_target 20240418
                    continue

                # number of files
                n = len(list(target_path.iterdir()))
                if n < 1: # skip emplty dir
                    continue

                # COPYING
                dest = DEST_PATH / target_san / date # TODO folder name should contain commentary info trailing in the original folder name
                try:
                    os.makedirs(dest, exist_ok=False)
                    print(copy(target_path, dest))

                    # record date and number of files being copied
                    dates.add(date)
                    nfile += n

                except FileExistsError:
                    print(f'{date} already exists, none copied')

                # attemp to copy calib
                print(copycalib(date), end='\n\n')

        # sort dates
        sorted_dates = sorted(dates)

        # TODO add creating file header

        # write file
        log_path = LOG_ROOT / datetime.now().isoformat().replace('.', '_').replace(':', '-')
        os.makedirs(log_path)
        with open(log_path / f'schcopy_{target_san}.log', mode='a') as f:
            if len(sorted_dates) > 1:
                f.writelines(date + '\n' for date in sorted_dates[:-1])
                f.write(f'{sorted_dates[-1]}\t{datetime.now().isoformat()}\t{nfile}\n')
            else:
                f.write('No science frame copied\n')

        # get total size
        total_size = [nfile * FILE_SIZE / 1024 / 1024 / 1024, 'GB']
        if total_size[0] < 1:
            total_size[0] *= 1024
            total_size[1] = 'MB'
    except Exception as e:
        excepted = e

    # print result stat
    print('\n---------------- Run Concluded ----------------\n')
    print(f'Target matching identifier: {target_san}', end='\n\n')
    print('Science copied:', sorted_dates, end='\n\n')
    if nfile > 1:
        print(f'There were {nfile} science frames copied, estimated to be {total_size[0]} {total_size[1]}.\n')
    elif nfile == 1:
        print(f'There was only one science frame copied... Are you sure???.\n')
    else:
        print(f'No science frame copied at all... What have you done!\n')
    
    print('Calib copied:', calib_dates, end='\n\n')
    print(f'There {len(calib_dates)} days of calib copied.\n')

    if excepted:
        raise excepted
