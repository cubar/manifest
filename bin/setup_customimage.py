#!/usr/bin/env python
import re
import os
import sys
from glob import glob
from environ import Env
from subprocess import Popen, PIPE
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

postgres = psycopg2.connect(database='manifestdb')
postgres.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

contents_image_models = """# models.py
from django.db import models
from wagtail.images.models import Image, Rendition, AbstractImage, AbstractRendition\n\n
class CustomImage(AbstractImage):
    # Add any extra fields to image here
    {}
    {}\n
    admin_form_fields = Image.admin_form_fields + (
        #Then add the field names here to make them appear in the form:
        {}
    )\n\n
class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')\n
    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )
"""

sql_setval = '''"select pg_catalog.setval('public.{app}_custom{table}_id_seq', (select max(id) from {app}_custom{table}), true);"'''
contents_copy_images_migration = '''from django.db import migrations\n
{copy_image}{copy_rendition}
class Migration(migrations.Migration):
    dependencies = [
        ('{app}', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(copy_Image),
        migrations.RunPython(copy_Rendition),
        migrations.RunSQL({sql_setval_image}),
        migrations.RunSQL({sql_setval_redition}),
    ]
'''
copy_table = '''
def copy_{from_model}(apps, schema_editor):
    from_model = apps.get_model('wagtailimages', '{from_model}')
    to_model   = apps.get_model('{app}', '{to_model}')
    for from_object in from_model.objects.all().order_by('id'):
        to_object = to_model()
        for f in from_object._meta.fields:
            if f.related_model:
                name = f.get_joining_columns()[0][0]
            else:
                name = f.name
            to_object.__dict__[name] = f.value_from_object(from_object)
        to_object.save()\n\n'''


def get_contents_images_models_text(complete):
    """return the text for the model.py file"""
    def mk_field(field):
        return f"{field} = models.CharField(max_length=255, blank=True, default='change-this-{field}')"

    if complete:
        values = [mk_field('source'), mk_field('caption'), "'source', 'caption'"]
    else:
        values = ['', '', '']
    return contents_image_models.format(*values)


def makemigration_copy_images():
    my_cmd(f'./manage.py makemigrations --empty {APP}')
    migration_0002 = glob(f'{APP}/migrations/0002_*.py')[0]
    contents = contents_copy_images_migration.format(
        app=APP,
        copy_image=copy_table.format(
            app=APP,
            from_model='Image',
            to_model='CustomImage'
        ),
        copy_rendition=copy_table.format(
            app=APP,
            from_model='Rendition',
            to_model='CustomRendition'
        ),
        sql_setval_image   =sql_setval.format(app=APP, table='image'),     # noqa
        sql_setval_redition=sql_setval.format(app=APP, table='rendition'),
    )
    my_write(migration_0002, contents)


def write_customimage_models(complete):
    contents = get_contents_images_models_text(complete=complete)
    my_write(f'{APP}/models.py', contents)


def my_log(s):
    print(f'  ======== {s}')


def db_exec(sql):
    rows = []
    select_query = ('select' == sql.strip()[:6].lower())
    with postgres.cursor() as cursor:
        cursor.execute(sql)
        if select_query:
            rows = cursor.fetchall()
    return rows


def db_rows(sql):
    return db_exec(sql)


def db_drop_all():
    rows = db_rows(
        "select table_name"
        " from information_schema.tables"
        " where table_schema='public'"
    )
    for row in rows:
        table = row[0]
        #print(f'==== dropping table {table}')
        db_exec(f"drop table {table} cascade")


def setval_custom_app_tables():
    setval('image')
    setval('rendition')


def setval(wat):
    table = f'{APP}_custom{wat}'
    rows = db_exec(f"select max(id) from {table}")
    value = rows[0][0]
    if not value:
        return
    print(f'setval {table=} {value=}')
    db_exec(f"SELECT pg_catalog.setval('public.{table}_id_seq', {value}, true)")


def my_write(filename, text, show=False):
    if show:
        print(f'==========\n{text}\n==========')
    with open(filename, 'w') as fp:
        fp.write(text)


