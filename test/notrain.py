import argparse
import logging

from clerk import init_clerk_logger, update_args_w_clerk

logging.basicConfig(
    format="%(asctime)s | clerk | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lr', type=float, default=1.)
    parser.add_argument('--bs', type=int, default=1)
    parser.add_argument('--wr', type=float, default=1.)
    args = parser.parse_args()

    clerk = init_clerk_logger()
    logger.info('ini args')
    logger.info(args)
    logger.info('post args')
    update_args_w_clerk(args, clerk)
    logger.info(args)

    logger.info('add log about test acc')
    logger.info('[clerk] train_loss=-1; test_acc=0.8')

    