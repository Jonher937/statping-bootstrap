# statping-bootstrap

## Background

statping-ng has an API and I wanted to use it for creating hosts from a YAML document

## How do I add a host?

The script accepts a path to YAML file. Here's an example of what it could look like:

```yaml
---
- name: "Name of my group"
  entries:
    - name: "A host I want to add"
      domain: localhost
    - name: "Some other host"
      domain: 127.0.0.1
      type: icmp
```

The example block defines a group called `Name of my group` with two hosts that would be created.

## How do I run this?

`python3 provision.py my.yaml` where `myhosts.yaml` is your file.


## Default values for service items

Some values are defaulted to match what Statping expects:

|Key|Value|
|--|--|
|expected|""|
|type|"http"|
|method|"GET"|
|post_data|""|
|port|0|
|expected_status|200|
|check_interval|30|
|timeout|30|
|order_id|0|
