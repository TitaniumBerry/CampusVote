# Generated manually for CampusVote
# Applies changes to accounts.User and adds the OTPVerification model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        # 1. Make email unique (was not unique before)
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True, verbose_name="email address"),
        ),

        # 2. Expand hostel field (was max_length=20, now 50)
        migrations.AlterField(
            model_name="user",
            name="hostel",
            field=models.CharField(max_length=50),
        ),

        # 3. Expand room_number field (was max_length=20, now 10 is plenty)
        migrations.AlterField(
            model_name="user",
            name="room_number",
            field=models.CharField(max_length=10),
        ),

        # 4. Remove the old single has_voted field
        migrations.RemoveField(
            model_name="user",
            name="has_voted",
        ),

        # 5. Add separate voted flags per position
        migrations.AddField(
            model_name="user",
            name="has_voted_president",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="has_voted_gensec",
            field=models.BooleanField(default=False),
        ),

        # 6. Create the OTPVerification table
        migrations.CreateModel(
            name="OTPVerification",
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
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="otp",
                        to="accounts.user",
                    ),
                ),
                ("code", models.CharField(max_length=4)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]