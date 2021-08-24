rapidsubproductsexport = "ExamplesubproductsfromRAPID.xlsx"

from gannt_data_prep import formatRAPIDproductsforGG,formatforGG

prod = formatRAPIDproductsforGG(rapidsubproductsexport)
formatforGG(prod)