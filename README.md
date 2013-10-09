Rewrites
========

As the years keep passing,
I keep migrating my personal web site from one solution to another.
This has the nasty side effect that URLs of things change.
To prevent link rot,
I used to keep *mod_rewrite* rules for every such change.
After a few iterations,
this was a big bunch of rewrite rules.

This daemon is meant to obsolete that.
URLs tend to differ in the crud:
controllers, categories and file extensions.
The important part,
which represents the title of the page in question,
is pretty much constant and unique.
Therefore,
when requested a non-existent URL,
it is enough to search for one with matching basename among the existing.
