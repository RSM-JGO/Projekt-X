from django.db import migrations

# Das Änderungsprotokoll ist nur anfügbar: UPDATE und DELETE werden in PostgreSQL abgewiesen.
FORWARD = """
CREATE OR REPLACE FUNCTION audit_auditlog_append_only() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_auditlog ist nur anfuegbar (% abgelehnt)', TG_OP;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_auditlog_no_update_delete
    BEFORE UPDATE OR DELETE ON audit_auditlog
    FOR EACH ROW EXECUTE FUNCTION audit_auditlog_append_only();
"""

BACKWARD = """
DROP TRIGGER IF EXISTS audit_auditlog_no_update_delete ON audit_auditlog;
DROP FUNCTION IF EXISTS audit_auditlog_append_only();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(FORWARD, BACKWARD),
    ]
