from watching.watcher import IctLogWatcher
from anytree import Node
from utils.logger import get_logger
from utils.config import results_table_name, ict_logs_path, server, database, user, password
from parsing.log_file import file_to_tree
from parsing.node import extract_result
from database.db_manager import DbManager
import time


def main():

    logger = get_logger(__name__)

    try:
        #test equipment database manager
        ted = DbManager( 
            server,
            database,
            user,
            password
        )
        ted.connect()


        #callable to handle new ict log files
        def on_new_ict_log(log_path:str):
            root = Node('root')
            time.sleep(3) #app needs to wait 3 seconds for the watcher to stop using the new file
            file_to_tree(log_path, root)
            uut_results = extract_result(root)
            ted.insert(results_table_name, uut_results)

        ict_log_watcher = IctLogWatcher(ict_logs_path, on_new_ict_log)
        ict_log_watcher.start()

    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
    