# helpers.py
from djangoInt.models import CompanyAuthorization

def fetch_table_name_for_user(user):
    if user.is_authenticated:
        try:
            authorization = CompanyAuthorization.objects.get(user=user)
            return authorization.table_name
        except CompanyAuthorization.DoesNotExist:
            pass
    return 'sample_company'
