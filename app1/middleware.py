from django.middleware.csrf import get_token
from django.utils.deprecation import MiddlewareMixin

class EnsureCsrfCookieMiddleware(MiddlewareMixin):
    """确保CSRF cookie被设置"""

    def process_request(self, request):
        # 确保CSRF token被生成
        if not request.META.get('CSRF_COOKIE'):
            get_token(request)
        return None