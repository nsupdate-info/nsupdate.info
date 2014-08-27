Standards used
==============

* Frontend Update-API: dyndns2 protocol

  + `dyndns2 api description on dyn.com <http://dyn.com/support/developers/api/>`_
  + `dyndns2 api description on noip.com <http://www.noip.com/integrate/>`_


* Backend: dynamic DNS update

  + `RFC2136 <http://www.ietf.org/rfc/rfc2136.txt>`_


Extensions we made to the standards
===================================

/nic/delete API url
-------------------

The dyndns2 standard does not give a means to delete a DNS record (like A or
AAAA), you can only update to a new address using /nic/update.

Thus, we created a /nic/delete URL that behaves just like the dyndns2 update
api, but removes the A or AAAA record in DNS instead of updating it.

While the update API would actually use the given IP address to put it into
an A or AAAA record, the delete API uses it only to determine the address
type, whether it is IPv6 or v6 and then deletes the A or AAAA record.
