from django.db import models
from django.http import Http404

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel


class HomePage(Page):
    body = RichTextField(blank=True)

    def route(self, request, path_components):
        # Check the request is for AMP page
        is_amp_request = False
        if path_components and path_components[0] == 'amp':
            is_amp_request = True
            # Remove the amp from path components to check if the page exist
            path_components = path_components[1:]

        page, args, kwargs = super(HomePage, self).route(
            request, path_components
        )
        if is_amp_request:
            # If the page has amp template serve it otherwise raise 404
            if hasattr(page, 'get_template_amp'):
                kwargs['is_amp_request'] = is_amp_request
            else:
                raise Http404

        return page, args, kwargs

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]

    parent_page_types = ['wagtailcore.Page']
