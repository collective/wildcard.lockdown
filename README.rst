Introduction
============

The intent of this package is to be able to make your plone
site completely read-only except for a set of conditions
that can be defined and enabled/disabled.


Adding a commit condition
-------------------------

An example commit rule::

	from wildcard.lockdown import addCommitCondition
	addCommitCondition("User Area",
		path="/someuserarea/*")
	addCommitCondition("R/W domain",
		host="backend.testsite.com")

You'll then need to enable them in the control panel.


addCommitCondition parameters
-----------------------------

name(required)
	Name of condition that'll show up in the management inteface
path
	An enabling glob expression. This path is always based off the relative
	Plone site, not the Zope root.
request_method
	Enabling HTTP request method
portal_type
	Published object's portal type
host
	Enabling globing globbing expression for the host name
logged_in
	require user to be logged in
custom
	Custom function to do manual checks against the request object.
	Return True if you want to commit, false if not.


Every rule parameter in the commit condition will need to be valid
in order for the condition to successfully allow the commit.

Only one condition needs to be valid on the request in order for the
commit to take place.


Web API
-------

The ``@@manage-lockdown`` view allows to get and set the add-on options.

Using the ``GET`` method with no parameters the view returns the options as
a JSON encoded mapping.

The ``POST`` method allows to set options, passing them on the query string.
The Zope 2 form marshalling is used. This means:

- For boolean options, use ``name:boolean`` as the key and ``True`` or
  ``False`` as the value. Case matters. Example: ``enabled:boolean=True``.
- For strings use ``name:ustring`` as the key. Example:
  ``status_message:ustring=My String`` as the key.
- For lists use ``name:list:type`` as the key, where type is ``boolean``,
  ``ustring``, ``int``, etc. Repeat the key to add more items to the list.
  Example: ``activated:list:ustring=Condition 1&activated:list:ustring=Condition 2``.


Examples
^^^^^^^^

Here are some examples using HTTPie_ from the command line. Assume the Plone
site is at ``http://127.0.0.1:8080/Plone`` and there's an ``admin`` user with
password ``admin``.


Set options: ``enabled=True``, ``activated=[u'Manager user, u'Web API']`` and
``status_message=u'The site is currently in read-only mode.'``.

.. code-block:: bash

	http -a admin:admin POST "http://127.0.0.1:8080/Plone/@@manage-lockdown?\
	enabled:boolean=True&\
	activated:list:ustring=Manager user&\
	activated:list:ustring=Web API&\
	status_message:ustring=The site is currently in read-only mode."

Output:

.. code-block:: json

	"OK"

Get the options:

.. code-block:: bash

	http -a admin:admin GET "http://127.0.0.1:8080/Plone/@@manage-lockdown"

Output:

.. code-block:: json

	{
	    "activated": [
	        "Manager user",
	        "Web API"
	    ],
	    "enabled": true,
	    "status_message": "The site is currently in read-only mode."
	}


.. References:
.. _HTTPie: https://httpie.org
