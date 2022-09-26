# method to return relative frequency of step value
def get_stage_woa_rel_adj(data, tr, i):
    foc_data = data[data.treatment == tr]
    try:
        foc_val = foc_data["stage_woa_rel_adj"].value_counts()[i]/len(foc_data)
    except KeyError:
        foc_val = 0
    return foc_val


# method for number formatting in German
def format_german_number(number, precision=0):
    # build format string
    format_str = '{{:,.{}f}}'.format(precision)

    # make number string
    number_str = format_str.format(number)

    # replace chars
    return number_str.replace(',', 'X').replace('.', ',').replace('X', '.')