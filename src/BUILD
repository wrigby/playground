python_requirement('flask')
python_requirement('influxdb')

python_binary(
    name = "slow_service",
    source = "slow_service.py",
    dependencies = [
        ":flask",
        ":influxdb"
    ]
)
