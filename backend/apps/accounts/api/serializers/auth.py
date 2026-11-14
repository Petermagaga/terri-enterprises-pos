from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import User

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
        ]
        read_only_fields = fields

class AccountSettingsSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )
    new_password = serializers.CharField(
        write_only=True,
        required=False,
        trim_whitespace=False,
    )
    confirm_new_password = serializers.CharField(
        write_only=True,
        required=False,
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "current_password",
            "new_password",
            "confirm_new_password",
        ]
        extra_kwargs = {
            "username": {"required": False},
        }

    def validate(self, attrs):
        user = self.instance

        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({
                "current_password": "Your current password is incorrect."
            })

        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_new_password")

        if not attrs.get("username") and not new_password:
            raise serializers.ValidationError(
                "Enter a new username or a new password."
            )

        if new_password:
            if new_password != confirm_password:
                raise serializers.ValidationError({
                    "confirm_new_password": "The new passwords do not match."
                })

            try:
                validate_password(new_password, user)
            except Exception as exc:
                from django.core.exceptions import ValidationError

                if isinstance(exc, ValidationError):
                    raise serializers.ValidationError({
                        "new_password": list(exc.messages)
                    })
                raise


        elif confirm_password:
            raise serializers.ValidationError({
                "new_password": "Enter a new password first."
            })

        return attrs

    def validate_username(self, value):
        user = self.instance

        if User.objects.exclude(pk=user.pk).filter(
            username__iexact=value
        ).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )

        return value

    def update(self, instance, validated_data):
        validated_data.pop("current_password")
        new_password = validated_data.pop("new_password", None)
        validated_data.pop("confirm_new_password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance