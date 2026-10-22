from django.db import migrations

# Abnahmekriterium 11, zusätzliche Absicherung in der Datenbank: Nach der ersten Genehmigung
# muss der Projektzeitraum (projects_project.start_date/end_date) dem Zeitraum der genehmigten
# Planversion entsprechen. Der Genehmigungsservice setzt zuerst die neue Version auf
# „genehmigt“ und speichert danach den Zeitraum; jede andere abweichende Änderung (auch per ORM
# oder SQL) wird abgewiesen.
FORWARD = """
CREATE OR REPLACE FUNCTION milestones_project_period_guard() RETURNS trigger AS $$
DECLARE
    plan_start date;
    plan_end date;
BEGIN
    IF NEW.start_date IS NOT DISTINCT FROM OLD.start_date
       AND NEW.end_date IS NOT DISTINCT FROM OLD.end_date THEN
        RETURN NEW;
    END IF;
    SELECT pe.start_date, pe.end_date INTO plan_start, plan_end
      FROM milestones_planentry pe
      JOIN milestones_planversion pv ON pv.id = pe.plan_version_id
     WHERE pv.project_id = NEW.id AND pv.status = 'GENEHMIGT' AND pe.kind = 'ZEITRAUM';
    IF NOT FOUND THEN
        RETURN NEW;
    END IF;
    IF NEW.start_date IS DISTINCT FROM plan_start OR NEW.end_date IS DISTINCT FROM plan_end THEN
        RAISE EXCEPTION 'Projektzeitraum weicht vom genehmigten Plan ab (Aenderung nur ueber Planversion)';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER milestones_project_period_guard
    BEFORE UPDATE ON projects_project
    FOR EACH ROW EXECUTE FUNCTION milestones_project_period_guard();
"""

BACKWARD = """
DROP TRIGGER IF EXISTS milestones_project_period_guard ON projects_project;
DROP FUNCTION IF EXISTS milestones_project_period_guard();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("milestones", "0003_standard_catalog_and_existing_projects"),
    ]

    operations = [
        migrations.RunSQL(FORWARD, BACKWARD),
    ]
