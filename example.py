rapidsubproductsexport = "ExamplesubproductsfromRAPID.xlsx"

from gannt_data_prep import formatRAPIDproductsforGG,formatforGG

prod = formatRAPIDproductsforGG(rapidsubproductsexport)
dump = formatforGG(prod)