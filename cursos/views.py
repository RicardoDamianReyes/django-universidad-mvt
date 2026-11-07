from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Curso, Profesor, Estudiante
from .forms import CursoForm, EstudianteForm, ProfesorForm

# Vistas de función originales
def lista_cursos(request):
    cursos = Curso.objects.all()
    return render(request, 'cursos/lista.html', {'cursos': cursos})

def lista_profesores(request):
    profesores = Profesor.objects.all()
    return render(request, 'cursos/lista_profesores.html', {'profesores': profesores})

def detalle_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    return render(request, 'cursos/detalle.html', {'curso': curso})


# 1. VISTAS PÚBLICAS (con Paginación)
class CursoListView(ListView):
    model = Curso
    template_name = 'cursos/lista.html'
    context_object_name = 'cursos'
    paginate_by = 6  # Muestra máximo 6 cursos por página
    ordering = ['titulo']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('profesor')
        query = self.request.GET.get('q', '').strip()  # Captura el parámetro ?q= de la URL

        if query:
            # Filtra en el título OR en la descripción OR en el nombre del profesor
            queryset = queryset.filter(
                Q(titulo__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(profesor__nombre__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Envía el término buscado a la plantilla para conservar el texto en el input
        context['query'] = self.request.GET.get('q', '').strip()
        return context

class CursoDetailView(DetailView):
    model = Curso
    template_name = 'cursos/detalle.html'
    context_object_name = 'curso'

class ProfesorListView(ListView):
    model = Profesor
    template_name = 'cursos/lista_profesores.html'
    context_object_name = 'profesores'
    paginate_by = 3
    ordering = ['nombre']

class ProfesorDetailView(DetailView):
    model = Profesor
    template_name = 'cursos/profesor_detalle.html'
    context_object_name = 'profesor'



class CursoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Curso
    form_class = CursoForm
    template_name = 'cursos/formulario.html'
    success_url = reverse_lazy('web_lista_cursos')
    success_message = "¡El curso '%(titulo)s' fue creado exitosamente!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Crear Nuevo Curso (Protegido)'
        return context

class CursoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Curso
    form_class = CursoForm
    template_name = 'cursos/formulario.html'
    success_url = reverse_lazy('web_lista_cursos')
    success_message = "¡El curso '%(titulo)s' fue actualizado correctamente!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Curso: {self.object.titulo}'
        return context

class CursoDeleteView(LoginRequiredMixin, DeleteView):
    model = Curso
    template_name = 'cursos/curso_confirm_delete.html'
    success_url = reverse_lazy('web_lista_cursos')
    context_object_name = 'curso'

    def form_valid(self, form):
        messages.warning(self.request, f"El curso '{self.object.titulo}' fue eliminado del sistema.")
        return super().form_valid(form)


class LoginBienvenidaView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        messages.info(self.request, f"¡Bienvenido, {form.get_user().username}!")
        return super().form_valid(form)


# ESTUDIANTES (CRUD completo con CBV)
class EstudianteListView(ListView):
    model = Estudiante
    template_name = 'cursos/lista_estudiantes.html'
    context_object_name = 'estudiantes'
    paginate_by = 5
    ordering = ['nombre']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '').strip()

        if query:
            # Filtra en el nombre OR en el correo del estudiante
            queryset = queryset.filter(
                Q(nombre__icontains=query) |
                Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context


class EstudianteDetailView(DetailView):
    model = Estudiante
    template_name = 'cursos/estudiante_detalle.html'
    context_object_name = 'estudiante'


class EstudianteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Estudiante
    form_class = EstudianteForm
    template_name = 'cursos/formulario.html'
    success_url = reverse_lazy('web_lista_estudiantes')
    success_message = "¡El estudiante '%(nombre)s' fue registrado exitosamente!"
    extra_context = {'titulo': 'Registrar Nuevo Estudiante', 'volver_url': reverse_lazy('web_lista_estudiantes')}


class EstudianteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Estudiante
    form_class = EstudianteForm
    template_name = 'cursos/formulario.html'
    success_url = reverse_lazy('web_lista_estudiantes')
    success_message = "¡El estudiante '%(nombre)s' fue actualizado correctamente!"
    extra_context = {'volver_url': reverse_lazy('web_lista_estudiantes')}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Estudiante: {self.object.nombre}'
        return context


class EstudianteDeleteView(LoginRequiredMixin, DeleteView):
    model = Estudiante
    template_name = 'cursos/estudiante_confirm_delete.html'
    success_url = reverse_lazy('web_lista_estudiantes')
    context_object_name = 'estudiante'

    def form_valid(self, form):
        messages.warning(self.request, f"El estudiante '{self.object.nombre}' fue eliminado del sistema.")
        return super().form_valid(form)


# PROFESORES (crear, editar y eliminar con CBV)
class ProfesorCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Profesor
    form_class = ProfesorForm
    template_name = 'cursos/formulario.html'
    success_url = reverse_lazy('lista_profesores')
    success_message = "¡El profesor '%(nombre)s' fue registrado exitosamente!"
    extra_context = {'titulo': 'Registrar Nuevo Profesor', 'volver_url': reverse_lazy('lista_profesores')}


class ProfesorUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Profesor
    form_class = ProfesorForm
    template_name = 'cursos/formulario.html'
    success_url = reverse_lazy('lista_profesores')
    success_message = "¡El profesor '%(nombre)s' fue actualizado correctamente!"
    extra_context = {'volver_url': reverse_lazy('lista_profesores')}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Profesor: {self.object.nombre}'
        return context


class ProfesorDeleteView(LoginRequiredMixin, DeleteView):
    model = Profesor
    template_name = 'cursos/profesor_confirm_delete.html'
    success_url = reverse_lazy('lista_profesores')
    context_object_name = 'profesor'

    def form_valid(self, form):
        messages.warning(self.request, f"El profesor '{self.object.nombre}' fue eliminado del sistema.")
        return super().form_valid(form)
