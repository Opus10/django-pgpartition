class DatabaseSchemaEditorMixin:
    """
    A schema editor mixin that can subclass a DatabaseSchemaEditor and
    handle partitioned tables and foreign keys.
    """

    def delete_model(self, model):
        partition = getattr(model._meta, "partition", None)

        if partition:
            # TODO: Use
            # https://stackoverflow.com/questions/49427036/postgresql-determine-schema-from-table-name
            # to determine the schema of the table
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM partman.part_config WHERE parent_table ="
                    f" 'public.{model._meta.db_table}'"
                )

        return super().delete_model(model)

    def table_sql(self, model):
        sql, params = super().table_sql(model)

        partition = getattr(model._meta, "partition", None)

        if partition:
            partition.check(model)

            key_sql = ", ".join(
                self.quote_name(model._meta.get_field(field).column) for field in partition.key
            )

            sql = (
                sql[:-1].replace(" PRIMARY KEY", "")
                + f", PRIMARY KEY ({key_sql})) PARTITION BY"
                + f" {partition.method.upper()} ({key_sql});"
            )

            def _quote(val):
                if isinstance(val, str):
                    return f"'{val}'"
                else:
                    return val

            if partition.method.upper() == "RANGE":
                create_parent_kwargs = partition.get_create_parent_kwargs(model)
                create_parent_sql = (
                    "partman.create_parent("
                    + ", ".join(
                        f"{key} => {_quote(val)}" for key, val in create_parent_kwargs.items()
                    )
                    + ")"
                )

                sql += f"""
                    CREATE SCHEMA IF NOT EXISTS partman;
                    CREATE EXTENSION IF NOT EXISTS pg_partman WITH SCHEMA partman;
                    SELECT {create_parent_sql};
                """

        return sql, params
