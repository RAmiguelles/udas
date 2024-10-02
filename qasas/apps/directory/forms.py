from django import forms


class DirectoryForm(forms.Form):
    bank = forms.IntegerField(label='Bank', required=True)
    account_number = forms.CharField(label='Account Number', required=True)
    account_name = forms.CharField(label='Account Name', required=True)
    account_type = forms.CharField(label='Account Type', required=True)
    account_currency = forms.CharField(label='Currency', required=True)
    account_address = forms.CharField(label='Address', required=True)
    account_city = forms.CharField(label='City', required=True)
    account_country = forms.CharField(label='Country', required=True)
    account_zip_code = forms.CharField(label='Zip Code', required=True)
    account_phone_number = forms.CharField(label='Phone Number', required=True)
    verification_amount = forms.CharField(label='Verification Amount', required=True)
