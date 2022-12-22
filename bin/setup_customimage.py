#!/usr/bin/env python
import os
import sys
from glob import glob
from environ import Env
from subprocess import Popen, PIPE, STDOUT, run


def my_write(filename, text, show=True):
    if show:
        print(f'==========\n{text}\n==========')
    with open(filename, 'w') as fp:
        fp.write(text)


def my_run(*args, show=True):
    process = run(args, capture_output=True)
    if process.returncode != 0:
        raise Exception(process.stderr.decode())
    result = process.stdout.decode().split('\n')
    if show:
        show_sequence(result)
    return result

def my_cmd(cmd, show=True):
    if show:
        print(f'======={cmd=}')
    process = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
    process = process.communicate()[0]
    result = process.decode().split('\n')
    if show:
        show_sequence(result)
    return result


def show_sequence(seq):
    for line in seq:
        print(line)


def get_migrations():
    migrations = my_run('./manage.py', 'showmigrations', 'coderedcms')
    return migrations


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
        os.unlink(migration)


def reset_settings():
    my_run(
        'sed', '-i',
        '-e', "/^WAGTAILIMAGES_IMAGE_MODEL = 'images.CustomImage'/d",
        '-e', "/^INSTALLED_APPS.append('images')/d",
        SETTINGS
    )


def drop_create_db():
    print(f"About to drop and recreate the database {DATABASE}")
    my_cmd(f"echo 'drop database {DATABASE}; create database {DATABASE}' | {PSQL_NODB}")


def get_images_models_text(app, complete=True):
    """return the text for the model.py file"""
    def mk_field(field):
        return f"{field} = models.CharField(max_length=255, blank=True, default='change-this-string-for-{field}')"
    if complete:
        values = [mk_field('source'), mk_field('caption'), "'source', 'caption'"]
    else:
        values = ['', '', '']

    # text until:                                            # "==== START-OF-TEXT ===="
    return f"""# models.py
from django.db import models
from wagtail.images.models import Image, AbstractImage, AbstractRendition\n\n
class CustomImage(AbstractImage):
    # Add any extra fields to image here
    {values[0]}
    {values[1]}\n
    admin_form_fields = Image.admin_form_fields + (
        #Then add the field names here to make them appear in the form:
        {values[2]}
    )\n\n
class CustomRendition(AbstractRendition):
    image = models.ForeignKey(CustomImage, on_delete=models.CASCADE, related_name='renditions')\n
    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )"""                                                 # "==== END-OF-TEXT ===="


def get_copy_images_migration():
    """Here is the text for a migration until"""             # "==== START-OF-TEXT ===="
    return f'''from django.db import migrations\n\n
def copy_images(apps, schema_editor):
    Image = apps.get_model('wagtailimages', 'Image')
    CustomImage = apps.get_model('{APP}', 'CustomImage')
    print('')
    for image in Image.objects.all():
        print(f'{{image.title=}}')
        customimage = CustomImage()
        for f in image._meta.fields:
            if f.name == 'id':
                continue
            customimage.__dict__[f.name] = f.value_from_object(image)
        customimage.save()\n\n
class Migration(migrations.Migration):
    dependencies = [
        ('{APP}', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(copy_images),
    ]'''                                                     # "==== END-OF-TEXT ===="


def makemigrations(app=''):
    my_cmd(f'./manage.py makemigrations {app}')


def migrate():
    my_cmd('./manage.py migrate')


def makemigration_copy_images():
    my_cmd(f'./manage.py makemigrations --empty {APP}')
    migration_0002 = glob(f'{APP}/migrations/0002_*.py')[0]
    my_write(migration_0002, get_copy_images_migration())


def start_app_customimage():
    my_cmd(f'./manage.py startapp {APP}')


def write_customimage_models(complete=True):
    my_write(f'{APP}/models.py', get_images_models_text({APP}, complete=complete))


def delete_settings_wagtail_image_model():
    my_cmd(f'''sed -i -e "/WAGTAILIMAGES_IMAGE_MODEL = 'images.CustomImage'/d" {SETTINGS}''')


def add_settings_wagtail_image_model():
    my_cmd(f'''echo "WAGTAILIMAGES_IMAGE_MODEL = 'images.CustomImage'" >> {SETTINGS}''')


def add_settings_customimages_app():
    my_cmd(f'''echo "INSTALLED_APPS.append('{APP}')" >> {SETTINGS}''')


def restore_db(filename=None):
    if not filename:
        filename = ORG_PG_DUMP
    my_cmd(f'cat {filename} | {PSQL} | tee {POPLOG}')
    print(f"\n\n\nDone\n\nDo check the file {POPLOG} to see if there where any errors\n\n\n")


def dump_db_tmp():
    my_cmd(f'{DUMP} > {TMP_PG_DUMP}')


