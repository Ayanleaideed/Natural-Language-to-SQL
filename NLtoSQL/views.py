from django.shortcuts import render, redirect, HttpResponse

# Create your views here.
def index(request):
  name = 'Doozy'
  return render(request, 'loading.html', {'name': name})



def query_func(request):
  return render(request, 'query.html', {})


def management(request):
  return render(request, 'management.html', {})

def generate_sql(request):
  return render(request, 'generate_sql.html', {})


if __name__ == '__main__':
  debug = True