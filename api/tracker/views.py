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
        ticket_status = get_ticket_status(self.object)
        context["status"] = ticket_status[1]
        context["status_dt"] = ticket_status[0]

        print(self.object.ticket_approved_dt)

        return context


# get the ticket status based on the date time history
def get_ticket_status(ticket):
    if ticket.ticket_rejected_dt:
        return (ticket.ticket_rejected_dt, STATUS_TYPES[0])
    elif ticket.data_accepted_dt:
        return (ticket.data_accepted_dt, STATUS_TYPES[6])
    elif ticket.data_uploaded_completed_dt:
        return (ticket.data_uploaded_completed_dt, STATUS_TYPES[5])
    elif ticket.data_uploaded_started_dt:
        return (ticket.data_uploaded_started_dt, STATUS_TYPES[4])
    elif ticket.bucket_created_dt:
        return (ticket.bucket_created_dt, STATUS_TYPES[3])
    elif ticket.ticket_approved_dt:
        return (ticket.ticket_approved_dt, STATUS_TYPES[2])
    else:
        return (ticket.ticket_created_dt, STATUS_TYPES[1])


STATUS_TYPES = {
    0: "Data Intake Form Rejected",
    1: "Ready for Bucket Creation",
    2: "Bucket Created; Ready for Data upload",
    3: "Ready for Data upload",
    4: "Data upload in Progress",
    5: "Data upload Complete",
    6: "Gen3 Accepted",
}
