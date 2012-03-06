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
	An enabling glob expression
request_method
	Enabling HTTP request method
portal_type
	Published object's portal type
domain
	Enabling globing globbing expression for the domain
custom
	Custom function to do manual checks against the request object
