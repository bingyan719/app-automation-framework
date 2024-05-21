
import time

from ui.utils.log import Logging
from ui.cli.arg_parse import parse_args
from ui.cli.arg_init import init_args
from ui.utils.version import print_version
from ui.cli.runner import run


def main(argv=None):
    start_time = int(time.time())
    print_version()
    # 解析命令行参数
    args = parse_args()
    init_args(args)
    # engine start
    run()
    end_time = int(time.time())
    Logging.info('cost time: {}s'.format(end_time - start_time))

if __name__ == '__main__':
    main()