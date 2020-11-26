def get_log_to_file(filename):

    def get_log_to (function):

        def create_recording(*args, **kwargs):
            result = function(*args, **kwargs)
            string_for_log = result.result_to_str()
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f'{string_for_log[0]}'+ '\n')
                f.write(f'{string_for_log[1]}'+ '\n')
                f.write(f'------------------------------------------------------------------'+ '\n')
            return result

        return create_recording

    return get_log_to