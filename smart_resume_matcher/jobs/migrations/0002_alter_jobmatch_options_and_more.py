# Generated by Django 5.2.1 on 2025-06-10 16:32

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
        ('resumes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobmatch',
            options={'ordering': ['-match_score'], 'verbose_name': 'Job Match', 'verbose_name_plural': 'Job Matches'},
        ),
        migrations.RenameField(
            model_name='jobmatch',
            old_name='experience_score',
            new_name='match_score',
        ),
        migrations.AlterUniqueTogether(
            name='jobmatch',
            unique_together={('job', 'resume')},
        ),
        migrations.AddField(
            model_name='jobmatch',
            name='match_details',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='jobmatch',
            name='matching_skills',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='jobmatch',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='jobmatch',
            name='missing_skills',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='is_applied',
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='is_dismissed',
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='is_saved',
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='is_viewed',
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='job_search',
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='location_score',
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='match_explanation',
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='matched_skills',
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='overall_score',
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='salary_score',
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='skills_score',
        ),
        migrations.RemoveField(
            model_name='jobmatch',
            name='title_score',
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_score', models.FloatField(default=0)),
                ('cover_letter', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('applied', 'Applied'), ('in_review', 'In Review'), ('interview', 'Interview'), ('offered', 'Offered'), ('rejected', 'Rejected'), ('accepted', 'Accepted'), ('withdrawn', 'Withdrawn')], default='applied', max_length=20)),
                ('applied_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_status_update', models.DateTimeField(auto_now=True)),
                ('employer_response', models.TextField(blank=True)),
                ('response_date', models.DateTimeField(blank=True, null=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='jobs.job')),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_applications', to='resumes.resume')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_applications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Job Application',
                'verbose_name_plural': 'Job Applications',
                'ordering': ['-applied_date'],
                'unique_together': {('job', 'user')},
            },
        ),
    ]
