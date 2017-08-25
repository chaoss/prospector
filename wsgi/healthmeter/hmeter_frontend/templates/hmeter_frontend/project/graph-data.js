{% for key, value in data.items %}
window.{{ key }} = {{ value|safe }};
{% endfor %}
