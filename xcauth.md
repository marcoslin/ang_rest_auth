# XCAUTH Protocol Implementation Proposal

*NOTE*: Implementation In Progress

## Overview
The purpose of the XCAUTH protocol is to supplement HTTP Basic and Digest Authentication allowing for simplyfied 
authentication requirement of web application and RESTful APIs.  This should be considered a transitional protocol
until better standard becomes available.

XCAUTH's main objective is to improve the following:

1. Avoid tranmission of password
1. Allow for strong hash storage of user's login credentials
1. Allow for webapp to implmenent timeout and logout

The main workflow can be summarized as:

1. Initial authentication **must** be performed under HTTPS
1. `cnonce` is created by client and POST to server
1. Server creates `nonce`, acting like authorization session ID
1. Server generates a `auth-token` and send back to the client
1. `auth-token` is then used to grant access server resouces

Both `cnonce` and `auth-token` are considered secrete and should only be transmitted during the authentication 
and only over SSL connection.

Following Quality of Protection (gop) can be configured for XCAUTH:

* `xauth`:    simple XOR based authentication
* `xauth-nc`: XAUTH with NC
* `xresp`:    XAUTH-NC with hashed uri as Response
* `pkresp`:   Public and Private Key based Auth and Response

For the purpose of this documentation, *Authentication* is define as process of verifying the username and
password, while *Access* is accessing the server resources after *Authentication*.

## `xauth` and `xauth-nc`
This is analogous to HTTP Basic Authentication but it does not send password to the server.  The main purpose
of `xauth` and `xauth-nc` is to minimize the amount of work on the client side.  This is achieved at expense of
security in case the `XAUTH` or `auth-token` is intercepted.  As result, HTTPS based communication is required 
for both Authentication and Access.  For application that performs data modification, the minimum acceptable
level of `gop` is `xauth-nc`.

As the objective of these 2 basic protocol is to minimize the work on the client size, the `cnonce` is only used
during Authentication and not during Access.  As `auth-token` is in effect ignored and `nonce` used for Access,
there is no support access token timeout and only login timeout.

### Formulas

1. `NC` = A simple counter
1. `HA1` = md5(username:realm:password)
1. `XAUTH` = XOR(HA1, cnonce)

**N.B.**: All hash and token is expected to be represented in HEX format

As `NC` in this case is a simple counter, a webapp could simply return the milliseconds since Epoch as `NC`.
For example: 

    var NC = (new Date()).getTime();

### Workflow

#### Authentication

* Client generates `cnonce` and `POST` it with choosen `gop` to server
* Server generates a `nonce` and associate received `cnonce` and `gop` with it.  Reply with `nonce` and `realm`
* Client prompt user for username and password, construct `XAUTH` and send to server
* Server verifies `XAUTH` and reply with user info and `auth-token`

#### Access

* Client sends:
  - `nonce`
  - `NC` -- if gop is set to `xauth-nc`


## `xresp`

This is analogous to HTTP Digest Authentication and build upon `xauth`.  As this `gop` requires `auth-token` for
Access and `XAUTH` for Token Refresh, client must find a secure way of caching these 2 data and only sending back 
to the server during the secured Authorization phase.  This should be easy for Native Code clients but for webapp,
it must rely on localStorage for HTML5 clients or techniques such as [Cookie-less Session][1].  If application loses
these information, server will respond with "401 Unauthorized" forcing the user to login again.

The primary benefit of this `gop` is to allow for HTTP based Access once user has been authenticated.

### Formula:

1. `NC` = A simple counter
1. `HA1` = md5(username:realm:password)
1. `HA2` = md5(method:uri)
1. `XAUTH` = XOR(HA1, cnonce)
1. `XRESP` = md5(auth-token:nonce:nc:HA2)

**N.B.**: All hash and token is expected to be represented in HEX format

### Workflow

#### Authentication

*Same as Authentication for `xauth` and `xauth-nc`*

#### Access

* Client sends:
  - `nonce`
  - `uri`
  - `NC`
  - `XRESP`

#### Token Refresh

* Client sends Access request to server
* Server detects that `auth-token` has expired using `nonce` and reply "401 Timeout"
* Client sends `XAUTH` over HTTPS to server
* Server verifies `XAUTH` and reply with user info and updated `auth-token`

**N.B.**:  If client is enable to reproduce XAUTH, must prompt user to login again using Anthentication workflow

## `pkresp`

This protocol require server generated public/private key pair.  To be defined in the next phase.

## Persistance

As `nonce` is create for every 401 response from server, it can be treated as an Authorized session id.  As result,
it should have long expiry.  There should have a client side equivanlent of `cnonce` and both these value must be
persisted in the non-volatile storage such as RDMS or NoSQL on the server side.  

On the other hand, `auth-token` is expected to expire and therefore it is possible to store it in a volatile storage
such as MEMCACHED or REDIS.

On the client side, if using `gop` of `xresp`, `XAUTH` must be securely stored and only used over HTTPS connections.

In Summary:

1. `nonce` and associated `cnonce` should be stored in the database
1. Client should generate `cnonce` and forget it after the Authorization phase
1. Server should store `nonce` and associated `auth-token` in cache

## Reference

* [RFC 1945/Section 11 -- HTTP 1.0 Access Authentication](http://tools.ietf.org/html/rfc1945#section-11)
* [RFC 2617 -- Basic and Digest Access Authentication](http://tools.ietf.org/html/rfc2617)
* [RFC 2069 -- Digest Access Authentication (Obsoleted by RFC 2617)](http://tools.ietf.org/html/rfc2069)


[1]: http://www.sitepoint.com/javascript-session-variable-library/

