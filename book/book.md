---
layout: page
title: "BOOK"
description: "A reader lives a thousand lives before he dies - George R.R. Martin"
header-img: "img/baby6.jpg"
header-mask: 0.3
---

{% for post in site.categories.book %}
<div class="post-preview">
    <a href="{{ post.url | prepend: site.baseurl }}">
        <h2 class="post-title">
            {{ post.title }}
        </h2>
        {% if post.subtitle %}
        <h3 class="post-subtitle">
            {{ post.subtitle }}
        </h3>
        {% endif %}
        <div class="post-content-preview">
            {% if post.lang == 'en' %}
                {{ post.content | strip_html | truncate:300 }}
            {% else %}
                {{ post.content | strip_html | truncate:200 }}
            {% endif %}
        </div>
    </a>
    <p class="post-meta">
        Posted by {% if post.author %}{{ post.author }}{% else %}{{ site.title }}{% endif %} on {{ post.date | date: "%B %-d, %Y" }}
    </p>
</div>
<hr>
{% endfor %}

<!-- Pager -->
{% if site.categories.book.total_pages > 1 %}
<ul class="pager">
    {% if site.categories.book.previous_page %}
    <li class="previous">
        <a href="{{ site.categories.book.previous_page_path | prepend: site.baseurl | replace: '//', '/' }}">&larr; Newer Posts</a>
    </li>
    {% endif %}
    {% if site.categories.book.next_page %}
    <li class="next">
        <a href="{{ site.categories.book.next_page_path | prepend: site.baseurl | replace: '//', '/' }}">Older Posts &rarr;</a>
    </li>
    {% endif %}
</ul>
{% endif %}
