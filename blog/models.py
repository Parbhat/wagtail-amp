from django.db import models
from django.template.response import TemplateResponse

from modelcluster.fields import ParentalKey

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, StreamFieldPanel
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from wagtail.contrib.routable_page.models import RoutablePageMixin, route


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

    def get_context(self, request):
        # Update context to include only published posts,
        # ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by(
            '-first_published_at').specific()
        context['blogpages'] = blogpages
        return context

    parent_page_types = ['home.HomePage']


class BlogPage(RoutablePageMixin, Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ])

    @route(r'^amp/$')
    def amp(self, request):
        context = self.get_context(request)
        response = TemplateResponse(
            request, 'blog/blog_page_amp.html', context
        )
        return response

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        StreamFieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

    parent_page_types = ['blog.BlogIndexPage']


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(
        BlogPage, on_delete=models.CASCADE, related_name='gallery_images'
    )
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


class AmpBlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ])

    def get_template_amp(self, request, *args, **kwargs):
        return 'blog/amp_blog_page_amp.html'

    def serve(self, request, *args, **kwargs):
        is_amp_request = kwargs.get('is_amp_request')
        if is_amp_request:
            kwargs.pop('is_amp_request')
            context = self.get_context(request, *args, **kwargs)

            return TemplateResponse(
                request,
                self.get_template_amp(request, *args, **kwargs),
                context
            )
        return super(AmpBlogPage, self).serve(request, *args, **kwargs)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        StreamFieldPanel('body'),
    ]

    parent_page_types = ['blog.BlogIndexPage']
