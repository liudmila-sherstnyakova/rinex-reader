def parse_number_with_exception(parse_function, arg, exception_msg: str):
    try:
        return parse_function(arg)
    except ValueError as exc:
        raise ValueError(exception_msg) from exc


def str2float(string: str, exception_msg: str):
    return parse_number_with_exception(float, string, exception_msg)


def str2int(string: str, exception_msg: str):
    return parse_number_with_exception(int, string, exception_msg)
