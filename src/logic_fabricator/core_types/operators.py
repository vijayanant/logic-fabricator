def op_set(current_value, new_value):
    return new_value


def op_increment(current_value, new_value):
    return (current_value or 0) + new_value


def op_decrement(current_value, new_value):
    return (current_value or 0) - new_value


def op_append(current_value, new_value):
    current_list = list(current_value or [])
    current_list.append(new_value)
    return current_list
