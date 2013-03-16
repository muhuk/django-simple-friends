=================
Package Reference
=================

How to display a list of friends for a user
===========================================

Use :func:`~friends.templatetags.friends_tags.friends` template filter to
obtain a :class:`~django.db.models.query.QuerySet` containing the
:class:`~django.contrib.auth.models.User`\ 's who are friends with the filter's
argument::


    {% load friends  %}
    <h3>Friends</h3>
    <ul>{% for friend in user|friends %}
      <li>{{ friend.get_full_name }}</li>
    {% endfor %}</ul>


The code above should produce a result like this::


    <h3>Friends</h3>
    <ul>
      <li>Lenda Murray</li>
      <li>Sharon Bruneau</li>
      <li>Cory Everson</li>
    </ul>
