from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, TemplateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy

from .models import Ticket

# initiate a submission ticket
# def create_ticket(request):
#     if request.method == "POST":
#         form = TicketCreateUpdateForm(request.POST)
#         if form.is_valid():
#             # Do something with the form data like send an email.
#             return HttpResponseRedirect(reverse('confirm_initiated_ticket'))
#     else:
#         form = SubmissionForm()
#
#     return render(request, 'tracker/initiate_ticket.html', {'form': form})


class IndexView(TemplateView):
    template_name = "tracker/index.html"


class TicketCreate(CreateView):
    model = Ticket
    fields = [
        "email",
        "name",
        "organization",
        "study_name",
        "dataset_description",
        "is_test_data",
        "google_email",
        "aws_iam",
        "data_size",
        "study_id",
        "consent_code",
    ]

    def form_valid(self, form):
        ticket_obj = form.save(commit=True)
        # FIXME - add checks here
        return super().form_valid(form)


# FIXME - see https://docs.djangoproject.com/en/3.2/topics/class-based-views/generic-editing/ for adding auth
class TicketUpdate(UpdateView):
    model = Ticket
    fields = [
        "email",
        "name",
        "organization",
        "study_name",
        "dataset_description",
        "is_test_data",
        "google_email",
        "aws_iam",
        "data_size",
        "study_id",
        "consent_code",
    ]


class TicketDelete(DeleteView):
    model = Ticket
    success_url = reverse_lazy("tracker:tickets-list")


class TicketsList(ListView):
    model = Ticket


class TicketDetail(DetailView):
    model = Ticket
    context_object_name = "ticket"

    def get_context_data(self, *args, **kwargs):
        context = super(DetailView, self).get_context_data(*args, **kwargs)

        # Compute ticket status and add to context
        # ticket_status = get_ticket_status(self.object)
        # context["status"] = ticket_status[1]
        # context["status_dt"] = ticket_status[0]

        return context
