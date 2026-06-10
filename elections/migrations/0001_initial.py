# Generated manually for CampusVote
# Creates all elections app tables

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # elections.Vote references accounts.User, so accounts must migrate first
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Election table
        migrations.CreateModel(
            name="Election",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("upcoming", "Upcoming"),
                            ("active", "Active"),
                            ("closed", "Closed"),
                            ("published", "Published"),
                        ],
                        default="upcoming",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),

        # 2. Candidate table
        migrations.CreateModel(
            name="Candidate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "election",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="candidates",
                        to="elections.election",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "position",
                    models.CharField(
                        choices=[
                            ("president", "President"),
                            ("gensec", "General Secretary"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "photo",
                    models.ImageField(blank=True, null=True, upload_to="candidates/"),
                ),
                ("manifesto", models.TextField(blank=True)),
                ("tagline", models.CharField(blank=True, max_length=300)),
                ("order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["position", "order", "name"],
            },
        ),
        migrations.AddConstraint(
            model_name="candidate",
            constraint=models.UniqueConstraint(
                fields=["election", "name", "position"],
                name="unique_candidate_per_position_per_election",
            ),
        ),

        # 3. Vote table
        migrations.CreateModel(
            name="Vote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "voter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="votes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "election",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="votes",
                        to="elections.election",
                    ),
                ),
                (
                    "candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="votes",
                        to="elections.candidate",
                    ),
                ),
                (
                    "position",
                    models.CharField(
                        choices=[
                            ("president", "President"),
                            ("gensec", "General Secretary"),
                        ],
                        max_length=20,
                    ),
                ),
                ("voted_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="vote",
            unique_together={("voter", "election", "position")},
        ),

        # 4. Result table
        migrations.CreateModel(
            name="Result",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "election",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="results",
                        to="elections.election",
                    ),
                ),
                (
                    "candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="result",
                        to="elections.candidate",
                    ),
                ),
                ("displayed_vote_count", models.PositiveIntegerField(default=0)),
                ("is_winner", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="result",
            unique_together={("election", "candidate")},
        ),

        # 5. AuditLog table
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "admin",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "election",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="audit_logs",
                        to="elections.election",
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("result_edit", "Edited Result"),
                            ("result_publish", "Published Results"),
                            ("result_republish", "Republished Results"),
                            ("email_sent", "Sent Result Email"),
                            ("candidate_add", "Added Candidate"),
                            ("candidate_edit", "Edited Candidate"),
                            ("candidate_delete", "Deleted Candidate"),
                            ("election_create", "Created Election"),
                            ("election_status_change", "Changed Election Status"),
                        ],
                        max_length=30,
                    ),
                ),
                ("previous_value", models.TextField(blank=True)),
                ("new_value", models.TextField(blank=True)),
                ("reason", models.TextField(blank=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
    ]