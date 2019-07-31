from django.http import HttpResponse


def download(filename, content):
    response = HttpResponse(content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename  # force browser to download file
    response.write(content)
    return response