def my_cmd(cmd, show=False):
    if show:
        print(f'{cmd=}')
    pipe = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    #pipe = pipe.communicate()[0]
    stdout = pipe.stdout.read()
    stderr = pipe.stderr.read()
    if stderr:
        raise Exception(stderr)
    #result = pipe.decode().split('\n')
    if show and stdout:
        print(stdout)
    return stdout


def get_virtualenv():
    return Env().get_value('VIRTUAL_ENV')


def get_coderedcms_migrations_folder():
    return glob(f'{VIRTUAL_ENV}/lib/python*/site-packages/coderedcms/migrations')[0] + '/'


def show_mig_0035():
    return show_mig(MIG_0035)


def show_mig_0036():
    return show_mig(MIG_0036)


def show_mig(mig):
    if mig == []:
        return 'Ok, no migrations to delete'
    return '  - ' + '\n    - '.join(
        [
            migration.replace(CODEREDCMS_MIGRATIONS_FOLDER,'')
            for migration in mig
        ]
    )


def rm_mig_0036():
    for migration in MIG_0036:
        print(f'deleting {migration}')
        os.unlink(migration)


def reset_settings():
    with open(SETTINGS) as fp:
        lines = fp.readlines()
    with open(SETTINGS, 'w') as fp:
        for line in lines:
            if line not in [
                "WAGTAILIMAGES_IMAGE_MODEL = 'images.CustomImage'\n",
                "INSTALLED_APPS.append('images')\n",
            ]:
                fp.write(line)


def makemigrations(app=''):
    my_cmd(f'./manage.py makemigrations {app}', show=True)


def migrate():
    my_cmd('./manage.py migrate', show=True)


def start_app_customimage():
    my_cmd(f'./manage.py startapp {APP}', show=True)


def writefile(filename, contents):
    with open(filename, 'w') as fp:
        fp.write(contents)


def readfile(filename):
    with open(filename) as fp:
        return fp.read()


def append_to_file(filename, text):
    contents = readfile(filename)
    contents += text
    writefile(filename, contents)


def add_settings_wagtailimages():
    append_to_file(SETTINGS, "WAGTAILIMAGES_IMAGE_MODEL = 'images.CustomImage'\n")


def add_settings_installed_apps():
    append_to_file(SETTINGS, f"INSTALLED_APPS.append('{APP}')\n")


def restore_db(filename=None):
    if not filename:
        filename = ORG_PG_DUMP
    my_cmd(f'cat {filename} | ./manage.py dbshell | tee {POPLOG}')


def dump_db_tmp():
    my_cmd(f'pg_dump {DATABASE} > {TMP_PG_DUMP}')


def get_edits():
    return (
        get_edit_bigint() +
        get_edit_customimage()
    )


def get_edit_bigint():
    return [(rf'^    ({field}_id) integer(,?)$', r'    \1 bigint\2') for field in IMAGE_FIELDS]


def get_edit_customimage():
    return [
        (
            r'^    (ADD CONSTRAINT coderedcms_.*) (REFERENCES public\.)wagtailimages_image\b',
            r'    \1\n    \2images_customimage'
        )
        for field in IMAGE_FIELDS
    ]


def edit_dump(file_in=None, file_out=None):
    if not file_in:
        file_in = TMP_PG_DUMP
    if not file_out:
        file_out = TMP_PG_RESTORE
    with open(file_in) as fp_in:
        with open(file_out, 'w') as fp_out:
            for line in fp_in:
                for van, naar in get_edits():
                    if re.match(van, line):
                        line = re.sub(van, naar, line)
                        print(line, end='')
                        break
                fp_out.write(line)


def restore_db_tmp():
    restore_db(TMP_PG_RESTORE)


def delete_app():
    """delete folder structure"""
    while APP in os.listdir('.'):
        for root, folders, files in os.walk('images'):
            for f in files:
                f = os.path.join(root, f)
                os.unlink(f)
            if not folders:
                os.rmdir(root)


def undo_previous_setup_customimage():
    rm_mig_0036()     # remove the relevant migrations in virtualenv conderedcms/migrations
    reset_settings()  # remove the customimage app from INSTALLED_APPS in settings
    delete_app()      # remove the customimage app


def check_exist_org_pg_dump(db=None):
    if not db:
        db = ORG_PG_DUMP
    if db in os.listdir():
        return
    raise Exception(
        "Oops! You don't seem to have dumped the database:\n"
        f"{ORG_PG_DUMP} does not exist in the current folder."
    )


