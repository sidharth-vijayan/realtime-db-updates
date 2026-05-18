CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100),
    product_name VARCHAR(100),
    status VARCHAR(20) CHECK (status IN ('pending', 'shipped', 'delivered')),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION notify_order_change()
RETURNS trigger AS $$
DECLARE
    payload JSON;
BEGIN
    payload = json_build_object(
        'operation', TG_OP,
        'id',            NEW.id,
        'customer_name', NEW.customer_name,
        'product_name',  NEW.product_name,
        'status',        NEW.status,
        'updated_at',    NEW.updated_at
    );

    PERFORM pg_notify('orders_channel', payload::text);

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_change_trigger
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION notify_order_change();