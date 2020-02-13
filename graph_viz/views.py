from django.shortcuts import render


def index(request):
    return render(request, "graph_viz/index.html")


def vue(request):
    return render(request, "graph_viz/testing_js_frameworks/vue.html")


def buefy(request):
    return render(request, "graph_viz/testing_js_frameworks/buefy.html")


def vuetify(request):
    return render(request, "graph_viz/testing_js_frameworks/vuetify.html")
