# endstone-bstats

`endstone-bstats` is a Python library that provides functionality for integrating bStats metrics into your Endstone
plugins. It is designed to be simple, extensible, and lightweight.

## Features

- Supports various types of charts, including:
    - Simple Pie
    - Advanced Pie
    - Drilldown Pie
    - Single Line
    - Multi Line
    - Simple Bar
    - Advanced Bar
- Easy-to-use APIs for collecting and sending metric data.
- Designed for flexibility and extensibility.

## Installation

Install the package using pip:

```bash
pip install endstone-bstats
```

## Quick start

[bStats](https://bstats.org/getting-started) is a free and open source website that helps you to collect usage data for
your plugin. Integrating bStats into your plugin is straight forward and done in a matter of seconds.

Here’s a simple example of how to add bStats to your plugin.

```python
from endstone.plugin import Plugin
from endstone_bstats import Metrics


class ExamplePlugin(Plugin):
    def on_enable(self):
        plugin_id = 1234  # <-- Replace with the id of your plugin!
        self._metrics = Metrics(self, plugin_id)

    def on_disable(self):
        self._metrics.shutdown()
```

After adding bStats to your plugin you have to [create an account](https://bstats.org/register) to register your plugin.
You can manage your plugins with this account, e.g. adding customs graphs, etc.

## Add custom charts

Adding charts to your plugin consists of two parts:

- Adding charts to your code
- Adding charts on the website

To add a chart on the website, check the [detailed instructions here](https://bstats.org/help/custom-charts).

A **Simple Pie** is the most basic chart type. It's a great option for config settings as it only accepts one value per
server. Adding the chart to your code is fairly easy:

```python
from endstone.plugin import Plugin
from endstone_bstats import Metrics, SimplePie


class ExamplePlugin(Plugin):
    def on_enable(self):
        plugin_id = 1234  # <-- Replace with the id of your plugin!
        self._metrics = Metrics(self, plugin_id)
        self._metrics.add_custom_chart(
            SimplePie("used_language", lambda: "en_US")
        )

    def on_disable(self):
        self._metrics.shutdown()
```

## Contributing

We welcome contributions! Feel free to open an issue or submit a pull request to improve the library.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

This library is inspired by [bStats for Java](https://bstats.org/), ported by the EndstoneMC team to Python.
