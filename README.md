# statping-bootstrap

## Background

statping-ng has an API and I wanted to use it for creating hosts from a YAML document

## How do I add a host?

The script accepts a path to YAML file. Here's an example of what it could look like:

```yaml
---
- name: "Name of my group"
  entries:
    # Minimum is name and domain, defaults to http check
    - name: "A host I want to add"
      domain: localhost
    # Ping Example
    - name: "Some other host"
      domain: 127.0.0.1
      type: icmp
    # Expect a specific http response code
    - name: "Github Current User"
      domain: "https://api.github.com/user"
      expected_status: 401
```

The example block defines a group called `Name of my group` with three hosts that would be created.

## How do I run this?

`python3 provision.py my.yaml` where `myhosts.yaml` is your file.


## Default values for service items

Some values are defaulted to match what Statping expects and can be overridden by providing them on a host

|Key|Value|
|--|--|
|expected|`""`|
|type|`"http"`|
|method|`"GET"`|
|post_data|`""`|
|port|0|
|expected_status|200|
|check_interval|30|
|timeout|30|
|order_id|0|
