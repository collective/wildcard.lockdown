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
		domain="backend.testsite.com")

You'll then need to enable them in the control panel.


addCommitCondition parameters
-----------------------------

name(required)
	Name of condition that'll show up in the management inteface
path
	An enabling glob expression. This path is always based of the relative
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
