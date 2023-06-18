from typing import Generator


def aws_parse(items:list)->dict:
    return {item['Name']:item['Value'] for item in items}
    