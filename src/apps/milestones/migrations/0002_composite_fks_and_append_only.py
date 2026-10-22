from django.db import migrations

# 1. Projektgrenzen in der Datenbank: zusammengesetzte Fremdschlüssel (wie tasks 0002).
#    Lieferobjekt, Freigabe, Planeintrag und Terminänderung verweisen auf (Meilenstein, Projekt),
#    Freigabe und Planeintrag auf (Planversion, Projekt). Eine Korrektur verweist auf
#    (ersetzte Freigabe, Meilenstein): Ersetzt werden kann nur eine Freigabe desselben
#    Meilensteins. Leere Spalten werden nach MATCH SIMPLE nicht geprüft.
# 2. Meilensteine werden nie gelöscht, nur ausgeblendet (DELETE abgewiesen).
# 3. Unveränderlichkeit: Freigaben, Beteiligte und Terminänderungen sind nur anfügbar.
#    Genehmigte Planversionen sind unveränderlich; erlaubt ist nur genehmigt -> abgelöst ohne
#    weitere Änderung. Einträge genehmigter oder abgelöster Versionen sind gesperrt.
#    TRUNCATE wird ebenfalls abgewiesen; die Testsuite schaltet nur die TRUNCATE-Trigger in der
#    Testdatenbank ab (tests/conftest.py).
FORWARD = """
ALTER TABLE milestones_deliverable
    ADD CONSTRAINT milestones_deliverable_same_project
    FOREIGN KEY (milestone_id, project_id) REFERENCES milestones_milestone (id, project_id);

ALTER TABLE milestones_approval
    ADD CONSTRAINT milestones_approval_milestone_same_project
    FOREIGN KEY (milestone_id, project_id) REFERENCES milestones_milestone (id, project_id);

ALTER TABLE milestones_approval
    ADD CONSTRAINT milestones_approval_plan_same_project
    FOREIGN KEY (plan_version_id, project_id) REFERENCES milestones_planversion (id, project_id);

ALTER TABLE milestones_approval
    ADD CONSTRAINT milestones_approval_replaces_same_milestone
    FOREIGN KEY (replaces_id, milestone_id) REFERENCES milestones_approval (id, milestone_id);

ALTER TABLE milestones_planentry
    ADD CONSTRAINT milestones_planentry_version_same_project
    FOREIGN KEY (plan_version_id, project_id) REFERENCES milestones_planversion (id, project_id);

ALTER TABLE milestones_planentry
    ADD CONSTRAINT milestones_planentry_milestone_same_project
    FOREIGN KEY (milestone_id, project_id) REFERENCES milestones_milestone (id, project_id);

ALTER TABLE milestones_datechange
    ADD CONSTRAINT milestones_datechange_same_project
    FOREIGN KEY (milestone_id, project_id) REFERENCES milestones_milestone (id, project_id);

CREATE OR REPLACE FUNCTION milestones_append_only() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION '% ist nur anfuegbar (% abgelehnt)', TG_TABLE_NAME, TG_OP;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER milestones_approval_no_update_delete
    BEFORE UPDATE OR DELETE ON milestones_approval
    FOR EACH ROW EXECUTE FUNCTION milestones_append_only();
CREATE TRIGGER milestones_approval_no_truncate
    BEFORE TRUNCATE ON milestones_approval
    FOR EACH STATEMENT EXECUTE FUNCTION milestones_append_only();

CREATE TRIGGER milestones_approvalparticipant_no_update_delete
    BEFORE UPDATE OR DELETE ON milestones_approvalparticipant
    FOR EACH ROW EXECUTE FUNCTION milestones_append_only();
CREATE TRIGGER milestones_approvalparticipant_no_truncate
    BEFORE TRUNCATE ON milestones_approvalparticipant
    FOR EACH STATEMENT EXECUTE FUNCTION milestones_append_only();

CREATE TRIGGER milestones_datechange_no_update_delete
    BEFORE UPDATE OR DELETE ON milestones_datechange
    FOR EACH ROW EXECUTE FUNCTION milestones_append_only();
CREATE TRIGGER milestones_datechange_no_truncate
    BEFORE TRUNCATE ON milestones_datechange
    FOR EACH STATEMENT EXECUTE FUNCTION milestones_append_only();

CREATE OR REPLACE FUNCTION milestones_milestone_no_delete() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'Meilensteine werden nur ausgeblendet, nie geloescht (DELETE abgelehnt)';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER milestones_milestone_no_delete
    BEFORE DELETE ON milestones_milestone
    FOR EACH ROW EXECUTE FUNCTION milestones_milestone_no_delete();

CREATE OR REPLACE FUNCTION milestones_planversion_guard() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'TRUNCATE' THEN
        RAISE EXCEPTION 'milestones_planversion: TRUNCATE abgelehnt';
    END IF;
    IF TG_OP = 'DELETE' THEN
        IF OLD.status <> 'ENTWURF' THEN
            RAISE EXCEPTION 'Genehmigte Planversion ist unveraenderlich (DELETE abgelehnt)';
        END IF;
        RETURN OLD;
    END IF;
    IF OLD.status = 'ENTWURF' THEN
        RETURN NEW;
    END IF;
    IF OLD.status = 'GENEHMIGT' AND NEW.status = 'ABGELOEST'
       AND ROW(NEW.id, NEW.project_id, NEW.number, NEW.reason, NEW.created_by_id,
               NEW.created_at, NEW.approved_by_id, NEW.approved_at, NEW.approved_as_admin)
           IS NOT DISTINCT FROM
           ROW(OLD.id, OLD.project_id, OLD.number, OLD.reason, OLD.created_by_id,
               OLD.created_at, OLD.approved_by_id, OLD.approved_at, OLD.approved_as_admin) THEN
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'Genehmigte Planversion ist unveraenderlich (UPDATE abgelehnt)';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER milestones_planversion_guard
    BEFORE UPDATE OR DELETE ON milestones_planversion
    FOR EACH ROW EXECUTE FUNCTION milestones_planversion_guard();
CREATE TRIGGER milestones_planversion_no_truncate
    BEFORE TRUNCATE ON milestones_planversion
    FOR EACH STATEMENT EXECUTE FUNCTION milestones_planversion_guard();

CREATE OR REPLACE FUNCTION milestones_planentry_guard() RETURNS trigger AS $$
DECLARE
    st varchar;
BEGIN
    IF TG_OP = 'TRUNCATE' THEN
        RAISE EXCEPTION 'milestones_planentry: TRUNCATE abgelehnt';
    END IF;
    IF TG_OP IN ('UPDATE', 'DELETE') THEN
        SELECT status INTO st FROM milestones_planversion WHERE id = OLD.plan_version_id;
        IF st IS DISTINCT FROM 'ENTWURF' THEN
            RAISE EXCEPTION 'Eintrag einer genehmigten Planversion ist unveraenderlich (% abgelehnt)', TG_OP;
        END IF;
    END IF;
    IF TG_OP IN ('INSERT', 'UPDATE') THEN
        SELECT status INTO st FROM milestones_planversion WHERE id = NEW.plan_version_id;
        IF st IS DISTINCT FROM 'ENTWURF' THEN
            RAISE EXCEPTION 'Eintrag einer genehmigten Planversion ist unveraenderlich (% abgelehnt)', TG_OP;
        END IF;
        RETURN NEW;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER milestones_planentry_guard
    BEFORE INSERT OR UPDATE OR DELETE ON milestones_planentry
    FOR EACH ROW EXECUTE FUNCTION milestones_planentry_guard();
CREATE TRIGGER milestones_planentry_no_truncate
    BEFORE TRUNCATE ON milestones_planentry
    FOR EACH STATEMENT EXECUTE FUNCTION milestones_planentry_guard();
"""

