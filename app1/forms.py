from django.contrib.auth.forms import PasswordChangeForm


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs.update({'class': 'form-control'})
            if field_name == 'old_password':
                field.label = '当前密码'
            elif field_name == 'new_password1':
                field.label = '新密码'
                field.help_text = '密码至少需要8个字符，不能全是数字'
            elif field_name == 'new_password2':
                field.label = '确认新密码'
