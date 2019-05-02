# Africa Swift Test Bed hackathon

Patched scripts to supply Forest with data for Africa Swift meeting. Operational UM model data is difficult to process, for very sensible reasons it has different levels and diagnostics at every forecast length. The tools that process this data should be simple as to make the suite robust 

# Suite.rc changes to parallelise slow processing

The following snippets can be used to convert the slow processing task `highway_testbed` into 19 small tasks that can each send one file to AWS

### 1: Define HOURS at the top of suite.rc
```
{% set HOURS = [
    '000',
    '003',
    '006',
    '009',
    '012',
    '015',
    '018',
    '021',
    '024',
    '027',
    '030',
    '033',
    '036',
    '039',
    '042',
    '045',
    '048',
    '051',
    '054'
] %}
```

The above variable can be used for iteration in the rest of suite.rc

### 2: Update graph dependencies

```
[[T1H]]]
graph = """
{% for H in HOURS %}
    highway_testbed_{{H}}:finish => highway_testbed_aws
    ...
{% endfor %}
"""
```

The various graph dependencies can be replicated with a loop
so that the AWS task waits for the processing tasks to complete
or a separate AWS task can be invoked for each file.

### 3: Update CLOCK_TRIGGERED task list

```
{% set TASKS = [] %}
{% for H in HOURS %}
    {% do TASKS.append('highway_testbed_' + H) %}
{% endfor %}
CLOCK_TRIGGERED = {{ TASKS | join(' ') }}
```

This is tricky due to Jinja2's scoping rules, but in my previous experience
`do` statements can be used to append to lists. To know whether or not this
has worked try

```
cat ~meso/cylc-run/forest/suite.rc.processed | grep --color CLOCK
```

### 4: Define additional tasks almost identical to the single task case

```
[[HIGHWAY_TESTBED]]
   ...

{% for H in HOURS %}
    [[highway_testbed_{{H}}]]
        inherit = HIGHWAY_TESTBED
        ...
        [[[environment]]]
            HOUR={{H}}  # Upgrade default.sh to use this variable
{% endfor %}
```

The only major difference between the one task processing all hours and having separate tasks per hour is the environment that gets passed to `app/bin/default.sh`, minor modifications of the shell script might be needed to make it work

