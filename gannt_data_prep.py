import pandas as pd
import argparse
import os
import json

products_to_GG_mapping = {
    "Product":"Task ID",
    "Product Start Date":"Start",
    "Product Planned Delivery Date":"End",
}

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


# def merge_names(row):
#     print(row)
#     if row["Subproduct"]=='nan':
#         row['Task']=row['Product']
#     else:
#         row['Task'] = row["Subproduct"]
#     return(row)
#
# def merge_product_subproduct(df):
#     df['Resource'] = ''
#     df = df.apply(merge_names)
#     return(df)

def splitnamefields(df):
    fields = ['Product', 'Subproduct']
    for f in fields:
        if f in df.columns:
            df_id_name = split_id_from_name(df[f])
            df_id_name.columns = ['Task_ID','Task_Name']
            df = df.drop(columns=f)
            df = pd.concat([df,df_id_name],axis=1)
    return df

def loadandcleanRAPIDexport(rapidsubproductsexport):
    """
    :param rapidsubproductsexport: an Excel file name with ".xlsx" extention
    :return:
    """
    exportfile = os.path.realpath("gannt_data/"+ rapidsubproductsexport)
    df = pd.read_excel(exportfile,na_values=["-"])
    df = convertFYQfieldstodates(df)
    #df = merge_product_subproduct(df)
    df = splitnamefields(df)
    return df

def formatRAPIDproductsforGG(rapidsubproductsexport):
    """
    :param rapidsubproductsexport: an
    :return:
    """
    df = loadandcleanRAPIDexport(rapidsubproductsexport)
    df = df.rename(columns=products_to_GG_mapping)
    # Convert the quarters for product end
    df["Task Name"] = df["Task_ID"]
    df["Resource"] = None
    df["Duration"] = None
    df["Percent Complete"] = None
    df["Dependencies"] = None
    df = df[GGcols]
    df = df.drop_duplicates()
    return df


    #df.to_csv("ganntdata/producttimetable.csv",index=False)
    #get as json

def formatforGG(df):
    #convert timestamps to simple date

    dl = df.values.tolist()
    cols = df.columns.tolist()
    dl.insert(0,cols)
    title = "Gannt"
    tempdata = json.dumps({'title':title,'data':dl})
    return tempdata

if __name__ == '__main__':

    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    parser.add_argument('-F', '--File', help = 'The file to extract from.',
                        default = 'RAPIDsubproductexport.xlsx',
                        required = True)
    args = parser.parse_args()
    formatRAPIDproductsforGG(args.File)

