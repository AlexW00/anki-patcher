import os

def parse_env(vars):
    env_values = []
    for var in vars:
        value = os.getenv(var)
        if not value:
            raise Exception(f"Environment variable {var} must be set")
        env_values.append(value)
    return env_values

def parse_config(props, config):
    config_values = []
    for prop in props:
        value = config.get(prop)
        if not value:
            raise Exception(f"Config must specify {prop}")
        config_values.append(value)
    return config_values

def parse_fields(field_names, fields):
    field_values = []
    for field_name in field_names:
        field_value = fields[field_name].get("value")
        if field_name == None:
            raise Exception(f"Field {field_name} must be set")
        field_values.append(field_value)
    return field_values