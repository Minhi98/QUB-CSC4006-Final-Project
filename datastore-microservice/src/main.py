import sys

from var import *
from backend import *

from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

CMS_DB = pr_sql_connection(
            MYSQL_HOST, 
            MYSQL_PORT, 
            MYSQL_USER, 
            MYSQL_PASS,
            MYSQL_DB,
            wait_period=5
        )
pr_schema()

def table_based_args(all_required: bool = False):
    try:
        table_description = {c[0]:mysql_to_python[c[1].decode().split("(")[0]] for c in execute_sql(f"DESCRIBE {SERVICE_TABLE}").fetchall()}
    except:
        table_description = {c[0]:mysql_to_python[c[1].split("(")[0]] for c in execute_sql(f"DESCRIBE {SERVICE_TABLE}").fetchall()}
    parser = reqparse.RequestParser()
    for arg_name, arg_type in table_description.items():
        parser.add_argument(arg_name, required=all_required, type=arg_type)
    return list(table_description.keys()), parser

class Data(Resource):
    def post(self):
        """
        Creates a new row entry

        Example: curl -X POST -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{"test_field1":"test_str", "test_field2": 123}'
        """
        arg_keys, args = table_based_args()
        args = args.parse_args()

        # ID will always be first, remove it or set its bind_data value to "NULL"
        del args["ID"]
        arg_keys = arg_keys[1:]

        execute_sql(
            f"""INSERT INTO {SERVICE_TABLE} ({','.join(arg_keys)}) VALUES ({','.join(['%s']*len(arg_keys))})""",
            bind_data=tuple([v for v in args.values()]),
            commit=True
        )

        return 201

    def get(self):
        """
        Retrieves table description (overriding parameter). Or all rows/specific row selected by ID.

        Example: curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{"desc": true}'
        Example: curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{"ID": 2}'
        Example: curl -X GET -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{}'
        """
        get_args = reqparse.RequestParser()
        get_args.add_argument("ID", type=int)
        get_args.add_argument("desc", type=bool)
        args = get_args.parse_args()

        if args["desc"]:
            desc = [[elem.decode("utf-8") if isinstance(elem, bytes) else elem for elem in column] for column in execute_sql(f"DESCRIBE {SERVICE_TABLE}").fetchall()]
            desc = {d[0]: {"type": d[1], "null": d[2], "key": d[3], "default": d[4], "extra": d[5]} for d in desc}
            desc = json.dumps(desc, default=str)
            return json.loads(desc), 200

        row_columns = get_table_columns()[1:]
        all_rows = execute_sql(f"""SELECT * FROM {SERVICE_TABLE}""").fetchall()
        all_rows = {row[0]: {row_columns[i]: row[i+1] for i in range(len(row_columns))} for row in all_rows}
        if args["ID"]:
            all_rows = json.dumps({args["ID"]: all_rows.get(args["ID"])}, default=str)
            return json.loads(all_rows), 200
        else:
            all_rows = json.dumps(all_rows, default=str)
            return json.loads(all_rows), 200

    def put(self):
        """
        Edit a row, using its ID to determine which row is edited

        Example: curl -X PUT -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{"ID": 2, "test_field1":"edit_str", "test_field2": 1234}'
        """
        _, args = table_based_args()
        args = args.parse_args()
        arg_data = list(args.values())
        existing_data = get_table_row(search_value=args["ID"], column="ID")

        arg_keys = [k + " = %s" for k in list(args.keys())[1:]]
        data = [arg_data[i] if arg_data[i] else existing_data[i] for i in range(len(arg_data))][1:]
        data.append(args["ID"])
        execute_sql(
            f"""UPDATE {SERVICE_TABLE} SET {', '.join(arg_keys)} WHERE ID = %s""",
            bind_data=tuple(data),
            commit=True
        )

        return 201

    def delete(self):
        """
        Delete a given row, chosen by inputted ID

        Example: curl -X DELETE -H "Content-Type: application/json" 127.0.0.1:5000/data -d '{"ID":1}'
        """
        id_only = reqparse.RequestParser()
        id_only.add_argument("ID", type=int)
        args = id_only.parse_args()
        execute_sql(
            f"""DELETE FROM {SERVICE_TABLE} WHERE ID = %s""",
            bind_data=(args["ID"],),
            commit=True
        )
        return 204

api.add_resource(Data, '/data')


if __name__ == "__main__":
    # Only run flask for development "flask --app main.py --debug run"
    app.run(host="0.0.0.0", port="5000", debug=True)