def edit_db_tmp():
    my_cmd(
        "sed"
        r" -e 's/^    \(image_id\) integer\(,\?\)$/    \1 bigint\2/'"
        r" -e 's/^    \(cover_image_id\) integer\(,\?\)$/    \1 bigint\2/'"
        r" -e 's/^    \(struct_org_image_id\) integer\(,\?\)$/    \1 bigint\2/'"
        r" -e 's/^    \(struct_org_logo_id\) integer\(,\?\)$/    \1 bigint\2/'"
        r" -e 's/^    \(favicon_id\) integer\(,\?\)$/    \1 bigint\2/'"
        r" -e 's/^    \(logo_id\) integer\(,\?\)$/    \1 bigint\2/'"
        r" -e 's/^    \(ADD CONSTRAINT coderedcms_.* REFERENCES public\.\)\(wagtailimages_image\)(id)/\1images_customimage(id)/'"
        f" {TMP_PG_DUMP}"
        f" > {TMP_PG_RESTORE}"
    )


def restore_db_tmp():
    restore_db(TMP_PG_RESTORE)


def undo_previous_setup_customimage():
    rm_mig_0036()            # remove the relevant migrations in virtualenv conderedcms/migrations
    reset_settings()         # remove the customimage app from INSTALLED_APPS in settings
    my_cmd('rm -rf images')  # remove the customimage app


def check_exist_org_pg_dump():
    if ORG_PG_DUMP in os.listdir():
        return
    raise Exception(
        "Oops! You don't seem to have dumped the database:\n"
        f"{ORG_PG_DUMP} does not exist in the current folder."
    )


def reset_db():
    print(readme)
    undo_previous_setup_customimage()
    check_exist_org_pg_dump()
    drop_create_db()
    restore_db()

def reset_and_setup_customimage():
    reset_db()
    start_app_customimage()
    write_customimage_models(complete=False)
    add_settings_customimages_app()
    makemigrations(APP)
    migrate()
    makemigration_copy_images()
    migrate()
    add_settings_wagtail_image_model()
    write_customimage_models(complete=True)
    makemigrations()
    migrate()
    dump_db_tmp()
    edit_db_tmp()
    drop_create_db()
    restore_db_tmp()


def main():
    if len(sys.argv) == 1:
        print(readme)
    else:
        reset_and_setup_customimage()


VIRTUAL_ENV = get_virtualenv()
CODEREDCMS_MIGRATIONS_FOLDER = get_coderedcms_migrations_folder()

DATABASE       = 'manifestdb'
USER           = 'chuck'
POSTGRES       = 'sudo su postgres -c'
POSTGRES       = 'ssh postgres@localhost'
PSQL_NODB      = f'{POSTGRES} psql'
PSQL           = f'{POSTGRES} "psql {DATABASE}"'
DUMP           = f'{POSTGRES} "pg_dump {DATABASE}"'
APP            = 'images'
SETTINGS       = 'manifest/settings/dev.py'
ORG_PG_DUMP    = 'dump-orig.sql'
TMP_PG_DUMP    = '_tmp_dump.dmp'
TMP_PG_RESTORE = '_tmp_restore.dmp'
POPLOG         = '_tmp_populate.log'
MIG_0035 = sorted(glob(f'{CODEREDCMS_MIGRATIONS_FOLDER}0035_*.py'))
MIG_0036 = sorted(glob(f'{CODEREDCMS_MIGRATIONS_FOLDER}003[6789]_*.py'))
readme = f"""
Background:
- Surpisingly, adding an app like this one, automatically adds migrations
  to coderedcms. These migrations live in the Python virtualenv.
- More surprising is that only a single reference to our new model is applied
  in these coderedcms migrations automatically. Therefore we needed to edit a
  pg_dump file and restore the result.

Requirements:
- Stop all programs that access the database {DATABASE}
- All migrations done
- pg_dump of the database in {ORG_PG_DUMP}
- check existance of the coderedcms migration file
    - 0035_remove_googleapisettings_site_and_more.py
  {show_mig_0035()}
  The above two lines should show the same migration files.
  See for the folder below.

This will reset the project by:
- dropping the {DATABASE} database and recreate it.
  (Postgresql will happily preserve the grants to user roles.)
- use the file <<{ORG_PG_DUMP}>> to repopulate the database.
- editing <<{SETTINGS}>>
- remove the complete app folder "./images"
- remove these migration files from the codercms folder in your virtualenv:
  {CODEREDCMS_MIGRATIONS_FOLDER}
  {show_mig_0036()}
You can configure some variables in this file just above the readme variable.

To run the setup just supply an arbitrary argument on the command line.
You should be able to run the setup multiple times.
"""


if __name__ == '__main__':
    main()
