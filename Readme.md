# AWS Cloud Infrastructure Management using Boto3 and REST API with Python

This repository contains a Python script that utilizes Boto3, the AWS SDK for Python, to create and delete AWS cloud infrastructure. The script also utilizes a REST API for interaction and takes configuration details from a JSON file.

## Requirements

- Python 3.x
- Boto3 library
- AWS account with appropriate permissions
- JSON configuration file with required parameters

## Installation

1. Clone this repository to your local machine:

    ```bash
    git clone https://github.com/Vortexdude/dexpo
    ```

2. Create virtual environment
    ``` bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

    ```bash
    pip3 install -r requirements.txt 
    ```

## Configuration

Before running the script, you need to configure the AWS credentials and other necessary parameters in the JSON configuration file (`devops/env/config.json`). Example configuration:

```json
{
    "vpcs": [
        {
            "vpc": {
                "name": "boto3-testing",
                "state": "present",
                "dry_run": "True",
                "region": "ap-south-1",
                "cidr_block": "10.0.0.0/16"
            },
            "route_tables": [
                {
                    "name": "public-route-table",
                    "state": "present",
                    "DestinationCidrBlock": "0.0.0.0/0"
                },
                {
                    "name": "private-route-table",
                    "state": "present"
                }
            ],
            "internet_gateway": {
                "name": "boto3-testing-ig",
                "state": "present"
            },
            "subnets": [
                {
                    "name": "public-A-boto3",
                    "state": "present",
                    "cidr": "10.0.20.0/24",
                    "zone": "a",
                    "route_table": "public-route-table"
                },
                {
                    "name": "private-A-boto3",
                    "state": "present",
                    "cidr": "10.0.255.0/24",
                    "zone": "b",
                    "route_table": "private-route-table"
                }
            ],
            "security_groups": [
                {
                    "name": "boto3-testing-sg",
                    "description": "For Boto3-testing",
                    "state": "present",
                    "permissions": [
                        {
                        "FromPort": 22,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {
                                "CidrIp": "0.0.0.0/0",
                                "Description": "SSH Access"
                            }
                        ],
                        "ToPort": 22
                }
                    ]

                }
            ]
        }
    ],
    "ec2": [
        {
            "name": "fd",
            "state": "present",
            "instance_type": "t2.micro",
            "ami": "ami-0a7cf821b91bcccbc",
            "subnet": "public-A-boto3",
            "key_file": "nns",
            "region": "ap-south-1",
            "vpc": "boto3-testing",
            "security_groups": ["boto3-testing-sg"]
        }
    ]
}
```

Make sure to replace placeholders with your actual AWS credentials and other relevant information.

## Usage

Run the Python script (`main.py`) with the following commands:

To create AWS infrastructure:

```bash
pythone main.py apply
```

To delete AWS infrastructure:

```bash
pythone main.py destroy
```

## Contributing

Contributions are welcome! Feel free to open issues or pull requests for any improvements or bug fixes.
