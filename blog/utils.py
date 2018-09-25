from bs4 import BeautifulSoup


def amplify_html(rendered_html):
    bs = BeautifulSoup(rendered_html)

    for image in bs.find_all('img', attrs={'src': True}):
        amp_img = bs.new_tag(
            'amp-img', src=image.get("src"),
            alt=image.get("alt", ""),
            layout="responsive",
            width=image.get("width", 550),
            height=image.get("height", 368)
        )
        amp_img['class'] = image.get("class", "")
        image.replace_with(amp_img)

    for iframe in bs.find_all('iframe', attrs={'src': True}):
        amp_iframe = bs.new_tag('amp-iframe')
        iframe_src = iframe['src']
        if iframe_src.startswith('//'):
            iframe_src = 'https:{}'.format(iframe_src)
        amp_iframe.attrs['src'] = iframe_src
        if iframe.has_attr('title'):
            amp_iframe.attrs['title'] = iframe['title']
        amp_iframe.attrs['width'] = '200'
        amp_iframe.attrs['height'] = '100'
        amp_iframe.attrs['layout'] = 'responsive'
        amp_iframe.attrs['frameborder'] = iframe.get('frameborder', 0)
        amp_iframe.attrs['sandbox'] = iframe.get(
            'sandbox', 'allow-scripts allow-same-origin')
        iframe.replace_with(amp_iframe)

    # Remove style attribute to remove large bottom padding
    for div in bs.find_all("div", {'class': 'responsive-object'}):
        del div['style']

    return bs.decode_contents()
