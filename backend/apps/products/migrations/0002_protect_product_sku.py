
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION prevent_product_sku_change()
                RETURNS TRIGGER AS $$
                BEGIN
                    IF OLD.sku IS DISTINCT FROM NEW.sku THEN
                        RAISE EXCEPTION
                            'Product SKU cannot be changed once assigned.';
                    END IF;

                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER protect_product_sku
                BEFORE UPDATE OF sku ON products_product
                FOR EACH ROW
                EXECUTE FUNCTION prevent_product_sku_change();
            """,
            reverse_sql="""
                DROP TRIGGER IF EXISTS protect_product_sku
                ON products_product;

                DROP FUNCTION IF EXISTS prevent_product_sku_change();
            """,
        ),
    ]