BACKWARD = """
DROP TRIGGER IF EXISTS milestones_milestone_no_delete ON milestones_milestone;
DROP FUNCTION IF EXISTS milestones_milestone_no_delete();
DROP TRIGGER IF EXISTS milestones_planentry_no_truncate ON milestones_planentry;
DROP TRIGGER IF EXISTS milestones_planentry_guard ON milestones_planentry;
DROP FUNCTION IF EXISTS milestones_planentry_guard();
DROP TRIGGER IF EXISTS milestones_planversion_no_truncate ON milestones_planversion;
DROP TRIGGER IF EXISTS milestones_planversion_guard ON milestones_planversion;
DROP FUNCTION IF EXISTS milestones_planversion_guard();
DROP TRIGGER IF EXISTS milestones_datechange_no_truncate ON milestones_datechange;
DROP TRIGGER IF EXISTS milestones_datechange_no_update_delete ON milestones_datechange;
DROP TRIGGER IF EXISTS milestones_approvalparticipant_no_truncate ON milestones_approvalparticipant;
DROP TRIGGER IF EXISTS milestones_approvalparticipant_no_update_delete ON milestones_approvalparticipant;
DROP TRIGGER IF EXISTS milestones_approval_no_truncate ON milestones_approval;
DROP TRIGGER IF EXISTS milestones_approval_no_update_delete ON milestones_approval;
DROP FUNCTION IF EXISTS milestones_append_only();
ALTER TABLE milestones_datechange DROP CONSTRAINT IF EXISTS milestones_datechange_same_project;
ALTER TABLE milestones_planentry DROP CONSTRAINT IF EXISTS milestones_planentry_milestone_same_project;
ALTER TABLE milestones_planentry DROP CONSTRAINT IF EXISTS milestones_planentry_version_same_project;
ALTER TABLE milestones_approval DROP CONSTRAINT IF EXISTS milestones_approval_replaces_same_milestone;
ALTER TABLE milestones_approval DROP CONSTRAINT IF EXISTS milestones_approval_plan_same_project;
ALTER TABLE milestones_approval DROP CONSTRAINT IF EXISTS milestones_approval_milestone_same_project;
ALTER TABLE milestones_deliverable DROP CONSTRAINT IF EXISTS milestones_deliverable_same_project;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("milestones", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(FORWARD, BACKWARD),
    ]
