# Vending Machine

## Supported APIs

> **Machine**
> - `/machine/create/<location>/<name>`           (POST), Creates a machine.
> - `/machine/all`                                (GET), Return information of all machines.
> - `/machine/at/<location>`                      (GET), Gets all machine at given location.
> - `/machine/at/<location>/<name>`               (GET), Get a machine with given name at location.
> - `/machine/<machine_id>`                       (GET), Get the machine with given ID.
> - `/machine/<machine_id>/add`                   (POST), Parses JSON product list and add all product(s) to machine.
> - `/machine/<machine_id>/edit`                  (POST), Parses JSON indicating desired changes and apply them to the machine if applicable.
> - `/machine/<machine_id>/destroy`               (POST), Destroy the machine.
> - `/machine/<machine_id>/buy/<product_id>`      (POST), Parses JSON with payment and attempt to purchase the item.
> - `/machine/<machine_id>/remove/<product_id>`   (POST), Removes the product with given ID from the machine.

> **Product**
> - `/product/create` (POST), Parses JSON for product information and creates a new product.
> - `/product/search/<identifier>` (GET), Search for product given ID or product name.
> - `/product/<product_id>` (GET), Get the product with the given ID.
> - `/product/<product_id>/edit` (POST), Parses JSON indicating desired changes and apply them to the product if applicable.
> - `/product/<product_id>/where` (GET), Return information of all machines which contains the product.
> - `/product/all` (GET), Return information of all products.

## Setup

> **_NOTE:_**  Docker must be running. You can run this command
```
docker-compose up
```

Install requirements:
```
pip install -r ./requirements.txt
```

> `reset_db.py`
> - Requires docker database running.
> - Drop all records in the database.
> - Must be run if changes are made to the tables design.

> `run.py`
> - Requres docker database running.
> - Main application entry point.

> `config.py`
> - Contains all config information required for the flask application (automatically applied)

## Directory Layout

```
.
├── app
│   ├── models
│   │     └── ...                 # All table declarations
│   ├── utils
│   │     ├── __init__.py         # utils module
│   │     └── ...
│   ├── product
│   │     ├── __init__.py         # product module
│   │     └── routes.py           # routes for product
│   ├── vending_machine
│   │     ├── __init__.py         # vending_machine module
│   │     └── routes.py           # routes for vending_machine
│   └── ...
├── __init__.py                   # app module, blueprints MUST be registered here
├── config.py                     # flask app config
├── reset_db.py
├── run.py
├── requirements.txt
└── docker_setup.sh
```

## Design Choice

- Almost all table methods returns a `Result` type (found in `app/utils/result.py`). This is nothing but a simple wrapper for a tuple in the form of `Tuple[Optional[Any], str]` this is useful because we can use the optional value as the success indicator, furthermore, the return message which accompanies the optional value will always appropriately reflect the result.
  - Example of setup
    ```python
    # Method for creating a new vending machine entry
    # Note that Result.error is simply [ None, msg ]
    @staticmethod
    def make(location: str, name: str) -> Result:

        if common.isnumber(location):
            return Result.error("Location can not be a number.")

        if common.isnumber(name):
            return Result.error("Name can not be a number.")

        if Machine.find(name=name, location=location):
            return Result.error( f"A machine with given name and location already exists. (Location: { location }, Name: { name })")

        new_machine = Machine(location=location, machine_name=name)

        return Result(new_machine, f"Successfully added vending machine named '{name}' at '{ location }'!")
    ```
  - Example of usage
    ```python
    @bp.route("/create/<location>/<name>", methods=["POST"])
    def create(location, name):

        result = Machine.make(location, name)

        if machine.object
            db.session.add(machine.object
            db.session.commit()

        # Used in conjunction with Log
        log = Log().addResult("Machine", f"New Machine: {location}, {name}", result, Machine.ERROR_CREATE_FAIL)

        return jsonify(log)
    ```
- Errors will not occur at the route level, and all errors which occurs will not forcefully break anything, and they will all be reported in the error log.
- The `Log` class (from `app/utils/log.py`) is used as a container of responses (when appropriate)
   - It has a method for easily adding Error logs.
   - An example of success log (from creating a new machine, the code example above)
     ```json
     "Logs": {
         "Machine": {
             "Records": {
                 "New Machine: newplace1, newmachine1": [
                     "Successfully added vending machine named 'newmachine1' at 'newplace1'!"
                 ]
             }
         }
     }
     ```
    - An example of failure log (also from creating a new machine)
      ```json
      "Logs": {
          "Error": {
              "Records": {
                  "Machine Creation Error": [
                      "A machine with given name and location already exists. (Location: newplace1, Name: newmachine1)"
                  ]
              }
          }
      }
      ```

## JSON Expectations

> _**NOTE**_: This is not ideal since normally we should never get a malformed JSON because it should have been built from our front end properly.

**Machine**
- `/machine/<machine_id>/add`
    - Note: You can list multiple stock information.
      ```JSON
      "stock_list": [
          {
              "product_id": 1,
              "quantity": 1
          }
      ]
      ```
- `/machine/<machine_id>/edit`
    - ```JSON
      "machine_name": "new_name",
      "location": "new_location",
      "stock_list": [
          {
              "product_id": 1,
              "quantity": 10
          }
      ]
      ```
- `/machine/<machine_id>/buy/<product_id>`
    - ```JSON
      "payment": 100.0
      ```

**Product**
- `/product/create`
    - ```JSON
      "product_name": "sample_name",
      "product_price": 100.0
      ```
- `/product/<product_id>/edit`
    - ```JSON
      "product_name": "new_name",
      "product_price": 120.0
      ```
