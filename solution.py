import datetime
import time
import json

def transform_value(key, value):
    if key == 'N':
        value = value.strip()
        # Remove leading zeros
        value = value.lstrip('0') or '0'  # ensure at least '0' if all are zeros
        try:
            return True, int(value)
        except ValueError:
            return False, None
    elif key == 'S':
        value = value.strip()
        if not value:
            return False, None
        try:
            # Check if the string is in RFC3339 format
            parsed_time = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            return True, int(time.mktime(parsed_time.timetuple()))
        except ValueError:
            return True, value
    elif key == 'BOOL':
        value = value.strip().lower()
        if value in {'1', 't', 'true'}:
            return True, True
        elif value in {'0', 'f', 'false'}:
            return True, False
        return False, None  # Omit invalid Boolean values
    elif key == 'NULL':
        value = value.strip().lower()
        if value in {'1', 't', 'true', 1}:
            return True, None
        elif value in {'0', 'f', 'false', 0}:
            return False, None
        return False, None
    elif key == 'L':
        if isinstance(value, list):
            transformed_list = [
                transform_value(item_type, item_value)
                for item in value
                if isinstance(item, dict) for item_type, item_value in item.items()
            ]
            # Remove None values and empty strings, maintain order
            res =  [item for res, item in transformed_list if  res ]
            if res:
                return True, res 
            else:
                return False, res
    elif key == 'M':
        res =  transform_json(value)
        if res:
            return True, res 
        else:
            return False, res 
    return False, None

def transform_json(input_json):
    output_json = {}
    for key, value in input_json.items():
        key = key.strip()  # Sanitize key
        if not key:  # Omit empty keys
            continue
        for data_type, data_value in value.items():
            valid, transformed_value = transform_value(data_type, data_value)
            if valid:  # Omit invalid fields
                output_json[key] = transformed_value
                break  # Only the first valid transformed value is taken
    return output_json

if "__main__" == __name__: 

    # Transform the input JSON
    file_path = "input.json"
    output_path = "output.json"
    output_json = transform_json(json.load(open(file_path)))
    print(output_json)
    # Print the transformed output
    json.dump(output_json, open(output_path,"w"), indent=4)
