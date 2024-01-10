from anytree import Node
from pandas import DataFrame
import pandas as pd
from datetime import datetime

def extract_result(node:Node):
    for batch in node.children:
        batch
        batch_data =  batch.data.split("|")
        for btest in batch.children:
            test_data = btest.data.split("|")
            

            return [
                batch_data[0], # product name
                batch_data[9], # part number
                datetime.strptime(test_data[2], "%y%m%d%H%M%S"), #start test datetime
                datetime.strptime(test_data[9], "%y%m%d%H%M%S"), #end test datetime
                "1" if test_data[1] == "00" else "0", # if diferent to "00", is a failure
            ]


def extract_failures(node:Node):
    pass #TODO