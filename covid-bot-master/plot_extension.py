import os
from pathlib import Path
import datetime


def get_binary(plt, log, name):
    file_path = f'output/{name}{str(datetime.datetime.now().timestamp())}.png'
    plt.savefig(file_path, dpi=150, bbox_inches='tight')

    log.info(f'<{file_path}> saved')
    binary_file = Path(file_path).read_bytes()
    os.remove(file_path)
    log.info(f'<{file_path}> removed')

    return binary_file

