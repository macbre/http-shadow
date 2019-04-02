# http-shadow
Compares HTTP responses from two different backends

### How to run

1. Set up virtualenv with python 3
2. Install dependencies by running `python setup.py develop`
3. Run the following (preferrably in `screen`):

```
get_urls | check_urls
```

This will pipe URLs found in Apache access log to the process that will perform two requests: to Apache and to Kubernetes. Response code and headers will be compared and results logged via syslog with `http-shadow` ident.

4. To compare production vs k8s-powered sandbox use:
```
get_urls | check_urls <sandbox name, e.g. sandbox-s6>
```

### Log entry example

```json
{
  "appname": "http-shadow",
  "is_ok": true,
  "url": "http://muppet.fandom.com/wiki/Elmo",
  "apache": {
    "response": {
      "status_code": 200,
      "location": null,
      "cache_control": "s-maxage=86400, must-revalidate, max-age=0",
      "content_type": "text/html; charset=utf-8"
    },
    "info": {
      "x_served_by": "ap-s204",
      "x_response_time": 0.083
    }
  },
  "kube": {
    "response": {
      "status_code": 200,
      "location": null,
      "cache_control": "s-maxage=86400, must-revalidate, max-age=0",
      "content_type": "text/html; charset=utf-8"
    },
    "info": {
      "x_served_by": "mediawiki-sandbox-s6-99597bbd4-f2h7q",
      "x_response_time": 0.124
    }
  }
}
```

### Tests

Run `py.test`.
