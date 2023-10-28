import argparse
import yaml
from dotenv import load_dotenv
from .patcher.patcher import patch
from .patcher.patcher import get_available_operations

load_dotenv()

def load_config(config_file):
    print(f"Loading config from {config_file}")
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def main():
    parser = argparse.ArgumentParser(description="Anki Patcher")
    parser.add_argument('action', help="The action to perform", choices=['patch', 'list'])
    parser.add_argument('-c', '--config', help="Path to the YML configuration file for the operation")
    parser.add_argument('-o', '--operation', help="The operation to perform")
    args = parser.parse_args()

    if args.action == 'patch':
        if not args.config or not args.operation:
            parser.error("the following arguments are required for patch: --config, --operation")
        operation_name = args.operation
        config = load_config(args.config)
        available_operations = get_available_operations()
        if operation_name not in available_operations:
            print(f"Operation {operation_name} not recognized")
            print(f"Available operations: {available_operations}")
            return
        patch(operation_name + "_operation", config)
    
    elif args.action == 'list':
        available_operations = get_available_operations()
        print(f"Available operations: {available_operations}")

if __name__ == "__main__":
    main()
