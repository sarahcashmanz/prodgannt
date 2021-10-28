"""
This module houses functions for converting exported product data in .xlsx format
from EPA/ORD's RAPID system into a Google Chart GANNT format
https://developers.google.com/chart/interactive/docs/gallery/ganttchart#data-format
"""

import pandas as pd
import argparse
import os
import json

GGcols = ['Task ID',
          'Task Name',
          'Start',
          'End',
          'Resource',
          'Duration',
          'Percent Complete',
          'Dependencies']

def convertFYQtodate(fyq):
   """
   Converts a pandas Series with string values like 'FY22 Q4' to dates
   :param fyq:
   :return:
   """
   qs = fyq.str.replace('FY', '20')
   qs = qs.str.replace(' ','-')
   dt = pd.PeriodIndex(qs, freq='Q').to_timestamp()
   dt = dt + pd.offsets.QuarterEnd(0)
   return dt

def convertFYQfieldstodates(df):
    fields = ['Product Planned Delivery Date','Subproduct Delivery FY-Quarter']
    for f in fields:
        if f in df.columns:
            df[f] = convertFYQtodate(df[f])
    #convert timestamps to dates
    othdate = "Product Start Date"
    if othdate in df.columns:
        fields.append(othdate)
    for f in fields:
        df[f] = pd.to_datetime(df[f])
        df[f] = df[f].dt.strftime("%Y-%m-%d")
    return df

def split_id_from_name(id_w_name):
    df = id_w_name.str.split(':',n=1,expand=True)
    return df

def select_product_or_subproduct_fields(row):
    """
    Adds a Task field to a row and assigns it product or subproduct name
    :param row:
    :return:
    """
    if pd.isnull(row["Subproduct"]):
        row['Task'] = row['Product']
        row['End'] = row['Product Planned Delivery Date']
        row["Resource"] = "Product"
    else:
        row['Task'] = row['Subproduct']
        row['End'] = row['Subproduct Delivery FY-Quarter']
        row["Resource"] = "Subproduct"
    row['Start'] = row['Product Start Date']
    return(row)

def merge_product_subproduct(df):
    df['Resource'] = ''
    df = df.apply(select_product_or_subproduct_fields, axis=1)
    return(df)

def splitnamefields(df):
    fields = ['Task']
    for f in fields:
        if f in df.columns:
            df_id_name = split_id_from_name(df[f])
            df_id_name.columns = ['Task ID','Task Name']
            df = df.drop(columns=f)
            df = pd.concat([df,df_id_name],axis=1)
    return df

def loadandcleanRAPIDexport(rapidsubproductsexport):
    """
    :param rapidsubproductsexport: an Excel file name with ".xlsx" extention
    :return:
    """
    exportfile = os.path.realpath("../gannt_data/"+ rapidsubproductsexport)
    df = pd.read_excel(exportfile,na_values=["-"])
    df = convertFYQfieldstodates(df)
    df = merge_product_subproduct(df)
    df = splitnamefields(df)
    return df

def formatRAPIDproductsforGG(rapidsubproductsexport):
    """
    :param rapidsubproductsexport: an
    :return:
    """
    df = loadandcleanRAPIDexport(rapidsubproductsexport)
    df["Duration"] = None
    df["Percent Complete"] = None
    df["Dependencies"] = None
    df = df[GGcols]
    df = df.drop_duplicates()
    return df

def formatforGG(df):
    #convert timestamps to simple date

    dl = df.values.tolist()
    cols = df.columns.tolist()
    dl.insert(0,cols)
    title = "Gannt"
    #tempdata = json.dumps(dl)
    return tempdata

#Code for running this module directly appopriate for integration into a Flask app
# if __name__ == '__main__':
#
#     parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
#     parser.add_argument('-F', '--File', help = 'The file to extract from.',
#                         default = 'RAPIDsubproductexport.xlsx',
#                         required = True)
#     args = parser.parse_args()
#     formatRAPIDproductsforGG(args.File)

