import yaml
import os

def read_config(config_path, base_path=None):
    if base_path is None:
        base_path = os.path.join(os.getcwd(), 'autorun_parameters')
    file_path = os.path.join(base_path, config_path)
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)

        raw_data_path = config.get("raw_data_path")
        processed_base = config.get("save_path")
        is_npix = config.get("is_npix")

        additional = config.get("additional_inputs", {})
        command_str_parts = []

        for key, value in additional.items():
            if not value: 
                continue
            if isinstance(value, dict):
                command_str_parts.append(f'{key}: ')
                for param_key, param_val in value.items():
                    command_str_parts.append(f"    '{param_key}': {repr(param_val)}")
            else:
                command_str_parts.append(f"{key}: {value}")

        additional_command_str = "\n".join(command_str_parts)

        return raw_data_path, processed_base, is_npix, additional_command_str
    
    except Exception as e:
        return ['','','','']

    