from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Item
from .forms import NewItemForm, EditItemForm


# Create your views here.
def detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    relates_items = Item.objects.filter(category = item.category, is_sold=False).exclude(pk=pk)[0:3]

    return render(request, 'item/detail.html', {
        'item': item,
        'related_items' : relates_items
    })

@login_required
def new(request):
    # Check if the HTTP request method is POST (usually when a form is submitted).
    if request.method == 'POST':
        # Create a form instance with the data from the POST request and any uploaded files.
        form = NewItemForm(request.POST, request.FILES)

        # Check if the form data is valid.
        if form.is_valid():
            # Create a new item object but don't save it to the database yet (commit=False).
            item = form.save(commit=False)
            
            # Set the 'created_by' field of the item to the current user.
            item.created_by = request.user
            
            # Save the item to the database.
            item.save()

            # Redirect the user to the detail view of the newly created item.
            return redirect('item:detail', pk=item.id)
    else:
        # If it's a GET request or the form is not valid, create an empty form to display.
        form = NewItemForm()

    return render(request, 'item/form.html', {
        'form': form, 
        'title': 'New Item'
    })

@login_required
def delete(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)
    item.delete()

    return redirect('dashboard:index')

@login_required
def edit(request, pk):
    item = get_object_or_404(Item, pk=pk, created_by=request.user)
    # Check if the HTTP request method is POST (usually when a form is submitted).
    if request.method == 'POST':
        # Create a form instance with the data from the POST request and any uploaded files.
        form = EditItemForm(request.POST, request.FILES, instance=item)

        # Check if the form data is valid.
        if form.is_valid():
            form.save()

            # Redirect the user to the detail view of the newly created item.
            return redirect('item:detail', pk=item.id)
    else:
        # If it's a GET request or the form is not valid, create an empty form to display.
        form = EditItemForm(instance=item)

    return render(request, 'item/form.html', {
        'form': form, 
        'title': 'Edit Item'
    })