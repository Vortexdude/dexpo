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

2. Go to the project Directory
    ``` bash
   cd dexpo
   ```

3. Install dependencies:

    ```bash
    make install 
    ```

## Configuration

Before running the script, you need to configure the AWS credentials and other necessary parameters in project home directory or user home direcotry
</br>

JSON configuration file (`dexpo/config/config.json`). Example configuration:


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

Make sure to create aws credentials file in the user home directory or project home directory.
example - 
``` bash
ls ~/.aws/credentials
ls ./dexpo/.aws/credentils
```
or set the Environment variable

``` bash
export aws_access_key_id=''
export aws_secret_access_key=''
```

## Usage

To create AWS infrastructure:

```bash
make apply
```

To delete AWS infrastructure:

```bash
make destroy
```

## Contributing

Contributions are welcome! Feel free to open issues or pull requests for any improvements or bug fixes.
