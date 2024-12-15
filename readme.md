Here is the README.md content for your Health Hub backend:
# Health Hub Backend

## Installations
To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```

For MySQL

Install MySQL from the official website.
Run migrations to initialize the database:

```bash
python manage.py migrate
```
For Testing
We leverage Swagger UI documentation, thanks to `drf-yasg`. To check all routes and test the API, visit:
http://127.0.0.1:8000/swagger/