def reset_and_setup():
    reset_db()
    setup_customimage()


def main():
    if len(sys.argv) == 1:
        print(readme)
    else:
        reset_and_setup()


VIRTUAL_ENV = get_virtualenv()
CODEREDCMS_MIGRATIONS_FOLDER = get_coderedcms_migrations_folder()

DATABASE       = 'manifestdb'
APP            = 'images'
SETTINGS       = 'manifest/settings/dev.py'
ORG_PG_DUMP    = 'dump-orig.sql'
TMP_PG_DUMP    = '_tmp_dump.dmp'
TMP_PG_RESTORE = '_tmp_restore.dmp'
POPLOG         = '_tmp_populate.log'
MIG_0035 = sorted(glob(f'{CODEREDCMS_MIGRATIONS_FOLDER}0035_*.py'))
MIG_0036 = sorted(glob(f'{CODEREDCMS_MIGRATIONS_FOLDER}003[6789]_*.py'))
IMAGE_FIELDS = [
    'image',
    'cover_image',
    'og_image',
    'struct_image',
    'struct_org_image',
    'struct_org_logo',
    'favicon',
    'logo',
]
readme = f"""
Background:
- Surpisingly, adding an app like this one, automatically adds migrations
  to coderedcms. These migrations live in the Python virtualenv.
- More surprising is that only a single reference to our new model is applied
  in these coderedcms migrations automatically. Therefore we needed to edit a
  pg_dump file and restore the result.

Requirements:
- the current login user must have access to the database: psql {DATABASE}
- Stop all programs that access the database {DATABASE}
- Activate your virtualenv
- Change directories to the project folder.
- All migrations done
- pg_dump of the database in {ORG_PG_DUMP}
- check existance of the coderedcms migration file
    - 0035_remove_googleapisettings_site_and_more.py
  {show_mig_0035()}
  The above two lines should show the same migration files.
  See for the folder below.

This will reset the project by:
- cascade dropping all tables in {DATABASE}, leaving it empty.
  (Postgresql will happily preserve the grants to user roles.)
- use the file <<{ORG_PG_DUMP}>> to repopulate the database.
- editing the settings file: {SETTINGS}
- remove the complete app folder "./images if it exists"
- remove these migration files from the codercms folder in your virtualenv:
  {CODEREDCMS_MIGRATIONS_FOLDER}
  {show_mig_0036()}
You can configure some variables in this file just above this readme variable.

To run the setup just supply an arbitrary argument on the command line.
You should be able to run the setup multiple times.
"""


def reset_db():
    print(readme)
    my_log(f"check_exist_org_pg_dump({ORG_PG_DUMP})")
    check_exist_org_pg_dump(ORG_PG_DUMP)
    my_log("undo_previous_setup_customimage()")
    undo_previous_setup_customimage()
    my_log("db_drop_all()")
    db_drop_all()
    my_log("restore_db()")
    restore_db()


def setup_customimage():
    my_log("start_app_customimage()")
    start_app_customimage()
    my_log("write_customimage_models(complete=False)")
    write_customimage_models(complete=False)
    my_log("add_settings_installed_apps()")
    add_settings_installed_apps()
    my_log(f"makemigrations({APP})")
    makemigrations(APP)
    my_log("migrate()")
    migrate()
    my_log("makemigration_copy_images()")
    makemigration_copy_images()
    my_log("migrate()")
    migrate()
    my_log("add_settings_wagtailimages()")
    add_settings_wagtailimages()
    my_log("write_customimage_models(complete=True)")
    write_customimage_models(complete=True)
    my_log("makemigrations()")
    makemigrations()
    my_log("migrate()")
    migrate()
    my_log("dump_db_tmp()")
    dump_db_tmp()
    my_log("edit_dump()")
    edit_dump()
    my_log("db_drop_all()")
    db_drop_all()
    my_log("restore_db_tmp()")
    restore_db_tmp()
    #my_log("setval_custom_app_tables()")
    #setval_custom_app_tables()
    print(f"\nDone\nDo check the file {POPLOG} to see if there where any errors\n")


if __name__ == '__main__':
    main()
