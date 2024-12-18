import yaml

def read_yaml_configuration(file_name):
    """
    Reads a YAML configuration file and returns its content as a Python dictionary.

    Args:
        file_name (str): The name of the YAML file to be read.

    Returns:
        dict or None: A dictionary containing the YAML configuration if successful, 
        or None if there was an error or the file was not found.
    """
    try:
        with open(file_name, 'r') as file:
            configuration = yaml.load(file, Loader=yaml.FullLoader)
            return configuration
    except FileNotFoundError:
        print(f"The file '{file_name}' was not found.")
        return None
    except Exception as e:
        print(f"Error while reading the file '{file_name}': {str(e)}")
        return None

def convert_to_list_of_tuples(configuration):
    """
    Converts a YAML configuration into a list of tuples in the specified format.

    Args:
        configuration (dict): The YAML configuration represented as a dictionary.

    Returns:
        list: A list of tuples where each tuple represents a block with its label 
        and a list of tuples for the fields within that block.
    """
    field_info_list = []
    
    for block in configuration:
        block_name = block['block_name']
        lines = block['lines']
        block_info = (block_name, [])
        
        for line in lines:
            fields = line['fields']
            field_info = []
            
            for field in fields:
                width = field['width']
                label = field['label']
                field_info.append((width, label))
            
            block_info[1].append(field_info)
        
        field_info_list.append(block_info)
    
    return field_info_list

# Example of usage
if __name__ == "__main__":
    yaml_file = "../data/yml/form.yaml"  # Replace with the actual YAML file name
    configuration = read_yaml_configuration(yaml_file)
    
    if configuration:
        list_of_tuples = convert_to_list_of_tuples(configuration)
        print(list_of_tuples)
