from django.db import migrations

# 1. Datenbankregel "Bucket gehört zum Projekt der Aufgabe": zusammengesetzter Fremdschlüssel
#    (bucket_id, project_id) -> tasks_bucket (id, project_id). Bei persönlichen Aufgaben sind
#    beide Spalten leer; MATCH SIMPLE prüft dann nicht.
# 2. Aufgabenverlauf nur anfügbar: UPDATE, DELETE und TRUNCATE werden abgewiesen. Die
#    Testsuite schaltet nur den TRUNCATE-Trigger in der Testdatenbank ab (tests/conftest.py).
FORWARD = """
ALTER TABLE tasks_task
    ADD CONSTRAINT tasks_task_bucket_same_project
    FOREIGN KEY (bucket_id, project_id) REFERENCES tasks_bucket (id, project_id);

CREATE OR REPLACE FUNCTION tasks_taskevent_append_only() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'tasks_taskevent ist nur anfuegbar (% abgelehnt)', TG_OP;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tasks_taskevent_no_update_delete
    BEFORE UPDATE OR DELETE ON tasks_taskevent
    FOR EACH ROW EXECUTE FUNCTION tasks_taskevent_append_only();

CREATE TRIGGER tasks_taskevent_no_truncate
    BEFORE TRUNCATE ON tasks_taskevent
    FOR EACH STATEMENT EXECUTE FUNCTION tasks_taskevent_append_only();
"""

BACKWARD = """
DROP TRIGGER IF EXISTS tasks_taskevent_no_truncate ON tasks_taskevent;
DROP TRIGGER IF EXISTS tasks_taskevent_no_update_delete ON tasks_taskevent;
DROP FUNCTION IF EXISTS tasks_taskevent_append_only();
ALTER TABLE tasks_task DROP CONSTRAINT IF EXISTS tasks_task_bucket_same_project;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(FORWARD, BACKWARD),
    ]
