from django.shortcuts import render


def index(request):
    return render(request, "graph_viz/index.html")


def vue(request):
    return render(request, "graph_viz/vue.html")


def buefy(request):
    return render(request, "graph_viz/buefy.html")


def vuetify(request):
    return render(request, "graph_viz/vuetify.html")
