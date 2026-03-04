from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('vet', '0005_vet_dossier_suivi_par'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vet',
            old_name='numero_de_la_redevance_annuelle',
            new_name='numero_ordre_de_recette',
        ),
    ]
