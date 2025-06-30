
1. Active virtual environment
`
$source .venv/bin/active

`

2. Run migrations, create super admin and load fixtures

`
$python manage.py migrate
$python manage.py createsuperuser
$python .\manage.py loaddata .\core\fixtures\data.json
`

3. Load sample data

`
$python manage.py generate_demo_movers
$python .\manage.py loaddata .\data\demo_vehicles_100.json
$python manage.py add_vehicle_to_movers
`