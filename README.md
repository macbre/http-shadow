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

4. To compare two sandboxes use:
```
get_urls | check_urls <apache-based sandbox> <k8s-based sandbox>
```

### Log entry example

```
Mar  4 20:55:32 debian backend[11046]: {"appname": "http-shadow", "is_ok": true, "url": "http://logosfake.wikia.com/wiki/Syco_Technologies", "apache": {"response": {"status_code": 301, "location": "http://logosfake.fandom.com/wiki/Syco_Technologies", "cache_control": "s-maxage=1200, must-revalidate, max-age=0", "content_type": "text/html; charset=utf-8", "surrogate_key": "wiki-798185 wiki-798185-mediawiki"}, "info": {"x_served_by": "ap-s265"}}, "kube": {"response": {"status_code": 301, "location": "http://logosfake.fandom.com/wiki/Syco_Technologies", "cache_control": "s-maxage=1200, must-revalidate, max-age=0", "content_type": "text/html; charset=utf-8", "surrogate_key": "wiki-798185 wiki-798185-mediawiki"}, "info": {"x_served_by": "mediawiki-prod-6db7584985-rl8k5"}}}
```

```json
{
  "appname": "http-shadow",
  "is_ok": true,
  "url": "http://logosfake.wikia.com/wiki/Syco_Technologies",
  "apache": {
    "response": {
      "status_code": 301,
      "location": "http://logosfake.fandom.com/wiki/Syco_Technologies",
      "cache_control": "s-maxage=1200, must-revalidate, max-age=0",
      "content_type": "text/html; charset=utf-8",
      "surrogate_key": "wiki-798185 wiki-798185-mediawiki"
    },
    "info": {
      "x_served_by": "ap-s265"
    }
  },
  "kube": {
    "response": {
      "status_code": 301,
      "location": "http://logosfake.fandom.com/wiki/Syco_Technologies",
      "cache_control": "s-maxage=1200, must-revalidate, max-age=0",
      "content_type": "text/html; charset=utf-8",
      "surrogate_key": "wiki-798185 wiki-798185-mediawiki"
    },
    "info": {
      "x_served_by": "mediawiki-prod-6db7584985-rl8k5"
    }
  }
}
```

### Tests

Run `py.test`.
