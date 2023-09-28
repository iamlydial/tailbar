from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from item.models import Item
from .models import Conversation
from .forms import ConversationMessagesForm
from django.http import HttpResponse  # Import HttpResponse

@login_required
# Create your views here.
def new_conversation(request, item_pk):
    # Retrieve the item with the specified primary key from the database, or return a 404 error if not found
    item = get_object_or_404(Item, pk=item_pk)

    # Check if the user requesting the conversation is also the creator of the item
    if item.created_by == request.user:
        # If the user is the creator, redirect them to the dashboard
        return redirect('dashboard:index')

    # Query the database to find existing conversations related to the item and involving the current user
    conversations = Conversation.objects.filter(item=item).filter(members__in=[request.user.id])

    if conversations:
        # If conversations exist, we can potentially redirect to one of them
        return redirect('conversation:detail', pk=conversations.first().id)

    # Check if the HTTP request method is POST (i.e., form submission)
    if request.method == 'POST':
        # Create a form instance using the data submitted in the POST request
        form = ConversationMessagesForm(request.POST)

        # Check if the form data is valid
        if form.is_valid():
            # Create a new conversation associated with the item
            conversation = Conversation.objects.create(item=item)

            # Add the current user and the item's creator as members of the conversation
            conversation.members.add(request.user)
            conversation.members.add(item.created_by)

            # Save the conversation to the database
            conversation.save()

            # Create a conversation message using the form data
            conversation_message = form.save(commit=False)
            
            # Associate the message with the newly created conversation and the current user
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user

            # Save the message to the database
            conversation_message.save()

            # Redirect to the item's detail page
            return redirect('item:detail', pk=item_pk)
        else:
            # If the form data is not valid, create a new empty form
            form = ConversationMessagesForm()

    else:  # Add an else block for non-POST requests
        # Create a form instance for non-POST requests
        form = ConversationMessagesForm()

    # Render the 'conversation/new.html' template with the form
    return render(request, 'conversation/new.html', {
        'form': form
    })

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(members__in=[request.user.id])
    return render(request, 'conversation/inbox.html', {
        'conversations': conversations
    })

@login_required
def detail(request, pk):
    conversation = Conversation.objects.filter(members__in=[request.user.id]).get(pk=pk)

    if request.method == 'POST':
        form = ConversationMessagesForm(request.POST)
        if form.is_valid():
            conversation_message = form.save(commit=False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user

            conversation.save()

            return redirect('conversation', pk=pk)
    else: 
        form=ConversationMessagesForm()
    

    return render(request, 'conversation/detail.html', {
        'conversation': conversation, 
        'form': form
    })