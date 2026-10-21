from django.db import migrations

# Zusätzlich zu UPDATE/DELETE (0002) wird auch TRUNCATE abgewiesen.
# Die Testsuite schaltet nur diesen Trigger in der Testdatenbank ab, weil Djangos flush
# (transactional_db) alle Tabellen per TRUNCATE leert; siehe tests/conftest.py.
FORWARD = """
CREATE OR REPLACE FUNCTION audit_auditlog_no_truncate() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_auditlog ist nur anfuegbar (TRUNCATE abgelehnt)';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_auditlog_no_truncate
    BEFORE TRUNCATE ON audit_auditlog
    FOR EACH STATEMENT EXECUTE FUNCTION audit_auditlog_no_truncate();
"""

BACKWARD = """
DROP TRIGGER IF EXISTS audit_auditlog_no_truncate ON audit_auditlog;
DROP FUNCTION IF EXISTS audit_auditlog_no_truncate();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0002_append_only_trigger"),
    ]

    operations = [
        migrations.RunSQL(FORWARD, BACKWARD),
    ]
