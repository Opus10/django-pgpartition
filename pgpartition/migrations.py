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
            if model._meta.pk.name not in partition.key:
                raise RuntimeError("Primary key must be in partition key")

            key_sql = ", ".join(
                self.quote_name(model._meta.get_field(field).column) for field in partition.key
            )

            sql = (
                sql[:-1].replace(" PRIMARY KEY", "")
                + f", PRIMARY KEY ({key_sql})) PARTITION BY"
                + f" {partition.method.upper()} ({key_sql});"
            )
            if partition.method.upper() == "RANGE":
                assert len(partition.key) == 1

                # TODO: Use
                # https://stackoverflow.com/questions/49427036/postgresql-determine-schema-from-table-name
                # to determine the schema of the table
                sql += f"""
                    CREATE SCHEMA IF NOT EXISTS partman;
                    CREATE EXTENSION IF NOT EXISTS pg_partman WITH SCHEMA partman;
                    SELECT partman.create_parent(
                        p_parent_table => 'public.{model._meta.db_table}',
                        p_control => '{model._meta.get_field(partition.key[0]).column}',
                        p_type => 'native',
                        p_interval=> 'daily',
                        p_premake => 1
                    );
                """

        return sql, params
