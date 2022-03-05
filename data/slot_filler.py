"""
A simple script which uses name dataframes and templates to do slot filling.
Templates are of the format that each new sentence is seperated by a newline.

arg1 = input directory where the names data can be found
arg2 = output directory to save slot-filled datasets
arg3 = template file location
"""

import sys
import os
import re
import pandas as pd
from jinja2 import Template


def parse_templates(template_file):
    result = list()
    temp = ''
    with open(template_file, 'r') as tfile:
        data = tfile.read().splitlines()
    return data


def slot_filler(templates, attribute_df, name_col, group_col, gender_col=None):  # TODO: think about labels
    """
    :param template_df: Dataframe with template slots
    :param attribute_df: Dataframe with names
    :param name_col: Column with names
    :param group_col: Column with race/ethnicity
    :param gender_col: Column with gender
    :return: list of dictionaries with slot filled templates and other information
    """
    result = list()
    template_id = 0
    for sentence in templates:
        template_id += 1
        current = sentence
        start_ix = re.search('{', current).start()
        for _, srow in attribute_df.iterrows():
            category = srow[group_col]
            if not pd.isnull(category):
                if name_col:
                    name = srow[name_col]
                else:
                    name = srow['first_name'] + ' ' + srow['last_name']
                end_ix = start_ix + len(name)
                filled_template = Template(current).render({'Name': name})
                record = {'Text': filled_template, 'Name': name, 'Group': category,
                          'Start_index': start_ix, 'End_index': end_ix, 'TemplateId': template_id}
                if gender_col:
                    record['Gender'] = srow[gender_col]
                result.append(record)
    return result


input_dir = sys.argv[1]
output_dir = sys.argv[2]
templates_file = sys.argv[3]

templates = parse_templates(templates_file)

# map of filename to columns for name, ethnicity, and gender demographics where available
name_files = {"LAR_1.csv": ("GivenName", "Ethnicity", None),
              "LAR_2.csv": ("GivenName", "Ethnicity", None),
              "NY.csv": ("GivenName", "Ethnicity", "Gender"),
              "congress.csv": (None, "race_ethnic_group", "gender")}

files = os.listdir(input_dir)
for file, cols in name_files.items():
    print(f"Processing {file}...")
    names_df = pd.read_csv(os.path.join(input_dir, file))
    filled_slots = slot_filler(templates, names_df, cols[0], cols[1], cols[2])
    slotted_df = pd.DataFrame(filled_slots)
    slotted_df.to_csv(os.path.join(output_dir, file))
