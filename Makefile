recreatedb:
	docker-compose down -v
	docker-compose up -d
	sleep 5
	python manage.py migrate
	python manage.py createsuperuser


run: recreatedb
	python manage.py import_data data_all/import_1.csv --owner_id 1
	python manage.py import_data data_all/import_2.yaml --owner_id 1
	python manage.py runserver

