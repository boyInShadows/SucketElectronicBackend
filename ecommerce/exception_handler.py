from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if response.status_code == 403:
            response.data['detail'] = 'شما اجازه انجام این عملیات را ندارید.'
        elif response.status_code == 404:
            response.data['detail'] = 'موردی یافت نشد.'
        elif response.status_code == 400 and 'detail' not in response.data:
            response.data['detail'] = 'درخواست نامعتبر است.'
        elif response.status_code >= 500:
            response.data['detail'] = 'خطای سرور. لطفا بعدا تلاش کنید.'
    return response 