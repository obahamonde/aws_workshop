from aws_framework import CloudAPI
from aws_framework._apprunner import AppRunner, Ecr, ServiceConfigurationT
from aws_framework._types import *

app = CloudAPI()
ecr = Ecr()

# Create a new AppRunner service

runner = AppRunner()

# Create API Endpoints


@app.get("/api/services")
async def get_services(params: ServiceConfigurationT):
    return await runner.create_service(params)
