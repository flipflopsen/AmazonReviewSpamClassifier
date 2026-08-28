import functools
import itertools

import ijson
import io
from enum import Enum
import string
import concurrent
from concurrent.futures import ProcessPoolExecutor
from itertools import chain
from nltk.tokenize import RegexpTokenizer


class JsonFilter(Enum):
    Standard_Keys = ['_id', '_id.$oid', 'asin', ' ', '', 'None', ' None']
    Standard_Values = ['_id', '_id.$oid', 'asin']
    Standard_Keys_No_ReviewTime = ['_id', '_id.$oid', 'asin', 'unixReviewTime', ' ', '', 'None', ' None']
    Standard_Values_No_ReviewTime = ['_id', '_id.$oid', 'asin', 'unixReviewTime']
    Standard_Keys_ASIN_No_ReviewTime = ['_id', '_id.$oid', 'unixReviewTime', ' ', '', 'None', ' None']
    Standard_Values_ASIN_No_ReviewTime = ['_id', '_id.$oid', 'unixReviewTime']
    Blank_Filter = [' ', '', 'None', ' None']

    def as_list(self):
        try:
            return list(self.value)
        except TypeError:
            return [str(self.value)]


def read_json(json_path, lines_to_read, json_keys_filter, json_values_filter):
    json_data = []

    with open(json_path, 'r') as json:
        ctr = 0
        for line in json:
            file_entry = io.StringIO(line)
            parser = ijson.parse(file_entry)
            row = []
            is_ok = True
            for prefix, ev, value in parser:
                if (prefix not in (json_keys_filter.as_list() or None)) and (value not in (json_values_filter.as_list() or None)):
                    #Cleanup \ and ' which both can cause errors in while parsing or doing sql
                    if ev == 'string' and '\\' in value:
                        value = value.replace('\\', '')
                    if ev == 'string' and '\'' in value:
                        value = value.replace('\'', '')

                    if prefix == 'reviewTime':
                        value = value.replace(',', '').replace(' ', '.')

                    if prefix == 'reviewText':
                        if len(value) < 90:
                            is_ok = False
                        else:
                            value = value.lower().replace('[^\w\s]', '')
                            value = "".join([char for char in value if char not in string.punctuation])

                    if prefix == 'reviewerName':
                        if len(value) < 1:
                            is_ok = False

                    if not (ev == 'start_array' or ev == 'end_array'):
                        row.append(value)
            if len(row) > 1 and is_ok:
                #print(row)
                json_data.append(row)

            ctr = ctr + 1
            if (ctr >= lines_to_read):
                break

    return json_data
